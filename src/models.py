from sqlalchemy import Column, Integer, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from .constants import StartConfig, GameType


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
    wins_2v2 = Column(Integer, nullable=False, default=StartConfig.STARTING_WINS)
    wins_3v3 = Column(Integer, nullable=False, default=StartConfig.STARTING_WINS)
    losses_2v2 = Column(Integer, nullable=False, default=StartConfig.STARTING_LOSSES)
    losses_3v3 = Column(Integer, nullable=False, default=StartConfig.STARTING_LOSSES)
    elo_2v2 = Column(Integer, nullable=False, default=StartConfig.STARTING_ELO)
    elo_3v3 = Column(Integer, nullable=False, default=StartConfig.STARTING_ELO)

    author_member = relationship('Member', back_populates='items')
    author_server = relationship('Server', back_populates='items')

    def get_info_by_game_type(self, game_type):
        if game_type == GameType.TWO_VS_TWO.value:
            return self.elo_2v2, self.wins_2v2, self.losses_2v2
        return self.elo_3v3, self.wins_3v3, self.losses_3v3
