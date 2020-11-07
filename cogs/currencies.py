from discord.ext import commands
from discord.ext.commands import has_permissions

from models import Guild
from models.currencies import Currency


class CurrenciesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='createcurrency')
    @has_permissions(administrator=True)
    def create_guild_currency(self, context, currency_name: str):
        guild = Guild.get_or_none(guild_id=context.guild.id)
        if guild:
            if not guild.currencies\
                    .where(Currency.name == currency_name)\
                    .exists():
                Currency.create(guild=guild, name=currency_name)
                await context.channel.send(f'Currency "{currency_name}" '
                                           f'created.')
            else:
                await context.channel.send(f'That currency already exists in '
                                           f'this guild.')
