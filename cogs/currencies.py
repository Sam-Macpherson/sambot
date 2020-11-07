from discord import Embed
from discord.ext import commands
from discord.ext.commands import has_permissions
from peewee import DoesNotExist

from models import Guild
from models.currencies import Currency


class CurrenciesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='createcurrency')
    @has_permissions(manage_guild=True)
    async def create_guild_currency(self, context,
                                    currency_name: str,
                                    symbol: str = None):
        guild = Guild.get_or_none(guild_id=context.guild.id)
        if guild:
            if not guild.currencies \
                    .where(Currency.name == currency_name) \
                    .exists():
                if symbol:
                    Currency.create(guild=guild,
                                    name=currency_name,
                                    symbol=symbol)
                else:
                    Currency.create(guild=guild,
                                    name=currency_name)
                await context.channel.send(f'Currency "{currency_name}" '
                                           f'created.')
            else:
                await context.channel.send(f'That currency already exists in '
                                           f'this guild.')

    @commands.command(name='changecurrencyname')
    @has_permissions(manage_guild=True)
    async def change_guild_currency_name(self, context,
                                         currency_name: str,
                                         new_currency_name: str = None):
        if new_currency_name:
            guild = Guild.get_or_none(guild_id=context.guild.id)
            if guild:
                try:
                    currency = guild.currencies\
                        .where(Currency.name == currency_name)\
                        .get()
                    currency.name = new_currency_name
                    currency.save()
                    await context.channel.send(f'Currency "{currency_name}" '
                                               f'has been updated to '
                                               f'"{new_currency_name}".')
                except DoesNotExist:
                    await context.channel.send(f'There is no currency by the '
                                               f'name "{currency_name}" in '
                                               f'this guild.')
        else:
            await context.channel.send(f'Supply a new name for the currency if '
                                       f'you want to change its name.')

    @commands.command(name='removecurrency')
    @has_permissions(manage_guild=True)
    async def remove_guild_currency(self, context, currency_name: str):
        guild = Guild.get_or_none(guild_id=context.guild.id)
        if guild:
            currency = Currency.get_or_none(guild=guild, name=currency_name)
            if currency:
                await context.channel.send(f'Are you absolutely sure that you '
                                           f'want to remove that currency from '
                                           f'this guild? This action cannot be '
                                           f'undone, and users of this guild '
                                           f'will lose their holdings. Type '
                                           f'"Yes" to confirm, type anything '
                                           f'else to cancel.')

                def check(msg):
                    return (msg.author == context.message.author and
                            msg.channel == context.channel)
                message = await self.bot.wait_for('message', check=check)
                if message.content == 'Yes':
                    currency.delete_instance()
                    await context.channel.send(f'The currency {currency_name} '
                                               f'was removed from this guild.')
                else:
                    await context.channel.send(f'Cancelled.')
            else:
                await context.channel.send(f'That currency does not exist in '
                                           f'this guild.')

    @commands.command(name='listcurrencies')
    @has_permissions(manage_guild=True)
    async def list_guild_currencies(self, context):
        guild = Guild.get_or_none(guild_id=context.guild.id)
        if guild:
            embed = Embed(title=f'Currencies in {guild.guild_name}',
                          color=0x358022)
            for currency in guild.currencies.order_by(Currency.name.asc()):
                embed.add_field(name=currency.symbol,
                                value=currency.name,
                                inline=False)
            await context.channel.send(embed=embed)
