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
    Servicio para registro y consulta de auditoría con soporte para filtros dinámicos.
    """
    def __init__(self):
        self._dynamic_logs: List[Dict[str, Any]] = []
        self._next_id = 100
    
    async def log_action(
        self,
        tipo_accion: Optional[str] = None,
        usuario_id: Optional[str] = None,
        detalles: Optional[Dict[str, Any]] = None,
        resultado: Optional[str] = "exitoso",
        entidad_tipo: Optional[str] = "Sistema",
        entidad_id: Optional[str] = "N/A",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Registra una acción en el log de auditoría
        """
        actor = usuario_id or kwargs.get("agente") or kwargs.get("usuario") or "supervisor_agente"
        act = tipo_accion or kwargs.get("accion") or "accion"
        res = resultado or "exitoso"
        self._next_id += 1
        
        entry = {
            "id": str(self._next_id),
            "usuario_id": actor,
            "usuario_nombre": "Supervisor Humano (HITL)" if "supervisor" in actor else "Agente IA (SON-IA)",
            "tipo_accion": act,
            "descripcion": str(detalles.get("descripcion", f"Acción {act} ejecutada en {entidad_tipo}")) if detalles else f"Acción {act}",
            "entidad_tipo": entidad_tipo or "Sistema",
            "entidad_id": str(detalles.get("factura_id") or entidad_id or f"ENT-{self._next_id}"),
            "fecha_accion": datetime.utcnow().isoformat(),
            "ip_origen": "127.0.0.1",
            "resultado": res,
            "cambios_anteriores": {},
            "cambios_nuevos": detalles or {},
        }
        self._dynamic_logs.insert(0, entry)
        logger.info(f"📝 Audit: {actor} - {act} - {res}")
        return entry
    
    async def get_audit_logs(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        tipo_accion: Optional[str] = None,
        usuario_id: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Obtiene el log de auditoría paginado y filtrado
        """
        base_logs = [
            {
                "id": "1",
                "usuario_id": "agent_billing",
                "usuario_nombre": "Billing Agent (IA)",
                "tipo_accion": "ejecutar_facturacion",
                "descripcion": "Emisión automática de ciclo de facturación B2B",
                "entidad_tipo": "Factura",
                "entidad_id": "S8AA-0008076684",
                "fecha_accion": "2026-08-15T18:30:00Z",
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
                "fecha_accion": "2026-08-15T17:15:00Z",
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
                "descripcion": "Generación de oferta predictiva con 10% de descuento",
                "entidad_tipo": "Oferta",
                "entidad_id": "OF-2026-001",
                "fecha_accion": "2026-08-15T16:00:00Z",
                "ip_origen": "127.0.0.1",
                "resultado": "exitoso",
                "cambios_anteriores": {},
                "cambios_nuevos": {"descuento": 10, "nuevo_plazo_dias": 30},
            },
            {
                "id": "4",
                "usuario_id": "agent_supervisor",
                "usuario_nombre": "Supervisor Agent (IA)",
                "tipo_accion": "analisis_metricas",
                "descripcion": "Revisión integral de salud del enjambre de agentes",
                "entidad_tipo": "Sistema",
                "entidad_id": "SYS-001",
                "fecha_accion": "2026-08-15T15:00:00Z",
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
                "fecha_accion": "2026-08-15T14:30:00Z",
                "ip_origen": "127.0.0.1",
                "resultado": "exitoso",
                "cambios_anteriores": {},
                "cambios_nuevos": {"destinatario": "904388543", "canal": "WhatsApp"},
            },
            {
                "id": "6",
                "usuario_id": "supervisor_humano",
                "usuario_nombre": "Supervisor de Facturación",
                "tipo_accion": "enviar_email",
                "descripcion": "Despacho de Recibo Oficial Movistar en PDF a cliente",
                "entidad_tipo": "Email",
                "entidad_id": "S8AA-0011000002",
                "fecha_accion": "2026-08-15T13:45:00Z",
                "ip_origen": "192.168.1.100",
                "resultado": "exitoso",
                "cambios_anteriores": {},
                "cambios_nuevos": {"destinatario": "marckgeo@gmail.com"},
            },
            {
                "id": "7",
                "usuario_id": "supervisor_hitl",
                "usuario_nombre": "Supervisor de Riesgo",
                "tipo_accion": "aprobar_solicitud",
                "descripcion": "Aprobación manual de ajuste de refacturación",
                "entidad_tipo": "Aprobacion",
                "entidad_id": "AP-1002",
                "fecha_accion": "2026-08-14T11:20:00Z",
                "ip_origen": "192.168.1.105",
                "resultado": "exitoso",
                "cambios_anteriores": {"estado": "pendiente"},
                "cambios_nuevos": {"estado": "aprobada"},
            },
            {
                "id": "8",
                "usuario_id": "supervisor_hitl",
                "usuario_nombre": "Supervisor de Riesgo",
                "tipo_accion": "rechazar_solicitud",
                "descripcion": "Rechazo de oferta fuera de umbral de política comercial",
                "entidad_tipo": "Aprobacion",
                "entidad_id": "AP-1003",
                "fecha_accion": "2026-08-14T09:10:00Z",
                "ip_origen": "192.168.1.105",
                "resultado": "exitoso",
                "cambios_anteriores": {"estado": "pendiente"},
                "cambios_nuevos": {"estado": "rechazada"},
            }
        ]

        all_logs = self._dynamic_logs + base_logs
        
        # Filtros
        if tipo_accion and tipo_accion.strip():
            filtro_act = tipo_accion.strip().lower()
            all_logs = [log for log in all_logs if filtro_act in log["tipo_accion"].lower()]
            
        if usuario_id and usuario_id.strip():
            filtro_u = usuario_id.strip().lower()
            all_logs = [log for log in all_logs if filtro_u in log["usuario_id"].lower() or filtro_u in log["usuario_nombre"].lower()]

        if fecha_desde and fecha_desde.strip():
            f_desde = fecha_desde.strip()
            all_logs = [log for log in all_logs if log["fecha_accion"][:10] >= f_desde]

        if fecha_hasta and fecha_hasta.strip():
            f_hasta = fecha_hasta.strip()
            all_logs = [log for log in all_logs if log["fecha_accion"][:10] <= f_hasta]

        if search and search.strip():
            q = search.strip().lower()
            all_logs = [
                log for log in all_logs
                if q in log["tipo_accion"].lower()
                or q in log["usuario_nombre"].lower()
                or q in log["entidad_id"].lower()
                or q in log["descripcion"].lower()
                or q in log["entidad_tipo"].lower()
            ]
        
        total = len(all_logs)
        paged = all_logs[skip : skip + limit]
        
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
        res = await self.get_audit_logs(db, skip=0, limit=500)
        for item in res["items"]:
            if str(item["id"]) == str(action_id):
                return item
        return None


# Singleton
audit_service = AuditService()

