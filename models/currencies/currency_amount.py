from peewee import ForeignKeyField, IntegerField

from models import BaseModelWithUUID
from models.currencies import Currency, Wallet


class CurrencyAmount(BaseModelWithUUID):
    wallet = ForeignKeyField(
        Wallet,
        Wallet.id,
        backref='currency_amounts'
    )
    currency = ForeignKeyField(
        Currency,
        Currency.id,
        backref='+',
    )
    amount = IntegerField()
