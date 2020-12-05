import uuid

from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase

db = SqliteExtDatabase('sambot.db', timeout=5)


class BaseModel(Model):

    class Meta:
        database = db


class BaseModelWithUUID(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
