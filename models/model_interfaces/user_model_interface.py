"""Class to interface with the User model."""
from models import User
from models.builders import UserBuilder
from models.currencies import Currency, CurrencyAmount
from models.exceptions import InsufficientFundsError
from models.model_interfaces import ModelInterface
from models.profiles import DiscordProfile


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
