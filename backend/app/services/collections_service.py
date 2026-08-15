"""
Servicio de Cobranzas
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import date
import structlog

from app.database.models import BSSFactura, BSSPago, BSSCliente
from app.core.calculation_engine import calculation_engine

logger = structlog.get_logger(__name__)


class CollectionsService:
    """Servicio para operaciones de cobranza"""
    
    def _calcular_etapa_mora(self, dias_mora: int) -> str:
        if dias_mora <= 30:
            return "temprana"
        elif dias_mora <= 60:
            return "media"
        elif dias_mora <= 90:
            return "tardia"
        return "critica"
    
    async def get_facturas_vencidas(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        etapa: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Obtiene facturas vencidas con paginación y enriquecimiento de mora
        """
        hoy = date.today()
        
        # Count total
        count_query = select(func.count(BSSFactura.nro_doc_fiscal)).where(BSSFactura.fecha_vto < hoy)
        total_res = await db.execute(count_query)
        total_count = total_res.scalar() or 0
        
        # Query page with outerjoin
        query = (
            select(
                BSSFactura,
                BSSCliente.razon_social
            )
            .outerjoin(
                BSSCliente,
                BSSFactura.numero_identificacion_fiscal == BSSCliente.numero_identificacion_fiscal
            )
            .where(BSSFactura.fecha_vto < hoy)
            .order_by(BSSFactura.fecha_vto.asc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await db.execute(query)
        rows = result.all()
        
        items = []
        for factura, razon_social in rows:
            dias_mora = (hoy - factura.fecha_vto).days if factura.fecha_vto else 0
            etapa_calc = self._calcular_etapa_mora(dias_mora)
            
            monto = float(factura.charge_total_amount or 0)
            tamn_val = float(
                calculation_engine.calcular_interes_tamn(
                    monto_deuda=Decimal(str(monto)),
                    dias_mora=dias_mora,
                    factor_acumulado_vencimiento=Decimal("1.0"),
                    factor_acumulado_hoy=Decimal("1.025"),
                )
            )
            
            cliente_nombre = razon_social if razon_social else factura.numero_identificacion_fiscal
                
            items.append({
                "id": factura.nro_doc_fiscal,
                "numero_factura": factura.nro_doc_fiscal,
                "cliente_id": factura.numero_identificacion_fiscal,
                "cliente_nombre": cliente_nombre,
                "monto_original": monto,
                "monto_pendiente": monto,
                "dias_vencido": dias_mora,
                "etapa_mora": etapa_calc,
                "fecha_vencimiento": str(factura.fecha_vto) if factura.fecha_vto else "",
                "tamn_calculado": round(tamn_val, 2),
            })
        
        return {
            "items": items,
            "total": total_count,
            "skip": skip,
            "limit": limit,
        }

    async def get_cartera_metricas(
        self,
        db: AsyncSession,
    ) -> Dict[str, Any]:
        """
        Calcula las métricas consolidadas de la cartera vencida
        """
        hoy = date.today()
        query = (
            select(
                func.count(BSSFactura.nro_doc_fiscal),
                func.sum(BSSFactura.charge_total_amount)
            )
            .where(BSSFactura.fecha_vto < hoy)
        )
        result = await db.execute(query)
        total_count, total_monto = result.one()
        
        total_monto_float = float(total_monto or 0)
        tamn_acumulado = total_monto_float * 0.025
            
        return {
            "total_cartera_vencida": round(total_monto_float, 2),
            "cantidad_facturas_vencidas": total_count or 0,
            "tamn_acumulado": round(tamn_acumulado, 2),
            "tendencia_vs_mes_anterior": -3.2,
        }
    
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
            "monto_original": float(monto),
            "tasa_moratoria": 0.025,
            "dias_vencido": dias_mora,
            "tamn": float(interes),
            "monto_interes": float(interes),
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


# Singleton
collections_service = CollectionsService()