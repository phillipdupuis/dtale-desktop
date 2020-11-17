from typing import List, Optional, Tuple

from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    """
    An object which keeps track of active websocket connections and exposes methods for sending
    messages via those connections. Useful for broadcasting state changes to users other than the
    one who initiated the change.

    In a multi-worker environment this will need to use some kind of persistent store like redis
    for tracking active connections (instead of just using a list in memory).
    """

    _instance = None

    def __init__(self):
        if ConnectionManager._instance is not None:
            raise Exception("ConnectionManager is a singleton, stop it")
        ConnectionManager._instance = self
        self.active_connections: List[Tuple[WebSocket, int]] = []

    async def connect(self, websocket: WebSocket, client_id: int) -> None:
        await websocket.accept()
        self.active_connections.append((websocket, client_id))

    def disconnect(self, websocket: WebSocket, client_id: int) -> None:
        self.active_connections.remove((websocket, client_id))

    async def send_message(self, message: str, client_id: int) -> None:
        websocket = next(
            (w for w, c in self.active_connections if c == client_id), None
        )
        if websocket is not None:
            await websocket.send_text(message)

    async def broadcast(
        self, message: str, exclude: Optional[List[int]] = None
    ) -> None:
        for websocket, client_id in self.active_connections:
            if exclude is None or client_id not in exclude:
                await websocket.send_text(message)


websocket_connection_manager = ConnectionManager()

websocket_path = "/ws/{client_id}/"


async def websocket_endpoint(websocket: WebSocket, client_id: int):
    """
    Endpoint that browsers can connect to in order to have state changes pushed to them in real time.
    The client_id is a unique identifier supplied by the client.
    TODO: figure out how to plug in authentication before accepting websocket connections.
    """
    await websocket_connection_manager.connect(websocket, client_id)
    try:
        while True:
            # Not sure what if anything will be done for receiving messages?..
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_connection_manager.disconnect(websocket, client_id)
