from discord import Embed
from discord.ext import commands
from discord.ext.commands import has_permissions
from peewee import DoesNotExist

from models import Guild, base_model
from models.currencies import Currency, CurrencyAmount
from models.model_interfaces import UserModelInterface


class CurrenciesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='createcurrency')
    @has_permissions(manage_messages=True)
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
    @has_permissions(manage_messages=True)
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
    @has_permissions(manage_messages=True)
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
    @has_permissions(manage_messages=True)
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

    @commands.command(name='give')
    async def give_currency(self, context,
                            recipient: str,
                            currency: str,
                            amount: int):
        if not recipient.startswith('<@!') and not recipient.startswith('<@'):
            print(recipient)
            await context.channel.send(f'You need to mention a user in order '
                                       f'to give to them.')
            return
        guild = Guild.get_or_none(guild_id=context.guild.id)
        if not guild:
            return
        # Mentions work like: <@!150816670493966336> so ignore extra characters.
        recipient_id = recipient[2:-1]
        if recipient.startswith('<@!'):
            recipient_id = recipient_id[1:]
        sender = UserModelInterface.get(
            discord_id=context.message.author.id
        )
        receiver = UserModelInterface.get(discord_id=recipient_id)
        if not receiver:
            await context.channel.send(f'Looks like that user is not an '
                                       f'active member of the guild. You '
                                       f'can only give to active members.')
            return
        guild_currency = guild.currencies \
            .where((Currency.name == currency) | (Currency.symbol == currency)) \
            .get()
        if not guild_currency:
            await context.channel.send(f'That is not a currency.')
            return
        sender_currency = sender.wallet.get().currency_amounts \
            .where(CurrencyAmount.currency == guild_currency)
        sender_currency = \
            sender_currency.get() if sender_currency.exists() else None
        sender_has_infinite_money = context.channel \
            .permissions_for(context.message.author) \
            .manage_messages
        receiver_has_infinite_money = context.channel \
            .permissions_for(context.guild.get_member(int(recipient_id))) \
            .manage_messages
        if (not sender_has_infinite_money and
                (not sender_currency or
                 sender_currency.amount < amount)):
            await context.channel.send(f'Insufficient funds.')
            return
        recipient_currency = receiver.wallet.get().currency_amounts \
            .where(CurrencyAmount.currency == guild_currency)
        recipient_currency = \
            recipient_currency.get() if recipient_currency.exists() else None
        if not receiver_has_infinite_money and not recipient_currency:
            CurrencyAmount.create(
                wallet=receiver.wallet.get(),
                currency=guild_currency,
                amount=amount
            )
        else:
            with base_model.db.atomic():
                if not receiver_has_infinite_money:
                    recipient_currency.amount += amount
                    recipient_currency.save()
                if not sender_has_infinite_money:
                    sender_currency.amount -= amount
                    sender_currency.save()
        await context.channel.send(f'Sent {amount} {currency} to '
                                   f'{receiver.display_name}.')

