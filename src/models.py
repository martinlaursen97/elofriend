from sqlalchemy import Column, Integer, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class Member(Base):
    __tablename__ = 'members'

    id = Column(BigInteger, primary_key=True)
    items = relationship('MemberItem', back_populates='author_member')


class Server(Base):
    __tablename__ = 'servers'

    id = Column(BigInteger, primary_key=True)
    items = relationship('MemberItem', back_populates='author_server')


class MemberItem(Base):
    __tablename__ = 'items'

    id = Column(BigInteger, primary_key=True, index=True)
    member_id = Column(BigInteger, ForeignKey('members.id'), nullable=False)
    server_id = Column(BigInteger, ForeignKey('servers.id'), nullable=False)
    wins = Column(Integer, nullable=False, default=0)
    losses = Column(Integer, nullable=False, default=0)
    elo_2v2 = Column(Integer, nullable=False, default=1200)
    elo_3v3 = Column(Integer, nullable=False, default=1200)

    author_member = relationship('Member', back_populates='items')
    author_server = relationship('Server', back_populates='items')