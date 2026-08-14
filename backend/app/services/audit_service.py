"""
Servicio de Auditoría
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from datetime import datetime

logger = structlog.get_logger(__name__)


class AuditService:
    """
    Servicio para registro y consulta de auditoría.
    """
    
    async def log_action(
        self,
        agente: str,
        modelo: str,
        accion: str,
        detalle: Dict[str, Any],
        resultado: str,
    ) -> Dict[str, Any]:
        """
        Registra una acción en el log de auditoría
        """
        logger.info(f"📝 Audit: {agente} - {accion} - {resultado}")
        
        return {
            "id": "1",
            "timestamp": datetime.utcnow().isoformat(),
            "agente": agente,
            "modelo": modelo,
            "accion": accion,
            "resultado": resultado,
        }
    
    async def get_audit_logs(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        tipo_accion: Optional[str] = None,
        usuario_id: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Obtiene el log de auditoría paginado
        """
        logs = [
            {
                "id": "1",
                "usuario_id": "agent_billing",
                "usuario_nombre": "Billing Agent (IA)",
                "tipo_accion": "ejecutar_facturacion",
                "descripcion": "Emisión automática de ciclo de facturación B2B",
                "entidad_tipo": "Factura",
                "entidad_id": "S8AA-0008076684",
                "fecha_accion": datetime.utcnow().isoformat(),
                "ip_origen": "127.0.0.1",
                "resultado": "exitoso",
                "cambios_anteriores": {},
                "cambios_nuevos": {"estado": "Emitida", "total": 101.15},
            },
            {
                "id": "2",
                "usuario_id": "agent_collections",
                "usuario_nombre": "Collections Agent (IA)",
                "tipo_accion": "calcular_tamn",
                "descripcion": "Cálculo de intereses moratorios TAMN",
                "entidad_tipo": "Factura",
                "entidad_id": "S9AA-0036317590",
                "fecha_accion": datetime.utcnow().isoformat(),
                "ip_origen": "127.0.0.1",
                "resultado": "exitoso",
                "cambios_anteriores": {},
                "cambios_nuevos": {"tamn": 1.92, "dias_mora": 1180},
            },
            {
                "id": "3",
                "usuario_id": "agent_negotiation",
                "usuario_nombre": "Negotiation Agent (IA)",
                "tipo_accion": "generar_oferta",
                "descripcion": "Generación de oferta predictiva con 15% de descuento",
                "entidad_tipo": "Oferta",
                "entidad_id": "OF-2026-001",
                "fecha_accion": datetime.utcnow().isoformat(),
                "ip_origen": "127.0.0.1",
                "resultado": "exitoso",
                "cambios_anteriores": {},
                "cambios_nuevos": {"descuento": 15, "nuevo_plazo_dias": 30},
            },
            {
                "id": "4",
                "usuario_id": "agent_supervisor",
                "usuario_nombre": "Supervisor Agent (IA)",
                "tipo_accion": "analisis_metricas",
                "descripcion": "Revisión integral de salud del enjambre de agentes",
                "entidad_tipo": "Sistema",
                "entidad_id": "SYS-001",
                "fecha_accion": datetime.utcnow().isoformat(),
                "ip_origen": "127.0.0.1",
                "resultado": "exitoso",
                "cambios_anteriores": {},
                "cambios_nuevos": {"estado": "Operacional"},
            },
            {
                "id": "5",
                "usuario_id": "agent_openwa",
                "usuario_nombre": "WhatsApp Gateway (OpenWA)",
                "tipo_accion": "notificacion_pago",
                "descripcion": "Envío de recordatorio preventivo vía WhatsApp",
                "entidad_tipo": "Notificacion",
                "entidad_id": "WA-88219",
                "fecha_accion": datetime.utcnow().isoformat(),
                "ip_origen": "127.0.0.1",
                "resultado": "exitoso",
                "cambios_anteriores": {},
                "cambios_nuevos": {"destinatario": "2028857166", "canal": "WhatsApp"},
            }
        ]
        
        if tipo_accion:
            logs = [log for log in logs if tipo_accion.lower() in log["tipo_accion"].lower()]
        
        total = len(logs)
        paged = logs[skip : skip + limit]
        
        return {
            "items": paged,
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    
    async def get_audit_detail(
        self,
        db: AsyncSession,
        action_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Obtiene detalle de una acción de auditoría"""
        res = await self.get_audit_logs(db, skip=0, limit=100)
        for item in res["items"]:
            if str(item["id"]) == str(action_id):
                return item
        return None
