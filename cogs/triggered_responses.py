import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

from models import Guild, TriggeredResponse


class TriggeredResponseCog(commands.Cog):
    """A cog to logically group all commands related to
    Triggered Responses.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='cooldowntype')
    @has_permissions(manage_messages=True)
    async def set_cooldown_type(self, context, type: str):
        valid_types = ['global', 'perpasta']
        if type not in valid_types:
            return
        guild = Guild.get(guild_id=context.guild.id)
        if type == 'global':
            guild.cooldown_type = guild.GLOBAL
        else:
            guild.cooldown_type = guild.PER_RESPONSE
        guild.save()
        await context.channel.send(f'Guild cooldown type changed '
                                   f'to {type}')
        print(f'Guild {guild.guild_id} ({guild.guild_name}) triggered response '
              f'cooldown type updated to {type}')

    @commands.command(name='addpasta')
    @has_permissions(manage_messages=True)
    async def add_triggered_text(self, context, trigger: str, response: str):
        guild_id = context.guild.id
        guild = Guild.get_or_none(
            guild_id=guild_id
        )
        if guild:
            triggered_response, created = TriggeredResponse.get_or_create(
                guild=guild,
                trigger=trigger,
                defaults={
                    'type': TriggeredResponse.TEXT,
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
    async def remove_triggered_text(self, context, trigger: str):
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
    async def set_triggered_text_cooldown(self, context, cooldown: int):
        guild_id = context.guild.id
        # It is guaranteed that the guild exists, because we already
        # had to pass through on_message.
        guild = Guild.get(guild_id=guild_id)
        old_cooldown = guild.triggered_text_cooldown
        guild.triggered_text_cooldown = cooldown
        guild.save()
        await context.channel.send(f'Guild pasta cooldown changed from '
                                   f'{old_cooldown} to {cooldown}')
        print(f'Guild {guild.guild_id} ({guild.guild_name}) triggered response '
              f'cooldown updated from {old_cooldown} to '
              f'{cooldown}')

    @commands.command(name='addimage')
    @has_permissions(manage_messages=True)
    async def add_triggered_image(self, context, trigger: str, url: str):
        guild_id = context.guild.id
        guild = Guild.get_or_none(
            guild_id=guild_id
        )
        if guild:
            triggered_response, _ = TriggeredResponse.get_or_create(
                guild=guild,
                trigger=trigger,
                defaults={
                    'type': TriggeredResponse.IMAGE,
                    'image': None
                }
            )
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await context.message.channel.send(
                            f'Could not find image.'
                        )
                    image_bytes = await resp.read()
                    triggered_response.image = image_bytes
                    triggered_response.save()
                    await context.message.channel.send(
                        file=discord.File(image_bytes, 'image.jpg')
                    )

    @commands.command(name='removeimage')
    @has_permissions(manage_messages=True)
    async def remove_triggered_image(self, context, trigger: str):
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
                await context.channel.send(f'Removed "{trigger}" trigger from '
                                           f'the guild.')
                print(f'{context.message.author.id} removed a trigger in '
                      f'the guild: {guild_id} ({context.guild.name}). '
                      f'Trigger: {trigger}')

    @commands.command(name='imagedelay')
    @has_permissions(manage_messages=True)
    async def set_triggered_image_cooldown(self, context, cooldown: int):
        guild_id = context.guild.id
        # It is guaranteed that the guild exists, because we already
        # had to pass through on_message.
        guild = Guild.get(guild_id=guild_id)
        old_cooldown = guild.triggered_image_cooldown
        guild.triggered_image_cooldown = cooldown
        guild.save()
        await context.channel.send(f'Guild image cooldown changed from '
                                   f'{old_cooldown} to {cooldown}')
        print(f'Guild {guild.guild_id} ({guild.guild_name}) image response '
              f'cooldown updated from {old_cooldown} to '
              f'{cooldown}')
