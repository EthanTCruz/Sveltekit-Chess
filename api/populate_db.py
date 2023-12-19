from sqlalchemy.orm import Session,sessionmaker
from database import Base,SessionLocal,engine
from models import UserDB
from sqlalchemy import create_engine
from models import Base


DATABASE_URL = "sqlite:///./test.db"

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
