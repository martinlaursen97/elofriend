from pydantic import BaseModel


class MemberBase(BaseModel):
    id: int


class ServerBase(BaseModel):
    id: int


class MemberItemBase(BaseModel):
    member_id: int
    server_id: int
