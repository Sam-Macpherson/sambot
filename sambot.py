from datetime import datetime, timedelta

from discord.ext import commands
from discord.ext.commands import Command, has_permissions

from environment import Environment
from models import User, TriggeredResponse
from models.guild import Guild
from models.triggered_response_usage_timestamp import TriggeredResponseUsageTimestamp
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
    guild_id = message.guild.id
    guild, guild_created = Guild.get_or_create(
        guild_id=guild_id,
        defaults={
            'guild_name': message.guild.name
        }
    )

    if user_created:
        print(f'User {message.author.id} has been added to the database.')
        await message.channel.send(f'Welcome to the server '
                                   f'{message.author.name}!')
    elif guild_user.display_name != message.author.name:
        print(f'User {message.author.id} updated their username and is being'
              f'updated in the database.')
        guild_user.display_name = message.author.name
    if not message.clean_content.startswith('$'):
        words_in_message = message.content.lower().split(' ')
        for word in words_in_message:
            response = TriggeredResponse.get_or_none(
                guild_id=message.guild.id,
                trigger=word
            )
            if response is not None:
                last_used, timestamp_created = \
                    TriggeredResponseUsageTimestamp.get_or_create(
                        user=guild_user,
                        triggered_response=response
                    )
                now = datetime.now()
                if (timestamp_created or last_used.timestamp + timedelta(
                        seconds=guild.triggered_response_cooldown) <= now):
                    last_used.timestamp = now
                    last_used.save()
                    print(f'{message.author.id} instigated the "{word}" '
                          f'triggered response.')
                    await message.channel.send(response.response)
                    break
    guild_user.save()
    await bot.process_commands(message)


@bot.command('addpasta')
@has_permissions(manage_messages=True)
async def add_triggered_response(context, trigger: str, response: str):
    guild_id = context.guild.id
    triggered_response, created = TriggeredResponse.get_or_create(
        guild_id=guild_id,
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


@bot.command('removepasta')
@has_permissions(manage_messages=True)
async def remove_triggered_response(context, trigger: str):
    guild_id = context.guild.id
    triggered_response = TriggeredResponse.get_or_none(
        guild_id=guild_id,
        trigger=trigger
    )
    if triggered_response is not None:
        print(f'{context.message.author.id} removed a copy-pasta in '
              f'the guild: {guild_id} ({context.guild.name}). '
              f'Trigger: {trigger}')
        triggered_response.delete_instance()


@bot.command('pastadelay')
@has_permissions(manage_messages=True)
async def set_triggered_response_cooldown(context, cooldown: int):
    guild_id = context.guild.id
    # It is guaranteed that the guild exists, because we already
    # had to pass through on_message.
    guild = Guild.get(guild_id=guild_id)
    old_cooldown = guild.triggered_response_cooldown
    guild.triggered_response_cooldown = cooldown
    guild.save()
    print(f'Guild {guild.guild_id} ({guild.guild_name}) triggered response '
          f'cooldown updated from {old_cooldown} to '
          f'{cooldown}')


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
