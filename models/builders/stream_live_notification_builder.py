from models.builders.model_builder import ModelBuilder
from models.twitch_notifications.stream_live_notification import (
    StreamLiveNotification,
)


class StreamLiveNotificationBuilder(ModelBuilder):
    model = StreamLiveNotification

    @classmethod
    def build(cls, **kwargs):
        return super().build(**kwargs)
