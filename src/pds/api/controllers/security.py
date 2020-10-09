import requests
from flask import current_app
from base64 import b64encode

# use connection pool for OAuth tokeninfo
adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
session = requests.Session()
session.mount('http://', adapter)
session.mount('https://', adapter)


def token_info(access_token) -> dict:
    request = {'token': access_token}
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    token_info_url = current_app.config['OIDC_INTROSPECTION_ENDPOINT']
    basic_auth_string = '%s:%s' % (current_app.config['OIDC_CLIENT_ID'], 
                                   current_app.config['OIDC_CLIENT_SECRET'])
    basic_auth_bytes = bytearray(basic_auth_string, 'utf-8')
    headers['Authorization'] = 'Basic %s' % b64encode(basic_auth_bytes).decode('utf-8')

    token_request = session.post(token_info_url, data=request, headers=headers)
    if not token_request.ok:
        return None
    return token_request.json()


def validate_scope(required_scopes, token_scopes) -> bool:
    return True
