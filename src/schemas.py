from pydantic import BaseModel


class MemberBase(BaseModel):
    discord_id: str
    server_id: str

class Member(MemberBase):
    id: int
    wins: int
    losses: int
    elo_2v2: int
    elo_3v3: int

    class Config:
        orm_mode = True
