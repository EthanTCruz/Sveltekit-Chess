from pydantic import BaseModel


class GameBase(BaseModel):
    white_player_id: int
    black_player_id: int
    class Config:
        orm_mode = True

class GameJoin(GameBase):
    game_id: int
    player_color: str
    pieces_and_positions: str
    waiting_for_other_player: bool
    class Config:
        orm_mode = True

class PastGamePGN(BaseModel):
    game_id: int
    move: str
    class Config:
        orm_mode = True

class GetGameBoard(BaseModel):
    id: int
    game_id: int
    class Config:
        orm_mode = True

class GameBoard(BaseModel):
    pieces_and_positions: str
    class Config:
        orm_mode = True

class GameCreate(GameBase):
    turn : str = 'w'
    pieces_and_positions: str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    move_no: int = 0
    class Config:
        orm_mode = True

class Current_Game(GameBase):
    game_id: int
    white_player_id: int
    black_player_id: int
    pieces_and_positions: str
    move_no: int
    class Config:
        orm_mode = True

class Past_Game(GameBase):
    game_id: int
    white_player_id: int
    black_player_id: int
    game_status: str
    pieces_and_positions: str
    move_no: int
    class Config:
        orm_mode = True

class UserBase(BaseModel):
    id: int
    username: str
    class Config:
        orm_mode = True

class UserCheck(UserBase):
    username: str 
    password: str
    ok: bool = False 
    
    class Config:
        orm_mode=True



class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    username: str
    password: str
    #past_games: List[Past_Game] = []
    #current_games: List[Current_Game] = []

    class Config:
        orm_mode = True
