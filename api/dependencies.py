from types import NoneType
from api.database import SessionLocal
from api.models import UserDB,CurrentGames
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime,timedelta
from sqlalchemy import or_, and_
import random

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

WAITING_TURN = 0
DEFAULT_INT = 0

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db: Session, username: str):
    return db.query(UserDB).filter(UserDB.username == username).first()

def get_user_by_id(db: Session, user_id: str):
    return db.query(UserDB).filter(UserDB.id == user_id).first()

def get_current_games(db: Session, user_id: int):
    results = db.query(CurrentGames).filter(or_(
        CurrentGames.white_player_id == user_id,
        CurrentGames.black_player_id == user_id)).first()
    return results

def find_empty_games(db: Session, user_id: int):
    results = db.query(CurrentGames).filter(CurrentGames.turn == WAITING_TURN).first()
    return results

start_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

def create_game(db: Session, white_player_id: int = DEFAULT_INT, black_player_id: int = DEFAULT_INT):
    
    if white_player_id is DEFAULT_INT and black_player_id is DEFAULT_INT:
        raise Exception("created game without host")
    
    new_game = CurrentGames(
        turn=WAITING_TURN,
        white_player_id=white_player_id,
        black_player_id=black_player_id,
        last_move="Start",
        fen=start_fen
    )
    db.add(new_game)
    db.commit()
    db.refresh(new_game)
    return new_game

def join_game(db: Session, game: CurrentGames,user_id: int):


    # Update the player IDs as needed
    if game.black_player_id == DEFAULT_INT:
        game.black_player_id = user_id
    elif game.white_player_id == DEFAULT_INT:
        game.white_player_id = user_id
    else:
        raise Exception("Neither players was None")

    game.turn = game.white_player_id

    
    db.commit()
    db.refresh(game)
    return game


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# decode tokens from webhooks
def decode_access_token(token: str):
    decoded_token = jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
    return decoded_token

def start_game(user_id: int, db: Session = Depends(get_db)):
    white_player_id = DEFAULT_INT
    black_player_id = DEFAULT_INT
    color = random.choice([0, 1])
    if color == 0:

        white_player_id = user_id
    else:

        black_player_id = user_id
    match = create_game(db=db,white_player_id=white_player_id,black_player_id=black_player_id)

    return match


temp = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMSIsImV4cCI6MTcwMjkzMDc4NX0.umoVsBCaK78AlMrYnj9MB4feSRn8wpajUWkKtf-UUfw"
#create game for users
def matchfinder(token: str, db: Session = Depends(get_db)):
    token = decode_access_token(token=token)
    username = token["sub"]
    user_id = get_user(db = db,username=username).id

    #Is my id already in a game with or without an opponent
    current_game = get_current_games(db=db,user_id=user_id)

    turn = WAITING_TURN
    
    #If not, make a game
    if current_game is None:

        #is there a game I can join
        match = find_empty_games(db=db,user_id=user_id)

        #If none host a game
        if match is None:
            match = start_game(db=db,user_id=user_id)
            
        else:
            #if one is found, join it
            match = join_game(db=db,game=match,user_id=user_id)
    else:

        match = current_game
        
    if match.turn == WAITING_TURN:
        turn = WAITING_TURN
    elif match.turn == user_id:
        turn = username
    else:
        turn = get_user_by_id(db=db,user_id=match.turn).username



    return match.fen,turn

