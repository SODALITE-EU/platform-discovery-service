import connexion
import os
import datetime
import pds.api.utils.templates as templates
import json

from opera.commands.deploy import deploy_service_template as opera_deploy
from opera.commands.outputs import outputs as opera_outputs

from pds.api.openapi.models.discovery_input import DiscoveryInput
from pds.api.openapi.models.discovery_output import DiscoveryOutput
from pds.api.openapi.models.update_input import UpdateInput
from pds.api.openapi.models.update_output import UpdateOutput
from pds.api.controllers.security import get_access_token
from pds.api.log import get_logger, debug_enabled
from pds.api.storages.memory_storage import SafeMemoryStorage
from pds.api.utils.inputs import preprocess_inputs
from pds.api.utils.reasoner_client import save_tosca
from pds.api.utils.environment import DeploymentEnvironment

logger = get_logger(__name__)


def discover(body: DiscoveryInput = None):
    """Automatic discovery and modeling of infrastructural resources.

     # noqa: E501

    :param discovery_input: Endpoint information and access credentials.
    :type discovery_input: dict | bytes

    :rtype: DiscoveryOutput
    """
    logger.debug("Entry: discover")
    logger.debug(body)

    if connexion.request.is_json:
        discovery_input = DiscoveryInput.from_dict(
            connexion.request.get_json()
            )
    else:
        return {"Incorrect input"}, 400
    try:
        return_value = _discover(discovery_input.inputs,
                                 discovery_input.namespace,
                                 discovery_input.platform_type)
    except Exception as ex:
        logger.exception("An error occurred during discovery process")
        return {"message": str(ex)}, 500
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    return DiscoveryOutput(now.isoformat(), return_value), 200


def discover_update(body: UpdateInput = None):
    """Automatic discovery and update resource database.

     # noqa: E501

    :param update_input: Endpoint information and access credentials.
    :type update_input: dict | bytes

    :rtype: UpdateOutput
    """
    logger.debug("Entry: update")
    logger.debug(body)

    if connexion.request.is_json:
        update_input = UpdateInput.from_dict(
            connexion.request.get_json()
            )
    else:
        return {"Incorrect input"}, 400

    try:
        discovery_result = _discover(update_input.inputs,
                                     update_input.namespace,
                                     update_input.platform_type)
    except Exception as ex:
        logger.exception("An error occurred during discovery process")
        return {"message": str(ex)}, 500
    access_token = get_access_token(connexion.request)

    try:
        save_response = save_tosca(discovery_result,
                                   update_input.namespace,
                                   access_token,
                                   update_input.aadm_uri,
                                   update_input.rm_uri)
        if save_response.ok:
            result = json.loads(save_response.text)
            return UpdateOutput(result.get("aadmuri"), result.get("rmuri")), 200
        else:
            return save_response.text, save_response.status_code

    except ConnectionError:
        return "Reasoner connection error to Semantic reasoner", 500


def _discover(inputs, namespace, platform_type):
    default_path = os.getcwd()
    path, template = templates.get_service_template(
        platform_type
        )

    environment = DeploymentEnvironment()

    try:
        # TODO: Disable verbose mode universally
        access_token = get_access_token(connexion.request)
        refined_inputs, ssh_keys, storage_key = \
            preprocess_inputs(inputs,
                              access_token,
                              namespace)
        environment.setup(ssh_keys)

        safe_storage = SafeMemoryStorage.create()
        os.chdir(path)
        opera_deploy(
            template, refined_inputs, safe_storage,
            verbose_mode=debug_enabled(),
            num_workers=1, delete_existing_state=True
            )
        result = opera_outputs(safe_storage)
        os.chdir(default_path)
        if len(result) != 1 or "value" not in list(result.values())[0]:
            raise KeyError("Error in discovery process output")
        return list(result.values())[0]["value"]
    finally:
        errors = environment.cleanup()
        for error in errors:
            logger.warn("An error occurred during cleanup")
            logger.warn(error)
