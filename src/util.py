from .constants import PlayerAmount, GameType


def get_game_type_by_player_amount(player_amount):
    if player_amount == PlayerAmount.TWO_VS_TWO:
        return GameType.TWO_VS_TWO
    else:
        return GameType.THREE_VS_THREE
