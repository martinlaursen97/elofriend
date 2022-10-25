import discord
from discord.ext import commands
from dotenv import load_dotenv

import os

load_dotenv()


def run():
    TOKEN = os.getenv('TOKEN')
    CHANNEL = os.getenv('CHANNEL')

    intents = discord.Intents.default()
    intents.messages = True

    bot = commands.Bot(command_prefix='!', intents=intents)

    def is_channel():
        async def predicate(ctx):
            return ctx.channel.name == CHANNEL
        return commands.check(predicate)

    @bot.command()
    @is_channel()
    async def register(ctx):
        pass

    @bot.command()
    @is_channel()
    async def info(ctx, member: discord.Member):
        pass

    @bot.command()
    @is_channel()
    async def ladder(ctx, arg):
        pass

    @bot.command()
    @is_channel()
    async def play(ctx, *args):
        pass

    @bot.command()
    @is_channel()
    async def help(ctx):
        pass

    bot.run(TOKEN)


if __name__ == '__main__':
    run()
