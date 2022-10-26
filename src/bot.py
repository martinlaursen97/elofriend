import discord
from discord.ext import commands

from dotenv import load_dotenv

from src.schemas import MemberBase, ServerBase, MemberItemBase
from src.service import Service
from src.database import engine, get_db
from src.models import Base

from table2ascii import table2ascii as t2a, PresetStyle

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

        # Will only be created if they don't already exist
        crud.create_server(server)
        crud.create_member(member)

        res = crud.create_member_item(member_item)
        await ctx.send(res)

    @bot.command()
    @is_channel()
    async def info(ctx, discord_member: discord.Member):
        if crud.get_member_item_info(discord_member.id, ctx.guild.id):
            member = crud.get_member_item_by_member_id_and_server_id(discord_member.id, ctx.guild.id)

            header = ['Player', '2v2', '3v3', 'Wins', 'Losses']
            body = [[await bot.fetch_user(member.member_id), member.elo_2v2, member.elo_3v3, member.wins, member.losses]]

            res = table_output(header, body)

            await ctx.send(res)
        else:
            await ctx.send(f'<@{discord_member.id}> is not registered!')

    @bot.command()
    @is_channel()
    async def ladder(ctx):
        member_items = crud.get_member_items_by_server_id(ctx.guild.id)
        if member_items:
            members = sorted(member_items, key=lambda t: t.elo_2v2, reverse=True)

            header = ['Rank', 'Player', '2v2', '3v3', 'Wins', 'Losses']
            body = []
            for i, m in enumerate(members, start=1):
                row = [i, await bot.fetch_user(m.member_id), m.elo_2v2, m.elo_3v3, m.wins, m.losses]
                body.append(row)

            res = table_output(header, body)

            await ctx.send(res)
        else:
            await ctx.send('No registered players!')

    def table_output(header, body):
        output = t2a(
            header=header,
            body=body,
            style=PresetStyle.thin_compact
        )
        return f"```\n{output}\n```"

    @bot.command()
    @is_channel()
    async def play(ctx, *discord_members: discord.Member):
        print(discord_members)
        pass

    bot.run(TOKEN)


if __name__ == '__main__':
    run()
