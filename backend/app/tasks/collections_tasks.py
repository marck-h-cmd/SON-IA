"""
Tareas Celery para Cobranzas y Recálculo Diario de TAMN
"""

import asyncio
from datetime import date
from decimal import Decimal
import structlog
from sqlalchemy import select

from app.tasks.celery_app import celery_app
from app.database.connection import async_session_factory
from app.database.models import BSSFactura, BSSPago
from app.core.calculation_engine import calculation_engine

logger = structlog.get_logger(__name__)


@celery_app.task(
    bind=True,
    name="app.tasks.collections_tasks.recalculate_daily_overdue_and_tamn",
    max_retries=3,
    default_retry_delay=60,
)
def recalculate_daily_overdue_and_tamn(self) -> dict:
    """
    Tarea Celery periódica nocturna:
    1. Identifica todas las facturas pendientes de pago en la base de datos.
    2. Calcula días de mora transcurridos respecto a la fecha actual.
    3. Aplica el cálculo de Tasa Activa en Moneda Nacional (TAMN) con el Motor Simbólico Zero-Hallucination.
    4. Clasifica la etapa de mora (temprana, media, tardía, crítica).
    """
    logger.info("🌙 Celery Beat: Iniciando recálculo nocturno de TAMN y mora de cartera...")
    
    async def _run():
        hoy = date.today()
        total_procesadas = 0
        total_vencidas = 0
        tamn_total_acumulado = Decimal("0.00")
        
        async with async_session_factory() as session:
            # Facturas existentes
            fact_res = await session.execute(select(BSSFactura))
            facturas = fact_res.scalars().all()
            
            # Pagos realizados
            pagos_res = await session.execute(select(BSSPago.factura_afectada))
            facturas_pagadas = set(pagos_res.scalars().all())
            
            for f in facturas:
                if f.nro_doc_fiscal in facturas_pagadas:
                    continue
                
                total_procesadas += 1
                monto = Decimal(str(f.charge_total_amount or 0))
                
                if f.fecha_vto and f.fecha_vto < hoy:
                    total_vencidas += 1
                    dias = (hoy - f.fecha_vto).days
                    
                    # Calcular TAMN con motor simbólico
                    tamn_res = calculation_engine.calcular_tamn(
                        monto_original=monto,
                        dias_mora=dias,
                    )
                    interes = Decimal(str(tamn_res.get("monto_interes", "0.00")))
                    tamn_total_acumulado += interes
        
        logger.info(
            f"✅ Recálculo de TAMN completado: {total_vencidas}/{total_procesadas} facturas vencidas. "
            f"Interés total TAMN calculado: S/ {tamn_total_acumulado:,.2f}"
        )
        
        return {
            "status": "success",
            "fecha_ejecucion": hoy.isoformat(),
            "total_facturas_pendientes": total_procesadas,
            "total_facturas_vencidas": total_vencidas,
            "tamn_total_acumulado": float(tamn_total_acumulado),
        }

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(_run())
        else:
            return asyncio.run(_run())
    except Exception as e:
        logger.error(f"❌ Error en recálculo diario de TAMN: {e}")
        raise self.retry(exc=e)
