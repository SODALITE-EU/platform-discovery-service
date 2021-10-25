import connexion
import datetime
import json
from validators import url as validate_endpoint
from validators import ValidationFailure

from pds.api.openapi.models.discovery_input import DiscoveryInput
from pds.api.openapi.models.discovery_output import DiscoveryOutput
from pds.api.openapi.models.update_input import UpdateInput
from pds.api.openapi.models.update_output import UpdateOutput
from pds.api.openapi.models.subscription_input import SubscriptionInput
from pds.api.openapi.models.subscription_output import SubscriptionOutput
from pds.api.service.security import get_access_token, get_username
from pds.api.service.discovery import discover as service_discover
from pds.api.log import get_logger
from pds.api.utils.reasoner_client import save_tosca
from pds.api.utils.notifier import Notifier

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
        discovery_input = DiscoveryInput.from_dict(connexion.request.get_json())
    else:
        return {"Incorrect input, expected JSON"}, 400

    access_token = get_access_token(connexion.request)
    username = get_username(connexion.context.get("token_info"))

    try:
        return_value = service_discover(discovery_input.inputs,
                                        discovery_input.namespace,
                                        discovery_input.platform_type,
                                        access_token,
                                        username)
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        return DiscoveryOutput(now.isoformat(), return_value), 200
    except Exception as ex:
        logger.exception("An error occurred during discovery process")
        return {"message": str(ex)}, 500



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
        update_input = UpdateInput.from_dict(connexion.request.get_json())
    else:
        return {"Incorrect input, expected JSON"}, 400

    access_token = get_access_token(connexion.request)
    username = get_username(connexion.context.get("token_info"))

    try:
        discovery_result = service_discover(update_input.inputs,
                                            update_input.namespace,
                                            update_input.platform_type,
                                            access_token,
                                            username)
    except Exception as ex:
        logger.exception("An error occurred during discovery process")
        return {"message": str(ex)}, 500

    try:
        save_response = save_tosca(discovery_result,
                                   update_input.namespace,
                                   access_token,
                                   update_input.aadm_uri,
                                   update_input.rm_uri)
        if save_response.ok:
            result = json.loads(save_response.text)
            # TODO: notifications can be run in background
            # TODO: handle failed subscribers
            failed_subscribers = Notifier.notify_subscribers(update_input.namespace)
            return UpdateOutput(result.get("aadmuri"), result.get("rmuri")), 200
        else:
            return save_response.text, save_response.status_code

    except ConnectionError:
        return "Reasoner connection error to Semantic reasoner", 500


def subscribe(body: SubscriptionInput = None):
    """Subscription for receiving a notification about discovery and KB updates.

     # noqa: E501

    :param subscription_input: Subscription information.
    :type subscription_input: dict | bytes

    :rtype: SubscriptionOutput
    """
    logger.debug("Entry: subscribe")
    logger.debug(body)

    if connexion.request.is_json:
        subscription_input = SubscriptionInput.from_dict(
            connexion.request.get_json()
            )
    else:
        return {"Incorrect input"}, 400

    if isinstance(validate_endpoint(subscription_input.endpoint), ValidationFailure):
        return {"Incorrect endpoint"}, 400

    Notifier.add_subscriber(subscription_input)

    return SubscriptionOutput(True), 200
