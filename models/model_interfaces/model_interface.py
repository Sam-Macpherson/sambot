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


class DiscordProfileModelInterface(ModelInterface):
    model = DiscordProfile
    builder = DiscordProfileBuilder


class UserModelInterface(ModelInterface):
    model = User
    builder = UserBuilder

    @classmethod
    def get_currency_amount_or_none(cls, user: DiscordProfile,
                                    currency: Currency):
        assert isinstance(user, DiscordProfile)
        assert isinstance(currency, Currency)
        currency_query = user.wallet.get().currency_amounts\
            .where(currency == currency)
        if currency_query.exists():
            return currency_query.get()
        return None

    @classmethod
    def pay(cls, user: DiscordProfile, currency: Currency, amount: int):
        assert isinstance(user, DiscordProfile)
        assert isinstance(currency, Currency)
        assert isinstance(amount, int)
        currency_amount = cls.get_currency_amount_or_none(
            user=user,
            currency=currency
        )
        if currency_amount is None or currency_amount.amount < amount:
            raise InsufficientFundsError()
        currency_amount.amount -= amount
        currency_amount.save()

    @classmethod
    def receive(cls, user: DiscordProfile, currency: Currency, amount: int):
        assert isinstance(user, DiscordProfile)
        assert isinstance(currency, Currency)
        assert isinstance(amount, int)
        currency_amount = cls.get_currency_amount_or_none(
            user=user,
            currency=currency
        )
        if currency_amount is None:
            CurrencyAmount.create(
                wallet=user.wallet.get(),
                currency=currency,
                amount=amount
            )
        else:
            currency_amount.amount += amount
            currency_amount.save()


class BannedWordModelInterface(ModelInterface):
    model = BannedWord
    builder = BannedWordBuilder

    @staticmethod
    def _hash_word(word):
        from hashlib import sha256
        return sha256(word.encode()).hexdigest()

    @classmethod
    def get_or_none(cls, word=None, **kwargs):
        return super().get_or_none(word=cls._hash_word(word), **kwargs)

    @classmethod
    def get_or_create(cls, word=None, **kwargs):
        return super().get_or_create(word=cls._hash_word(word), **kwargs)


class GuildModelInterface(ModelInterface):
    model = Guild
    builder = GuildBuilder
    GLOBAL = Guild.GLOBAL
    PER_RESPONSE = Guild.PER_RESPONSE

    @classmethod
    def get_currency_for_guild_or_none(cls, guild: Guild, name: str):
        assert isinstance(guild, Guild)
        assert isinstance(name, str)
        currency_query = guild.currencies.where((Currency.name == name) |
                                                (Currency.symbol == name))
        if currency_query.exists():
            return currency_query.get()
        return None

    @classmethod
    def create_currency_for_guild(cls, guild: Guild,
                                  name: str,
                                  symbol: str = None):
        assert isinstance(guild, Guild)
        assert isinstance(name, str)
        assert isinstance(symbol, str) or symbol is None
        if symbol is not None:
            Currency.create(guild=guild, name=name, symbol=symbol)
        else:
            Currency.create(guild=guild, name=name)

    @classmethod
    def get_all_currencies_for_guild(cls, guild: Guild):
        assert isinstance(guild, Guild)
        if guild.currencies.exists():
            return list(guild.currencies)
        return []


class TriggeredResponseModelInterface(ModelInterface):
    model = TriggeredResponse
    builder = TriggeredResponseBuilder
    TEXT = TriggeredResponse.TEXT
    IMAGE = TriggeredResponse.IMAGE

    @classmethod
    def get_allowed_or_none(cls, user: User = None,
                            guild: Guild = None,
                            trigger: str = None,
                            **kwargs):
        """Works the same way as get_or_none, except that it does not return
        results that the given user is not allowed to use, based on the
        guild's cooldown type and relevant cooldown, and the user's
        usage timestamps.
        """
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


class CurrencyModelInterface(ModelInterface):
    model = Currency
    builder = CurrencyBuilder

    @classmethod
    def get_or_create(cls, **kwargs):
        raise NotImplementedError

    @classmethod
    def get_or_none(cls, **kwargs):
        raise NotImplementedError


class StreamLiveNotificationModelInterface(ModelInterface):
    model = StreamLiveNotification
    builder = StreamLiveNotificationBuilder

    @classmethod
    def get_expiring_soon(cls):
        """Return all the StreamLiveNotification objects which are expiring
        within the next 10 minutes. 10 minutes == 600 seconds.
        """
        now = datetime.now()
        subscriptions = StreamLiveNotification.select().where(
            StreamLiveNotification.expires <= now + timedelta(minutes=10)
        )
        return subscriptions

    @classmethod
    def get_all(cls):
        """Return all StreamLiveNotification objects."""
        return StreamLiveNotification.select()

    @classmethod
    def get_all_for_streamer(cls, streamer_twitch_id: int):
        """Return all the StreamLiveNotification objects for which the streamer
        matches the given streamer ID.
        """
        return StreamLiveNotification.select().where(
            StreamLiveNotification.streamer_twitch_id == streamer_twitch_id
        )

