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
"""


def migration():
    database = SqliteDatabase('/home/sam/Documents/shared/sambot/sambot.db')
    migrator = SqliteMigrator(database)
    # Step 1: Rename User to DiscordProfile.
    migrate(
        migrator.rename_table('user', 'discord_profile'),
        migrator.rename_column('discord_profile', 'discord_id', 'id')
    )
    # Step 2: Create TwitchProfile table.
    database.create_tables([TwitchProfile])
