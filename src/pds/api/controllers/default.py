import connexion
import os
import datetime
import pds.api.utils.templates as templates

from opera.commands.deploy import deploy_service_template as opera_deploy
from opera.commands.outputs import outputs as opera_outputs

from pds.api.openapi.models.discovery_input import DiscoveryInput
from pds.api.openapi.models.discovery_output import DiscoveryOutput
from pds.api.controllers.security import get_access_token
from pds.api.log import get_logger, debug_enabled
from pds.api.storages.safe_storage import SafeStorage
from pds.api.utils.inputs import preprocess_inputs
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
        return {"Incorrect input"}, 500

    path, template = templates.get_service_template(
        discovery_input.platform_type
        )

    environment = DeploymentEnvironment()

    try:
        # TODO: Disable verbose mode universally
        access_token = get_access_token(connexion.request)
        prerequisites = preprocess_inputs(discovery_input.inputs, access_token)
        environment.setup(prerequisites[2], prerequisites[3])

        safe_storage = SafeStorage.create(
            prerequisites[1],
            path + "/.opera/"
            )
        os.chdir(path)
        opera_deploy(
            template, prerequisites[0], safe_storage,
            verbose_mode=debug_enabled(),
            num_workers=1, delete_existing_state=True
            )
        result = opera_outputs(safe_storage)
    except Exception as ex:
        logger.exception("An error occurred during discovery process")
        return {"message": str(ex)}, 500
    finally:
        errors = environment.cleanup()
        for error in errors:
            logger.warn("An error occurred during cleanup")
            logger.warn(error)

    now = datetime.datetime.now(tz=datetime.timezone.utc)
    return DiscoveryOutput(now.isoformat(), result), 200
