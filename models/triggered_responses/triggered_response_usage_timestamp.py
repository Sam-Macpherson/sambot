from datetime import datetime

from peewee import ForeignKeyField, DateTimeField

from models import BaseModel, User
from models.triggered_responses import TriggeredResponse


class TriggeredResponseUsageTimestamp(BaseModel):
    user = ForeignKeyField(
        User,
        backref='triggered_response_usage_timestamps'
    )
    triggered_response = ForeignKeyField(
        TriggeredResponse,
        backref='triggered_response_usage_timestamps'
    )
    # When the TriggeredResponse was last used by User.
    timestamp = DateTimeField(default=datetime.now)
