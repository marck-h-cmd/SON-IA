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
    Obtiene el log de auditoría de todas las acciones de los agentes.
    
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
    Obtiene el detalle de una acción de auditoría específica.
    """
    detail = await audit_service.get_audit_detail(db, action_id)
    if not detail:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Acción no encontrada")
    return detail