from peewee import CharField, ForeignKeyField

from models import BaseModelWithUUID, Guild


class Currency(BaseModelWithUUID):
    guild = ForeignKeyField(
        Guild,
        Guild.guild_id,
        backref='currencies'
    )
    name = CharField()
    symbol = CharField(default='💵')
