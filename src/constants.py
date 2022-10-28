from enum import IntEnum


class StartConfig(IntEnum):
    STARTING_ELO = 1200
    STARTING_WINS = 0
    STARTING_LOSSES = 0


class PlayerAmount(IntEnum):
    TWO_VS_TWO = 4
    THREE_VS_THREE = 6


class TeamSize(IntEnum):
    TWO_VS_TWO = 2
    THREE_VS_THREE = 3
