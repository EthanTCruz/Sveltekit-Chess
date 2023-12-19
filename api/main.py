from fastapi import FastAPI, Depends, HTTPException, status, WebSocket
from fastapi.security import  OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from api.dependencies import *
from api.models import UserDB





# FastAPI instance
app = FastAPI()

# OAuth2


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
async def websocket_endpoint(websocket: WebSocket,db: Session = Depends(get_db)):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        # Process the data received via WebSocket
        match,turn = matchfinder(token=data,db=db)
        
        await websocket.send_text(f"match: {match}, turn: {turn}, data: {data}")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
