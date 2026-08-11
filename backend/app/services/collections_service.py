"""
Servicio de Cobranzas
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date
import structlog

from app.database.models import BSSFactura, BSSPago
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
        hoy = date.today()
        query = select(BSSFactura).where(
            BSSFactura.fecha_vto < hoy
        )
        
        result = await db.execute(query.offset(skip).limit(limit))
        facturas = result.scalars().all()
        
        return [
            {
                "nro_doc_fiscal": f.nro_doc_fiscal,
                "total": float(f.charge_total_amount) if f.charge_total_amount else 0,
                "estado": "Vencido",
            }
            for f in facturas
        ]
    
    async def calcular_tamn(
        self,
        db: AsyncSession,
        factura_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Calcula intereses TAMN para una factura
        """
        result = await db.execute(
            select(BSSFactura).where(BSSFactura.nro_doc_fiscal == factura_id)
        )
        factura = result.scalar_one_or_none()
        
        if not factura:
            return None
        
        monto = Decimal(str(factura.charge_total_amount or 0))
        dias_mora = 0
        if factura.fecha_vto and factura.fecha_vto < date.today():
            dias_mora = (date.today() - factura.fecha_vto).days

        interes = calculation_engine.calcular_interes_tamn(
            monto_deuda=monto,
            dias_mora=dias_mora,
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
        factura_id: str,
        monto_pagado: float,
        fecha_pago: str,
    ) -> bool:
        """
        Procesa un pago insertando en BSSPago
        """
        result = await db.execute(
            select(BSSFactura).where(BSSFactura.nro_doc_fiscal == factura_id)
        )
        factura = result.scalar_one_or_none()
        
        if not factura:
            return False
            
        pago = BSSPago(
            factura_afectada=factura_id,
            numero_identificacion_fiscal=factura.numero_identificacion_fiscal,
            monto_pagado=Decimal(str(monto_pagado)),
            moneda_factura=factura.moneda
        )
        db.add(pago)
        await db.commit()
        
        return True