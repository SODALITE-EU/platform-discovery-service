import requests
from base64 import b64encode
from pds.api.utils.settings import Settings

# use connection pool for OAuth tokeninfo
adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
session = requests.Session()
session.mount('http://', adapter)
session.mount('https://', adapter)


def check_api_key(apikey, required_scopes=None):
    configured_key = Settings.AUTH_API_KEY
    if not configured_key or apikey != configured_key:
        return None

    return {'scope': ['apiKey']}


def token_info(access_token) -> dict:
    request = {'token': access_token}
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    token_info_url = Settings.OIDC_INTROSPECTION_ENDPOINT
    # currently we are using access tokens only for secret retrieval
    # so if no introspection endpoint is configured we can proceed
    # as it is currently not a security risk
    if token_info_url == "":
        return {'scope': ['uid']}
    basic_auth_string = '{0}:{1}'.format(Settings.OIDC_CLIENT_ID, Settings.OIDC_CLIENT_SECRET)
    basic_auth_bytes = bytearray(basic_auth_string, 'utf-8')
    headers['Authorization'] = 'Basic {0}'.format(b64encode(basic_auth_bytes).decode('utf-8'))

    token_request = session.post(token_info_url, data=request, headers=headers)
    if not token_request.ok:
        return None
    return token_request.json()


def validate_scope(required_scopes, token_scopes) -> bool:
    return True


def get_access_token(request) -> str:
    authorization = request.headers.get("Authorization")
    if not authorization:
        return None
    try:
        auth_type, token = authorization.split(None, 1)
    except ValueError:
        return None
    if auth_type.lower() != "bearer":
        return None
    return token


def get_username(info) -> str:
    if info is None:
        return None

    # TODO decide what to do in case of apiKey
    # use default username or None?
    if "scope" in info and "apiKey" in info["scope"]:
        return None

    return info.get("preferred_username", None)
