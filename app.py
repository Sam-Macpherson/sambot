import asyncio
import threading

import aiohttp
from flask import request, Flask, render_template, Response

import sambot

# Create a child thread for the bot to run on.
sambot.bot.loop.create_task(sambot.run())
threading.Thread(target=sambot.bot.loop.run_forever).start()

# Create the Flask app
app = Flask(__name__)

# Make a request to this URL for tantooni's stream changed topic.
# https://api.twitch.tv/helix/streams?user_id=48379839
headers = {
    'client-id': '',
    'Authorization': ''
}
payload = {
    'hub.callback': 'https://sambot.loca.lt/webhook',
    'hub.mode': 'subscribe',
    'hub.topic': 'https://api.twitch.tv/helix/streams?user_id=48379839',
    'hub.lease_seconds': 60
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


@app.route('/webhook', methods=['GET'])
def webhook_confirm():
    challenge = request.form.get('hub.challenge')
    print(challenge)
    return Response(challenge, status=200)


loop = asyncio.get_event_loop()
loop.run_until_complete(subscribe())
