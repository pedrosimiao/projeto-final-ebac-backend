# notifications/tests/factories.py

import factory
from factory.django import DjangoModelFactory
from notifications.models import Notification
from accounts.tests.factories import UserFactory


class NotificationFactory(DjangoModelFactory):
    class Meta:
        model = Notification
    
    type = factory.Iterator([
        Notification.LIKE, 
        Notification.COMMENT, 
        Notification.FOLLOW, 
        Notification.RETWEET, 
        Notification.MENTION,
    ])
    from_user = factory.SubFactory(UserFactory)
    to_user = factory.SubFactory(UserFactory)
    is_read = False