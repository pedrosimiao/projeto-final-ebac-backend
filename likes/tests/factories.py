# likes/tests/factories.py

import factory
from factory.django import DjangoModelFactory
from likes.models import Like
from accounts.tests.factories import UserFactory
from posts.tests.factories import PostFactory
from comments.tests.factories import CommentFactory


class LikeFactory(DjangoModelFactory):
    class Meta:
        model = Like
    
    user = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)
    comment = None