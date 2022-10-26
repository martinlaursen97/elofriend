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

    def table_output(header, body):
        output = t2a(
            header=header,
            body=body,
            style=PresetStyle.thin_compact
        )
        return f"```\n{output}\n```"

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
            body = [[await bot.fetch_user(member.member_id),
                     member.elo_2v2, member.elo_3v3, member.wins, member.losses]]

            res = table_output(header, body)

            await ctx.send(res)
        else:
            await ctx.send(f'Error: <@{discord_member.id}> is not registered!')

    @bot.command()
    @is_channel()
    async def ladder(ctx, arg):
        member_items = crud.get_member_items_by_server_id(ctx.guild.id)
        if arg != '2v2' or arg != '3v3':
            await ctx.send('Error: invalid argument')
            return

        if member_items:
            if arg == '2v2':
                members = sorted(member_items, key=lambda t: t.elo_2v2, reverse=True)
            else:
                members = sorted(member_items, key=lambda t: t.elo_3v3, reverse=True)

            header = ['Rank', 'Player', '2v2', '3v3', 'Wins', 'Losses']
            body = []
            for i, m in enumerate(members, start=1):
                row = [i, await bot.fetch_user(m.member_id), m.elo_2v2, m.elo_3v3, m.wins, m.losses]
                body.append(row)

            res = table_output(header, body)

            await ctx.send(res)
        else:
            await ctx.send('Error: No registered players!')

    @bot.command()
    @is_channel()
    async def play(ctx, discord_members: commands.Greedy[discord.Member]):
        if len(discord_members) != len(set(discord_members)):
            await ctx.send('Error: Duplicate found!')
            return

        # Check if members are registered
        for i in discord_members:
            if not crud.member_item_exists_by_member_id_and_server_id(i.id, ctx.guild.id):
                await ctx.send(f'{i.mention} is not registered!')
                return

        header = [m.name for m in discord_members]
        body = [[]]

        if len(discord_members) == 4:
            winners = discord_members[0:2]
            losers = discord_members[2:]
            body = crud.adjust_elo(winners, losers, ctx.guild.id)
        elif len(discord_members) == 6:
            winners = discord_members[:3]
            losers = discord_members[3:]
            body = crud.adjust_elo(winners, losers, ctx.guild.id)
        else:
            await ctx.send(f'Error: Player count({len(discord_members)}) != 4 or 6')

        res = table_output(header, body)

        await ctx.send('Elo change:')
        await ctx.send(res)

    bot.run(TOKEN)


if __name__ == '__main__':
    run()
