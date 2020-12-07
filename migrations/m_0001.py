from playhouse.migrate import *


"""
Migration 0001.
This migration adds a customizable footer text field to the stream notification
model.
"""


def migration():
    database = SqliteDatabase('sambot.db')
    migrator = SqliteMigrator(database)
    footer = CharField(
        max_length=128,
        default='See you there!',
        help_text='The footer text of the stream notification.'
    )
    migrate(
        migrator.add_column('streamlivenotification', 'footer', footer)
    )
