from pds.api.log import get_logger
from .settings import Settings
from .vault_client import get_secret


logger = get_logger(__name__)


def preprocess_inputs(inputs, access_token, namespace):
    refined_inputs = inputs.copy()
    ssh_keys = []

    refined_inputs["namespace"] = namespace

    for key in inputs:
        if key.startswith(Settings.SECRET_PREFIX):
            logger.info("Resolving input starting with {0}".format(Settings.SECRET_PREFIX))
            values = inputs[key].split(':')
            if not isinstance(values, list):
                raise Exception("Incorrect input format for secret: {0}".format(inputs[key]))
            secret = get_secret(values[0], values[1], access_token)
            if isinstance(secret, dict):
                refined_inputs.pop(key)
                refined_inputs.update(secret)
            else:
                raise Exception("Incorrect secret: {0} for role {1}".format(values[0], values[1]))

    for key in list(refined_inputs.keys()):
        if key.startswith(Settings.SSH_KEY_PREFIX):
            logger.info("Resolving input starting with {0}".format(Settings.SSH_KEY_PREFIX))
            ssh_key = refined_inputs.pop(key)
            ssh_keys.append(ssh_key)

    return refined_inputs, ssh_keys
