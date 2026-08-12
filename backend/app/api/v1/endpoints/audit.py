"""
Endpoints de Auditoría
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.services.audit_service import AuditService

router = APIRouter()
audit_service = AuditService()


@router.get("/log")
async def get_audit_log(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    agente: Optional[str] = Query(None, description="Filtrar por agente"),
    accion: Optional[str] = Query(None, description="Filtrar por tipo de acción"),
    db: AsyncSession = Depends(get_db),
):
    """
    Log de auditoría de todas las acciones de los agentes.

    PARA EL FRONTEND:
    - URL:  GET /api/v1/audit/log?skip=0&limit=100&agente=billing&accion=...
    - Uso:  tabla de auditoría (transparencia/trazabilidad) del dashboard interno.
    - Query params:
      - skip:   paginación
      - limit:  máx. registros
      - agente: filtro por nombre de agente (supervisor, billing, ...)
      - accion: filtro por tipo de acción
    - Respuesta: lista de eventos registrados por el sistema (tabla de auditoría).
    
    Cada acción incluye:
    - Agente que la ejecutó
    - Modelo de IA utilizado
    - Acción realizada
    - Timestamp
    - Resultado
    """
    return await audit_service.get_audit_log(db, skip, limit, agente, accion)


@router.get("/log/{action_id}")
async def get_audit_detail(
    action_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Detalle de una acción de auditoría específica.

    PARA EL FRONTEND:
    - URL:  GET /api/v1/audit/log/{action_id}
    - Uso:  expandir/abrir un registro del log para ver su detalle completo.
    - Respuesta: 404 si la acción no existe.
    """
    detail = await audit_service.get_audit_detail(db, action_id)
    if not detail:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Acción no encontrada")
    return detail