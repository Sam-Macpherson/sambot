from datetime import datetime

from peewee import ForeignKeyField, DateTimeField

from models import BaseModel, User
from models.profiles import DiscordProfile
from models.triggered_responses import TriggeredResponse


class TriggeredResponseUsageTimestamp(BaseModel):
    # discord_profile = ForeignKeyField(
    #     DiscordProfile,
    #     backref='triggered_response_usage_timestamps'
    # )
    user = ForeignKeyField(
        User,
        field=User.id,
        backref='triggered_response_usage_timestamps',
        null=True
    )
    triggered_response = ForeignKeyField(
        TriggeredResponse,
        backref='triggered_response_usage_timestamps'
    )
    # When the TriggeredResponse was last used by User.
    timestamp = DateTimeField(default=datetime.now)
