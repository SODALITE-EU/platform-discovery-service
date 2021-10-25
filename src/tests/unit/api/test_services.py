import pytest

from pds.api.service.security import token_info, validate_scope, get_access_token
from pds.api.utils.settings import Settings


class TestServices:
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
            mocker.patch("pds.api.service.security.session.post")
            mocker.patch("pds.api.utils.settings.Settings.OIDC_INTROSPECTION_ENDPOINT", "")
            result = token_info("ACCESS_TOKEN")
            assert len(result) == 1
            assert result["scope"][0] == "uid"
            mocker.patch("pds.api.utils.settings.Settings.OIDC_INTROSPECTION_ENDPOINT", "test_endpoint")
            result = token_info("ACCESS_TOKEN")
