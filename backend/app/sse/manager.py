import asyncio
import json
from typing import Dict, List, Optional
from app.enums.role import UserRole

class ConnectionManager:
    def __init__(self):
        # Maps user_id -> Queue
        self.active_connections: Dict[int, asyncio.Queue] = {}
        # Maps user_id -> role
        self.user_roles: Dict[int, UserRole] = {}

    async def connect(self, user_id: int, role: UserRole) -> asyncio.Queue:
        queue = asyncio.Queue()
        self.active_connections[user_id] = queue
        self.user_roles[user_id] = role
        return queue

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_roles:
            del self.user_roles[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].put(message)

    async def broadcast_to_roles(self, message: dict, roles: List[UserRole]):
        """
        Send a message to all connected users who have one of the specified roles.
        """
        for user_id, queue in self.active_connections.items():
            user_role = self.user_roles.get(user_id)
            if user_role in roles:
                await queue.put(message)

manager = ConnectionManager()
