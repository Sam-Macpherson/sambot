"""A base model interface class, to abstract away from the peewee ORM."""
from datetime import datetime, timedelta

from peewee import DoesNotExist

from models import User, Guild
from models.banned_words import BannedWord
from models.builders import (
    BannedWordBuilder,
    GuildBuilder,
    UserBuilder,
    TriggeredResponseBuilder,
)
from models.triggered_responses import TriggeredResponse, TriggeredResponseUsageTimestamp


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
    def save_instance(cls, instance: model):
        assert isinstance(instance, cls.model)
        instance.save()

    @classmethod
    def delete_instance(cls, instance: model):
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


class TriggeredResponseModelInterface(UserModelInterface):
    model = TriggeredResponse
    builder = TriggeredResponseBuilder
    TEXT = TriggeredResponse.TEXT
    IMAGE = TriggeredResponse.IMAGE

    @classmethod
    def get_or_none(cls, user: User = None,
                    guild: Guild = None,
                    trigger: str = None,
                    **kwargs):
        assert isinstance(user, User)
        assert isinstance(guild, Guild)
        assert isinstance(trigger, str)
        now = datetime.now()
        if guild.cooldown_type == Guild.GLOBAL:
            user_cannot_trigger = \
                TriggeredResponseUsageTimestamp.select().where(
                    (TriggeredResponseUsageTimestamp.triggered_response <<
                     guild.triggered_responses) &
                    (TriggeredResponseUsageTimestamp.user ==
                     user) &
                    (TriggeredResponseUsageTimestamp.timestamp >
                     now - timedelta(seconds=guild.triggered_text_cooldown))
                ).exists()
            if user_cannot_trigger:
                return None
        response = super().get_or_none(guild=guild, trigger=trigger, **kwargs)
        if response is None:
            return None
        if guild.cooldown_type == Guild.GLOBAL:
            cooldown = guild.triggered_text_cooldown
        else:
            cooldown = (guild.triggered_text_cooldown
                        if response.type == TriggeredResponse.TEXT
                        else guild.triggered_image_cooldown)
        last_used, timestamp_created = \
            TriggeredResponseUsageTimestamp.get_or_create(
                user=user,
                triggered_response=response
            )
        if (timestamp_created or
                last_used.timestamp + timedelta(seconds=cooldown) <= now):
            last_used.timestamp = now
            last_used.save()
            return response
        return None
