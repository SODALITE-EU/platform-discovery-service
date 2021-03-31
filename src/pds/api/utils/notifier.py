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
    def notify_subscribers(cls):
        failed_subscribers = []
        for subscriber in cls.subscribers:
            try:
                requests.post(subscriber.endpoint,
                              json=subscriber.payload,
                              verify=True,
                              timeout=int(current_app.config['SUBSCRIBER_TIMEOUT']))
            except (requests.RequestException, ConnectionError) as e:
                logger.info("An error occurred during notifications of: {}".format(subscriber.endpoint))
                failed_subscribers.append(subscriber)
        return failed_subscribers
