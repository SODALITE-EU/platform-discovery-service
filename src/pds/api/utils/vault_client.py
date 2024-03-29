import urllib.parse
import requests

from pds.api.log import get_logger
from requests.exceptions import ConnectionError
from .settings import Settings

adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
session = requests.Session()
session.mount('http://', adapter)
session.mount('https://', adapter)


logger = get_logger(__name__)


def get_vault_token(vault_role, access_token) -> str:
    if access_token is None:
        raise ValueError(
            "Vault secret retrieval error. Access token is not provided."
        )
    request = {'jwt': access_token, 'role': vault_role}
    secret_vault_login_uri = Settings.VAULT_LOGIN_URI
    token_request = session.post(secret_vault_login_uri, data=request)
    if not token_request.ok:
        raise ConnectionError(
            "Vault auth error. {}".format(token_request.text)
        )
    return token_request.json()['auth']['client_token']


def get_secret(secret_path, vault_role, access_token) -> dict:
    logger.debug("Obtaining secret from Vault")
    vault_token = get_vault_token(vault_role, access_token)
    headers = {'X-Vault-Token': vault_token}
    secret_vault_uri = Settings.VAULT_SECRET_URI
    secret_request = session.get(
        urllib.parse.urljoin(secret_vault_uri, secret_path), headers=headers
    )
    if not secret_request.ok:
        raise ConnectionError(
            "Vault secret retrieval error. {}".format(secret_request.text)
        )
    return secret_request.json()["data"]


def list_secrets(secret_path, vault_role, access_token) -> list:
    logger.debug("Listing users secrets in Vault")
    vault_token = get_vault_token(vault_role, access_token)
    headers = {'X-Vault-Token': vault_token}
    secret_vault_uri = Settings.VAULT_SECRET_URI
    secret_request = session.get(
        urllib.parse.urljoin(secret_vault_uri, secret_path + "?list=true"), headers=headers
    )
    if not secret_request.ok:
        raise ConnectionError(
            "Vault secret retrieval error. {}".format(secret_request.text)
        )
    if secret_request.json()["data"] and "keys" in secret_request.json()["data"]:
        return secret_request.json()["data"]["keys"]
    return []
