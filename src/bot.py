import discord
from discord.ext import commands
from dotenv import load_dotenv
from src.schemas import MemberBase, ServerBase, MemberItemBase
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
            id=ctx.author.id
        )

        server = ServerBase(
            id=ctx.guild.id
        )

        member_item = MemberItemBase(member_id=member.id, server_id=server.id)

        res_server = crud.create_server(server)
        print(res_server)

        res_member = Response(crud.create_member(member))
        print(res_member)

        res_created = crud.create_member_item(member_item)
        await ctx.send(res_created)

    @bot.command()
    @is_channel()
    async def info(ctx, discord_member: discord.Member):
        if crud.get_member_item_info(discord_member.id, ctx.guild.id):
            member = crud.get_member_item_by_member_id_and_server_id(discord_member.id, ctx.guild.id)
            res = Response(f'2v2: {member.elo_2v2}',
                           f'3v3: {member.elo_3v3}',
                           f'win/loss: {member.wins}/{member.losses}')

            await ctx.send(res)
        else:
            await ctx.send(Response(f'<@{discord_member.id}> is not registered!'))

    @bot.command()
    @is_channel()
    async def ladder(ctx, arg):
        pass

    @bot.command()
    @is_channel()
    async def play(ctx, *discord_members: discord.Member):
        print(discord_members)
        pass

    bot.run(TOKEN)


if __name__ == '__main__':
    run()
