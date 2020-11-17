from peewee import ForeignKeyField

from models import BaseModelWithUUID
from models.profiles import DiscordProfile


class Wallet(BaseModelWithUUID):
    user = ForeignKeyField(
        DiscordProfile,
        DiscordProfile.id,
        backref='wallet',
        unique=True,
    )
