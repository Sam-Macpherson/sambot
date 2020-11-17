from peewee import *

from models import BaseModel


class DiscordProfile(BaseModel):
    id = IntegerField(primary_key=True)
    display_name = CharField()
