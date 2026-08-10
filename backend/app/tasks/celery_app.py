"""
Configuración de Celery para tareas asíncronas
"""

from celery import Celery
from app.config.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "sonia_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.billing_tasks",
        "app.tasks.notification_tasks",
    ],
)

# Configuración
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Lima",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

celery_app.conf.beat_schedule = {
    "check-overdue-invoices-daily": {
        "task": "app.tasks.billing_tasks.check_overdue_invoices",
        "schedule": 86400.0,  # Cada 24 horas
    },
    "generate-monthly-report": {
        "task": "app.tasks.billing_tasks.generate_monthly_report",
        "schedule": 2592000.0,  # Cada 30 días
    },
}