import pytest

from pds.api.controllers.default import discover 
from pds.api.controllers.security import token_info, validate_scope, get_access_token


class TestControllers:
    @pytest.fixture
    def discovery_input(self):
        inputs = {
                        "inputs":
                        {
                            "frontend-address": "14.15.11.12",
                            "user": "alexander",
                            "namespace": "TestSlurm",
                            "_storage_key": "STORAGE_KEY"
                        },
                        "platform_type": "slurm"
                    }
        return inputs

    def test_discovery(self, mocker, flask_app, discovery_input):
        with flask_app.app.test_request_context():
            request = mocker.patch("connexion.request")
            request.is_json = True
            mocker.patch("pds.api.controllers.default.opera_deploy")
            mocker.patch("pds.api.controllers.default.opera_outputs")
            mocker.patch("pds.api.storages.safe_storage.SafeStorage.create")
            mocker.patch("os.chdir")
            mocker.patch("pds.api.controllers.security.get_access_token", return_value="TEST_TOKEN")
            mocker.patch("pds.api.utils.inputs.preprocess_inputs")
            flask_app.app.config['OIDC_INTROSPECTION_ENDPOINT'] = ""
            mocker.patch("connexion.request.get_json", return_value=discovery_input)
            result = discover()
            assert result[1] == 200

            mocker.patch("pds.api.controllers.default.opera_deploy", side_effect=Exception("Test error"))
            result = discover()
            assert result[1] == 500        
            assert result[0]["message"] == "Test error"

    def test_get_token(self, mocker):
        mock = mocker.MagicMock()
        mock.headers = {"Authorization": "Bearer TEST_TOKEN"}
        token = get_access_token(mock)
        assert token == "TEST_TOKEN"

        mock.headers = {}
        token = get_access_token(mock)
        assert token is None

        mock.headers = {"Authorization": "BearerTEST_TOKEN"}
        token = get_access_token(mock)
        assert token is None

        mock.headers = {"Authorization": "None TEST_TOKEN"}
        token = get_access_token(mock)
        assert token is None  

    def test_validate_scope(self):
        assert validate_scope(None, None) is True
        assert validate_scope([], []) is True
        assert validate_scope(["test"], None) is True

    def test_token_info(self, mocker, flask_app):
        with flask_app.app.app_context():
            mocker.patch("pds.api.controllers.security.session.post")
            flask_app.app.config['OIDC_INTROSPECTION_ENDPOINT'] = ""
            result = token_info("ACCESS_TOKEN")
            assert len(result) == 1
            assert result["scope"][0] == "uid"
            flask_app.app.config['OIDC_INTROSPECTION_ENDPOINT'] = "test_endpoint"
            result = token_info("ACCESS_TOKEN")
