"""
Utilidades para manejo de fechas
"""

from datetime import date, datetime, timedelta
from typing import Optional
import calendar


def get_last_day_of_month(year: int, month: int) -> int:
    """Retorna el último día del mes"""
    return calendar.monthrange(year, month)[1]


def add_business_days(start_date: date, days: int) -> date:
    """
    Suma días hábiles a una fecha.
    No cuenta sábados ni domingos.
    """
    current = start_date
    days_added = 0
    
    while days_added < days:
        current += timedelta(days=1)
        if current.weekday() < 5:  # Lunes a Viernes
            days_added += 1
    
    return current


def get_days_until_due(due_date: date) -> int:
    """Calcula días hasta la fecha de vencimiento"""
    today = date.today()
    delta = due_date - today
    return delta.days


def is_weekend(check_date: date) -> bool:
    """Verifica si una fecha es fin de semana"""
    return check_date.weekday() >= 5


def format_date_iso(date_obj: date) -> str:
    """Formatea fecha a ISO 8601"""
    return date_obj.isoformat()


def parse_date(date_str: str) -> date:
    """Parsea string a date"""
    return datetime.strptime(date_str, "%Y-%m-%d").date()