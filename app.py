import asyncio
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

# Make a request to this URL for tantooni's stream changed topic.
# https://api.twitch.tv/helix/streams?user_id=48379839
headers = {
    'client-id': 'gp762nuuoqcoxypju8c569th9wz7q5',
    'Authorization': f'Bearer {Environment.instance().TWITCH_AUTH}'
}
payload = {
    'hub.callback': 'https://sambot.loca.lt/webhook',
    'hub.mode': 'subscribe',
    'hub.topic': 'https://api.twitch.tv/helix/streams?user_id=48379839',
    'hub.lease_seconds': 864000
}


async def subscribe():
    async with aiohttp.ClientSession() as session:
        async with session.post(url='https://api.twitch.tv/helix/webhooks/hub',
                                headers=headers,
                                data=payload) as resp:
            print(await resp.text())


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
        print('Data received:')
        print(request.form)
        print(request.args)
        print(request.data)
        # Hardcode for Twitch.tv/tantooni
        # Use the request.data body:
        """
        b'{
        "data":
        [
        {"game_id":"459931",
        "game_name":"Old School RuneScape",
        "id":"40699668606",
        "language":"en",
        "started_at":"2020-11-26T20:49:59Z",
        "tag_ids":null,
        "thumbnail_url":"https://static-cdn.jtvnw.net/previews-ttv
        /live_user_tantooni-{width}x{height}.jpg",
        "title":"The title | !lights | !lego",
        "type":"live",
        "user_id":"48379839",
        "user_name":"Tantooni",
        "viewer_count":0
        }
        ]
        }'
        """
        # import json
        # data = json.loads(request.data)
        # data.get('data')[0].get('game_name'), etc.
        # channel = sambot.bot.get_channel(523994990402207747)
        # embed = discord.Embed(title="Tantooni is now live on Twitch, swing by!",
        #                       url="https://www.twitch.tv/tantooni",
        #                       color=0x6441a5)
        # embed.set_author(name="It's stream time",
        #                  url="https://www.twitch.tv/tantooni",
        #                  icon_url="https://upload.wikimedia.org/wikipedia/commons/6/6c/Yip_Man.jpg")
        # embed.set_thumbnail(
        #     url="https://static-cdn.jtvnw.net/jtv_user_pictures/4a738226-02c8-470d-b252-760eaece3780-profile_image-300x300.png")
        # embed.set_footer(text='See you there!')
        # sambot.bot.loop.create_task(channel.send(embed=embed))
        return Response(status=200)


loop = asyncio.get_event_loop()
loop.run_until_complete(subscribe())
