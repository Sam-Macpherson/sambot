from peewee import *


db = SqliteDatabase('sambot.db')


class BaseModel(Model):

    class Meta:
        database = db
