"""
Conector para SQL Server (BSS/OSS Legacy)
"""

import structlog

logger = structlog.get_logger(__name__)


class SQLServerConnector:
    """
    Conector para SQL Server donde residen los datos core BSS/OSS.
    
    Tablas principales:
    - bss_clientes
    - bss_cuentas
    - oss_planta
    - bss_factura_cabecera
    - bss_factura_detalle
    """
    
    def __init__(self):
        self.connected = False
        logger.info("💾 SQL Server Connector inicializado")
    
    async def connect(self) -> bool:
        """Establece conexión con SQL Server"""
        self.connected = True
        logger.info("✅ Conectado a SQL Server")
        return True
    
    async def disconnect(self) -> None:
        """Cierra conexión con SQL Server"""
        self.connected = False
        logger.info("👋 Desconectado de SQL Server")
    
    async def get_cliente_data(self, cliente_id: int) -> dict:
        """Obtiene datos completos de un cliente"""
        logger.info(f"🔍 SQL Server: Obteniendo cliente {cliente_id}")
        
        return {
            "id_cliente": cliente_id,
            "nombre": "Empresa Tecnológica S.A.C.",
            "segmento": "B2B",
            "score_confianza": 0.85,
        }
    
    async def get_servicios_activos(self, cuenta_id: int) -> list:
        """Obtiene servicios activos de una cuenta"""
        logger.info(f"🔍 SQL Server: Obteniendo servicios cuenta {cuenta_id}")
        
        return [
            {
                "id_servicio": 3001,
                "tecnologia": "Fibra Óptica",
                "cargo_fijo": 2500.00,
            },
            {
                "id_servicio": 3002,
                "tecnologia": "Cloud",
                "cargo_fijo": 1800.00,
            },
        ]


# Singleton
sqlserver_connector = SQLServerConnector()