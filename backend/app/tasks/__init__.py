"""
Tareas asíncronas y programación periódica Celery para SON-IA
"""

from app.tasks.celery_app import celery_app
from app.tasks.billing_tasks import (
    proactive_billing_t7,
    execute_billing_cycle,
    generate_monthly_report,
)
from app.tasks.collections_tasks import (
    recalculate_daily_overdue_and_tamn,
)
from app.tasks.negotiation_tasks import (
    predictive_negotiation_t5,
)
from app.tasks.learning_tasks import (
    periodic_learning_and_score_update,
)

__all__ = [
    "celery_app",
    "proactive_billing_t7",
    "execute_billing_cycle",
    "generate_monthly_report",
    "recalculate_daily_overdue_and_tamn",
    "predictive_negotiation_t5",
    "periodic_learning_and_score_update",
]