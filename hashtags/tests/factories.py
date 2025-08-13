# hashtags/tests/factories.py

import factory
from factory.django import DjangoModelFactory
from hashtags.models import Hashtag


class HashtagFactory(DjangoModelFactory):
    class Meta:
        model = Hashtag
    
    name = factory.Sequence(lambda n: f'hashtag{n}')