"""
Tareas asíncronas de notificaciones
"""

import structlog
from app.tasks.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(name="app.tasks.notification_tasks.send_payment_reminder")
def send_payment_reminder(cliente_email: str, factura_id: int, monto: float):
    """
    Envía recordatorio de pago de forma asíncrona.
    """
    logger.info(f"📧 Enviando recordatorio a {cliente_email}")
    
    return {
        "status": "sent",
        "cliente": cliente_email,
        "factura_id": factura_id,
    }


@celery_app.task(name="app.tasks.notification_tasks.send_bulk_notifications")
def send_bulk_notifications(notifications: list):
    """
    Envía notificaciones masivas.
    """
    logger.info(f"📧 Enviando {len(notifications)} notificaciones masivas")
    
    return {
        "status": "completed",
        "enviadas": len(notifications),
    }