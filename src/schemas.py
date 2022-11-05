from pydantic import BaseModel


class Member(BaseModel):
    id: int


class Server(BaseModel):
    id: int


class MemberItem(BaseModel):
    member_id: int
    server_id: int
