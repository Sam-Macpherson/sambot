from peewee import *


db = SqliteDatabase('sambot.db',
                    pragmas={
                        'journal_mode': 'wal',
                    })


class BaseModel(Model):

    class Meta:
        database = db
