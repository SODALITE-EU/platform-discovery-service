import pytest
import pds.api.utils.templates as templates
import pds.api.utils.inputs as inputs
from unittest.mock import MagicMock
from pds.api.utils.environment import DeploymentEnvironment
from pds.api.openapi.models.platform_type import PlatformType


class TestUtils:

    @pytest.fixture
    def inputs_dict(self):
        inputs = {
                "frontend-address": "14.15.11.12",
                "user": "alexander",
                "_get_secret_ssh": "pds/ssh_key_slurm:pds",
                "_ssh_password": "my_password",
                "namespace": "TestSlurm"
                }

        return inputs

    @pytest.fixture
    def inputs_dict(self):
        inputs = {
                "frontend-address": "14.15.11.12",
                "user": "alexander",
                "_get_secret_ssh": "pds/ssh_key_slurm:pds",
                "_ssh_password": "my_password",
                "namespace": "TestSlurm",
                "_storage_key": "TEST_STORAGE_KEY"
                }

        return inputs

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

    def test_environment_setup(self, mocker, flask_app):
        with flask_app.app.app_context():
            mocker.patch("pds.api.utils.environment.opera_deploy")
            mocker.patch("pds.api.utils.environment.opera_undeploy")
            ssh_keys = [("TEST_KEY", "TEST_PASS")]
            env_vars = ["TEST_VAR"]
            env = DeploymentEnvironment()
            env.setup(ssh_keys, env_vars)
            assert len(env.deployments) == 1
            env.cleanup()
            assert len(env.deployments) == 1

    def test_preprocess(self, mocker, flask_app, inputs_dict):
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
            mocker.patch("pds.api.utils.inputs.session.get",
                         return_value=get_response)
            mocker.patch("pds.api.utils.inputs.session.post")
            result = inputs.preprocess_inputs(inputs_dict, "ACCESS_TOKEN")
            assert len(result[0]) == 3
            assert len(result[2]) == 1
            assert result[2][0][0] == "test"
            assert result[2][0][1] == inputs_dict["_ssh_password"]
