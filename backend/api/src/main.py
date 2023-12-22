from fastapi import FastAPI, Depends, HTTPException, WebSocketDisconnect, status, WebSocket
from fastapi.security import  OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from api.src.dependencies import *
from api.src.models import UserDB
from api.src.websocket_class import ConnectionManager 
import json
import chess

match_key = "match"
team = "team"
turn_color = "turn"



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

        data, user_id = await receive_data(websocket=websocket,db=db)
        manager.storeConnection(user_id, websocket)
        message = initialize_connection(user_id=user_id,db=db)

        await websocket.send_text(message)

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
                message, match = has_match_logic(message_dict=message_dict,data=data,match=match,user_id=user_id,db=db)
                await manager.send_personal_message(message=message,user_id=match.turn)
                




            else:
                #if no match is active, idle and just send start board
                message = json.dumps(message_dict)
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
