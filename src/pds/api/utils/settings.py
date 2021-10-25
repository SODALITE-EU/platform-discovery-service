from os import getenv
from pds.api.log import get_logger

logger = get_logger(__name__)


class Settings:

    OIDC_INTROSPECTION_ENDPOINT = getenv("OIDC_INTROSPECTION_ENDPOINT", "")
    OIDC_CLIENT_ID = getenv("OIDC_CLIENT_ID", "sodalite-ide")
    OIDC_CLIENT_SECRET = getenv("OIDC_CLIENT_SECRET","")
    OIDC_OPENID_REALM = "SODALITE"
    OIDC_SCOPES = ["openid", "email", "profile"]
    STORAGE_KEY = getenv("PDS_STORAGE_KEY", "")
    BLUEPRINT_PATH = getenv("PDS_BLUEPRINT_PATH", "/root/projects/platform-discovery-service/blueprints")
    VAULT_SECRET_URI = getenv("SECRET_VAULT_URI", "http://localhost:8200/v1/")
    if not VAULT_SECRET_URI.endswith("/"):
        VAULT_SECRET_URI = VAULT_SECRET_URI + "/"
    VAULT_LOGIN_URI = getenv("SECRET_VAULT_LOGIN_URI", VAULT_SECRET_URI + "auth/jwt/login")
    AUTH_API_KEY = getenv("AUTH_API_KEY", "")
    SEMANTIC_REASONER_UPDATE_URI = getenv("SEMANTIC_REASONER_UPDATE_URI", "http://localhost:8080/reasoner-api/v0.6/saveTOSCA")
    SUBSCRIBER_TIMEOUT = getenv("SUBSCRIBER_TIMEOUT", "5")

    SECRET_PREFIX = "_get_secret"
    SSH_KEY_PREFIX = "_ssh_key"
    SSH_KEY_PATH_TEMPLATE = "ssh/{username}"
    SSH_KEY_SECRET_NAME = "ssh_pkey"

    if not OIDC_INTROSPECTION_ENDPOINT:
        logger.warn("Security alert. OIDC_INTROSPECTION_ENDPOINT in not configured.")
    else:
        logger.info("OIDC_INTROSPECTION_ENDPOINT {}".format(OIDC_INTROSPECTION_ENDPOINT))
    logger.info("VAULT_SECRET_URI {}".format(VAULT_SECRET_URI))
    logger.info("SEMANTIC_REASONER_UPDATE_URI {}".format(SEMANTIC_REASONER_UPDATE_URI))
