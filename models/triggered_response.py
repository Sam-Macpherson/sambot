from peewee import CharField, IntegerField, ForeignKeyField

from models import BaseModel
from models.guild import Guild


class TriggeredResponse(BaseModel):
    guild = ForeignKeyField(
        Guild,
        backref='triggered_responses'
    )
    trigger = CharField()
    response = CharField()
