from fastapi import FastAPI, Depends, HTTPException, WebSocketDisconnect, status, WebSocket
from fastapi.security import  OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from api.src.dependencies import *
from api.src.models import UserDB
from api.src.websocket_class import ConnectionManager 
import json
import chess




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
    access_token = create_access_token(data={"sub": user.username})


    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    return current_user



@app.websocket("/ws/game")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    try:
        # Accepting the WebSocket connection
        await manager.connect(websocket=websocket)

        # The first message could be used to pass the user's token
        data = await websocket.receive_text()
        data = json.loads(data)
        token = decode_access_token(token=data["token"])
        username = token["sub"]
        user = get_user(db=db, username=username)


        
        if user is None:
            # Handle the case where the user is not found
            await websocket.close(code=1000)  # 1000 is a normal closure
            return

        user_id = user.id  # Converting user_id to string if it's not already

        # Registering the connection with the manager
        manager.storeConnection(user_id, websocket)

        match, turn = matchfinder(username=username, user_id=user_id, db=db)

        # Send response back to client
        await websocket.send_text(f"{match.fen},{turn},{data}")

        while True:
            #two cases to handle: looking for game or receiving a move

            #on recieved data prop
            data = await websocket.receive_text()
            data = json.loads(data)
            token = decode_access_token(token=data["token"])
            username = token["sub"]
            user_id = get_user(db=db, username=username).id


            #matchfinder handles finding open games or finding current game
            match, turn = matchfinder(username=username, user_id=user_id, db=db)
            message = f"{match.fen},{turn}"
            # if game has two players already
            if match.turn != 0:

                #to tell player what color they are as locally they will not know
                if match.turn == match.white_player_id:
                    color_turn,turn_id = 'b',match.black_player_id

                else:
                    color_turn,turn_id = 'w',match.white_player_id
                
                # if they sent a move and it's their turn update and return new board
                if data.get('move') != None and match.turn == user_id:



                    move = data['move']
                    board = chess.Board(fen=match.fen)
                    #add error handling here for invalid moves

                    board.push_uci(move)
                    fen = board.fen()
                    match = update_game(db=db,game=match,fen=fen,move=move)
                    #if move is good, message will have new board and players turn
                    message = f"{match.fen},{turn}"

                #if board is active, give player their color
                message = message + f",{color_turn}"

                #when it is players turn, send them board
                await manager.send_personal_message(message=f"{match.fen}",user_id=match.turn)

            else:
                #if no match is active, idle and just send start board
                message = f"{match.fen},{turn}"
                await manager.send_personal_message(message=message,user_id=user_id)

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
