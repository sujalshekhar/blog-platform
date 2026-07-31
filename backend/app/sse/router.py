import asyncio
import json
from fastapi import APIRouter, Request, Query, HTTPException, status
# pyrefly: ignore [missing-import]
from sse_starlette.sse import EventSourceResponse

from app.core.security import decode_access_token
from app.enums.role import UserRole
from app.sse.manager import manager

router = APIRouter(
    prefix="/sse",
    tags=["Server Sent Events"],
)

async def event_generator(request: Request, user_id: int, role: UserRole):
    """
    Yields events from the user's personal queue.
    """
    queue = await manager.connect(user_id, role)
    try:
        while True:
            # If the client disconnects, stop sending events
            if await request.is_disconnected():
                break
                
            # Wait for a new message in the queue with a timeout to check disconnection
            try:
                message = await asyncio.wait_for(queue.get(), timeout=1.0)
                yield {
                    "event": "notification",
                    "data": json.dumps(message)
                }
            except asyncio.TimeoutError:
                # Timeout is expected, it lets us loop back and check is_disconnected()
                pass
    finally:
        manager.disconnect(user_id)

@router.get("/stream")
async def sse_stream(request: Request, token: str = Query(...)):
    """
    Endpoint for clients to subscribe to Server Sent Events.
    Requires token as query param since EventSource doesn't support custom headers.
    """
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
        role_str = payload.get("role")
        role = UserRole(role_str) if role_str else UserRole.USER
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
        
    return EventSourceResponse(event_generator(request, user_id, role))

