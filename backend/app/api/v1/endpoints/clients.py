"""
Endpoints de Clientes
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.services.billing_service import BillingService

router = APIRouter()
billing_service = BillingService()


@router.get("/")
async def listar_clientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    segmento: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Lista clientes con filtros opcionales.
    
    Args:
        skip: Registros para saltar
        limit: Máximo de registros
        segmento: Filtrar por segmento (B2B, B2C, Gobierno)
    """
    return await billing_service.get_clientes(db, skip, limit, segmento)


@router.get("/{cliente_id}")
async def obtener_cliente(
    cliente_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene información detallada de un cliente.
    
    Incluye:
    - Datos del cliente
    - Score de confianza
    - Cuentas asociadas
    - Servicios activos
    """
    cliente = await billing_service.get_cliente(db, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.get("/{cliente_id}/historial-facturas")
async def historial_facturas_cliente(
    cliente_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene el historial de facturas de un cliente específico.
    
    Args:
        cliente_id: ID del cliente
        skip: Registros para saltar
        limit: Máximo de registros
    """
    return await billing_service.get_historial_facturas(db, cliente_id, skip, limit)


@router.get("/{cliente_id}/score")
async def obtener_score_cliente(
    cliente_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene el score de confianza detallado del cliente.
    
    Incluye:
    - Score actual
    - Factores que lo componen
    - Historial de cambios
    """
    score = await billing_service.get_score_cliente(db, cliente_id)
    if not score:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return score