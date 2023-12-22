from sqlalchemy import create_engine
from api.src.models import Base, UserDB
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "sqlite:///C:/Users/ethan/git/Sveltekit-Chess/backend/data/test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)

hashed_pass = "$2b$12$VYD8bmkRyiqrDp5ocK2LFujtvDi4Qh59ARW5HHkLypbJ6cBYzV3n2"
def populate_db_if_empty():
    db: Session = SessionLocal()

    # Check if UserDB is empty
    if db.query(UserDB).first() is None:
        # Add default users
        default_users = [UserDB(username='user1', hashed_password=hashed_pass), 
                         UserDB(username='user2', hashed_password=hashed_pass),
                         UserDB(username='user3', hashed_password=hashed_pass)]
        db.add_all(default_users)

    # Similarly check and populate for other tables if needed
    # ...

    db.commit()
    db.close()

# Call the function after initializing the database
populate_db_if_empty()