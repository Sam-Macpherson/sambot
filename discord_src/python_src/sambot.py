import os
from discord.ext import commands

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

bot = commands.Bot(command_prefix='$', description=description)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}, id: {bot.user.id}')
    print(f'Debug mode is '
          f'{"ENABLED" if Environment.get_instance().DEBUG else "DISABLED"}.')
    print('=========')


@bot.event
@debuggable
async def on_message(message):
    # We don't want the bot replying to itself.
    if message.author == bot.user:
        return
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
