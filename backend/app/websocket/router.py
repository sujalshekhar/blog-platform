from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.websocket.manager import ws_manager
from app.core import security
from app.core.config import settings
from app.core.logger import logger

router = APIRouter(
    prefix="/ws",
    tags=["Websocket"],
)

@router.websocket("")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    # Authenticate via token
    try:
        payload = security.decode_access_token(token)
        user_id = int(payload.get("sub"))
    except Exception as e:
        logger.warning(f"WebSocket auth failed: {e}")
        await websocket.close(code=1008)
        return
    # adding user to active_connections
    await ws_manager.connect(websocket, user_id)
    
    try:
        while True:
            # We expect JSON payloads from the frontend
            data = await websocket.receive_json()
            
            msg_type = data.get("type")
            blog_group_id = data.get("blog_group_id")
            room_id = f"blog_{blog_group_id}"
            
            logger.debug(f"Received WS message from user {user_id}: type={msg_type}, room={room_id}")

            if msg_type == "subscribe":
                ws_manager.subscribe_to_room(websocket, room_id)
            elif msg_type == "unsubscribe":
                ws_manager.unsubscribe_from_room(websocket, room_id)
            elif msg_type == "message":
                content = data.get("content")
                if content and blog_group_id:
                    # Save to DB via a fresh session
                    from app.core.database import SessionLocal
                    from app.services.chat_service import ChatService
                    
                    db = SessionLocal()
                    try:
                        chat_service = ChatService(db)
                        new_msg = chat_service.save_message(int(blog_group_id), user_id, content)
                        
                        # Broadcast to everyone in the room
                        await ws_manager.broadcast_to_room(room_id, {
                            "type": "new_message",
                            "message": new_msg.model_dump(mode='json')
                        })
                    except Exception as e:
                        logger.error(f"Error saving chat message for room {room_id}: {e}", exc_info=True)
                    finally:
                        db.close()
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected normally for user {user_id}")
        ws_manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"Unexpected WebSocket error for user {user_id}: {e}", exc_info=True)
        ws_manager.disconnect(websocket, user_id)
