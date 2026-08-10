"""
Conector para Teradata (Legacy)
"""

import structlog

logger = structlog.get_logger(__name__)


class TeradataConnector:
    """
    Conector para sistemas Teradata legacy.
    
    Permite leer datos históricos de clientes y facturación
    almacenados en sistemas legacy.
    """
    
    def __init__(self):
        self.connected = False
        logger.info("📡 Teradata Connector inicializado")
    
    async def connect(self) -> bool:
        """Establece conexión con Teradata"""
        # Simulación
        self.connected = True
        logger.info("✅ Conectado a Teradata")
        return True
    
    async def disconnect(self) -> None:
        """Cierra conexión con Teradata"""
        self.connected = False
        logger.info("👋 Desconectado de Teradata")
    
    async def execute_query(self, query: str) -> list:
        """
        Ejecuta una consulta en Teradata.
        
        Args:
            query: Consulta SQL
            
        Returns:
            Lista de resultados
        """
        logger.info(f"🔍 Teradata: Ejecutando query")
        
        # Simulación de datos
        return [
            {"cliente_id": 1001, "factura_id": 4001, "monto": 4300.00},
            {"cliente_id": 1002, "factura_id": 4002, "monto": 5000.00},
        ]
    
    async def get_historical_data(
        self,
        cliente_id: int,
        years_back: int = 2,
    ) -> list:
        """
        Obtiene datos históricos de un cliente.
        """
        logger.info(f"📊 Teradata: Obteniendo histórico cliente {cliente_id}")
        
        return [
            {"año": 2022, "total_facturado": 45000.00},
            {"año": 2023, "total_facturado": 48000.00},
        ]


# Singleton
teradata_connector = TeradataConnector()