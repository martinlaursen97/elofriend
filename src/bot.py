import discord
from discord.ext import commands
from dotenv import load_dotenv
from src.schemas import MemberBase
from src.service import Service
from src.database import engine, get_db
from src.models import Base
from src.response import Response

import os

load_dotenv()
Base.metadata.create_all(bind=engine)


def run():
    TOKEN = os.getenv('TOKEN')
    CHANNEL = os.getenv('CHANNEL')

    intents = discord.Intents.default()
    intents.messages = True

    bot = commands.Bot(command_prefix='!', intents=intents)

    crud = Service(next(get_db()))

    def is_channel():
        async def predicate(ctx):
            return ctx.channel.name == CHANNEL

        return commands.check(predicate)

    @bot.command()
    @is_channel()
    async def register(ctx):
        member = MemberBase(
            discord_id=ctx.author.id,
            server_id=ctx.guild.id
        )

        res = crud.create_member(member)
        await ctx.send(res)

    @bot.command()
    @is_channel()
    async def info(ctx, discord_member: discord.Member):
        member = crud.get_member_by_discord_id(str(discord_member.id))
        res = Response("asd", "ads", "cd", indexed=True)
        print(res)

        # await ctx.send(member)

    @bot.command()
    @is_channel()
    async def ladder(ctx, arg):
        pass

    @bot.command()
    @is_channel()
    async def play(ctx, *args):
        pass

    bot.run(TOKEN)


if __name__ == '__main__':
    run()
