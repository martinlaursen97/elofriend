from enum import IntEnum, Enum


class StartConfig(IntEnum):
    STARTING_ELO = 1200
    STARTING_WINS = 0
    STARTING_LOSSES = 0


class PlayerAmount(IntEnum):
    ONE_VS_ONE = 2
    TWO_VS_TWO = 4
    THREE_VS_THREE = 6


class GameType(Enum):
    ONE_VS_ONE = '1v1'
    TWO_VS_TWO = '2v2'
    THREE_VS_THREE = '3v3'
