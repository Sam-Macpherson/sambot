"""Class to interface with the Guild model."""
from models import Guild
from models.builders import GuildBuilder
from models.currencies import Currency
from models.model_interfaces import ModelInterface


class GuildModelInterface(ModelInterface):
    model = Guild
    builder = GuildBuilder
    GLOBAL = Guild.GLOBAL
    PER_RESPONSE = Guild.PER_RESPONSE

    @classmethod
    def get_currency_for_guild_or_none(cls, guild: Guild, name: str):
        assert isinstance(guild, Guild)
        assert isinstance(name, str)
        currency_query = guild.currencies.where((Currency.name == name) |
                                                (Currency.symbol == name))
        if currency_query.exists():
            return currency_query.get()
        return None

    @classmethod
    def create_currency_for_guild(cls, guild: Guild,
                                  name: str,
                                  symbol: str = None):
        assert isinstance(guild, Guild)
        assert isinstance(name, str)
        assert isinstance(symbol, str) or symbol is None
        if symbol is not None:
            Currency.create(guild=guild, name=name, symbol=symbol)
        else:
            Currency.create(guild=guild, name=name)

    @classmethod
    def get_all_currencies_for_guild(cls, guild: Guild):
        assert isinstance(guild, Guild)
        if guild.currencies.exists():
            return list(guild.currencies)
        return []
