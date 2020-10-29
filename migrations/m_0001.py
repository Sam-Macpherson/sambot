from playhouse.migrate import *

from models import Guild, TriggeredResponse

"""
This migration alters the TriggeredResponse object to use a foreign
key reference to Guild instead of storing a Guild's ID as an 
integer.

1. Change IntegerField to ForeignKeyField.
"""


def migration():
    database = SqliteDatabase('sambot.db')
    migrator = SqliteMigrator(database)

    # We may modify an IntegerField to a FK IntegerField.
    # This migration is somewhat redundant because a guild
    # foreign key is stored as guild_id on the TriggeredResponse
    # model anyway, so you can already use guild= in lookups.
    # Therefore, this migration serves as a standard for future
    # migrations.
    guild_fk = ForeignKeyField(
        Guild,
        field=Guild.guild_id,
        backref='triggered_responses',
        null=True,
    )
    migrate(
        migrator.alter_column_type('triggeredresponse', 'guild_id', guild_fk)
    )
