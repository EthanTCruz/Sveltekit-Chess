from fastapi import FastAPI, Depends, HTTPException, WebSocketDisconnect, status, WebSocket
from fastapi.security import  OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from api.src.dependencies import *
from api.src.models import UserDB, UserCreate
from api.src.websocket_class import ConnectionManager 
import json
import chess

ai_id = -1
ai_api = 'http://127.0.0.1:8001/aimove'
match_key = "match"
team = "team"
turn_color = "turn"

access_token_exp = 30
refresh_token_exp = 1000

# FastAPI instance
app = FastAPI()

# OAuth2

manager = ConnectionManager()

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # In your /token endpoint
    access_token = create_access_token(data={"sub": user.username},expire=access_token_exp)
    refresh_token = create_access_token(data={"sub": user.username},expire=refresh_token_exp)


    return {"access_token": access_token, "token_type": "bearer","refresh_token":refresh_token}


@app.get("/users/me")
async def read_users_me(current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    return current_user

@app.post("/register")
async def register_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Check if the user already exists
    db_user = db.query(UserDB).filter(UserDB.username == form_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Create new user instance
    hashed_password = hash_password(form_data.password)
    new_user = UserDB(username=form_data.username, hashed_password=hashed_password)

    # Add new user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    user = authenticate_user(db, form_data.username,  form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # In your /token endpoint
    access_token = create_access_token(data={"sub": user.username},expire=access_token_exp)
    refresh_token = create_access_token(data={"sub": user.username},expire=refresh_token_exp)



    return {"access_token": access_token, "token_type": "bearer","refresh_token":refresh_token}



@app.websocket("/ws/game")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    user_id = 0
    try:
        # Accepting the WebSocket connection
        await manager.connect(websocket=websocket)

        data, user_id = await receive_data(websocket=websocket,db=db)
        manager.storeConnection(user_id, websocket)
        message_dict, match = initialize_connection(user_id=user_id,db=db)

        if match.black_player_id != 0:
            message_dict[team] = 'b'
            message = json.dumps(message_dict)
            await manager.send_personal_message(message=message,user_id=match.black_player_id)
        if match.white_player_id != 0:
            message_dict[team] = 'w'
            message = json.dumps(message_dict)
            await manager.send_personal_message(message=message,user_id=match.white_player_id)


        while True:
            data, user_id = await receive_data(websocket=websocket,db=db)
            message_dict = {}
            #matchfinder handles finding open games or finding current game
            match = matchfinder(user_id=user_id, db=db)
            #initial values for searching for match
            message_dict[match_key] = f"{match.fen}"
            message_dict[turn_color] = 'Waiting'
            message_dict[team] = '0'
            message_dict["winner"] = 'n'

            # if game has two players already
            if match.turn != 0:
                message_dict, match = has_match_logic(message_dict=message_dict,data=data,match=match,user_id=user_id,db=db)
                await game_over_or_continue_logic(message_dict=message_dict,match=match,manager=manager)

            else:
                #if no match is active, idle and just send start board
                message = json.dumps(message_dict)
                await manager.send_personal_message(message=message,user_id=user_id)

    except WebSocketDisconnect:
        # Handling WebSocket disconnections
        manager.disconnect(user_id)


@app.websocket("/ai/game")
async def play_computer(websocket: WebSocket, db: Session = Depends(get_db)):
    user_id = 0
    try:
        # Accepting the WebSocket connection
        await manager.connect(websocket=websocket)

        data, user_id = await receive_data(websocket=websocket,db=db)
        manager.storeConnection(user_id, websocket)
        message_dict, match = initialize_connection_ai(user_id=user_id,db=db)


        if match.black_player_id == user_id:
            message_dict[team] = 'b'
            message = json.dumps(message_dict)
            await manager.send_personal_message(message=message,user_id=match.black_player_id)
        elif match.white_player_id == user_id:
            message_dict[team] = 'w'
            message = json.dumps(message_dict)
            await manager.send_personal_message(message=message,user_id=match.white_player_id)


        if match.turn == ai_id:
            data = {"fen":match.fen}
            headers = {
                'accept': 'application/json'
                }
            data = requests.post(ai_api,headers=headers,params=data)
            data_json = json.loads(data.text)
            move = data_json["move"]
            print(move)
            match, winner = process_move(move=move,match=match,db=db)
            await ai_match_logic(message_dict=message_dict,match=match,manager=manager)
        while True:

            data, user_id = await receive_data(websocket=websocket,db=db)
            message_dict = {}
            #matchfinder handles finding open games or finding current game
            match = matchfinder(user_id=user_id, db=db)
            #initial values for searching for match
            message_dict[match_key] = f"{match.fen}"
            message_dict[turn_color] = get_turn_color_from_match(match=match)
            message_dict[team] = determine_player_color(match=match,player_id=user_id)
            message_dict["winner"] = 'n'

            # if game has two players already

            message_dict, match = has_match_logic(message_dict=message_dict,data=data,match=match,user_id=user_id,db=db,ai=True)
            await ai_match_logic(message_dict=message_dict,match=match,manager=manager)
            if match.turn == ai_id:
                data = {"fen":match.fen}
                headers = {
                    'accept': 'application/json'
                    }
                data = requests.post(ai_api,headers=headers,params=data)
                data_json = json.loads(data.text)
                move = data_json["move"]
                print(move)
                match, winner = process_move(move=move,match=match,db=db)

                await ai_match_logic(message_dict=message_dict,match=match,manager=manager)
            


    except WebSocketDisconnect:
        # Handling WebSocket disconnections
        manager.disconnect(user_id)




# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
