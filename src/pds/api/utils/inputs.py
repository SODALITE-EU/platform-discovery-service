import requests
import urllib.parse
from flask import current_app

# use connection pool for OAuth tokeninfo
adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
session = requests.Session()
session.mount('http://', adapter)
session.mount('https://', adapter)

SECRET_PREFIX = "_get_secret"
SSH_KEY_PREFIX = "_ssh_key"
SSH_KEY_PASSWORD_PREFIX = "_ssh_password"
STORAGE_KEY_PREFIX = "_storage_key"

def preprocess_inputs(inputs, access_token):
    refined_inputs = inputs.copy()
    ssh_keys = []
    env_vars = []

    for key in inputs:
        if key.startswith(SECRET_PREFIX):
            values = inputs[key].split(':')
            if not isinstance(values, list):
                raise Exception(
                    "Incorrect input format for secret: {0}".format(
                        inputs[key]
                        )
                    )
            secret = _get_secret(values[0], values[1], access_token)
            if isinstance(secret, dict):
                refined_inputs.pop(key)
                refined_inputs.update(secret)
            else:
                raise Exception(
                    "Incorrect secret: {0} for role {1}".format(
                        values[0],
                        values[1]
                        )
                    )

    for key in list(refined_inputs.keys()):
        if key.startswith(SSH_KEY_PREFIX):
            ssh_key = refined_inputs.pop(key)
            password_key = SSH_KEY_PASSWORD_PREFIX + key[len(SSH_KEY_PREFIX):]
            password = None
            if(password_key in refined_inputs):
                password = refined_inputs.pop(password_key)
            ssh_keys.append((ssh_key, password))

    if STORAGE_KEY_PREFIX in refined_inputs:
        storage_key = refined_inputs.pop(STORAGE_KEY_PREFIX).encode()
    else:
        storage_key = current_app.config['STORAGE_KEY'].encode()

    return refined_inputs, storage_key, ssh_keys, env_vars


def _get_secret(secret_path, vault_role, access_token) -> dict:
    if access_token is None:
        raise Exception(
            "Vault secret retrieval error. Access token is not provided."
            )
    request = {'jwt': access_token, 'role': vault_role}
    secret_vault_login_uri = current_app.config['VAULT_LOGIN_URI']
    token_request = session.post(secret_vault_login_uri, data=request)
    if not token_request.ok:
        raise Exception(
            "Vault auth error. {}".format(token_request.text)
            )
    vault_token = token_request.json()['auth']['client_token']
    headers = {'X-Vault-Token': vault_token}
    secret_vault_uri = current_app.config['VAULT_SECRET_URI']
    secret_request = session.get(
        urllib.parse.urljoin(secret_vault_uri, secret_path), headers=headers
        )
    if not secret_request.ok:
        raise Exception(
            "Vault secret retrieval error. {}".format(secret_request.text)
            )
    return secret_request.json()["data"]
