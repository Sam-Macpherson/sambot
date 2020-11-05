from playhouse.migrate import *


"""
Migration 0004.
This migration changes the column type of triggered responses' text response
to Text so that more characters can be stored.
"""


def migration():
    database = SqliteDatabase('sambot.db')
    migrator = SqliteMigrator(database)
    # Alter the column type.
    text_field = TextField(null=True)
    migrate(
        migrator.alter_column_type('triggeredresponse',
                                   'response',
                                   text_field)
    )
