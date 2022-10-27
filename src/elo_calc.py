def win_prop(avg, opponent_avg):
    return 1 / (1 + 10 ** ((opponent_avg - avg) / 400))


def new_elo(old_elo, K, win_prop, win=True):
    if win:
        return int(old_elo + K * (1 - win_prop))
    return int(old_elo + K * (0 - win_prop))

