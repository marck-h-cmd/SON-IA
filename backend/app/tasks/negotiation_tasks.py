"""
Tareas Celery para Negociación Predictiva T-5 y Disparo de Ofertas por WhatsApp
"""

import asyncio
from datetime import date, timedelta
from decimal import Decimal
import structlog
from sqlalchemy import select

from app.tasks.celery_app import celery_app
from app.database.connection import async_session_factory
from app.database.models import BSSFactura, BSSPago, BSSCliente, BSSOfertaNegociacion
from app.agents.negotiation_agent import negotiation_agent
from app.integrations.openwa_client import openwa_client

logger = structlog.get_logger(__name__)


@celery_app.task(
    bind=True,
    name="app.tasks.negotiation_tasks.predictive_negotiation_t5",
    max_retries=3,
    default_retry_delay=120,
)
def predictive_negotiation_t5(self) -> dict:
    """
    Tarea Celery periódica matutina (Predictiva T-5 días):
    1. Busca facturas cuya fecha de vencimiento es exactamente en 5 días (T-5).
    2. Consulta el score de confianza del cliente.
    3. Si amerita (score < 0.80 o warning path), genera oferta preventiva en `BSSOfertaNegociacion`.
    4. Envía notificación preventiva por WhatsApp mediante OpenWAClient.
    """
    logger.info("🔮 Celery Beat: Ejecutando evaluación predictiva T-5 de vencimiento...")
    
    async def _run():
        hoy = date.today()
        fecha_t5 = hoy + timedelta(days=5)
        ofertas_generadas = []
        mensajes_enviados = 0
        
        async with async_session_factory() as session:
            # 1. Facturas que vencen en T-5
            stmt = select(BSSFactura).where(BSSFactura.fecha_vto == fecha_t5)
            res = await session.execute(stmt)
            facturas_t5 = res.scalars().all()
            
            # Facturas ya pagadas
            pagos_res = await session.execute(select(BSSPago.factura_afectada))
            facturas_pagadas = set(pagos_res.scalars().all())
            
            for fact in facturas_t5:
                if fact.nro_doc_fiscal in facturas_pagadas:
                    continue
                
                # 2. Obtener cliente
                cli_res = await session.execute(
                    select(BSSCliente).where(
                        BSSCliente.numero_identificacion_fiscal == fact.numero_identificacion_fiscal
                    )
                )
                cliente = cli_res.scalars().first()
                if not cliente:
                    continue
                
                score = float(cliente.score_confianza or 0.75)
                monto = float(fact.charge_total_amount or 0.0)
                
                # 3. Evaluar con NegotiationAgent
                neg_res = await negotiation_agent.execute({
                    "type": "evaluate_and_offer",
                    "factura_id": fact.nro_doc_fiscal,
                    "monto_pendiente": monto,
                    "score_confianza": score,
                    "dias_mora": 0,
                    "is_predictive_t5": True,
                })
                
                descuento_pct = float(neg_res.get("descuento_sugerido", 0.0))
                
                # 4. Guardar oferta si aplica descuento
                if descuento_pct > 0:
                    monto_desc = monto * (descuento_pct / 100.0)
                    oferta = BSSOfertaNegociacion(
                        factura_id=fact.nro_doc_fiscal,
                        numero_identificacion_fiscal=cliente.numero_identificacion_fiscal,
                        tipo_oferta="descuento_pronto_pago_t5",
                        descuento_porcentaje=Decimal(str(descuento_pct)),
                        monto_original=Decimal(str(monto)),
                        monto_con_descuento=Decimal(str(monto - monto_desc)),
                        fecha_expiracion=fecha_t5,
                        estado="pendiente",
                    )
                    session.add(oferta)
                    ofertas_generadas.append({
                        "factura": fact.nro_doc_fiscal,
                        "ruc": cliente.numero_identificacion_fiscal,
                        "descuento": descuento_pct,
                    })
                    
                    # 5. Enviar mensaje de alerta preventiva si tiene celular
                    if cliente.numero_celular:
                        nombre = (cliente.razon_social or "Cliente").split("_")[-1]
                        msg = (
                            f"Hola {nombre} 👋, tu factura *{fact.nro_doc_fiscal}* vence en 5 días ({fecha_t5.strftime('%d/%m/%Y')}).\n"
                            f"💡 Aprovecha un *{descuento_pct:.0f}% de descuento por pronto pago* (Monto: S/ {(monto - monto_desc):,.2f}) "
                            f"si abonas antes del vencimiento. Responde *'negociar'* para confirmar."
                        )
                        send_res = await openwa_client.send_message(
                            phone_number=cliente.numero_celular,
                            message=msg,
                        )
                        if send_res.get("success"):
                            mensajes_enviados += 1
            
            await session.commit()
        
        logger.info(
            f"✅ Negociación predictiva T-5 completada: {len(ofertas_generadas)} ofertas generadas, "
            f"{mensajes_enviados} alertas enviadas por WhatsApp."
        )
        
        return {
            "status": "success",
            "fecha_t5": fecha_t5.isoformat(),
            "ofertas_generadas_total": len(ofertas_generadas),
            "alertas_whatsapp_enviadas": mensajes_enviados,
            "ofertas": ofertas_generadas,
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
        logger.error(f"❌ Error en negociación predictiva T-5: {e}")
        raise self.retry(exc=e)
