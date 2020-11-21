from peewee import ForeignKeyField

from models import BaseModelWithUUID, User
from models.profiles import DiscordProfile


class Wallet(BaseModelWithUUID):
    user = ForeignKeyField(
        User,
        User.id,
        backref='wallet',
        unique=True,
        null=True,
    )
