import requests
from flask import current_app
from pds.api.log import get_logger

# use connection pool for OAuth tokeninfo
adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
session = requests.Session()
session.mount('http://', adapter)
session.mount('https://', adapter)

logger = get_logger(__name__)


def save_tosca(tosca, namespace, access_token, aadm_uri, rm_uri):
    logger.info("Saving TOSCA into KB")
    if access_token:
        headers = {"Authorization": f"Bearer {access_token}"}
    else:
        headers = None

    reasoner_update_uri = current_app.config['SEMANTIC_REASONER_UPDATE_URI']

    data = {
        "modelTOSCA": tosca,
        "rmNamespace": namespace,
        "aadmNamespace": namespace,
        "rmName": "{0}.rm".format(namespace),
        "aadmName": "{0}.aadm".format(namespace),
        "rmURI": rm_uri,
        "aadmURI": aadm_uri
        }

    return requests.post(reasoner_update_uri,
                         data=data,
                         headers=headers,
                         verify=True)
