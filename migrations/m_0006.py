import uuid

from playhouse.migrate import *

from models.profiles import TwitchProfile

"""
Migration 0006.
This migration updates the way a user is defined in the database.
Old:
User:
discord_id: xxxx, primary key (FROM DISCORD)
display_name: yyyyy

New:
DiscordProfile (same as the old User table):
discord_id: xxxx, primary key (FROM DISCORD)
display_name: yyyy

TwitchProfile:
twitch_id: zzz, primary key (FROM TWITCH)
display_name: wwww

A future migration will add a User table back into the mix, which will 
have the wallet object, and all of its profiles and usage timestamps pointing 
to it.
"""


def migration():
    database = SqliteDatabase('sambot.db')
    migrator = SqliteMigrator(database)
    # Step 1: Rename User to DiscordProfile.
    migrate(
        migrator.rename_table('user', 'discordprofile'),
        migrator.rename_column('discordprofile', 'discord_id', 'id'),
        migrator.rename_column('wallet', 'user_id', 'discord_profile_id'),
        migrator.rename_column('triggeredresponseusagetimestamp',
                               'user_id', 'discord_profile_id')
    )
    # Step 2: Create TwitchProfile table.
    database.create_tables([TwitchProfile])
