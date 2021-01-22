"""Class to interface with the StreamLiveNotification model."""
from datetime import datetime, timedelta

from models.builders import StreamLiveNotificationBuilder
from models.model_interfaces import ModelInterface
from models.twitch_notifications import StreamLiveNotification


class StreamLiveNotificationModelInterface(ModelInterface):
    model = StreamLiveNotification
    builder = StreamLiveNotificationBuilder
    FOOTER_MAX_LENGTH = StreamLiveNotification.FOOTER_MAX_LENGTH

    @classmethod
    def get_expiring_soon(cls):
        """Return all the StreamLiveNotification objects which are expiring
        within the next 30 minutes.
        """
        now = datetime.now()
        subscriptions = StreamLiveNotification.select().where(
            StreamLiveNotification.expires <= now + timedelta(minutes=30)
        )
        return subscriptions

    @classmethod
    def get_all(cls):
        """Return all StreamLiveNotification objects."""
        return StreamLiveNotification.select()

    @classmethod
    def get_all_for_streamer(cls, streamer_twitch_id: int):
        """Return all the StreamLiveNotification objects for which the streamer
        matches the given streamer ID.
        """
        now = datetime.now()
        return StreamLiveNotification.select().where(
            (StreamLiveNotification.streamer_twitch_id == streamer_twitch_id)
        )
