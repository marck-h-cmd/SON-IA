"""
Motor Simbólico de Cálculos Financieros
Zero-Hallucination: Todos los cálculos matemáticos se hacen aquí, NO en los LLMs
"""

import calendar
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Tuple

import structlog

logger = structlog.get_logger(__name__)


class CalculationEngine:
    """
    Motor de cálculo determinista para operaciones financieras.
    Cumple con normativa SUNAT Perú.
    """
    
    # Constantes tributarias Perú
    IGV_RATE = Decimal("0.18")  # 18%
    IGV_FACTOR = Decimal("1.18")
    
    @staticmethod
    def calcular_prorrateo_pxq(
        cargo_fijo_mensual: Decimal,
        fecha_inicio: date,
        fecha_fin: date,
    ) -> Decimal:
        """
        Cálculo de Prorrateo (PxQ): (Cargo Fijo / Días del Mes) * Días de Uso
        
        Args:
            cargo_fijo_mensual: Monto mensual del servicio
            fecha_inicio: Fecha de inicio del servicio
            fecha_fin: Fecha fin del período a facturar
        
        Returns:
            Monto prorrateado con 2 decimales
        """
        if fecha_inicio > fecha_fin:
            raise ValueError("fecha_inicio no puede ser mayor a fecha_fin")
        
        # Días del mes (basado en fecha_inicio)
        dias_del_mes = calendar.monthrange(fecha_inicio.year, fecha_inicio.month)[1]
        
        # Días de uso
        dias_uso = (fecha_fin - fecha_inicio).days + 1
        
        # Cálculo: (Cargo Fijo / Días del Mes) * Días de Uso
        cargo_diario = cargo_fijo_mensual / Decimal(str(dias_del_mes))
        prorrateo = cargo_diario * Decimal(str(dias_uso))
        
        # Redondear a 2 decimales (SUNAT)
        prorrateo = prorrateo.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        logger.debug(
            f"Prorrateo PxQ: {cargo_fijo_mensual} / {dias_del_mes} * {dias_uso} = {prorrateo}"
        )
        
        return prorrateo
    
    @staticmethod
    def calcular_igv(monto_total: Decimal) -> Tuple[Decimal, Decimal]:
        """
        Desglose de IGV (18%)
        Base Imponible: Precio Total / 1.18
        IGV: Base Imponible * 0.18
        
        Args:
            monto_total: Monto total incluyendo IGV
        
        Returns:
            Tuple[base_imponible, igv]
        """
        base_imponible = monto_total / CalculationEngine.IGV_FACTOR
        base_imponible = base_imponible.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        igv = base_imponible * CalculationEngine.IGV_RATE
        igv = igv.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        logger.debug(f"IGV: Base={base_imponible}, IGV={igv}")
        
        return base_imponible, igv
    
    @staticmethod
    def calcular_igv_desde_base(base_imponible: Decimal) -> Decimal:
        """
        Calcula IGV a partir de la base imponible
        """
        igv = base_imponible * CalculationEngine.IGV_RATE
        return igv.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calcular_interes_tamn(
        monto_deuda: Decimal,
        dias_mora: int,
        factor_acumulado_vencimiento: Decimal,
        factor_acumulado_hoy: Decimal,
    ) -> Decimal:
        """
        Intereses Moratorios (TAMN)
        Deuda * (Factor_Acumulado_Hoy / Factor_Acumulado_Vencimiento - 1)
        
        Args:
            monto_deuda: Monto de la deuda vencida
            dias_mora: Días de morosidad
            factor_acumulado_vencimiento: Factor TAMN al vencimiento
            factor_acumulado_hoy: Factor TAMN actual
        
        Returns:
            Monto de intereses moratorios
        """
        if factor_acumulado_vencimiento == 0:
            raise ValueError("factor_acumulado_vencimiento no puede ser 0")
        
        factor = factor_acumulado_hoy / factor_acumulado_vencimiento - Decimal("1")
        interes = monto_deuda * factor
        
        interes = interes.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        logger.debug(
            f"TAMN: Deuda={monto_deuda}, Factor={factor}, Interés={interes}"
        )
        
        return max(interes, Decimal("0"))  # No puede ser negativo
    
    @staticmethod
    def calcular_total_factura(
        subtotal: Decimal,
        igv: Decimal,
    ) -> Decimal:
        """
        Calcula el total de la factura
        """
        total = subtotal + igv
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# Singleton del motor de cálculo
calculation_engine = CalculationEngine()