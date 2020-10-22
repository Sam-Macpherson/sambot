from peewee import *

from discord_src.python_src.models.base_model import BaseModel


class User(BaseModel):
    discord_id = IntegerField(primary_key=True)
    display_name = CharField()
