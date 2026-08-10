"""
Servicio de Cobranzas
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.database.models import BSSFacturaCabecera
from app.core.calculation_engine import calculation_engine

logger = structlog.get_logger(__name__)


class CollectionsService:
    """Servicio para operaciones de cobranza"""
    
    async def get_facturas_vencidas(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        etapa: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene facturas vencidas
        """
        query = select(BSSFacturaCabecera).where(
            BSSFacturaCabecera.estado_pago == "Vencido"
        )
        
        result = await db.execute(query.offset(skip).limit(limit))
        facturas = result.scalars().all()
        
        return [
            {
                "id_factura": f.id_factura,
                "total": float(f.importe_total) if f.importe_total else 0,
                "estado": f.estado_pago,
            }
            for f in facturas
        ]
    
    async def calcular_tamn(
        self,
        db: AsyncSession,
        factura_id: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Calcula intereses TAMN para una factura
        """
        result = await db.execute(
            select(BSSFacturaCabecera).where(BSSFacturaCabecera.id_factura == factura_id)
        )
        factura = result.scalar_one_or_none()
        
        if not factura:
            return None
        
        # Simulación de cálculo TAMN
        monto = Decimal(str(factura.importe_total or 0))
        interes = calculation_engine.calcular_interes_tamn(
            monto_deuda=monto,
            dias_mora=15,
            factor_acumulado_vencimiento=Decimal("1.0"),
            factor_acumulado_hoy=Decimal("1.025"),
        )
        
        return {
            "factura_id": factura_id,
            "monto_deuda": float(monto),
            "interes_tamn": float(interes),
            "total_pagar": float(monto + interes),
        }
    
    async def procesar_pago(
        self,
        db: AsyncSession,
        factura_id: int,
        monto_pagado: float,
        fecha_pago: str,
    ) -> bool:
        """
        Procesa un pago y actualiza la factura
        """
        result = await db.execute(
            select(BSSFacturaCabecera).where(BSSFacturaCabecera.id_factura == factura_id)
        )
        factura = result.scalar_one_or_none()
        
        if not factura:
            return False
        
        factura.estado_pago = "Pagado"
        await db.commit()
        
        return True