from discord.ext import commands
from discord.ext.commands import has_permissions

from models.model_interfaces import (
    GuildModelInterface,
    BannedWordModelInterface,
)


class BannedWordsCog(commands.Cog, name='cogs.banned_words_cog'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='banword')
    @has_permissions(manage_messages=True)
    async def ban_word(self, context, word: str):
        guild = GuildModelInterface.get_or_none(guild_id=context.guild.id)
        if guild is None:
            return
        banned_word, created = BannedWordModelInterface.get_or_create(
            guild=guild,
            word=word.lower(),
        )
        if created:
            print(f'{context.message.author.id} banned a word in '
                  f'the guild: {guild.guild_id} ({guild.guild_name}). '
                  f'word: {word}')
        else:
            print(f'{context.message.author.id} tried to ban word in '
                  f'the guild: {guild.guild_id} ({guild.guild_name}). '
                  f'word: {word}, but it is already banned.')
        await context.channel.send(f'That word is now banned in this '
                                   f'guild.')

    @commands.command(name='unbanword')
    @has_permissions(manage_messages=True)
    async def unban_word(self, context, word: str):
        guild = GuildModelInterface.get_or_none(guild_id=context.guild.id)
        if guild is None:
            return
        banned_word = BannedWordModelInterface.get_or_none(
            guild=guild,
            word=word
        )
        if banned_word is None:
            return
        BannedWordModelInterface.delete_instance(banned_word)
        await context.channel.send(f'That word is now un-banned '
                                   f'in this guild.')
        print(f'{context.message.author.id} unbanned a word in '
              f'the guild: {guild.guild_id} ({guild.guild_name}). '
              f'word: {word}')
