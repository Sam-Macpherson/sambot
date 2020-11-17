from peewee import IntegerField, CharField

from models import BaseModel


class TwitchProfile(BaseModel):
    id = IntegerField(primary_key=True)
    display_name = CharField()
