"""A base model interface class, to abstract away from the peewee ORM."""
from datetime import datetime, timedelta

from peewee import DoesNotExist

from models import Guild, User
from models.banned_words import BannedWord
from models.builders import (
    BannedWordBuilder,
    GuildBuilder,
    DiscordProfileBuilder,
    TriggeredResponseBuilder,
    CurrencyBuilder,
)
from models.builders.stream_live_notification_builder import StreamLiveNotificationBuilder
from models.builders.user_builder import UserBuilder
from models.currencies import Currency, CurrencyAmount
from models.exceptions import InsufficientFundsError
from models.profiles import DiscordProfile
from models.triggered_responses import (
    TriggeredResponse,
    TriggeredResponseUsageTimestamp,
)
from models.twitch_notifications.stream_live_notification import StreamLiveNotification


class ModelInterface:
    """Some utilities that are common to all model interfaces."""
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
    def save_instance(cls, instance):
        assert isinstance(instance, cls.model)
        instance.save()

    @classmethod
    def delete_instance(cls, instance):
        assert isinstance(instance, cls.model)
        instance.delete_instance()
