"""
Constantes de negocio para SON-IA
"""

from decimal import Decimal

# ============================================
# Constantes Tributarias Perú
# ============================================
IGV_RATE = Decimal("0.18")  # 18%
IGV_FACTOR = Decimal("1.18")

# ============================================
# Ciclos de Facturación
# ============================================
CICLOS_FACTURACION = [5, 10, 15, 20, 25, 30]  # Días del mes

# ============================================
# Scores y Umbrales
# ============================================
SCORE_CONFIANZA_THRESHOLD = Decimal("0.80")  # Validación automática
SCORE_ALERTA_THRESHOLD = Decimal("0.50")  # Revisión manual
SCORE_CRITICO_THRESHOLD = Decimal("0.30")  # Alto riesgo

# ============================================
# Negociación
# ============================================
DIAS_ANTES_VENCIMIENTO_OFERTA = 5
DIAS_RECORDATORIO_VENCIMIENTO = 2
DESCUENTO_MAXIMO = Decimal("20.0")  # 20% máximo
DESCUENTO_MINIMO = Decimal("2.0")  # 2% mínimo

# ============================================
# Cobranzas
# ============================================
ETAPAS_MORA = {
    "temprana": (1, 5),
    "media": (6, 15),
    "tardia": (16, 30),
    "critica": (31, 999),
}

# ============================================
# Plazos de Pago
# ============================================
PLAZO_ESTANDAR_DIAS = 8
PLAZO_EXTENDIDO_DIAS = 15
PLAZO_MAXIMO_DIAS = 30

# ============================================
# Segmentos de Cliente
# ============================================
SEGMENTOS = ["B2B", "B2C", "Gobierno"]

# ============================================
# Canales de Comunicación
# ============================================
CANALES = ["email", "whatsapp", "sms", "llamada"]

# ============================================
# Estados de Factura
# ============================================
ESTADOS_FACTURA = ["Pendiente", "Pagado", "Vencido", "Anulado", "Disputado"]

# ============================================
# Estados de Oferta
# ============================================
ESTADOS_OFERTA = ["pendiente", "aceptada", "rechazada", "expirada"]