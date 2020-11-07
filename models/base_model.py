import uuid

from peewee import *


db = SqliteDatabase('sambot.db',
                    pragmas={
                        'journal_mode': 'wal',
                    })


class BaseModel(Model):

    class Meta:
        database = db


class BaseModelWithUUID(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
