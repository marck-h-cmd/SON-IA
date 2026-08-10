"""
Endpoints de Negociación
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.services.billing_service import BillingService

router = APIRouter()
billing_service = BillingService()


@router.get("/ofertas")
async def listar_ofertas(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    estado: Optional[str] = Query(None, description="pendiente, aceptada, rechazada, expirada"),
    db: AsyncSession = Depends(get_db),
):
    """
    Lista ofertas de negociación con filtros.
    """
    return await billing_service.get_ofertas(db, skip, limit, estado)


@router.post("/ofertas/{oferta_id}/aceptar")
async def aceptar_oferta(
    oferta_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Cliente acepta una oferta de negociación.
    
    Acciones:
    1. Genera nota de crédito
    2. Actualiza fecha de pago
    3. Notifica al cliente
    """
    result = await billing_service.aceptar_oferta(db, oferta_id)
    if not result:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    return {"status": "success", "message": "Oferta aceptada"}


@router.post("/ofertas/{oferta_id}/rechazar")
async def rechazar_oferta(
    oferta_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Cliente rechaza una oferta de negociación.
    """
    result = await billing_service.rechazar_oferta(db, oferta_id)
    if not result:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    return {"status": "success", "message": "Oferta rechazada"}