from peewee import IntegerField, CharField

from models import BaseModel


class Guild(BaseModel):
    GLOBAL = 1
    PER_RESPONSE = 2

    COOLDOWN_TYPE_CHOICES = (
        (GLOBAL, 'GLOBAL'),
        (PER_RESPONSE, 'PER RESPONSE')
    )
    guild_id = IntegerField(primary_key=True)
    guild_name = CharField()
    cooldown_type = IntegerField(
        choices=COOLDOWN_TYPE_CHOICES,
        help_text='The cooldown for a guild can either be set on a global '
                  'basis, where any user of the guild is allowed to trigger '
                  'any text or image response once per cooldown, or on a '
                  'per-response basis, where a user\'s ability to use a '
                  'text/image response is based on a cooldown between that '
                  'response, and the user. If the type is "GLOBAL", only '
                  'the "triggered_text_cooldown" cooldown is used, for all '
                  'responses.')
    triggered_text_cooldown = IntegerField(default=0)
    triggered_image_cooldown = IntegerField(default=0)
