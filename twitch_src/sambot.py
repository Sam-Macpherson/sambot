from twitchio.ext import commands


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

    @commands.command(name='test')
    async def test_command(self, context):
        print(f'Test command received.')
        await context.channel.send(f'You talkin\' to me?')
