"""
A singleton class to store the environment variables.
"""
import os

from dotenv import load_dotenv
from models import base_model
from models.banned_words import BannedWord
from models.currencies import Currency, Wallet, CurrencyAmount
from models import Guild, User
from models.profiles import DiscordProfile, TwitchProfile
from models.triggered_responses import (
    TriggeredResponse,
    TriggeredResponseUsageTimestamp,
)
from models.twitch_notifications import StreamLiveNotification
from utilities import truthy


class Environment:
    __instance = None
    base_tables = [Guild, User]
    profile_tables = [DiscordProfile, TwitchProfile]
    banned_words_tables = [BannedWord]
    triggered_responses_tables = [
        TriggeredResponse,
        TriggeredResponseUsageTimestamp,
    ]
    currency_tables = [Currency, Wallet, CurrencyAmount]
    twitch_tables = [StreamLiveNotification]

    database_tables = (
            base_tables +
            profile_tables +
            banned_words_tables +
            triggered_responses_tables +
            currency_tables +
            twitch_tables
    )

    @staticmethod
    def instance():
        """Static access method. """
        if Environment.__instance is None:
            Environment()
        return Environment.__instance

    def __init__(self):
        """Virtually private constructor. """
        if Environment.__instance is not None:
            raise Exception("Environment is a singleton!")
        else:
            load_dotenv()
            # You cannot cast None to integer, so this check
            # guarantees we end up with integer values for these environment
            # variables.
            integer_variables = {
                'DEBUG_CHANNEL_ID': 0,
                'OWNER_USER_ID': 0
            }
            for var in integer_variables:
                var_entry = os.getenv(var)
                if var_entry is not None:
                    integer_variables[var] = int(var_entry)

            # Set DEBUG=True in the .env file to enable debug mode.
            self.TOKEN = os.getenv('DISCORD_TOKEN')
            self.TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
            self.TWITCH_AUTH = os.getenv('TWITCH_AUTH')
            self.TWITCH_SECRET = os.getenv('TWITCH_SECRET')
            self.DEBUG = truthy(os.getenv('DEBUG'))
            self.DEBUG_CHANNEL_ID = integer_variables['DEBUG_CHANNEL_ID']
            self.OWNER_USER_ID = integer_variables['OWNER_USER_ID']
            self.DB = base_model.db
            # The number of seconds between triggered response availabilities.
            # Defaults to 2 minutes.
            self.TRIGGERED_RESPONSE_COOLDOWN = 120
            self.DB.connect()
            self.DB.create_tables(self.database_tables)
            self.BOT_COMMANDS = []
            Environment.__instance = self


Environment()
