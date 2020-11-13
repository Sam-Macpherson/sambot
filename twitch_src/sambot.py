from twitchio.ext import commands

from environment import Environment
from models.model_interfaces import TriggeredResponseModelInterface, UserModelInterface, GuildModelInterface


class Sambot(commands.Bot):

    def __init__(self, event_loop, irc_token: str):
        super().__init__(irc_token=irc_token,
                         prefix='$',
                         nick='sambot__',
                         initial_channels=['tantooni', 'artsypig'],
                         loop=event_loop)

    async def event_pubsub(self, data):
        # Not sure what this is yet.
        pass

    async def event_ready(self):
        print(f'Logged in twitch bot as {self.nick}.')

    async def event_message(self, message):
        words_in_message = message.content.lower().split(' ')
        user = message.author
        # artyspig's user id: 43490535
        if not user.id == 43490535:
            return
        first_word = words_in_message[0]
        if not (first_word.startswith('$') and
                first_word[1:] in Environment.instance().BOT_COMMANDS):
            # Local cache of words so we don't have to hit the database for
            # repeated words, like if a message is "bot bot bot bot bot dead"
            # it won't do a query for "bot" 5 times.
            checked_words = []
            for word in words_in_message:
                # Remove all punctuation and symbols.
                if word in checked_words:
                    continue
                checked_words.append(word)
                user = UserModelInterface.get_or_none(
                    discord_id=150816670493966336)
                guild = GuildModelInterface.get_or_none(
                    guild_id=270010247811170307)
                response = TriggeredResponseModelInterface.get_allowed_or_none(
                    user=user,
                    guild=guild,
                    trigger=word,
                )
                if response is not None:
                    if response.type == TriggeredResponseModelInterface.TEXT:
                        await message.channel.send(response.response)
                    # Only 1 triggered response per message.
                    break
        await self.handle_commands(message)

    @commands.command(name='test')
    async def test_command(self, context):
        print(f'Test command received.')
        await context.channel.send(f'You talkin\' to me?')

