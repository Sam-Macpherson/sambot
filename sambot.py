import io
import string
import threading
import asyncio

import discord
from discord.ext import commands as discord_commands
from twitchio.ext import commands as twitch_commands
from discord.ext.commands import has_permissions

from twitch_src import Sambot
from discord_src.cogs import (
    BannedWordsCog,
    TriggeredResponseCog,
    CurrenciesCog,
)
from environment import Environment
from models.model_interfaces import (
    BannedWordModelInterface,
    GuildModelInterface, TriggeredResponseModelInterface,
)
from models.model_interfaces.model_interface import DiscordProfileModelInterface
from utilities.decorators import debuggable
from utilities.lru_cache import LRUCache

description = '''sambot in Python.'''

intents = discord.Intents.all()
discord_bot = discord_commands.Bot(command_prefix='$',
                                   description=description,
                                   intents=intents,  # Camping is in-tents.
                                   help_command=None)
twitch_bot = None

guild_cache = LRUCache(capacity=5)
user_cache = LRUCache(capacity=10)


@discord_bot.event
async def on_ready():
    print(f'Logged in discord bot as {discord_bot.user.name}, id: {discord_bot.user.id}')
    print(f'Debug mode is '
          f'{"ENABLED" if Environment.instance().DEBUG else "DISABLED"}.')
    print('=========')
    discord_bot.add_cog(TriggeredResponseCog(discord_bot))
    discord_bot.add_cog(BannedWordsCog(discord_bot))
    discord_bot.add_cog(CurrenciesCog(discord_bot))
    Environment.instance().BOT_COMMANDS = [
        command.name for command in discord_bot.commands
    ]


@discord_bot.event
@debuggable
async def on_message(message):
    # We don't want the bot replying to itself.
    if message.author == discord_bot.user:
        return
    print(f'Message received, author: {message.author}, '
          f'content: {message.content}, '
          f'cleaned content: {message.clean_content}')
    profile, profile_created = DiscordProfileModelInterface.get_or_create(
        id=message.author.id,
        defaults={
            'display_name': message.author.name
        }
    )
    guild, guild_created = GuildModelInterface.get_or_create(
        guild_id=message.guild.id,
        defaults={
            'guild_name': message.guild.name
        }
    )
    if not guild_created and guild.guild_name != message.guild.name:
        print(f'Guild {guild.guild_id} has had its name updated and is being '
              f'updated in the database.')
        guild.guild_name = message.guild.name
        GuildModelInterface.save_instance(guild)
    if profile_created:
        print(f'Discord profile {message.author.id} has been added '
              f'to the database.')
    elif profile.display_name != message.author.name:
        print(f'User {message.author.id} updated their username and is being'
              f'updated in the database.')
        profile.display_name = message.author.name
        DiscordProfileModelInterface.save_instance(profile)
    words_in_message = message.content.lower().split(' ')
    first_word = words_in_message[0]
    punctuation_removal_translation = str.maketrans('', '', string.punctuation)
    if not (first_word.startswith('$') and
            first_word[1:] in Environment.instance().BOT_COMMANDS):
        # Local cache of words so we don't have to hit the database for
        # repeated words, like if a message is "bot bot bot bot bot dead"
        # it won't do a query for "bot" 5 times.
        checked_words = []
        for word in words_in_message:
            # Remove all punctuation and symbols.
            word = word.translate(punctuation_removal_translation)
            if word in checked_words:
                continue
            # Delete messages if they contain banned words.
            banned_word = BannedWordModelInterface.get_or_none(
                guild=guild,
                word=word
            )
            if banned_word is not None:
                await message.delete()
                # Send a warning DM to the sender.
                await message.author.send(f'Don\'t be saying that stuff.')
                break
            checked_words.append(word)
            response = TriggeredResponseModelInterface.get_allowed_or_none(
                user=profile.user,
                guild=guild,
                trigger=word,
            )
            if response is not None:
                print(f'{message.author.id} triggered the "{word}" '
                      f'triggered response (type {response.type}).')
                if response.type == TriggeredResponseModelInterface.TEXT:
                    await message.channel.send(response.response)
                else:
                    data = io.BytesIO(response.image)
                    await message.channel.send(
                        file=discord.File(data, 'image.jpg')
                    )
                # Only 1 triggered response per message.
                break
    await discord_bot.process_commands(message)


@discord_bot.command()
@has_permissions(manage_messages=True)
async def test(context):
    await context.channel.send('You talkin\' to me?')
    print(f'{context.message.author} tested me successfully.')


@discord_bot.command()
async def kill(context):
    """This can only be run by the bot owner."""
    if context.message.author.id == Environment.instance().OWNER_USER_ID:
        print(f'{context.message.author} successfully killed the bot.')
        await context.bot.logout()
    else:
        print(f'{context.message.author} (not owner) tried to kill the bot.')

if Environment.instance().TWITCH_TOKEN is None:
    print('Specify the TWITCH_TOKEN in the .env file.')
else:
    twitch_bot = Sambot(
        asyncio.new_event_loop(),
        irc_token=Environment.instance().TWITCH_TOKEN,
    )


def twitch_worker():
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    new_loop.run_until_complete(twitch_bot.run())
    return


threading.Thread(target=twitch_worker).start()
if Environment.instance().DISCORD_TOKEN is None:
    print('Specify the DISCORD_TOKEN in the .env file.')
else:
    discord_bot.run(Environment.instance().DISCORD_TOKEN)
