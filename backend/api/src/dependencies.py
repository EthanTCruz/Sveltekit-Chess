from api.src.database import SessionLocal
from api.src.models import UserDB,CurrentGames, PastGames
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status, WebSocket
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime,timedelta
from sqlalchemy import or_, and_
import random
import json
import chess
import hashlib

match_key = "match"
team = "team"
turn_color = "turn"
start_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

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
        CurrentGames.black_player_id == user_id)
        ).order_by(CurrentGames.id.desc()).first()
    return results

def find_empty_games(db: Session, user_id: int):
    results = db.query(CurrentGames).filter(CurrentGames.turn == WAITING_TURN).first()
    return results

def create_game(db: Session, white_player_id: int = DEFAULT_INT, black_player_id: int = DEFAULT_INT):
    
    if white_player_id is DEFAULT_INT and black_player_id is DEFAULT_INT:
        raise Exception("created game without host")
    
    new_game = CurrentGames(
        move_no = 0,
        turn=WAITING_TURN,
        game_id = "Waiting",
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

    data = {"white": game.white_player_id,"black":game.black_player_id}
    game.game_id = create_game_id(data=data)
    game.turn = game.white_player_id

    
    db.commit()
    db.refresh(game)
    return game

def update_game(db: Session, game: CurrentGames,fen: str,move: str):

    if game.turn == game.black_player_id:
        turn = game.white_player_id
    else:
        turn = game.black_player_id

    new_game = CurrentGames(
        move_no = game.move_no + 1,
        game_id = game.game_id,
        turn=turn,
        white_player_id=game.white_player_id,
        black_player_id=game.black_player_id,
        last_move=move,
        fen=fen
    )
    db.add(new_game)
    db.commit()
    db.refresh(new_game)

    return new_game

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



def create_game_id(data: dict) -> str:
    to_encode = data.copy()
    current_time = str(datetime.utcnow())
    to_encode["time"] = current_time
    to_encode = json.dumps(to_encode)
    return hashlib.sha256(to_encode.encode()).hexdigest()



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

def matchfinder(user_id:str, db: Session = Depends(get_db)):

    #Is my id already in a game with or without an opponent
    current_game = get_current_games(db=db,user_id=user_id)

    
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
        

    return match

def user_id_from_ws(data: dict,db: Session = Depends(get_db)):
    token = decode_access_token(token=data["token"])
    username = token["sub"]
    user_id = get_user(db=db, username=username).id
    return user_id

def determine_player_color(match: CurrentGames,player_id: int):
        if player_id == match.white_player_id:
            results  = 'w'
        elif player_id == match.black_player_id:
            results = 'b'
        else:
            raise Exception("User was neither player colors")
        return results

def process_move(move:str,match: CurrentGames,db: Session = Depends(get_db)):
    board = chess.Board(fen=match.fen)
    board.push_uci(move)
    fen = board.fen()
    match = update_game(db=db,game=match,fen=fen,move=move)
    winner = 'n'
    if board.is_checkmate():
        if board.turn:
            winner = 'b'
            winner_id = match.black_player_id
        else:
            winner = 'w'
            winner_id = match.white_player_id
        
        for game in get_current_games_by_id(db=db,game_id=match.game_id):
            move_current_to_past(match=game,winner_id=winner_id,db=db)

    return match, winner

def get_current_games_by_id(db: Session,game_id: str):
    return db.query(CurrentGames).filter(CurrentGames.game_id == game_id).all()

def move_current_to_past(match: CurrentGames, winner_id: str,db: Session = Depends(get_db)):
    past_game = PastGames(
    game_id = match.game_id,
    move_no = match.move_no,
    winner = winner_id,
    white_player_id = match.white_player_id,
    black_player_id = match.black_player_id,
    last_move = match.last_move,
    fen = match.fen   
    )
    db.add(past_game)
    db.delete(match)
    db.commit()
    db.refresh(past_game)

    return past_game

def initialize_connection(user_id: int,db: Session = Depends(get_db)):
        match = matchfinder(user_id=user_id, db=db)
        message_dict = {}

        message_dict[match_key] = f"{match.fen}"
        message_dict[team] = determine_player_color(match=match,player_id=user_id)


        if match.turn == match.white_player_id:
            message_dict[turn_color] = 'w'
        elif match.turn == match.black_player_id:
            message_dict[turn_color] = 'b'

        message_dict["winner"] = 'n'

        message = json.dumps(message_dict)
        return message

def get_turn_color_from_match(match: CurrentGames):
    if match.turn == match.white_player_id:
        results = 'w'
    elif match.turn == match.black_player_id:
        results = 'b'
    return results

def has_match_logic(message_dict: dict,data: dict,match: CurrentGames,user_id: int, db: Session = Depends(get_db)):
    message_dict[team] = determine_player_color(match=match,player_id=user_id)
    winner = 'n'
    # if they sent a move and it's their turn update and return new board
    if data.get('move') != None and match.turn == user_id:
        move = data['move']
        match, winner = process_move(move=move,match=match,db=db)

        if user_id == match.white_player_id:
            message_dict[team] = 'b'
        elif user_id == match.black_player_id:
            message_dict[team] = 'w'


    message_dict[match_key] = f"{match.fen}"
    message_dict[turn_color] = get_turn_color_from_match(match=match)
    message_dict["winner"] = winner

    message = json.dumps(message_dict)
    return message, match

async def receive_data(websocket: WebSocket,db: Session = Depends(get_db)):
        data = await websocket.receive_text()
        data = json.loads(data)
        user_id = user_id_from_ws(data=data,db=db)
  
        if user_id is None:
            await websocket.close(code=1000)
            return
        
        return data, user_id