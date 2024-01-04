from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.connections = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()


    def storeConnection(self, user_id: str, websocket: WebSocket):
        self.connections[str(user_id)] = websocket

    def disconnect(self, user_id: str):
        user_id = str(user_id)
        if user_id in self.connections:
            del self.connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        user_id = str(user_id)
        if user_id in self.connections:
            await self.connections[user_id].send_text(message)


