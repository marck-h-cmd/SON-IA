"""
Endpoints del Dashboard Interno
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.services.billing_service import BillingService
from app.services.audit_service import AuditService

router = APIRouter()
billing_service = BillingService()
audit_service = AuditService()


@router.get("/metrics")
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene métricas en tiempo real para el dashboard.
    
    Retorna:
    - Total de facturas procesadas hoy
    - Monto total recaudado
    - Índice de morosidad
    - Ofertas de negociación activas
    - Facturas pendientes de revisión humana
    """
    # Simulación de métricas - En producción consultaría BD
    metrics = {
        "facturas_procesadas_hoy": 245,
        "monto_total_recaudado": 892500.00,
        "indice_morosidad": 3.2,
        "ofertas_activas": 15,
        "facturas_pendientes_revision": 3,
        "tasa_aceptacion_ofertas": 34.5,
        "tiempo_promedio_emision_seg": 12,
        "agentes_activos": 7,
        "timestamp": "2024-10-01T10:00:00",
    }
    
    return {
        "status": "success",
        "metrics": metrics,
    }


@router.get("/agentes/estado")
async def get_estado_agentes():
    """
    Obtiene el estado actual de todos los agentes del ecosistema.
    
    Retorna:
    - Estado de cada agente (activo, inactivo, error)
    - Última ejecución
    - Total de tareas procesadas
    """
    from app.agents.supervisor_agent import supervisor_agent
    
    health = supervisor_agent.check_system_health()
    
    agentes_estado = {
        "supervisor": {
            "estado": "activo",
            "modelo": "Llama-3.3",
            "ultima_ejecucion": "2024-10-01T09:55:00",
            "tareas_procesadas": 1250,
        },
        "billing": {
            "estado": "activo",
            "modelo": "Llama-3.3",
            "ultima_ejecucion": "2024-10-01T09:50:00",
            "tareas_procesadas": 450,
        },
        "collections": {
            "estado": "activo",
            "modelo": "Llama-3.3",
            "ultima_ejecucion": "2024-10-01T09:45:00",
            "tareas_procesadas": 320,
        },
        "negotiation": {
            "estado": "activo",
            "modelo": "Llama-3.3",
            "ultima_ejecucion": "2024-10-01T09:40:00",
            "tareas_procesadas": 180,
        },
        "customer": {
            "estado": "activo",
            "modelo": "gemini-1.5-pro",
            "ultima_ejecucion": "2024-10-01T09:58:00",
            "tareas_procesadas": 890,
        },
        "classifier": {
            "estado": "activo",
            "modelo": "gemini-1.5-flash",
            "ultima_ejecucion": "2024-10-01T09:59:00",
            "tareas_procesadas": 2100,
        },
        "learning": {
            "estado": "idle",
            "modelo": "Llama-3.3 + gemini",
            "ultima_ejecucion": "2024-09-30T23:00:00",
            "tareas_procesadas": 30,
        },
    }
    
    return {
        "status": "success",
        "system_health": health,
        "agentes": agentes_estado,
    }


@router.get("/alertas")
async def get_alertas_excepcion(
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene alertas de excepción que requieren intervención humana.
    
    Retorna:
    - Facturas con anomalías
    - Clientes con cambios significativos en score
    - Errores de sistema
    """
    alertas = [
        {
            "id": 1,
            "tipo": "anomalia_factura",
            "severidad": "alta",
            "mensaje": "Factura #4001: Monto 500% superior al promedio",
            "factura_id": 4001,
            "cliente": "María García Romero",
            "fecha": "2024-10-01T09:30:00",
            "estado": "pendiente_revision",
        },
        {
            "id": 2,
            "tipo": "cambio_score",
            "severidad": "media",
            "mensaje": "Cliente #1005: Score bajó de 0.52 a 0.45",
            "cliente_id": 1005,
            "fecha": "2024-10-01T08:15:00",
            "estado": "pendiente_revision",
        },
    ]
    
    return {
        "status": "success",
        "total_alertas": len(alertas),
        "alertas": alertas,
    }
