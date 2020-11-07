from peewee import DoesNotExist

from models import User
from models.builders import UserBuilder


class UserModelInterface:

    @staticmethod
    def get_or_create(**kwargs):
        defaults = kwargs.pop('defaults', {})
        try:
            user = User.get(**kwargs)
            created = False
        except DoesNotExist:
            for key in defaults:
                kwargs[key] = defaults[key]
            user = UserBuilder.build(**kwargs)
            created = True
        return user, created

    @staticmethod
    def get(**kwargs):
        try:
            user = User.get(**kwargs)
        except DoesNotExist:
            user = None
        return user
