"""
engine/websocket_adapter.py
WebSocket adapter stub — integrates websockets transport with CommandRouter.
"""
import asyncio
from typing import Any

async def ws_handler(websocket, path, router=None):
    """Placeholder ws handler. Will accept JSON messages and call router.execute()."""
    try:
        async for msg in websocket:
            # echo until router implemented
            await websocket.send('{"status":"error","message":"ws handler not implemented"}')
    except Exception:
        pass
