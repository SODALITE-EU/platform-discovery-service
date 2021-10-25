import pytest

from pds.api.controllers.default import discover, subscribe


class TestControllers:
    @pytest.fixture
    def discovery_input(self):
        inputs = {
                        "inputs":
                        {
                            "frontend-address": "14.15.11.12",
                            "user": "alexander",
                            "_storage_key": "STORAGE_KEY"
                        },
                        "namespace": "TestSlurm",
                        "platform_type": "slurm"
                    }
        return inputs

    @pytest.fixture
    def subscription_test_inputs(self):
        return {
            "invalid_endpoint": {
                "endpoint": "http://some - host . de:7777/abc"
            },
            "valid_endpoint": {
                "endpoint": "http://some-host.de:7777/abc"
            }
        }

    def test_discovery(self, mocker, flask_app, discovery_input):
        def get_token_info(_):
            return {
                        "token_info":
                        {
                            "preferred_username": "test"
                        }
                   }
        with flask_app.app.test_request_context():
            request = mocker.patch("connexion.request")
            request.is_json = True
            mocker.patch("pds.api.service.discovery.opera_deploy")
            mocker.patch("pds.api.service.discovery.opera_outputs",
                         return_value={"output": {"value": "test"}})
            mocker.patch("pds.api.storages.safe_storage.SafeStorage.create")
            mocker.patch("os.chdir")
            mocker.patch("pds.api.service.security.get_access_token",
                         return_value="TEST_TOKEN")
            mocker.patch("pds.api.utils.inputs.preprocess_inputs")
            context = mocker.patch("connexion.context")
            context.get = get_token_info
            flask_app.app.config['OIDC_INTROSPECTION_ENDPOINT'] = ""
            mocker.patch("connexion.request.get_json",
                         return_value=discovery_input)
            result = discover()
            assert result[1] == 200

            mocker.patch("pds.api.service.discovery.opera_deploy", side_effect=Exception("Test error"))
            result = discover()
            assert result[1] == 500
            assert result[0]["message"] == "Test error"


    def test_subscription(self, mocker, flask_app, subscription_test_inputs):
        with flask_app.app.test_request_context():
            request = mocker.patch("connexion.request")
            request.is_json = True
            mocker.patch("pds.api.service.security.get_access_token",
                         return_value="TEST_TOKEN")
            flask_app.app.config['OIDC_INTROSPECTION_ENDPOINT'] = ""
            inputs = subscription_test_inputs

            mocker.patch("connexion.request.get_json",
                         return_value=inputs["invalid_endpoint"])
            result = subscribe()
            assert result[1] == 400

            mocker.patch("connexion.request.get_json",
                         return_value=inputs["valid_endpoint"])
            result = subscribe()
            assert result[1] == 200
