import pytest
import pds.api.utils.templates as templates
import pds.api.utils.inputs as inputs
from unittest.mock import MagicMock
from pds.api.utils.notifier import Notifier
from pds.api.openapi.models.platform_type import PlatformType
from pds.api.openapi.models.subscription_input import SubscriptionInput
from requests import RequestException
from requests import Response


class TestUtils:
    @pytest.fixture
    def inputs_dict_ssh(self):
        inputs = {
                  "frontend-address": "14.15.11.12",
                  "user": "alexander",
                  "_get_secret_ssh": "pds/ssh_key_slurm:pds",
                  "namespace": "TestSlurm"
                 }

        return inputs

    @pytest.fixture
    def inputs_dict_simple(self):
        inputs = {
                "frontend-address": "14.15.11.12",
                "user": "alexander",
                "namespace": "TestSlurm"
                }

        return inputs

    @pytest.fixture
    def subscription_test_inputs(self):
        return {
            "only_endpoint": SubscriptionInput("namespace-1", "http://some-host.de:7777/abc"),
            "endpoint_with_payload": SubscriptionInput("namespace-1","http://some-host.de:6666/abc", { "some": "data" }),
            "different_namespace": SubscriptionInput("namespace-2","http://some-host.de:5555/abc"),
        }

    def test_templates(self, flask_app):
        with flask_app.app.app_context():
            bp_name = templates.get_service_template(PlatformType.AWS)
            assert bp_name[1] == "aws_info.yaml"
            bp_name = templates.get_service_template(PlatformType.SLURM)
            assert bp_name[1] == "slurm_wm_info.yaml"
            bp_name = templates.get_service_template(PlatformType.OPENSTACK)
            assert bp_name[1] == "openstack_info.yaml"
            bp_name = templates.get_service_template(PlatformType.TORQUE)
            assert bp_name[1] == "torque_wm_info.yaml"
            bp_name = templates.get_service_template(PlatformType.KUBERNETES)
            assert bp_name[1] == "kubernetes_info.yaml"

    def test_preprocess_ssh(self, mocker, flask_app, inputs_dict_ssh):
        def get_json():
            return {
                        "data":
                        {
                            "_ssh_key": "test"
                        }
                   }
        with flask_app.app.app_context():
            get_response = MagicMock()
            get_response.json = get_json
            mocker.patch("pds.api.utils.vault_client.session.get",
                         return_value=get_response)
            mocker.patch("pds.api.utils.vault_client.session.post")
            result = inputs.preprocess_inputs(inputs_dict_ssh,
                                              "ACCESS_TOKEN",
                                              "testNamespace")
            assert len(result[0]) == 3
            assert len(result[1]) == 1
            assert result[1][0] == "test"

    def test_preprocess_simple(self, mocker, flask_app, inputs_dict_simple):
        with flask_app.app.app_context():
            result = inputs.preprocess_inputs(inputs_dict_simple,
                                              "",
                                              "testNamespace")
            assert len(result[0]) == 3
            assert len(result[1]) == 0
            assert result[0]["namespace"] == "testNamespace"

    def test_notifier_reset_subscribers(self, subscription_test_inputs):
        Notifier.reset_subscribers()
        assert len(Notifier.get_subscribers()) == 0

    def test_notifier_add_subscriber(self, subscription_test_inputs):
        inputs = subscription_test_inputs
        Notifier.reset_subscribers()

        Notifier.add_subscriber(inputs["only_endpoint"])
        assert len(Notifier.get_subscribers()) == 1
        assert Notifier.get_subscribers()[0].namespace == inputs["only_endpoint"].namespace
        assert Notifier.get_subscribers()[0].endpoint == inputs["only_endpoint"].endpoint

        Notifier.add_subscriber(inputs["endpoint_with_payload"])
        assert len(Notifier.get_subscribers()) == 2
        assert Notifier.get_subscribers()[1].namespace == inputs["endpoint_with_payload"].namespace
        assert Notifier.get_subscribers()[1].endpoint == inputs["endpoint_with_payload"].endpoint
        assert Notifier.get_subscribers()[1].payload == inputs["endpoint_with_payload"].payload

    def test_notifier_notify_subscribers(self, mocker, flask_app, subscription_test_inputs):
        with flask_app.app.app_context():
            flask_app.app.config['SUBSCRIBER_TIMEOUT'] = "5"

            inputs = subscription_test_inputs
            Notifier.reset_subscribers()

            Notifier.add_subscriber(inputs["only_endpoint"])
            mocker.patch("requests.post")
            assert len(Notifier.notify_subscribers("namespace-1")) == 0

            Notifier.add_subscriber(inputs["endpoint_with_payload"])
            mocker.patch("requests.post", side_effect=RequestException("Connection errors"))
            assert len(Notifier.notify_subscribers("namespace-1")) == 2

            response_404=Response()
            response_404.status_code = 404
            mocker.patch("requests.post", return_value=response_404)
            assert len(Notifier.notify_subscribers("namespace-1")) == 2

            response_503=Response()
            response_503.status_code = 503
            mocker.patch("requests.post", return_value=response_503)
            assert len(Notifier.notify_subscribers("namespace-1")) == 2

            Notifier.add_subscriber(inputs["different_namespace"])
            mocker.patch("requests.post", side_effect=RequestException("Connection errors"))
            # still 2 failed subscribers, since new subscriber is of different namespace
            assert len(Notifier.notify_subscribers("namespace-1")) == 2