from peewee import ForeignKeyField

from models import BaseModelWithUUID, User


class Wallet(BaseModelWithUUID):
    user = ForeignKeyField(
        User,
        User.discord_id,
        backref='wallet',
        unique=True,
    )
