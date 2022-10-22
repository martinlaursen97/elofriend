import discord
import os
from src.validation import get_teams

from re import search
from src.database import *
from sqlite3 import IntegrityError
from src.formatting import add_tags, tag_to_id
from dotenv import load_dotenv

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
            msg = message.content

            if msg == '!register':
                try:
                    register_player(str(message.author.id))
                    await message.channel.send('You have been registered!')
                except IntegrityError:
                    await message.channel.send('You are already registered!')

            elif msg.startswith('!info '):
                player_tag = search(r'!info(.*)', msg)[1]
                player = get_player(tag_to_id(player_tag))

                response = f'Info: {player_tag}\n'
                response += f'2v2: {player[1]}\n'
                response += f'3v3: {player[2]}'

                await message.channel.send(response)

            elif msg == '!reset':
                reset_elo()
                await message.channel.send('Elo has been reset!')

            elif msg == '!ladder 2v2':
                players = sorted(get_players(), key=lambda t: t[1], reverse=True)

                response = '2v2 Ladder:\n'
                for i, p in enumerate(players, start=1):
                    response += f'{i}: {add_tags(p[0])} -----> {p[1]}\n'

                await message.channel.send(response)

            elif msg == '!ladder 3v3':
                players = sorted(get_players(), key=lambda t: t[2], reverse=True)

                response = '3v3 Ladder:\n'
                for i, p in enumerate(players, start=1):
                    response += f'{i}: {add_tags(p[0])} -----> {p[2]}\n'

                await message.channel.send(response)

            elif msg.startswith('!2v2 '):
                tags = search(r'!2v2(.*)', msg)[1]

                try:
                    teams = await get_teams(tags, message, team_size=2)
                    update_elo(teams, 'twos')
                    await message.channel.send('Elo has been updated!')
                except Exception:
                    return

            elif msg.startswith('!3v3 '):
                tags = search(r'!3v3(.*)', msg)[1]

                try:
                    teams = await get_teams(tags, message, team_size=3)
                    update_elo(teams, 'threes')
                    await message.channel.send('Elo has been updated!')
                except Exception:
                    return

            elif msg == '!help':
                response = "Prefix your command with !2v2 or !3v3, followed by the tag of each player with each team " \
                           "separated by a comma. The team on the left side of the comma, are the " \
                           "winners.\n\nExample:\n!2v2 " \
                           "@P1#1234 @P2#4321, @P3#2345, @P45432\nAfterwards, the elo of each player will be updated "

                await message.channel.send(response)

    client.run(TOKEN)


if __name__ == '__main__':
    run()
