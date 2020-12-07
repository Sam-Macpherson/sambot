from discord import Embed
from discord.ext import commands
from discord.ext.commands import has_permissions

from models.exceptions import InsufficientFundsError
from models.model_interfaces import (
    UserModelInterface,
    GuildModelInterface,
    DiscordProfileModelInterface,
    CurrencyModelInterface,
)


class CurrenciesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='createcurrency')
    @has_permissions(manage_messages=True)
    async def create_guild_currency(self, context,
                                    currency_name: str,
                                    symbol: str = None):
        guild = GuildModelInterface.get_or_none(guild_id=context.guild.id)
        if guild is None:
            return
        currency = GuildModelInterface.get_currency_for_guild_or_none(
            guild=guild,
            name=currency_name,
        )
        if currency is not None:
            await context.channel.send(f'That currency already exists in '
                                       f'this guild.')
            return
        GuildModelInterface.create_currency_for_guild(
            guild=guild,
            name=currency_name,
            symbol=symbol,
        )
        await context.channel.send(f'Currency "{currency_name}" created.')

    @commands.command(name='changecurrencyname')
    @has_permissions(manage_messages=True)
    async def change_guild_currency_name(self, context,
                                         currency_name: str,
                                         new_currency_name: str = None):
        if new_currency_name is None:
            await context.channel.send(f'Supply a new name for the currency if '
                                       f'you want to change its name.')
            return
        guild = GuildModelInterface.get_or_none(guild_id=context.guild.id)
        if guild is None:
            return
        currency = GuildModelInterface.get_currency_for_guild_or_none(
            guild=guild,
            name=currency_name
        )
        if currency is None:
            await context.channel.send(f'There is no currency by the '
                                       f'name "{currency_name}" in '
                                       f'this guild.')
            return
        currency.name = new_currency_name
        CurrencyModelInterface.save_instance(currency)
        await context.channel.send(f'Currency "{currency_name}" '
                                   f'has been updated to '
                                   f'"{new_currency_name}".')

    @commands.command(name='removecurrency')
    @has_permissions(manage_messages=True)
    async def remove_guild_currency(self, context, currency_name: str):
        guild = GuildModelInterface.get_or_none(guild_id=context.guild.id)
        if guild is None:
            return
        currency = GuildModelInterface.get_currency_for_guild_or_none(
            guild=guild,
            name=currency_name,
        )
        if currency is None:
            await context.channel.send(f'That currency does not exist in '
                                       f'this guild.')
            return
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
            CurrencyModelInterface.delete_instance(currency)
            await context.channel.send(f'The currency {currency_name} '
                                       f'was removed from this guild.')
        else:
            await context.channel.send(f'Cancelled.')

    @commands.command(name='listcurrencies')
    @has_permissions(manage_messages=True)
    async def list_guild_currencies(self, context):
        guild = GuildModelInterface.get_or_none(guild_id=context.guild.id)
        if guild is None:
            return
        embed = Embed(title=f'Currencies in {guild.guild_name}', color=0x358022)
        for currency in GuildModelInterface.get_all_currencies_for_guild(guild):
            embed.add_field(name=currency.symbol,
                            value=currency.name,
                            inline=False)
        await context.channel.send(embed=embed)

    @commands.command(name='give')
    async def give_currency(self, context,
                            recipient: str,
                            currency: str,
                            amount: int):
        if not recipient.startswith('<@'):
            await context.channel.send(f'You need to mention a user in order '
                                       f'to give to them.')
            return
        if not isinstance(amount, int):
            await context.channel.send(f'You can only send whole number '
                                       f'amounts.')
            return
        guild = GuildModelInterface.get_or_none(guild_id=context.guild.id)
        if guild is None:
            return
        # Mentions work like: <@!150816670493966336> so ignore extra characters.
        recipient_id = recipient[2:-1]
        if recipient.startswith('<@!'):
            recipient_id = recipient_id[1:]
        sender_profile = DiscordProfileModelInterface.get_or_none(
            id=context.message.author.id
        )
        if sender_profile is not None:
            sender = sender_profile.user
        else:
            print(f'Something went wrong and the sender DiscordProfile has '
                  f'no user.')
            return
        receiver = DiscordProfileModelInterface.get_or_none(
            id=recipient_id
        )
        if receiver is not None:
            receiver = receiver.user
        else:
            print(f'Something went wrong and the receiver DiscordProfile has '
                  f'no user.')
            return
        if receiver is None:
            await context.channel.send(f'Looks like that user is not an '
                                       f'active member of the guild. You '
                                       f'can only give to active members.')
            return
        guild_currency = \
            GuildModelInterface.get_currency_for_guild_or_none(
                guild=guild,
                name=currency
            )
        if guild_currency is None:
            await context.channel.send(f'That is not a currency.')
            return
        sender_has_infinite_money = context.channel \
            .permissions_for(context.message.author) \
            .manage_messages
        receiver_has_infinite_money = context.channel \
            .permissions_for(context.guild.get_member(int(recipient_id))) \
            .manage_messages
        if not sender_has_infinite_money:
            try:
                UserModelInterface.pay(
                    user=sender,
                    currency=guild_currency,
                    amount=amount,
                )
            except InsufficientFundsError as exc:
                await context.channel.send(exc.detail)
                return
        if not receiver_has_infinite_money:
            UserModelInterface.receive(
                user=receiver,
                currency=guild_currency,
                amount=amount,
            )
        await context.channel.send(f'Gave {amount} {currency} to '
                                   f'{receiver.display_name}.')

