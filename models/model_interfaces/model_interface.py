"""A base model interface class, to abstract away from the peewee ORM."""

from peewee import DoesNotExist

from models import User, Guild
from models.banned_words import BannedWord
from models.builders import BannedWordBuilder, GuildBuilder, UserBuilder


class ModelInterface:
    model = None
    builder = None

    @classmethod
    def get_or_create(cls, **kwargs):
        defaults = kwargs.pop('defaults', {})
        try:
            record = cls.model.get(**kwargs)
            created = False
        except DoesNotExist:
            for key in defaults:
                kwargs[key] = defaults[key]
            record = cls.builder.build(**kwargs)
            created = True
        return record, created

    @classmethod
    def get_or_none(cls, **kwargs):
        try:
            record = cls.model.get(**kwargs)
        except DoesNotExist:
            record = None
        return record

    @classmethod
    def delete_instance(cls, instance):
        assert isinstance(instance, cls.model)
        instance.delete_instance()


class UserModelInterface(ModelInterface):
    model = User
    builder = UserBuilder


class BannedWordModelInterface(ModelInterface):
    model = BannedWord
    builder = BannedWordBuilder


class GuildModelInterface(ModelInterface):
    model = Guild
    builder = GuildBuilder
    GLOBAL = Guild.GLOBAL
    PER_RESPONSE = Guild.PER_RESPONSE
