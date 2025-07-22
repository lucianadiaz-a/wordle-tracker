from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    player_id = Column(Integer, ForeignKey("users.id"))
    score = Column(Integer)
    raw_result = Column(String)

    player = relationship("User")
