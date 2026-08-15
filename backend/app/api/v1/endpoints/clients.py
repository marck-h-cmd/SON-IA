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
    search: Optional[str] = Query(None, description="Búsqueda por RUC, razón social o teléfono"),
    db: AsyncSession = Depends(get_db),
):
    """
    Lista paginada de clientes (tabla bss_clientes).

    PARA EL FRONTEND:
    - URL:  GET /api/v1/clients?skip=0&limit=100&segmento=B2B&search=904388543
    - Uso:  tablas/buscadores de clientes (paginación con skip/limit y búsqueda por RUC, razón social o teléfono).
    - Query params:
      - skip:     registros a saltar (paginación)
      - limit:    máx. registros (1-500)
      - segmento: filtro (B2B, B2C, Gobierno) - opcional
      - search:   término de búsqueda (RUC, razón social o número de celular) - opcional
    - Respuesta: lista de clientes con RUC, razón social, segmento, score, teléfono.

    Args:
        skip: Registros para saltar
        limit: Máximo de registros
        segmento: Filtrar por segmento (B2B, B2C, Gobierno)
        search: Búsqueda por RUC, razón social o teléfono
    """
    return await billing_service.get_clientes(db, skip, limit, segmento, search)


@router.get("/{cliente_id}")
async def obtener_cliente(
    cliente_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Detalle completo de un cliente (consumida por Portal / Dashboard).

    PARA EL FRONTEND:
    - URL:  GET /api/v1/clients/{cliente_id}   (cliente_id = RUC)
    - Uso:  perfil de cliente: datos, score de confianza, cuentas y servicios.
    - Respuesta: 404 si no existe.
    
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
    cliente_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """
    Historial de facturas de un cliente (consumida por Portal de autogestión).

    PARA EL FRONTEND:
    - URL:  GET /api/v1/clients/{cliente_id}/historial-facturas?skip=0&limit=50
    - Uso:  tabla de recibos históricos del cliente en su portal.
    - Respuesta: lista de facturas del cliente (bss_facturas).

    Args:
        cliente_id: ID del cliente (RUC)
        skip: Registros para saltar
        limit: Máximo de registros
    """
    return await billing_service.get_historial_facturas(db, cliente_id, skip, limit)


@router.get("/{cliente_id}/score")
async def obtener_score_cliente(
    cliente_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Score de confianza de un cliente (usado por los agentes IA).

    PARA EL FRONTEND:
    - URL:  GET /api/v1/clients/{cliente_id}/score
    - Uso:  mostrar score y su desglose (elemento "score_confianza", 0-1).
    - Respuesta: 404 si el cliente no existe.
    
    Incluye:
    - Score actual
    - Factores que lo componen
    - Historial de cambios
    """
    score = await billing_service.get_score_cliente(db, cliente_id)
    if not score:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return score