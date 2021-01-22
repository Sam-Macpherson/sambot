import asyncio
import random
import hashlib
import hmac
import json
import threading
from datetime import datetime, timedelta

import aiohttp
import discord
from flask import request, Flask, render_template, Response

import sambot

from environment import Environment

# Create a child thread for the bot to run on.
from models import base_model, BaseModel
from models.model_interfaces import StreamLiveNotificationModelInterface

sambot.bot.loop.create_task(sambot.run())
threading.Thread(target=sambot.bot.loop.run_forever).start()

# Create the Flask app
app = Flask(__name__)


async def send_notification(channel, embed):
    await channel.send('Hey @everyone, it\'s stream time!', embed=embed)


async def renew_all_subscriptions(startup: bool = False):
    headers = {
        'client-id': Environment.instance().TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {Environment.instance().TWITCH_AUTH}'
    }
    one_day = 60 * 60 * 24
    old_uuid = 'x'

    while True:
        with open('/home/pi/sambot_uuid', 'r') as uuid_file:
            new_uuid = uuid_file.readline().rstrip('\n')
        
        if startup or old_uuid != new_uuid:
            subscriptions = StreamLiveNotificationModelInterface.get_all()
        else:
            subscriptions = \
                StreamLiveNotificationModelInterface.get_expiring_soon()
        for subscription in subscriptions:
            # Update the subscription's profile picture URL.
            url = f'https://api.twitch.tv/helix/users?id=' \
                  f'{subscription.streamer_twitch_id}'
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as resp:
                    if resp.status != 200:
                        print(f'Could not reach Twitch backend when attempting '
                              f'to update the profile picture for the streamer '
                              f'{subscription.streamer_display_name}')
                        return
                    data = await resp.json()
                    if len(data['data']) == 0:
                        print(f'Could not find the Twitch streamer: '
                              f'{subscription.streamer_display_name}')
                    data = data['data'][0]
                    subscription.profile_image_url = data['profile_image_url']
            # Renew each subscription.
            payload = {
                'hub.callback': f'https://{new_uuid}.loca.lt/webhook',
                'hub.mode': 'subscribe',
                'hub.topic': f'https://api.twitch.tv/helix/streams?user_id='
                             f'{subscription.streamer_twitch_id}',
                'hub.lease_seconds': one_day,
                'hub.secret': Environment.instance().TWITCH_SECRET
            }
            now = datetime.now()
            subscription.subscription_length = one_day
            subscription.created = now
            subscription.expires = now + timedelta(
                seconds=subscription.subscription_length)
            StreamLiveNotificationModelInterface.save_instance(subscription)
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        url='https://api.twitch.tv/helix/webhooks/hub',
                        headers=headers,
                        data=payload) as resp:
                    print(await resp.text())
        old_uuid = new_uuid
        startup = False
        await asyncio.sleep(60)  # Renew subscriptions every minute.


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/webhook', methods=['GET', 'POST'])
def webhook_confirm():
    if request.method == 'GET':
        challenge = request.args.get('hub.challenge')
        return Response(challenge, status=200)
    else:
        received_signature = request.headers.get('X-Hub-Signature')
        generated_signature = 'sha256=' + hmac.new(
            Environment.instance().TWITCH_SECRET.encode('utf-8'),
            request.data,
            hashlib.sha256
        ).hexdigest()
        if received_signature is None or \
                received_signature != generated_signature:
            return Response(render_template('404.html'), status=404)

        data = json.loads(request.data).get('data')
        if not data or data[0].get('type') != 'live':
            return Response(status=200)
        data = data[0]
        # Get the StreamLiveNotification objects for this streamer.
        notifications = \
            StreamLiveNotificationModelInterface.get_all_for_streamer(
                streamer_twitch_id=int(data['user_id'])
            )
        for notification in notifications:
            channel = sambot.bot.get_channel(notification.notify_channel)
            image_url = data.get('thumbnail_url').replace(
                '{width}', '320', 1
            ).replace('{height}', '180', 1) + f'?r={random.randint(1, 99999)}'
            embed = discord.Embed(title=data.get('title'),
                                  url=f'https://www.twitch.tv/'
                                      f'{data.get("user_name")}',
                                  color=0x6441a5)
            embed.set_author(
                name=f'{data.get("user_name")} just went live!',
                url=f'https://www.twitch.tv/{data.get("user_name")}',
                icon_url="https://upload.wikimedia.org/wikipedia/"
                         "commons/6/6c/Yip_Man.jpg")
            embed.set_thumbnail(url=notification.profile_image_url)
            embed.add_field(name='Game',
                            value=data.get('game_name'),
                            inline=True)
            embed.add_field(name='Viewers',
                            value=data.get('viewer_count'),
                            inline=True)
            embed.set_footer(text=notification.footer)
            embed.set_image(url=image_url)
            sambot.bot.loop.create_task(send_notification(channel, embed))
            notification.last_notified = datetime.now()
            StreamLiveNotificationModelInterface.save_instance(notification)
        return Response(status=200)


startup_loop = asyncio.new_event_loop()
startup_loop.create_task(renew_all_subscriptions(startup=True))
#renew_loop = asyncio.new_event_loop()
#renew_loop.create_task(renew_all_subscriptions())
#threading.Thread(target=renew_loop.run_forever).start()
threading.Thread(target=startup_loop.run_forever).start()
