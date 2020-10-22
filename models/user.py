from peewee import *

from . import BaseModel


class User(BaseModel):
    discord_id = IntegerField(primary_key=True)
    display_name = CharField()
