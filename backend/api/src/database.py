from sqlalchemy import create_engine
from api.src.models import Base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///C:/Users/ethan/git/Sveltekit-Chess/backend/data/test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)