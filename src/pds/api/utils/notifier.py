import requests

from flask import current_app
from pds.api.log import get_logger
from pds.api.openapi.models.subscription_input import SubscriptionInput

logger = get_logger(__name__)


class Notifier:

    subscribers = []

    @classmethod
    def get_subscribers(cls):
        return cls.subscribers

    @classmethod
    def reset_subscribers(cls):
        cls.subscribers = []

    @classmethod
    def add_subscriber(cls, subscriber: SubscriptionInput):
        cls.subscribers.append(subscriber)

    @classmethod
    def notify_subscribers(cls, namespace: str):
        failed_subscribers = []
        for subscriber in cls.subscribers:
            if namespace != subscriber.namespace:
                continue
            try:
                response = requests.post(subscriber.endpoint,
                              json=subscriber.payload,
                              verify=True,
                              timeout=int(current_app.config['SUBSCRIBER_TIMEOUT']))
                if not response.ok:
                    raise requests.RequestException("Unsuccessful response code")
            except (requests.RequestException, ConnectionError) as e:
                logger.info("An error occurred during notifications of: {}".format(subscriber.endpoint))
                failed_subscribers.append(subscriber)
        return failed_subscribers
