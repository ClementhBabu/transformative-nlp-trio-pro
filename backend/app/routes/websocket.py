import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.websocket_service import handle_websocket

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/process")
async def websocket_process(websocket: WebSocket):
    await handle_websocket(websocket)
