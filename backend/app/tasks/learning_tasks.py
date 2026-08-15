"""
Tareas Celery para Aprendizaje Continuo y Re-entrenamiento Periódico
"""

import asyncio
import structlog

from app.tasks.celery_app import celery_app
from app.agents.learning_agent import learning_agent

logger = structlog.get_logger(__name__)


@celery_app.task(
    bind=True,
    name="app.tasks.learning_tasks.periodic_learning_and_score_update",
    max_retries=2,
    default_retry_delay=300,
)
def periodic_learning_and_score_update(self) -> dict:
    """
    Tarea Celery periódica semanal:
    1. Ejecuta el pipeline del LearningAgent.
    2. Analiza el historial de pagos y facturas en PostgreSQL.
    3. Re-entrena/recalcula los scores de confianza de todos los clientes y actualiza la BD.
    4. Genera diagnóstico y reporte de efectividad.
    """
    logger.info("🧠 Celery Beat: Ejecutando ciclo periódico de aprendizaje continuo...")
    
    async def _run():
        result = await learning_agent.execute({
            "type": "retrain_and_update_scores",
            "apply_db_updates": True,
        })
        logger.info(f"✅ Ciclo de aprendizaje finalizado: {result.get('total_clientes_procesados', 0)} clientes actualizados.")
        return result

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(_run())
        else:
            return asyncio.run(_run())
    except Exception as e:
        logger.error(f"❌ Error en ciclo de aprendizaje periódico: {e}")
        raise self.retry(exc=e)
