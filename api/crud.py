
from pyexpat import model
from sqlalchemy.orm import Session
from sqlalchemy import or_
import chess
import random
from . import models, schemas


def get_user(db: Session, id: int):
    return db.query(models.User).filter(models.User.id == id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def validate_credentials(db: Session, username: str, password: str):
    return db.query(models.User).filter(models.User.username == username,models.User.password==password).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = user.password
    #fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(id=user.id,username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_game(db: Session, game: schemas.GameCreate):
    positions = ""
    db_game = models.Current_games()
    pass

def get_current_games(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Current_games).offset(skip).limit(limit).all()


def create_user_game(db: Session, game_data: schemas.GameBase):
    game = schemas.GameCreate(black_player_id = game_data.black_player_id,white_player_id = game_data.white_player_id)
    game.pieces_and_positions='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    game.turn = 'w'
    game.move_no = 0
    db_game = models.Current_games(**game.dict())
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game

def join_a_game(db: Session, user: schemas.UserBase):
    game_id = find_player_games(db=db,user=user)
    if game_id is not None:
        return game_id
    game_id = find_empty_games(db=db)
    if game_id is None:
        game = schemas.GameBase(black_player_id=user.id,white_player_id=user.id)
        create_user_game(db=db,game_data=game)
        game_id = find_empty_games(db=db)
    else:
        print(game_id)
        game_id = player_join_game(db=db,game=game_id,user=user)
    return game_id

def find_empty_games(db: Session):
    return db.query(models.Current_games).filter(models.Current_games.white_player_id == models.Current_games.black_player_id).first()

def find_player_games(db: Session,user: schemas.UserBase):
    return db.query(models.Current_games).filter(or_(models.Current_games.white_player_id == user.id, 
    models.Current_games.black_player_id == user.id)).first()

def player_join_game(db: Session,game: schemas.GameBase, user: schemas.UserBase):
    team = random.randint(0, 1)
    if team == 0:
        setattr(game, 'white_player_id', user.id)
    else:
        setattr(game, 'black_player_id', user.id)
    db.add(game)
    db.commit()
    db.refresh(game)
    return game

def get_game_board(game: schemas.GetGameBoard, db: Session):
    return db.query(models.Current_games).filter(or_(models.Current_games.white_player_id == game.id, 
    models.Current_games.black_player_id == game.id),(models.Current_games.game_id == game.game_id)).first()

def move(db: Session, game: schemas.GetGameBoard, move: str):
    game = get_game_board(db=db,game=game)
    db_game = models.Past_games()
    fen = game.pieces_and_positions
    board = chess.Board(fen)
    print(board.push_san(move))
    print("=============")
    fen=board.fen()
    print(fen)
    board.pieces_and_positions = fen
    setattr(game,'pieces_and_positions',fen)
    if board.turn:
        setattr(game,'turn','W')
    else:
        setattr(game,'turn','B')
    if board.is_checkmate():
        setattr(db_game,'game_status',game.turn)
    elif board.is_stalemate():
        setattr(db_game,'game_status','D')
    else: 
        setattr(db_game,'game_status','C')
    if board.turn and game.turn == 'B':
        setattr(game,'move_no',fen.split(" ")[-1])
    db.add(game)
    db.commit()
    db.refresh(game)

   
    db_game.game_id = game.game_id
    db_game.white_player_id = game.white_player_id
    db_game.black_player_id = game.black_player_id
    db_game.pieces_and_positions = game.pieces_and_positions
    db_game.move_no = fen.split(" ")[-1]
    db_game.move = move

    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    
    return game


def getPastGamesPGNs(id,db: Session,skip,limit):
    return db.query(models.Past_games).filter(or_(models.Past_games.white_player_id == id,
    models.Past_games.black_player_id == id)).offset(skip).limit(limit).all()