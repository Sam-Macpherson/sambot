import threading

from flask import Flask, render_template

import sambot

# Create a child thread for the bot to run on.
sambot.bot.loop.create_task(sambot.run())
threading.Thread(target=sambot.bot.loop.run_forever).start()

# Create the Flask app
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')
