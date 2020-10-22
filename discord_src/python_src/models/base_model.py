from peewee import *

from discord_src.python_src.environment import Environment


class BaseModel(Model):

    class Meta:
        database = Environment.get_instance().DB
