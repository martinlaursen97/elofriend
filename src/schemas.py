from pydantic import BaseModel


class MemberBase(BaseModel):
    discord_id: str


class Member(MemberBase):
    id: int
    wins: int
    losses: int
    elo_2v2: int
    elo_3v3: int

    class Config:
        orm_mode = True


class ServerBase(BaseModel):
    server_id: str


class Server(ServerBase):
    id: int

class MemberItemBase(BaseModel):
    pass