from discord.ext import commands
from discord.ext.commands import has_permissions

from models import TriggeredResponse
from models.guild import Guild


class TriggeredResponseCog(commands.Cog):
    """A cog to logically group all commands related to
    Triggered Responses.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='addpasta')
    @has_permissions(manage_messages=True)
    async def add_triggered_response(self, context, trigger: str, response: str):
        guild_id = context.guild.id
        guild = Guild.get_or_none(
            guild_id=guild_id
        )
        if guild:
            triggered_response, created = TriggeredResponse.get_or_create(
                guild=guild,
                trigger=trigger,
                defaults={
                    'response': response
                }
            )
            if created:
                print(f'{context.message.author.id} created a copy-pasta in '
                      f'the guild: {guild_id} ({context.guild.name}). '
                      f'Trigger: {trigger}, Response: {response}')
            else:
                triggered_response.response = response
                triggered_response.save()
                print(f'{context.message.author.id} updated the copy-pasta in '
                      f'the guild: {guild_id} ({context.guild.name}). '
                      f'Trigger: {trigger}, New Response: {response}')
            await context.channel.send(response)

    @commands.command(name='removepasta')
    @has_permissions(manage_messages=True)
    async def remove_triggered_response(self, context, trigger: str):
        guild_id = context.guild.id
        guild = Guild.get_or_none(
            guild_id=guild_id
        )
        if guild:
            triggered_response = TriggeredResponse.get_or_none(
                guild=guild,
                trigger=trigger
            )
            if triggered_response is not None:
                triggered_response.delete_instance()
                await context.channel.send(f'Removed pasta "{trigger}" from the '
                                           f'guild.')
                print(f'{context.message.author.id} removed a copy-pasta in '
                      f'the guild: {guild_id} ({context.guild.name}). '
                      f'Trigger: {trigger}')

    @commands.command(name='pastadelay')
    @has_permissions(manage_messages=True)
    async def set_triggered_response_cooldown(self, context, cooldown: int):
        guild_id = context.guild.id
        # It is guaranteed that the guild exists, because we already
        # had to pass through on_message.
        guild = Guild.get(guild_id=guild_id)
        old_cooldown = guild.triggered_response_cooldown
        guild.triggered_response_cooldown = cooldown
        guild.save()
        await context.channel.send(f'Guild pasta cooldown changed from '
                                   f'{old_cooldown} to {cooldown}')
        print(f'Guild {guild.guild_id} ({guild.guild_name}) triggered response '
              f'cooldown updated from {old_cooldown} to '
              f'{cooldown}')
