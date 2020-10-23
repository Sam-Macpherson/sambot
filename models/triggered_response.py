from peewee import CharField, IntegerField

from models import BaseModel


class TriggeredResponse(BaseModel):
    guild_id = IntegerField()
    trigger = CharField()
    response = CharField()
