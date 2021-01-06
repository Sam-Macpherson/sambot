import json

import aiohttp
from discord.ext import commands
from discord.ext.commands import has_permissions

from environment import Environment
from models.model_interfaces import StreamLiveNotificationModelInterface


class TwitchNotificationsCog(commands.Cog, name='cogs.twitch_notifications_cog'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='streamnotify')
    @has_permissions(manage_messages=True)
    async def create_twitch_stream_notification(self,
                                                context,
                                                streamer_name: str,
                                                channel: str,
                                                footer: str = None):
        if not channel.startswith('<#'):
            return await context.channel.send(f'You need to mention a channel '
                                              f'to notify when that streamer '
                                              f'goes live.')
        channel_id = channel[2:-1]
        #if self.bot.get_channel(channel_id) is None:
        #    return await context.channel.send('That\'s not a real channel!')

        # Get the twitch streamer.
        url = f'https://api.twitch.tv/helix/users?login={streamer_name}'
        headers = {
            'client-id': Environment.instance().TWITCH_CLIENT_ID,
            'Authorization': f'Bearer {Environment.instance().TWITCH_AUTH}'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    return await context.message.channel.send(
                        'Could not reach the Twitch backend.'
                    )
                data = await resp.json()
                if len(data['data']) == 0:
                    return await context.message.channel.send(
                        f'Could not find the Twitch streamer: {streamer_name}.'
                    )
                data = data['data'][0]
                twitch_display_name = data['display_name']
                twitch_id = data['id']
                twitch_profile_picture_url = data['profile_image_url']
                defaults = {
                    'streamer_display_name': twitch_display_name,
                    'profile_image_url': twitch_profile_picture_url,
                }
                max_footer_length = \
                    StreamLiveNotificationModelInterface.FOOTER_MAX_LENGTH
                if footer is not None:
                    if len(footer) > max_footer_length:
                        return await context.message.channel.send(
                            f'Maximum footer text length is '
                            f'{max_footer_length} characters, you gave one '
                            f'that is {len(footer)}. Try again.'
                        )
                    defaults['footer'] = footer
                notification, created = \
                    StreamLiveNotificationModelInterface.get_or_create(
                        streamer_twitch_id=twitch_id,
                        notify_channel=channel_id,
                        defaults=defaults
                    )
                if not created:
                    return await context.message.channel.send(
                        f'There is already a notification for '
                        f'{twitch_display_name} in that channel.'
                    )
                return await context.message.channel.send(
                    f'Stream notification created. When {twitch_display_name} '
                    f'goes live, that channel will be notified.'
                )

    @commands.command(name='removestreamnotify')
    @has_permissions(manage_messages=True)
    async def remove_twitch_stream_notification(self,
                                                context,
                                                streamer_name: str,
                                                channel: str):
        if not channel.startswith('<#'):
            return await context.channel.send(f'You need to mention a channel '
                                              f'to notify when that streamer '
                                              f'goes live.')
        channel_id = channel[2:-1]
        #if self.bot.get_channel(channel_id) is None:
        #    return await context.channel.send('That\'s not a real channel!')
        # Get the twitch streamer.
        url = f'https://api.twitch.tv/helix/users?login={streamer_name}'
        headers = {
            'client-id': Environment.instance().TWITCH_CLIENT_ID,
            'Authorization': f'Bearer {Environment.instance().TWITCH_AUTH}'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    return await context.message.channel.send(
                        'Could not reach the Twitch backend.'
                    )
                data = await resp.json()
                if len(data['data']) == 0:
                    return await context.message.channel.send(
                        f'Could not find the Twitch streamer: {streamer_name}.'
                    )
                data = data['data'][0]
                twitch_id = data['id']
                notification = StreamLiveNotificationModelInterface.get_or_none(
                    streamer_twitch_id=twitch_id,
                    notify_channel=channel_id
                )
                if notification is None:
                    return await context.message.channel.send(
                        'That is not a notification that has been created.'
                    )
                StreamLiveNotificationModelInterface.delete_instance(
                    notification)
                return await context.message.channel.send(
                    f'That channel will no longer be notified when '
                    f'{streamer_name} goes live.'
                )
