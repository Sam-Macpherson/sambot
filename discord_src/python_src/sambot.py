from discord.ext import commands
from discord.ext.commands import Command

from environment import Environment
from utilities.decorators import debuggable

description = '''sambot in Python'''

# These are loaded into RAM, maybe at some point I'll use text files.
pastas = {
    'saturday': 'guys i have exciting news to announce! Next saturday, naked '
                'tantooni stream! come one, come all, get ready for the thrill'
                ' of a lifetime!',
    'cat': 'HeyGuys Hope you are all doing wonderful. I know I\'m not. My '
           ':cat: was just put down. I just wanted to let you know. And my '
           'friend is making a painting of him. I found that very nice. '
           'Please be more like my friend and spread positivity. :smiley:',
    'homeless': 'no lie chat i started watching tantooni like a week ago '
                'and i went from homeless to making 7 figures overnight'
}
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
          f'{"ENABLED" if Environment.get_instance().DEBUG else "DISABLED"}.')
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
    # Copy pastas
    for pasta_key in pastas:
        if pasta_key in message.content.lower():
            print(f'{message.author} instigated the "{pasta_key}" copy-pasta.')
            await message.channel.send(pastas[pasta_key])
    await bot.process_commands(message)


@bot.command()
async def test(context):
    await context.channel.send("You talkin' to me?")
    print(f'{context.message.author} tested me successfully.')


@bot.command()
async def kill(context):
    """This can only be run by the bot owner."""
    if context.message.author.id == Environment.get_instance().OWNER_USER_ID:
        print(f'{context.message.author} successfully killed the bot.')
        await context.bot.logout()
    else:
        print(f'{context.message.author} (not owner) tried to kill the bot.')


if Environment.get_instance().TOKEN is None:
    print("Specify the DISCORD_TOKEN in the .env file.")
else:
    bot.run(Environment.get_instance().TOKEN)
