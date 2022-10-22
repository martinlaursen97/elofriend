import sqlite3

conn = sqlite3.connect('elofriend.db')
print('conn: OK')

conn.execute('''CREATE TABLE IF NOT EXISTS players
            (id TEXT PRIMARY KEY NOT NULL,
            twos INT NOT NULL,
            threes INT NOT NULL);''')
print('table: OK')

STARTING_ELO = 100


def register_player(player_id):
    query = f'INSERT INTO players (id, twos, threes) ' \
            f'VALUES ({player_id}, {STARTING_ELO}, {STARTING_ELO});'

    conn.execute(query)
    conn.commit()


def player_exists(player_id):
    return get_player(player_id) is not None


def reset_elo():
    players = get_players()
    for p in players:
        set_player_elo(p[0], 'twos', STARTING_ELO)
        set_player_elo(p[0], 'threes', STARTING_ELO)


def get_players():
    query = 'SELECT * FROM players'
    return conn.execute(query).fetchall()


def get_player(player_id):
    query = f'SELECT * FROM players WHERE id = "{player_id}";'
    return conn.execute(query).fetchone()


def get_elo_by_player(player_id, bracket):
    query = f'SELECT {bracket} FROM players WHERE id = "{player_id}";'
    return conn.execute(query).fetchone()[0]


def get_avg_team_elo(team, bracket):
    avg = 0
    for player in team:
        avg += get_elo_by_player(player, bracket)
    return avg / len(team)


def set_player_elo(player_id, bracket, new_elo):
    query = f'UPDATE players SET {bracket} = {new_elo} WHERE id = "{player_id}"'
    conn.execute(query)
    conn.commit()


def update_elo(teams, bracket):
    winner_avg = get_avg_team_elo(teams[0], bracket)
    loser_avg = get_avg_team_elo(teams[1], bracket)

    winner_win_prop = 1 / (1 + 10 ** ((loser_avg - winner_avg) / 400))
    loser_win_prop = 1 / (1 + 10 ** ((winner_avg - loser_avg) / 400))

    K = 16

    for player in teams[0]:
        old_elo = get_elo_by_player(player, bracket)
        new_elo = old_elo + K * (1 - winner_win_prop)
        set_player_elo(player, bracket, int(new_elo))

    for player in teams[1]:
        old_elo = get_elo_by_player(player, bracket)
        new_elo = old_elo + K * (0 - loser_win_prop)
        set_player_elo(player, bracket, int(new_elo))
