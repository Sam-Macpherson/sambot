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
    CurrencyBuilder,
)
from models.currencies import Currency, CurrencyAmount
from models.triggered_responses import (
    TriggeredResponse,
    TriggeredResponseUsageTimestamp,
)


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


class UserModelInterface(ModelInterface):
    model = User
    builder = UserBuilder

    @classmethod
    def get_currency_amount_or_none(cls, user: User, currency: Currency):
        assert isinstance(user, User)
        assert isinstance(currency, Currency)
        currency_query = user.wallet.get().currency_amounts\
            .where(currency == currency)
        if currency_query.exists():
            return currency_query.get()
        return None

    @classmethod
    def pay(cls, user: User, currency: Currency, amount: int):
        assert isinstance(user, User)
        assert isinstance(currency, Currency)
        assert isinstance(amount, int)
        currency_amount = cls.get_currency_amount_or_none(
            user=user,
            currency=currency
        )
        if currency_amount is None or currency_amount.amount < amount:
            raise ValueError
        currency_amount.amount -= amount
        currency_amount.save()

    @classmethod
    def receive(cls, user: User, currency: Currency, amount: int):
        assert isinstance(user, User)
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
