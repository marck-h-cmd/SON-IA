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
    Cartera de facturas vencidas (consumida por la sección Cobranzas).

    PARA EL FRONTEND:
    - URL:  GET /api/v1/collections/facturas-vencidas?skip=0&limit=100&etapa=media
    - Uso:  tabla de morosidad/cartera vencida (PCD).
    - Query params:
      - skip:  paginación offset
      - limit: máx. registros
      - etapa: filtro de severidad de mora: temprana, media, tardia, critica
    - Respuesta: lista de facturas vencidas con su etapa de mora (Agente Cobranzas).

    Lista facturas vencidas con su etapa de mora.
    """
    return await collections_service.get_facturas_vencidas(db, skip, limit, etapa)


@router.post("/calcular-tamn/{factura_id}")
async def calcular_tamn_factura(
    factura_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Calcula intereses moratorios (TAMN) de una factura vencida.

    PARA EL FRONTEND:
    - URL:  POST /api/v1/collections/calcular-tamn/{factura_id}
    - Uso:  antes de una cobranza, obtener el recargo por mora (TAMN)
            para mostrarlo o incluirlo en gestiones de cobro.
    - Respuesta: 404 si la factura no existe; si no, detalle del cálculo.
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
    Registra un pago y concilia la factura (Agente de Cobranzas).

    PARA EL FRONTEND:
    - URL:  POST /api/v1/collections/procesar-pago?factura_id=...&monto_pagado=...&fecha_pago=...
    - Uso:  registro manual de un pago llegado por bancos/conciliación,
            o confirmación desde el portal. Dispara conciliación y, si el
            cliente está por WhatsApp, la notificación de confirmación.
    - Params (query): factura_id, monto_pagado, fecha_pago (ISO yyyy-mm-dd)
    - Respuesta: { status: "success", message }
    """
    result = await collections_service.procesar_pago(db, factura_id, monto_pagado, fecha_pago)
    return {"status": "success", "message": "Pago procesado correctamente"}