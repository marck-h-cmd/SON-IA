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
    Dispara un ciclo de facturación completo (acción del Agente Supervisor).

    PARA EL FRONTEND:
    - URL:    POST /api/v1/billing/ciclos/ejecutar?ciclo_id=N&force_review=true|false
    - Uso:    botón "Ejecutar ciclo" de la sección Facturación.
    - Cuerpo: no requiere body; usa query params (ciclo_id, force_review).
    - Respuesta: resultado del Supervisor Agent con el estado del flujo
      (facturas generadas, validación, anomalías detectadas).

    El Agente Supervisor orquesta el proceso completo:
    1. Validación de datos de insumos (plantas BSS/OSS)
    2. Cálculo de facturas vía motor simbólico (PxQ e IGV)
    3. Verificación de anomalías (monto 500% superior, etc.)
    4. Decisión HITL si es necesario (envía alerta al dashboard)
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
    Lista paginada de facturas (consumida por la sección Facturación).

    PARA EL FRONTEND:
    - URL:  GET /api/v1/billing/facturas?skip=0&limit=100&estado=Pendiente
    - Uso:  tablas de facturas (paginar con skip/limit).
    - Query params:
      - skip:   registros a saltar (paginación offset)
      - limit:  máx. registros a retornar (1-500)
      - estado: filtro booleano de color (Pendiente, Pagado, Vencido) - opcional
    - Respuesta: lista de facturas de la tabla bss_facturas.

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
    Detalle completo de una factura (consumida por Facturación / Portal).

    PARA EL FRONTEND:
    - URL:  GET /api/v1/billing/facturas/{factura_id}
    - Uso:  vista de detalle de factura (cabecera + detalle + ofertas activas).
    - Path param: factura_id (ej: S9AA-0082761955).
    - Respuesta: 404 si no existe; si no, cabecera, líneas y ofertas.
    
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
    Validación manual (HITL) de una factura marcada como excepcion.

    PARA EL FRONTEND:
    - URL:  POST /api/v1/billing/facturas/{factura_id}/validar
    - Uso:  botón "Validar" / "Aprobar" en el flujo de revisión humana
            (dashboard -> facturas_pendientes_revision).
    - Efecto: marca la factura como revisada por un operador y continúa el flujo.

    Solo aplica a facturas con validacion_automatica=False.
    """
    result = await billing_service.validar_factura_manual(db, factura_id)
    if not result:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return {"status": "success", "message": "Factura validada manualmente"}