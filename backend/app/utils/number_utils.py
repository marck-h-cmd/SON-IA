"""
Utilidades para manejo de números y decimales
"""

from decimal import Decimal, ROUND_HALF_UP


def round_currency(amount: Decimal) -> Decimal:
    """Redondea a 2 decimales (estándar SUNAT)"""
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_percentage(amount: Decimal, percentage: Decimal) -> Decimal:
    """Calcula un porcentaje de un monto"""
    result = amount * (percentage / Decimal("100"))
    return round_currency(result)


def format_currency(amount: Decimal) -> str:
    """Formatea monto a string con símbolo S/"""
    return f"S/ {amount:,.2f}"


def safe_divide(numerator: Decimal, denominator: Decimal) -> Decimal:
    """División segura (evita división por cero)"""
    if denominator == 0:
        return Decimal("0")
    return numerator / denominator