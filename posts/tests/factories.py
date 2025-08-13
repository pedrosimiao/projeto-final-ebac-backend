# posts/tests/factories.py

import factory
from factory.django import DjangoModelFactory
from posts.models import Post
from accounts.tests.factories import UserFactory

class PostFactory(DjangoModelFactory):
    class Meta:
        model = Post
    
    user = factory.SubFactory(UserFactory)
    content = factory.Faker('sentence')