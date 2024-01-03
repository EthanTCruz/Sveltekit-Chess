from pydantic import BaseModel
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base



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

class UserCreate(BaseModel):
    username: str
    password: str

# Create the database tables
    
class CurrentGames(Base):
    __tablename__ = "CurrentGames"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    game_id = Column(String)
    move_no = Column(Integer)
    turn = Column(Integer,index=True)
    white_player_id = Column(Integer)
    black_player_id = Column(Integer)
    last_move = Column(String)
    fen = Column(String)

class PastGames(Base):
    __tablename__ = "PastGames"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    game_id = Column(String)
    move_no = Column(Integer)
    winner = Column(Integer,index=True)
    white_player_id = Column(Integer)
    black_player_id = Column(Integer)
    last_move = Column(String)
    fen = Column(String)