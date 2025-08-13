# accounts/tests/factories.py

import factory
from accounts.models import User

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall(
        'set_password', '123456Abc'
    )
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')