from typing import Dict, Set
from fastapi import WebSocket
from app.core.logger import logger

class WebSocketManager:
    """
    Manages active WebSocket connections for real-time features like Chat.

    Crucially, it supports multiple simultaneous connections per user (e.g., when a user 
    has multiple browser tabs open). This also natively resolves the React 18 Strict Mode 
    issue where components mount, unmount, and remount instantly, creating overlapping 
    websocket connections. By mapping a `user_id` to a `Set[WebSocket]` rather than a 
    single WebSocket, it prevents premature disconnection of the active socket.
    """
    def __init__(self):
        # Maps user_id -> set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Maps room_id -> set of WebSockets
        self.rooms: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"WebSocket connected for user {user_id}. Connections for user: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                logger.info(f"All WebSockets disconnected for user {user_id}.")
            else:
                logger.info(f"One WebSocket disconnected for user {user_id}. Remaining: {len(self.active_connections[user_id])}")
                
        # Remove websocket from any rooms they were in
        for room_id in self.rooms:
            if websocket in self.rooms[room_id]:
                self.rooms[room_id].remove(websocket)
                logger.debug(f"Removed websocket from room {room_id} on disconnect.")

    def subscribe_to_room(self, websocket: WebSocket, room_id: str):
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
        self.rooms[room_id].add(websocket)
        logger.info(f"WebSocket subscribed to room {room_id}.")

    def unsubscribe_from_room(self, websocket: WebSocket, room_id: str):
        if room_id in self.rooms and websocket in self.rooms[room_id]:
            self.rooms[room_id].remove(websocket)
            logger.info(f"WebSocket unsubscribed from room {room_id}.")



    async def broadcast_to_room(self, room_id: str, message: dict):
        if room_id in self.rooms:
            for connection in list(self.rooms[room_id]):
                try:
                    await connection.send_json(message)
                except Exception:
                    # Let disconnect handle cleanup if it fails
                    pass

ws_manager = WebSocketManager()

