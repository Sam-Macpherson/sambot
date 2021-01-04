import io

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

from models.model_interfaces import (
    GuildModelInterface,
    TriggeredResponseModelInterface,
)


class TriggeredResponseCog(commands.Cog):
    """A cog to logically group all commands related to
    Triggered Responses.
    """
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def _remove_triggered_response(context, trigger: str, type: int):
        guild = GuildModelInterface.get_or_none(guild_id=context.guild.id)
        if guild is None:
            return
        triggered_response = TriggeredResponseModelInterface.get_or_none(
            type=type,
            guild=guild,
            trigger=trigger
        )
        if triggered_response is None:
            return
        TriggeredResponseModelInterface.delete_instance(triggered_response)
        await context.channel.send(f'Removed pasta "{trigger}" from the '
                                   f'guild.')
        print(f'{context.message.author.id} removed a copy-pasta in '
              f'the guild: {guild.guild_id} ({guild.guild_name}). '
              f'Trigger: {trigger}')

    @staticmethod
    async def _set_cooldown(context, cooldown_type: int, cooldown: int):
        guild = GuildModelInterface.get_or_none(guild_id=context.guild.id)
        if guild is None:
            return
        if cooldown_type == TriggeredResponseModelInterface.TEXT:
            old_cooldown = guild.triggered_text_cooldown
            guild.triggered_text_cooldown = cooldown
        else:
            old_cooldown = guild.triggered_image_cooldown
            guild.triggered_image_cooldown = cooldown
        GuildModelInterface.save_instance(guild)
        await context.channel.send(f'Guild cooldown changed from '
                                   f'{old_cooldown} to {cooldown}')
        print(f'Guild {guild.guild_id} ({guild.guild_name}) triggered response '
              f'cooldown (type {cooldown_type}) updated from {old_cooldown} to '
              f'{cooldown}')

    @commands.command(name='cooldowntype')
    @has_permissions(manage_messages=True)
    async def set_cooldown_type(self, context, type: str):
        valid_types = ['global', 'perpasta']
        if type not in valid_types:
            return
        guild = GuildModelInterface.get_or_none(guild_id=context.guild.id)
        if guild is None:
            return
        if type == 'global':
            guild.cooldown_type = guild.GLOBAL
        else:
            guild.cooldown_type = guild.PER_RESPONSE
        GuildModelInterface.save_instance(guild)
        await context.channel.send(f'Guild cooldown type changed to {type}')
        print(f'Guild {guild.guild_id} ({guild.guild_name}) triggered response '
              f'cooldown type updated to {type}')

    @commands.command(name='addpasta')
    @has_permissions(manage_messages=True)
    async def add_triggered_text(self, context, trigger: str, response: str):
        guild = GuildModelInterface.get_or_none(guild_id=context.guild.id)
        if guild is None:
            return
        triggered_response, created = \
            TriggeredResponseModelInterface.get_or_create(
                guild=guild,
                trigger=trigger,
                defaults={
                    'type': TriggeredResponseModelInterface.TEXT,
                    'response': response
                }
            )
        if created:
            print(f'{context.message.author.id} created a copy-pasta in '
                  f'the guild: {guild.guild_id} ({guild.guild_name}). '
                  f'Trigger: {trigger}, Response: {response}')
        else:
            triggered_response.response = response
            TriggeredResponseModelInterface.save_instance(triggered_response)
            print(f'{context.message.author.id} updated the copy-pasta in '
                  f'the guild: {guild.guild_id} ({guild.guild_name}). '
                  f'Trigger: {trigger}, New Response: {response}')
        await context.channel.send(response)

    @commands.command(name='removepasta')
    @has_permissions(manage_messages=True)
    async def remove_triggered_text(self, context, trigger: str):
        await self._remove_triggered_response(
            context,
            trigger,
            TriggeredResponseModelInterface.TEXT,
        )

    @commands.command(name='pastadelay')
    @has_permissions(manage_messages=True)
    async def set_triggered_text_cooldown(self, context, cooldown: int):
        await self._set_cooldown(
            context,
            TriggeredResponseModelInterface.TEXT,
            cooldown
        )

    @commands.command(name='addimage')
    @has_permissions(manage_messages=True)
    async def add_triggered_image(self, context, trigger: str, url: str):
        guild = GuildModelInterface.get_or_none(guild_id=context.guild.id)
        if guild is None:
            return
        image_headers = [
            'image/png',
            'image/jpg',
            'image/jpeg',
            'image/webp',
        ]
        async with aiohttp.ClientSession() as session:
            response, _ = \
                TriggeredResponseModelInterface.get_or_create(
                    guild=guild,
                    trigger=trigger,
                    defaults={
                        'type': TriggeredResponseModelInterface.IMAGE,
                        'image': None
                    }
                )
            async with session.get(url) as resp:
                if resp.headers.get('Content-Type', '') not in \
                        image_headers:
                    return await context.channel.send(
                        f'Only PNG, JPG images are supported.'
                    )
                if resp.status != 200:
                    return await context.message.channel.send(
                        f'Could not find image.'
                    )
                image_bytes = await resp.read()
                response.image = image_bytes
                TriggeredResponseModelInterface.save_instance(response)
                data = io.BytesIO(image_bytes)
                await context.message.channel.send(
                    file=discord.File(data, 'image.jpg')
                )

    @commands.command(name='removeimage')
    @has_permissions(manage_messages=True)
    async def remove_triggered_image(self, context, trigger: str):
        await self._remove_triggered_response(
            context,
            trigger,
            TriggeredResponseModelInterface.IMAGE,
        )

    @commands.command(name='imagedelay')
    @has_permissions(manage_messages=True)
    async def set_triggered_image_cooldown(self, context, cooldown: int):
        await self._set_cooldown(
            context,
            TriggeredResponseModelInterface.IMAGE,
            cooldown
        )
