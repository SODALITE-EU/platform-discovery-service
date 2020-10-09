import connexion
import os
import datetime

from pds.api.openapi.models.discovery_input import DiscoveryInput  # noqa: E501
from pds.api.openapi.models.discovery_output import DiscoveryOutput  # noqa: E501
from pds.api.openapi.models.platform_type import PlatformType  # noqa: E501

from opera.commands.deploy import deploy as opera_deploy
from opera.commands.outputs import outputs as opera_outputs
from pds.api.safe_storage import SafeStorage
from flask import current_app


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
    if connexion.request.is_json:
        discovery_input = DiscoveryInput.from_dict(connexion.request.get_json())  # noqa: E501
    path, template = _get_service_template(discovery_input.platform_type)
    os.chdir(path)
    opera_storage = SafeStorage.create(current_app.config['STORAGE_KEY'].encode(), path + ".opera/")
    opera_deploy(template, discovery_input.inputs, opera_storage,
                 verbose_mode=True, num_workers=1, delete_existing_state=True)
    result = opera_outputs(opera_storage)
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    return DiscoveryOutput(now.isoformat(), result), 200


def _get_service_template(platform_type: str):
    if platform_type == PlatformType.SLURM:
        return current_app.config['BLUEPRINT_PATH'] + "/slurm/", "wm_info.yaml"
