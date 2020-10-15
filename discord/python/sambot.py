import os
import discord
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

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
    print('=========')


@bot.event
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


bot.run(TOKEN)
