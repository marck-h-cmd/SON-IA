"""
Validadores personalizados para Pydantic
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any


def validate_ruc(ruc: str) -> bool:
    """
    Valida un RUC peruano (11 dígitos, empieza con 10, 15, 17, 20)
    """
    if len(ruc) != 11:
        return False
    
    if not ruc.isdigit():
        return False
    
    prefijos_validos = ["10", "15", "17", "20"]
    if ruc[:2] not in prefijos_validos:
        return False
    
    return True


def validate_dni(dni: str) -> bool:
    """
    Valida un DNI peruano (8 dígitos)
    """
    if len(dni) != 8:
        return False
    
    if not dni.isdigit():
        return False
    
    return True


def validate_monto_positivo(monto: Decimal) -> Decimal:
    """
    Valida que un monto sea positivo
    """
    if monto < 0:
        raise ValueError("El monto no puede ser negativo")
    return monto


def validate_score_range(score: Decimal) -> Decimal:
    """
    Valida que un score esté entre 0 y 1
    """
    if score < 0 or score > 1:
        raise ValueError("El score debe estar entre 0 y 1")
    return score


def validate_fecha_futura(fecha: date) -> date:
    """
    Valida que una fecha sea futura
    """
    if fecha < date.today():
        raise ValueError("La fecha debe ser futura")
    return fecha