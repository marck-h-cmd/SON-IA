"""
WebSocket para notificaciones en tiempo real
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import structlog
import json

logger = structlog.get_logger(__name__)

router = APIRouter()


class ConnectionManager:
    """
    Maneja conexiones WebSocket para notificaciones en tiempo real.
    
    Canales:
    - dashboard: Actualizaciones para dashboard interno
    - cliente_{id}: Notificaciones para cliente específico
    """
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "dashboard": set(),
        }
    
    async def connect(self, websocket: WebSocket, channel: str = "dashboard"):
        """Acepta y registra una conexión WebSocket"""
        await websocket.accept()
        
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        
        self.active_connections[channel].add(websocket)
        logger.info(f"🔌 WebSocket conectado al canal '{channel}'")
    
    def disconnect(self, websocket: WebSocket, channel: str = "dashboard"):
        """Elimina una conexión WebSocket"""
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
        logger.info(f"🔌 WebSocket desconectado del canal '{channel}'")
    
    async def broadcast(self, message: dict, channel: str = "dashboard"):
        """
        Envía mensaje a todos los clientes en un canal.
        
        Args:
            message: Mensaje a enviar
            channel: Canal de broadcast
        """
        if channel not in self.active_connections:
            return
        
        disconnected = set()
        
        for connection in self.active_connections[channel]:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                disconnected.add(connection)
        
        # Limpiar conexiones muertas
        for conn in disconnected:
            self.active_connections[channel].discard(conn)
    
    async def send_to_client(self, cliente_id: int, message: dict):
        """
        Envía mensaje a un cliente específico.
        
        Args:
            cliente_id: ID del cliente
            message: Mensaje a enviar
        """
        channel = f"cliente_{cliente_id}"
        await self.broadcast(message, channel)


# Singleton
manager = ConnectionManager()


@router.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """
    WebSocket para actualizaciones del dashboard en tiempo real.
    """
    await manager.connect(websocket, "dashboard")
    
    try:
        # Enviar mensaje de bienvenida
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "message": "Conectado al dashboard de SON-IA",
        }))
        
        # Mantener conexión abierta
        while True:
            data = await websocket.receive_text()
            # Procesar mensajes entrantes si es necesario
            await websocket.send_text(json.dumps({
                "type": "echo",
                "data": data,
            }))
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, "dashboard")
    except Exception as e:
        logger.error(f"Error en WebSocket dashboard: {e}")
        manager.disconnect(websocket, "dashboard")


@router.websocket("/ws/cliente/{cliente_id}")
async def websocket_cliente(websocket: WebSocket, cliente_id: int):
    """
    WebSocket para notificaciones personalizadas del cliente.
    """
    channel = f"cliente_{cliente_id}"
    await manager.connect(websocket, channel)
    
    try:
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "message": f"Conectado al portal de autogestión - Cliente {cliente_id}",
        }))
        
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(json.dumps({
                "type": "echo",
                "data": data,
            }))
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)