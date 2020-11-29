import asyncio
import hashlib
import hmac
import json
import threading

import aiohttp
import discord
from flask import request, Flask, render_template, Response

import sambot

from environment import Environment

# Create a child thread for the bot to run on.
sambot.bot.loop.create_task(sambot.run())
threading.Thread(target=sambot.bot.loop.run_forever).start()

# Create the Flask app
app = Flask(__name__)

# Tantooni's twitch id: 48379839
# artsypig's twitch id: 43490535
headers = {
    'client-id': 'gp762nuuoqcoxypju8c569th9wz7q5',
    'Authorization': f'Bearer {Environment.instance().TWITCH_AUTH}'
}
tantooni_payload = {
    'hub.callback': 'https://sambot.loca.lt/webhook',
    'hub.mode': 'subscribe',
    'hub.topic': 'https://api.twitch.tv/helix/streams?user_id=48379839',
    'hub.lease_seconds': 864000,
    'hub.secret': Environment.instance().TWITCH_SECRET
}


async def subscribe():
    async with aiohttp.ClientSession() as session:
        async with session.post(url='https://api.twitch.tv/helix/webhooks/hub',
                                headers=headers,
                                data=tantooni_payload) as resp:
            print(await resp.text())


async def send_notification(channel, embed):
    await channel.send('Hey @everyone, it\'s stream time!')
    await channel.send(embed=embed)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/webhook', methods=['GET', 'POST'])
def webhook_confirm():
    if request.method == 'GET':
        challenge = request.args.get('hub.challenge')
        print(f'Challenge received: {challenge}')
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
        data.get('game_name')
        channel = sambot.bot.get_channel(523994990402207747)
        image_url = data.get('thumbnail_url').replace(
            '{width}', '320', 1
        ).replace('{height}', '180', 1)
        embed = discord.Embed(title=data.get('title'),
                              url=f'https://www.twitch.tv/'
                                  f'{data.get("user_name")}',
                              color=0x6441a5)
        embed.set_author(name="It's stream time",
                         url=f'https://www.twitch.tv/{data.get("user_name")}',
                         icon_url="https://upload.wikimedia.org/wikipedia/commons/6/6c/Yip_Man.jpg")
        embed.set_thumbnail(
            url="https://static-cdn.jtvnw.net/jtv_user_pictures/4a738226-02c8-470d-b252-760eaece3780-profile_image-300x300.png")
        embed.add_field(name='Game', value=data.get('game_name'), inline=True)
        embed.add_field(name='Viewers', value=data.get('viewer_count'), inline=True)
        embed.set_footer(text='See you there!')
        embed.set_image(url=image_url)
        sambot.bot.loop.create_task(send_notification(channel, embed))
        return Response(status=200)


loop = asyncio.get_event_loop()
loop.run_until_complete(subscribe())
