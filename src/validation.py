from .formatting import tags_to_teams
from .database import player_exists


def has_duplicates(teams):
    return len(set(teams)) != len(teams)


async def registered_tags(teams, message):
    for player in teams:
        if not player_exists(player):
            await message.channel.send(f'ERROR: <@{player}> is not registered!')
            return False
    return True


def valid_sizes(t1, t2, team_size):
    return len(t1) == team_size and len(t2) == team_size


async def get_teams(tags, message, team_size):
    t1, t2 = tags_to_teams(tags)
    teams = t1 + t2

    if not valid_sizes(t1, t2, team_size):
        await message.channel.send(f'ERROR: Each team have to contain {team_size} players!')
        raise Exception

    if has_duplicates(teams):
        await message.channel.send('ERROR: Duplicate tags!')
        raise Exception

    if not await registered_tags(teams, message):
        raise Exception

    return t1, t2
