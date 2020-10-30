import io
import string
from datetime import datetime, timedelta

import discord
from discord.ext import commands
from discord.ext.commands import Command

from cogs import (
    BannedWordsCog,
    TriggeredResponseCog,
)
from environment import Environment
from models import User, TriggeredResponse, BannedWord
from models.guild import Guild
from models.triggered_response_usage_timestamp import (
    TriggeredResponseUsageTimestamp,
)
from utilities.decorators import debuggable


description = '''sambot in Python'''

# These only work in APSH, because of the ID fields, and are very much
# a temporary proof-of-concept. At the very least we could use
# await message.channel.guild.fetch_emojis() to get the emojis available.
emotes = {
    'cheer': '<:tantooCheer:699108024190632026>',
    'clown': '<:tantooClown:699108024232706208>',
    'sad': '<:tantooSad:702719869551902760>',
    'engineer': '<:tantooGineer:700136352146260009>',
}

bot = commands.Bot(command_prefix='$', description=description)


async def duplicate_emotes(context, number: int):
    command = context.message.content.split(' ')[0][1:]
    length = len(command)
    # Discord has a 2000 character limit
    number_to_print = min(2000 // length, number)
    message = ''.join([emotes[command] for _ in range(number_to_print)])
    await context.channel.send(message)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}, id: {bot.user.id}')
    print(f'Debug mode is '
          f'{"ENABLED" if Environment.instance().DEBUG else "DISABLED"}.')
    print('=========')
    bot.add_cog(TriggeredResponseCog(bot))
    bot.add_cog(BannedWordsCog(bot))
    Environment.instance().BOT_COMMANDS = [
        command.name for command in bot.commands
    ]
    for emote in emotes:
        command = Command(duplicate_emotes, name=emote)
        bot.add_command(command)


@bot.event
@debuggable
async def on_message(message):
    # We don't want the bot replying to itself.
    if message.author == bot.user:
        return

    print(f'Message received, author: {message.author}, '
          f'content: {message.content}, '
          f'cleaned content: {message.clean_content}')
    guild_user, user_created = User.get_or_create(
        discord_id=message.author.id,
        defaults={
            'display_name': message.author.name
        }
    )
    guild, guild_created = Guild.get_or_create(
        guild_id=message.guild.id,
        defaults={
            'guild_name': message.guild.name
        }
    )

    if user_created:
        print(f'User {message.author.id} has been added to the database.')
    elif guild_user.display_name != message.author.name:
        print(f'User {message.author.id} updated their username and is being'
              f'updated in the database.')
        guild_user.display_name = message.author.name
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
            if word not in checked_words:
                # Delete messages if they contain banned words.
                banned_word = BannedWord.get_or_none(guild=guild, word=word)
                if banned_word is not None:
                    await message.delete()
                    # Send a warning DM to the sender.
                    await message.author.send(f'Don\'t be saying that stuff.')
                    break
                response = TriggeredResponse.get_or_none(
                    guild=guild,
                    trigger=word
                )
                checked_words.append(word)
                if response is not None:
                    last_used, timestamp_created = \
                        TriggeredResponseUsageTimestamp.get_or_create(
                            user=guild_user,
                            triggered_response=response
                        )
                    now = datetime.now()
                    if response.type == TriggeredResponse.TEXT:
                        if (timestamp_created or last_used.timestamp + timedelta(
                                seconds=guild.triggered_text_cooldown) <= now):
                            last_used.timestamp = now
                            last_used.save()
                            print(f'{message.author.id} instigated the "{word}" '
                                  f'triggered response.')
                            await message.channel.send(response.response)
                            # Only 1 triggered response per message.
                            break
                    elif response.type == TriggeredResponse.IMAGE:
                        if(timestamp_created or last_used.timestamp + timedelta(
                                seconds=guild.triggered_image_cooldown) <= now):
                            last_used.timestamp = now
                            last_used.save()
                            data = io.BytesIO(response.image)
                            await message.channel.send(
                                file=discord.File(data, 'image.jpg')
                            )
                            break

    guild_user.save()
    await bot.process_commands(message)


@bot.command()
async def test(context):
    await context.channel.send('You talkin\' to me?')
    print(f'{context.message.author} tested me successfully.')


@bot.command()
async def kill(context):
    """This can only be run by the bot owner."""
    if context.message.author.id == Environment.instance().OWNER_USER_ID:
        print(f'{context.message.author} successfully killed the bot.')
        await context.bot.logout()
    else:
        print(f'{context.message.author} (not owner) tried to kill the bot.')


if Environment.instance().TOKEN is None:
    print('Specify the DISCORD_TOKEN in the .env file.')
else:
    bot.run(Environment.instance().TOKEN)
