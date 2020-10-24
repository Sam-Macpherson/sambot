from peewee import IntegerField, CharField

from models import BaseModel


class Guild(BaseModel):
    guild_id = IntegerField(primary_key=True)
    guild_name = CharField()
    triggered_response_cooldown = IntegerField(default=0)
