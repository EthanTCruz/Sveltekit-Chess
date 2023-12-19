from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class User(BaseModel):
    username: str

class UserInDB(User):
    hashed_password: str


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique = True,index=True)
    hashed_password = Column(String)

# Create the database tables
    
class CurrentGames(Base):
    __tablename__ = "CurrentGames"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    turn = Column(Integer,index=True)
    white_player_id = Column(Integer)
    black_player_id = Column(Integer)
    last_move = Column(String)
    fen = Column(String)
