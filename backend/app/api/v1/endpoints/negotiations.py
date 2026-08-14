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
    Lista de ofertas de negociación predictiva.
    """
    return await billing_service.get_ofertas(db, skip, limit, estado)


@router.get("/tasa-aceptacion")
async def get_tasa_aceptacion(
    db: AsyncSession = Depends(get_db),
):
    """
    Tasa de aceptación y métricas de ofertas de negociación.
    """
    return await billing_service.get_tasa_aceptacion(db)


@router.get("/ofertas/{oferta_id}")
async def get_oferta(
    oferta_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Detalle completo de una oferta de negociación.
    """
    oferta = await billing_service.get_oferta_detalle(db, oferta_id)
    if not oferta:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    return oferta


@router.post("/ofertas/{oferta_id}/aceptar")
async def aceptar_oferta(
    oferta_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Cliente o agente acepta una oferta de negociación.
    """
    result = await billing_service.aceptar_oferta(db, oferta_id)
    if not result:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    return {"status": "success", "message": "Oferta aceptada"}


@router.post("/ofertas/{oferta_id}/rechazar")
async def rechazar_oferta(
    oferta_id: str,
    razon: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Cliente o agente rechaza una oferta de negociación.
    """
    result = await billing_service.rechazar_oferta(db, oferta_id, razon)
    if not result:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    return {"status": "success", "message": "Oferta rechazada"}