from sqlalchemy.orm import Session,sessionmaker
from sqlalchemy import create_engine, Column, String, Integer
from pydantic import BaseModel
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

class CurrentGames(Base):
    __tablename__ = "CurrentGames"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    turn = Column(Integer,index=True)
    white_player_id = Column(Integer)
    black_player_id = Column(Integer)
    last_move = Column(String)
    fen = Column(String)


DATABASE_URL = "sqlite:///C:/Users/ethan/git/Sveltekit-Chess/backend/data/test.db"


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)

def seed_data(db: Session):
    for user_data in users_to_add:
        user = UserDB(**user_data)
        db.add(user)
    db.commit()


# Example seed data
users_to_add = [
    {"username": "user1", "hashed_password": "$2b$12$204BFdf6EeEKNtty6dOlfeiumypfvephe5pmxjv8WjEBXVotSRsdC"},
    {"username": "user2", "hashed_password": "$2b$12$204BFdf6EeEKNtty6dOlfeiumypfvephe5pmxjv8WjEBXVotSRsdC"},
    {"username": "user3", "hashed_password": "$2b$12$204BFdf6EeEKNtty6dOlfeiumypfvephe5pmxjv8WjEBXVotSRsdC"}
]


def main():
    # Create the database tables
    Base.metadata.create_all(bind=engine)

    # Seed the database
    db = SessionLocal()
    seed_data(db)
    db.close()

if __name__ == "__main__":
    db = SessionLocal()
    seed_data(db)
    db.close()
