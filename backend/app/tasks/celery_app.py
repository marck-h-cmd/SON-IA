"""
Configuración de Celery & Celery Beat para Tareas Asíncronas y Automatización
"""

from celery import Celery
from celery.schedules import crontab
from app.config.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "sonia_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.billing_tasks",
        "app.tasks.collections_tasks",
        "app.tasks.negotiation_tasks",
        "app.tasks.learning_tasks",
        "app.tasks.notification_tasks",
    ],
)

# Configuración del Celery Worker
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Lima",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,       # 30 minutos límite duro
    task_soft_time_limit=25 * 60,  # 25 minutos límite suave
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=500,
)

# Programación periódica automatizada (Celery Beat)
celery_app.conf.beat_schedule = {
    # 1. Recálculo nocturno diario de días de mora y TAMN acumulado (Medianoche Lima 00:30)
    "recalculate-daily-overdue-and-tamn": {
        "task": "app.tasks.collections_tasks.recalculate_daily_overdue_and_tamn",
        "schedule": crontab(hour=0, minute=30),
    },
    # 2. Evaluación predictiva T-5 días: generación de ofertas y disparo preventivo de WhatsApp (08:00 AM)
    "predictive-negotiation-t5-daily": {
        "task": "app.tasks.negotiation_tasks.predictive_negotiation_t5",
        "schedule": crontab(hour=8, minute=0),
    },
    # 3. Pre-validación proactiva T-7 días: estimación de facturación del siguiente ciclo (09:00 AM)
    "proactive-billing-t7-daily": {
        "task": "app.tasks.billing_tasks.proactive_billing_t7",
        "schedule": crontab(hour=9, minute=0),
    },
    # 4. Ciclo periódico semanal de aprendizaje continuo y recálculo de scores de confianza (Domingos 23:00)
    "weekly-learning-and-score-update": {
        "task": "app.tasks.learning_tasks.periodic_learning_and_score_update",
        "schedule": crontab(hour=23, minute=0, day_of_week=0),
    },
    # 5. Generación de reporte mensual de facturación (Día 1 de cada mes a las 06:00)
    "monthly-billing-summary-report": {
        "task": "app.tasks.billing_tasks.generate_monthly_report",
        "schedule": crontab(hour=6, minute=0, day_of_month=1),
    },
}