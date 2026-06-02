import logging
import json
import asyncio
from typing import Optional

from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from app.services.speech_service import speech_to_text
from app.services.summarize_service import summarize_text
from app.services.translate_service import translate_text
from app.services.tts_service import generate_speech

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Active: {len(self.active_connections)}")

    async def send_message(self, websocket: WebSocket, message: dict):
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_text(json.dumps(message))

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            if connection.client_state == WebSocketState.CONNECTED:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    self.disconnect(connection)


manager = WebSocketManager()


async def handle_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    collected_text = ""

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            action = message.get("action", "")

            if action == "ping":
                await manager.send_message(websocket, {"type": "pong"})
                continue

            if action == "disconnect":
                await manager.send_message(websocket, {"type": "disconnected"})
                break

            # Process audio chunk or text
            audio_data = message.get("audio_data", "")
            text_chunk = message.get("text", "")
            target_lang = message.get("target_lang", "en")
            summary_mode = message.get("mode", "medium")

            if text_chunk:
                collected_text += " " + text_chunk
            elif audio_data:
                # In production, this would process audio chunks
                collected_text += " " + audio_data

            collected_text = collected_text.strip()

            await manager.send_message(websocket, {
                "type": "text",
                "text": collected_text,
            })

            # Generate summary if enough text
            if len(collected_text.split()) > 10:
                try:
                    summary_result = summarize_text(collected_text, mode=summary_mode)
                    await manager.send_message(websocket, {
                        "type": "summary",
                        "summary": summary_result["summary"],
                    })
                except Exception as e:
                    logger.error(f"WS summary error: {e}")
                    await manager.send_message(websocket, {
                        "type": "error",
                        "error": "Summarization failed",
                    })

            # Generate translation if enough text
            if len(collected_text.split()) > 5 and target_lang != "en":
                try:
                    translation_result = translate_text(
                        collected_text, target_lang=target_lang
                    )
                    await manager.send_message(websocket, {
                        "type": "translation",
                        "translated_text": translation_result["translated_text"],
                        "target_lang": target_lang,
                    })
                except Exception as e:
                    logger.error(f"WS translation error: {e}")
                    await manager.send_message(websocket, {
                        "type": "error",
                        "error": "Translation failed",
                    })

            # Generate TTS audio URL
            if len(collected_text.split()) > 10:
                try:
                    tts_result = generate_speech(collected_text, language=target_lang)
                    await manager.send_message(websocket, {
                        "type": "audio",
                        "audio_url": tts_result["audio_url"],
                    })
                except Exception as e:
                    logger.error(f"WS TTS error: {e}")

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except json.JSONDecodeError:
        await manager.send_message(websocket, {
            "type": "error",
            "error": "Invalid JSON message",
        })
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await manager.send_message(websocket, {
                "type": "error",
                "error": str(e),
            })
        except Exception:
            pass
    finally:
        manager.disconnect(websocket)
