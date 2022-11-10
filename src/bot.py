import asyncio
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from table2ascii import table2ascii as t2a, PresetStyle

from src.crud_service import CrudService
from src.database import engine, get_db
from src.models import Base
from src.schemas import Member, Server, MemberItem
from src.util import *

load_dotenv()
Base.metadata.create_all(bind=engine)


def run():
    TOKEN = os.getenv('TOKEN')
    CHANNEL = os.getenv('CHANNEL')

    intents = discord.Intents.default()
    intents.messages = True

    bot = commands.Bot(command_prefix='!', intents=intents)
    service = CrudService(next(get_db()))

    def is_channel():
        async def predicate(ctx):
            return ctx.channel.name == CHANNEL

        return commands.check(predicate)

    @bot.command()
    @is_channel()
    async def register(ctx):

        member = Member(
            id=ctx.author.id
        )

        server = Server(
            id=ctx.guild.id
        )

        member_item = MemberItem(
            member_id=member.id,
            server_id=server.id
        )

        # Will only be created if they don't already exist
        service.create_server(server)
        service.create_member(member)

        res = service.create_member_item(member_item)
        await ctx.send(res)

    @bot.command()
    @is_channel()
    async def info(ctx, discord_member: discord.Member):
        if not service.member_item_exists_by_member_id_and_server_id(discord_member.id, ctx.guild.id):
            await ctx.send(f'Error: {discord_member.mention} is not registered!')
            return

        member = service.get_member_item_by_member_id_and_server_id(discord_member.id, ctx.guild.id)

        header = ['Player', '1v1', 'W/L', '2v2', 'W/L', '3v3', 'W/L']
        body = [[discord_member.name,
                 member.elo_1v1, f'{member.wins_1v1}/{member.losses_1v1}',
                 member.elo_2v2, f'{member.wins_2v2}/{member.losses_2v2}',
                 member.elo_3v3, f'{member.wins_3v3}/{member.losses_3v3}']]

        res = table_output(header, body)

        await ctx.send(res)

    @bot.command()
    @is_channel()
    async def ladder(ctx, arg):
        member_items = service.get_member_items_by_server_id(ctx.guild.id)
        valid_args = [GameType.ONE_VS_ONE.value, GameType.TWO_VS_TWO.value, GameType.THREE_VS_THREE.value]

        if arg not in valid_args:
            await ctx.send('Error: Invalid argument!')
            return

        if not member_items:
            await ctx.send('Error: No registered players!')
            return

        members = sort_member_items_by_game_type(member_items, arg)

        header = ['Rank', 'Player', arg, 'W/L']

        body = []
        for index, member in enumerate(members, start=1):
            user = await bot.fetch_user(member.member_id)

            elo, wins, losses = member.get_info_by_game_type(arg)

            row = [index, user.display_name, elo, f'{wins}/{losses}']
            body.append(row)

        res = table_output(header, body)

        await ctx.send(res)

    @bot.command()
    @is_channel()
    async def match(ctx, discord_members: commands.Greedy[discord.Member]):
        if not discord_members:
            await ctx.send('Error: Invalid argument!')
            return

        player_amount = len(discord_members)

        if player_amount != len(set(discord_members)):
            await ctx.send('Error: Duplicate found!')
            return

        valid_player_amounts = [PlayerAmount.ONE_VS_ONE, PlayerAmount.TWO_VS_TWO, PlayerAmount.THREE_VS_THREE]
        if player_amount not in valid_player_amounts:
            await ctx.send(f'Error: Invalid played amount ({player_amount}). '
                           f'Valid amounts are: {[amount.value for amount in valid_player_amounts]}')
            return

        # Check if members are registered
        for member in discord_members:
            if not service.member_item_exists_by_member_id_and_server_id(member.id, ctx.guild.id):
                await ctx.send(f'Error: {member.mention} is not registered!')
                return

        winners = discord_members[:player_amount // 2]
        losers = discord_members[player_amount // 2:]

        # Confirm match
        CHECK_EMOJI = '✅'

        message = await ctx.send(f'Confirm the match {CHECK_EMOJI}\n```'
                                 f'Winners : {", ".join([winner.name for winner in winners])}\n'
                                 f'Losers  : {", ".join([loser.name for loser in losers])}\n'
                                 f'```')
        await message.add_reaction(CHECK_EMOJI)

        try:
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) == CHECK_EMOJI

            reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)

            # If reacted, setup table response
            header = [member.name for member in discord_members]
            body = service.adjust_elo(winners, losers, get_game_type_by_player_amount(player_amount), ctx.guild.id)

            res = table_output(header, body)

            await ctx.send(f'Elo has been updated:\n{res}')
        except asyncio.TimeoutError:
            await ctx.send('TimeOutError: No changes were made.')

    @bot.command()
    @is_channel()
    async def reset(ctx, discord_member: discord.Member):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send('Error: You have to be admin to use this command!')
            return

        if not service.member_item_exists_by_member_id_and_server_id(discord_member.id, ctx.guild.id):
            await ctx.send('Error: Player not found!')
            return

        service.reset_member_item_by_member_id_and_server_id(discord_member.id, ctx.guild.id)
        await ctx.send('Player has been reset!')

    @bot.event
    @is_channel()
    async def on_command_error(ctx, error):
        if isinstance(error, discord.ext.commands.errors.MemberNotFound):
            await ctx.send('Error: Invalid argument!')
            return

    bot.run(TOKEN)


if __name__ == '__main__':
    run()
