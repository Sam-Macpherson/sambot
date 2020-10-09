import discord
from discord.ext import commands

TOKEN = 'TOKEN'

description = '''sambot in Python'''
bot = commands.Bot(command_prefix='?', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def test(context):
    await context.channel.send("You talkin' to me?")
    print(f'{context.message.author} tested me succesfully.')


bot.run(TOKEN)
