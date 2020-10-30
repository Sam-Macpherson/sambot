from peewee import CharField, IntegerField, ForeignKeyField, BlobField

from models import BaseModel
from models.guild import Guild


class TriggeredResponse(BaseModel):
    TEXT = 1
    IMAGE = 2

    TYPE_CHOICES = (
        (TEXT, 'TEXT'),
        (IMAGE, 'IMAGE')
    )
    # A field to be used externally.
    type = IntegerField(choices=TYPE_CHOICES)
    guild = ForeignKeyField(
        Guild,
        field=Guild.guild_id,
        backref='triggered_responses'
    )
    trigger = CharField()
    response = CharField(null=True)
    image = BlobField(null=True)

    def get_status_label(self):
        return dict(self.TYPE_CHOICES)[self.status]
