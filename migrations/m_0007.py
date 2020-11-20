from playhouse.migrate import *

from models import User
from models.currencies import Wallet
from models.profiles import DiscordProfile
from models.triggered_responses import TriggeredResponseUsageTimestamp

"""
Migration 0007.
Adds the Foreign Key to User to the discord and twitch profile models.
This migration assumes there are no twitch profile in the database, it comes 
from before twitch integration was implemented.
"""


def migration():
    database = SqliteDatabase('sambot.db')
    migrator = SqliteMigrator(database)
    # Step 1: create the User table.
    # database.create_tables([User])
    # # Step 2: add the FK fields to the discord and twitch profiles.
    # user_fk_field = ForeignKeyField(
    #     model=User,
    #     field=User.id,
    #     unique=True,
    #     null=True,
    #     backref='discord_profile'
    # )
    # migrate(
    #     migrator.add_column('discordprofile', 'user_id', user_fk_field)
    # )
    # user_fk_field = ForeignKeyField(
    #     model=User,
    #     field=User.id,
    #     unique=True,
    #     null=True,
    #     backref='twitch_profile'
    # )
    # migrator.add_column('twitchprofile', 'user_id', user_fk_field)
    # # Step 3: create a User for each discord and twitch profile.
    # for discord_profile in DiscordProfile.select():
    #     user = User.create()
    #     discord_profile.user = user
    #     discord_profile.save()
    # Step 4: Add the User id's FK to wallet and triggered response usage
    # timestamp, and populate it.
    user_fk_for_wallet = ForeignKeyField(
        User,
        User.id,
        backref='wallet',
        unique=True,
        null=True,
    )
    user_fk = ForeignKeyField(
        User,
        field=User.id,
        backref='triggered_response_usage_timestamps',
        null=True
    )
    migrate(
        migrator.drop_index('wallet', 'wallet_user_id'),
        migrator.drop_index('triggeredresponseusagetimestamp',
                            'triggeredresponseusagetimestamp_user_id'),
        migrator.add_column('wallet', 'user_id', user_fk_for_wallet),
        migrator.add_column('triggeredresponseusagetimestamp',
                            'user_id', user_fk)
    )
    for discord_profile in DiscordProfile.select():
        # This wallet is guaranteed to exist.
        wallet = Wallet.select().where(
            Wallet.discord_profile_id == discord_profile.id
        ).get()
        print('wallet id', wallet.id)
        print('discord profile user id', discord_profile.user_id)
        wallet.user_id = discord_profile.user_id
        wallet.save()
        tr_usage_timestamps = TriggeredResponseUsageTimestamp.select().where(
            TriggeredResponseUsageTimestamp.discord_profile_id ==
            discord_profile.id
        )
        for tr_usage_timestamp in tr_usage_timestamps:
            tr_usage_timestamp.user_id = discord_profile.user_id
            tr_usage_timestamp.save()
    # Step 5: Remove the DiscordProfile FK from wallet and tr usage timestamp
    migrate(
        migrator.drop_column('wallet', 'discord_profile_id'),
        migrator.drop_column('triggeredresponseusagetimestamp',
                             'discord_profile_id'),
    )
