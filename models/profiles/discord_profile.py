from peewee import *

from models import BaseModel, User


class DiscordProfile(BaseModel):
    id = IntegerField(primary_key=True)
    display_name = CharField()
    user = ForeignKeyField(
        model=User,
        field=User.id,
        unique=True,
        null=True,
        backref='discord_profile'
    )
