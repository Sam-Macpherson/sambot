"""Class to interface with the TriggeredResponse model."""
from datetime import datetime, timedelta

from models import User, Guild
from models.builders import TriggeredResponseBuilder
from models.model_interfaces import ModelInterface
from models.triggered_responses import (
    TriggeredResponse,
    TriggeredResponseUsageTimestamp,
)


class TriggeredResponseModelInterface(ModelInterface):
    model = TriggeredResponse
    builder = TriggeredResponseBuilder
    TEXT = TriggeredResponse.TEXT
    IMAGE = TriggeredResponse.IMAGE

    @classmethod
    def get_allowed_or_none(cls, user: User = None,
                            guild: Guild = None,
                            trigger: str = None,
                            **kwargs):
        """Works the same way as get_or_none, except that it does not return
        results that the given user is not allowed to use, based on the
        guild's cooldown type and relevant cooldown, and the user's
        usage timestamps.
        """
        assert isinstance(user, User)
        assert isinstance(guild, Guild)
        assert isinstance(trigger, str)
        now = datetime.now()
        if guild.cooldown_type == Guild.GLOBAL:
            user_cannot_trigger = \
                TriggeredResponseUsageTimestamp.select().where(
                    (TriggeredResponseUsageTimestamp.triggered_response <<
                     guild.triggered_responses) &
                    (TriggeredResponseUsageTimestamp.user ==
                     user) &
                    (TriggeredResponseUsageTimestamp.timestamp >
                     now - timedelta(seconds=guild.triggered_text_cooldown))
                ).exists()
            if user_cannot_trigger:
                return None
        response = super().get_or_none(guild=guild, trigger=trigger, **kwargs)
        if response is None:
            return None
        if guild.cooldown_type == Guild.GLOBAL:
            cooldown = guild.triggered_text_cooldown
        else:
            cooldown = (guild.triggered_text_cooldown
                        if response.type == TriggeredResponse.TEXT
                        else guild.triggered_image_cooldown)
        last_used, timestamp_created = \
            TriggeredResponseUsageTimestamp.get_or_create(
                user=user,
                triggered_response=response
            )
        if (timestamp_created or
                last_used.timestamp + timedelta(seconds=cooldown) <= now):
            last_used.timestamp = now
            last_used.save()
            return response
        return None
