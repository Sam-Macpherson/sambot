from datetime import datetime

from peewee import CharField, IntegerField, DateTimeField

from models import BaseModelWithUUID


class StreamLiveNotification(BaseModelWithUUID):
    """A model to represent a webhook subscription which will send notifications
    to a channel in discord when a streamer goes live.
    """
    streamer_display_name = CharField(help_text='The streamer\'s display name.')
    streamer_twitch_id = IntegerField(help_text='The streamer\'s unique twitch'
                                                'ID.')
    profile_image_url = CharField(help_text='The URL of their profile image, '
                                            'which will be used in the '
                                            'notifications.')
    notify_channel = IntegerField(help_text='The discord channel ID that will '
                                            'be notified when this streamer '
                                            'goes live.')
    last_notified = DateTimeField(
        null=True,
        help_text='The last time this notification was fired off.'
    )
    created = DateTimeField(
        default=datetime.now,
        help_text='The time when this subscription was created.'
    )
    expires = DateTimeField(
        default=datetime.now,
        help_text='The time when this subscription expires. Defaults to expire '
                  'immediately so that on the subscription renewer\'s next '
                  'pass this subscription is created.'
    )
    subscription_length = IntegerField(
        default=0,
        help_text='The number of seconds that this subscription lasts for.'
    )
