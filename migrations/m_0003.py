from playhouse.migrate import *

from models import Guild

"""
Migration 0003.
This migration adds a cooldown_type field to each guild, which will 
allow a server owner to specify if they want triggered responses to be 
available to users on a per-response basis, or on a global cooldown.
"""


def migration():
    database = SqliteDatabase('sambot.db')
    migrator = SqliteMigrator(database)

    cooldown_type_field = IntegerField(
        choices=Guild.COOLDOWN_TYPE_CHOICES,
        null=False,
        default=Guild.PER_RESPONSE,
        help_text='The cooldown for a guild can either be set on a global '
                  'basis, where any user of the guild is allowed to trigger '
                  'any text or image response once per cooldown, or on a '
                  'per-response basis, where a user\'s ability to use a '
                  'text/image response is based on a cooldown between that '
                  'response, and the user. If the type is "GLOBAL", only '
                  'the "triggered_text_cooldown" cooldown is used, for all '
                  'responses.')

    migrate(
        migrator.add_column('guild', 'cooldown_type', cooldown_type_field)
    )
