from peewee import IntegerField, CharField, ForeignKeyField

from models import BaseModel, User


class TwitchProfile(BaseModel):
    id = IntegerField(primary_key=True)
    display_name = CharField()
    user = ForeignKeyField(
        model=User,
        field=User.id,
        unique=True,
        null=True,
        backref='twitch_profile'
    )
