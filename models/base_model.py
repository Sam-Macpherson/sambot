from peewee import *


db = SqliteDatabase('sambot.db',
                    pragmas={
                        'foreign_keys': 1,
                        'journal_mode': 'wal',
                    })


class BaseModel(Model):

    class Meta:
        database = db
