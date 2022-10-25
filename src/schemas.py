from pydantic import BaseModel


class Member(BaseModel):
    id: int
    discord_id: str
    server_id: str
    wins: int
    losses: int
    elo_2v2: int
    elo_3v3: int

    class Config:
        orm_mode = True

