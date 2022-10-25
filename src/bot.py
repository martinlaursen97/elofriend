import discord
from dotenv import load_dotenv

import os

load_dotenv()


def run():
    TOKEN = os.getenv('TOKEN')
    CHANNEL = os.getenv('CHANNEL')

    intents = discord.Intents.default()
    intents.messages = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'Logged in as {client.user}')

    @client.event
    async def on_message(message):

        if message.author == client.user:
            return

        if message.channel.name == CHANNEL:
            pass

    client.run(TOKEN)


if __name__ == '__main__':
    run()
