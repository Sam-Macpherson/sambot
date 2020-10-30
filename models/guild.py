from peewee import IntegerField, CharField

from models import BaseModel


class Guild(BaseModel):
    guild_id = IntegerField(primary_key=True)
    guild_name = CharField()
    triggered_text_cooldown = IntegerField(default=0)
    triggered_image_cooldown = IntegerField(default=0)
