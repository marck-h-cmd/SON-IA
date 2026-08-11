"""
Endpoints de Cobranzas
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.services.collections_service import CollectionsService

router = APIRouter()
collections_service = CollectionsService()


@router.get("/facturas-vencidas")
async def get_facturas_vencidas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    etapa: Optional[str] = Query(None, description="temprana, media, tardia, critica"),
    db: AsyncSession = Depends(get_db),
):
    """
    Lista facturas vencidas con su etapa de mora.
    """
    return await collections_service.get_facturas_vencidas(db, skip, limit, etapa)


@router.post("/calcular-tamn/{factura_id}")
async def calcular_tamn_factura(
    factura_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Calcula los intereses moratorios TAMN para una factura vencida.
    """
    result = await collections_service.calcular_tamn(db, factura_id)
    if not result:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return result


@router.post("/procesar-pago")
async def procesar_pago(
    factura_id: str,
    monto_pagado: float,
    fecha_pago: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Registra un pago y concilia con la factura correspondiente.
    """
    result = await collections_service.procesar_pago(db, factura_id, monto_pagado, fecha_pago)
    return {"status": "success", "message": "Pago procesado correctamente"}