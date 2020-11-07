from playhouse.migrate import *

from models import User
from models.currencies import Currency, Wallet, CurrencyAmount

"""
Migration 0005.
Adds the currency tables, and creates a wallet for each user.
"""


def migration():
    database = SqliteDatabase('sambot.db')
    migrator = SqliteMigrator(database)

    database.create_tables([Currency, Wallet, CurrencyAmount])
    for user in User.select():
        if not Wallet.select()\
                .where(Wallet.user_id == user.discord_id)\
                .exists():
            print(f'Creating wallet for user: {user.discord_id}')
            Wallet.create(user=user)
