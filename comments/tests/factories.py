# comments/tests/factories.py

import factory
from factory.django import DjangoModelFactory
from comments.models import Comment
from accounts.tests.factories import UserFactory
from posts.tests.factories import PostFactory

class CommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment
    
    user = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)
    content = factory.Faker('sentence')
    parent_comment = None