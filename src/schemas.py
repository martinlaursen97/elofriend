from pydantic import BaseModel


class Player(BaseModel):
    id: int
    discord_id: str
    server_id: str
    elo_2v2: int
    elo_3v3: int

