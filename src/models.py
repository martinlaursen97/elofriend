from sqlalchemy import Column, Integer, String
from .database import Base


class Member(Base):
    __tablename__ = 'members'

    id = Column(Integer, primary_key=True, index=True)
    discord_id = Column(String, unique=True, nullable=False)
    server_id = Column(String, nullable=False)
    wins = Column(Integer, nullable=False, default=0)
    losses = Column(Integer, nullable=False, default=0)
    elo_2v2 = Column(Integer, nullable=False, default=1200)
    elo_3v3 = Column(Integer, nullable=False, default=1200)
