from pydantic import BaseModel


class MemberBase(BaseModel):
    id: int


class Member(MemberBase):
    items: list

    class Config:
        orm_mode = True


class ServerBase(BaseModel):
    id: int


class Server(ServerBase):
    items: list

    class Config:
        orm_mode = True


class MemberItemBase(BaseModel):
    member_id: int
    server_id: int


class MemberItem(MemberItemBase):
    id: int
    wins: int
    losses: int
    elo_2v2: int
    elo_3v3: int

    class Config:
        orm_mode = True
