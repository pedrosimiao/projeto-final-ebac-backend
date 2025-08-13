# follows/tests/factories.py

import factory
from factory.django import DjangoModelFactory
from follows.models import Follow
from accounts.tests.factories import UserFactory


class FollowFactory(DjangoModelFactory):
    class Meta:
        model = Follow
    
    follower = factory.SubFactory(UserFactory)
    following = factory.SubFactory(UserFactory)