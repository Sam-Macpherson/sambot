import asyncio
import threading

import aiohttp
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
        return Response(status=200)


loop = asyncio.get_event_loop()
loop.run_until_complete(subscribe())
