import connexion
import os
import datetime

from pds.api.openapi.models.discovery_input import DiscoveryInput  # noqa: E501
from pds.api.openapi.models.discovery_output import DiscoveryOutput  # noqa: E501
from pds.api.openapi.models.platform_type import PlatformType  # noqa: E501

from pds.api.log import get_logger
from opera.commands.deploy import deploy as opera_deploy
from opera.commands.undeploy import undeploy as opera_undeploy
from opera.commands.outputs import outputs as opera_outputs
from pds.api.safe_storage import SafeStorage
from pds.api.memory_storage import SafeMemoryStorage
from flask import current_app

logger = get_logger(__name__)

AUTH_BLUEPRINT = "auth"

def status():  # noqa: E501
    """Fetch the status of a deployment

     # noqa: E501


    :rtype: str
    """
    return 'do some magic!'


def discover(body: DiscoveryInput = None):  # noqa: E501
    """Automatic discovery and modeling of infrastructural resources.

     # noqa: E501

    :param discovery_input: Endpoint information and access credentials.
    :type discovery_input: dict | bytes

    :rtype: DiscoveryOutput
    """
    logger.debug("Entry: discover")
    logger.debug(body)

    if connexion.request.is_json:
        discovery_input = DiscoveryInput.from_dict(connexion.request.get_json())  # noqa: E501
    path, template = _get_service_template(discovery_input.platform_type)
    auth_path, auth_template = _get_service_template(AUTH_BLUEPRINT)

    mem_storage = SafeMemoryStorage.create(
        current_app.config['STORAGE_KEY'].encode(),
        auth_path + ".opera/"
        )
    safe_storage = SafeStorage.create(
        current_app.config['STORAGE_KEY'].encode(),
        path + ".opera/"
        )

    try:
        #add key
        os.chdir(auth_path)
        opera_deploy(
            auth_template, discovery_input.inputs, mem_storage,
            verbose_mode=True, num_workers=1, delete_existing_state=True
            )
    except Exception as ex:
        logger.exception(ex)
        return {"message": str(ex)}, 500

    try:
        os.chdir(path)
        opera_deploy(
            template, discovery_input.inputs, safe_storage,
            verbose_mode=True, num_workers=1, delete_existing_state=True
            )
        result = opera_outputs(safe_storage)
    except Exception as ex:
        logger.exception(ex)
        return {"message": str(ex)}, 500
    finally:
        #remove key
        os.chdir(auth_path)
        opera_undeploy(
            mem_storage, verbose_mode=True, num_workers=1
            )

    now = datetime.datetime.now(tz=datetime.timezone.utc)
    return DiscoveryOutput(now.isoformat(), result), 200


def _get_service_template(blueprint_type: str):
    if blueprint_type == PlatformType.SLURM:
        return current_app.config['BLUEPRINT_PATH'] + "/slurm/", "wm_info.yaml"
    if blueprint_type == AUTH_BLUEPRINT:
        return current_app.config['BLUEPRINT_PATH'] + "/auth/", "ssh_key.yaml"