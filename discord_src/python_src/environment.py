"""
A singleton class to store the environment variables.
"""
import os

from dotenv import load_dotenv
from peewee import SqliteDatabase

from utilities.utilities import truthy

from discord_src.python_src.models.user import User


class Environment:
    __instance = None
    DATABASE_TABLES = [User]

    @staticmethod
    def get_instance():
        """ Static access method. """
        if Environment.__instance is None:
            Environment()
        return Environment.__instance

    def __init__(self):
        """ Virtually private constructor. """
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
            self.DEBUG = truthy(os.getenv('DEBUG'))
            self.DEBUG_CHANNEL_ID = integer_variables['DEBUG_CHANNEL_ID']
            self.OWNER_USER_ID = integer_variables['OWNER_USER_ID']
            self.DB = SqliteDatabase('sambot.db')
            self.DB.connect()
            self.DB.create_tables(self.DATABASE_TABLES)
            Environment.__instance = self


Environment()
