from .constants import PlayerAmount, GameType


def get_game_type_by_player_amount(player_amount):
    if player_amount == PlayerAmount.ONE_VS_ONE:
        return GameType.ONE_VS_ONE
    elif player_amount == PlayerAmount.TWO_VS_TWO:
        return GameType.TWO_VS_TWO
    else:
        return GameType.THREE_VS_THREE


def sort_member_items_by_game_type(member_items, game_type):
    if game_type == GameType.ONE_VS_ONE.value:
        return sorted(member_items, key=lambda member_item: member_item.elo_1v1, reverse=True)
    elif game_type == GameType.TWO_VS_TWO.value:
        return sorted(member_items, key=lambda member_item: member_item.elo_2v2, reverse=True)
    else:
        return sorted(member_items, key=lambda member_item: member_item.elo_3v3, reverse=True)
