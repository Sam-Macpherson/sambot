from peewee import CharField, ForeignKeyField

from models import BaseModel
from models.guild import Guild


class BannedWord(BaseModel):
    guild = ForeignKeyField(
        Guild,
        backref='banned_words'
    )
    word = CharField()
