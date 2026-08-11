"""
Endpoints de Facturación
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.services.billing_service import BillingService
from app.agents.supervisor_agent import supervisor_agent

router = APIRouter()
billing_service = BillingService()


@router.post("/ciclos/ejecutar")
async def ejecutar_ciclo_facturacion(
    ciclo_id: int = Query(..., description="ID del ciclo de facturación"),
    force_review: bool = Query(False, description="Forzar revisión humana"),
):
    """
    Inicia un ciclo de facturación.
    
    El Agente Supervisor orquesta el proceso completo:
    1. Validación de datos
    2. Cálculo de facturas
    3. Verificación de anomalías
    4. Decisión HITL si es necesario
    """
    task = {
        "type": "start_billing_cycle",
        "ciclo_id": ciclo_id,
        "force_human_review": force_review,
    }
    
    result = await supervisor_agent.execute(task)
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    
    return result


@router.get("/facturas")
async def listar_facturas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    estado: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Lista facturas con filtros opcionales.
    
    Args:
        skip: Registros para saltar (paginación)
        limit: Máximo de registros a retornar
        estado: Filtrar por estado (Pendiente, Pagado, Vencido)
    """
    return await billing_service.get_facturas(db, skip, limit, estado)


@router.get("/facturas/{factura_id}")
async def obtener_factura(
    factura_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene el detalle completo de una factura.
    
    Incluye:
    - Cabecera de factura
    - Líneas de detalle
    - Ofertas de negociación activas
    """
    factura = await billing_service.get_factura(db, factura_id)
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return factura


@router.post("/facturas/{factura_id}/validar")
async def validar_factura(
    factura_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Valida manualmente una factura que requiere revisión humana.
    Solo aplica a facturas con validacion_automatica=False.
    """
    result = await billing_service.validar_factura_manual(db, factura_id)
    if not result:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return {"status": "success", "message": "Factura validada manualmente"}