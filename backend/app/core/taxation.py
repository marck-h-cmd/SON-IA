"""
Normativa Tributaria SUNAT Perú
Cálculos fiscales y validaciones para facturación electrónica
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from typing import Tuple, Optional
import structlog

logger = structlog.get_logger(__name__)


class TaxationEngine:
    """
    Motor de cumplimiento tributario peruano.
    
    Normativas implementadas:
    - IGV 18% (Ley del IGV)
    - Recibos Tipo 14 (SUNAT)
    - TAMN (Tasa Activa de Mercado Nominal)
    - Retenciones y detracciones
    """
    
    # ============================================
    # IGV - Impuesto General a las Ventas
    # ============================================
    IGV_RATE = Decimal("0.18")  # 18%
    IGV_FACTOR = Decimal("1.18")
    
    @staticmethod
    def calcular_base_imponible(monto_total: Decimal) -> Decimal:
        """
        Calcula la base imponible a partir del monto total (incluye IGV).
        Fórmula: Base = Total / 1.18
        
        Args:
            monto_total: Monto total incluyendo IGV
            
        Returns:
            Base imponible redondeada a 2 decimales
        """
        base = monto_total / TaxationEngine.IGV_FACTOR
        return base.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calcular_igv_desde_total(monto_total: Decimal) -> Tuple[Decimal, Decimal]:
        """
        Desglosa IGV desde el monto total.
        
        Args:
            monto_total: Monto total incluyendo IGV
            
        Returns:
            Tuple[base_imponible, igv]
        """
        base = TaxationEngine.calcular_base_imponible(monto_total)
        igv = monto_total - base
        return base, igv.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calcular_igv_desde_base(base_imponible: Decimal) -> Decimal:
        """
        Calcula IGV a partir de la base imponible.
        Fórmula: IGV = Base * 0.18
        
        Args:
            base_imponible: Base imponible
            
        Returns:
            IGV redondeado a 2 decimales
        """
        igv = base_imponible * TaxationEngine.IGV_RATE
        return igv.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calcular_total(base_imponible: Decimal, igv: Decimal) -> Decimal:
        """
        Calcula el total de la factura.
        Fórmula: Total = Base + IGV
        
        Args:
            base_imponible: Base imponible
            igv: Monto de IGV
            
        Returns:
            Total redondeado a 2 decimales
        """
        total = base_imponible + igv
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    # ============================================
    # TAMN - Tasa Activa de Mercado Nominal
    # ============================================
    
    @staticmethod
    def calcular_factor_tamn(tasa_anual: Decimal, dias: int) -> Decimal:
        """
        Calcula el factor acumulado TAMN para un período.
        Fórmula: Factor = (1 + Tasa)^(días/360)
        
        Args:
            tasa_anual: Tasa TAMN anual (ej: 0.15 para 15%)
            dias: Número de días
            
        Returns:
            Factor acumulado
        """
        if dias <= 0:
            return Decimal("1.0")
        
        exponente = Decimal(str(dias)) / Decimal("360")
        factor = (Decimal("1") + tasa_anual) ** exponente
        return factor.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calcular_interes_tamn(
        monto_deuda: Decimal,
        dias_mora: int,
        factor_vencimiento: Decimal,
        factor_actual: Decimal,
    ) -> Decimal:
        """
        Calcula intereses moratorios según TAMN.
        Fórmula: Interés = Deuda * (Factor_Actual / Factor_Vencimiento - 1)
        
        Args:
            monto_deuda: Monto de la deuda vencida
            dias_mora: Días de morosidad
            factor_vencimiento: Factor TAMN al vencimiento
            factor_actual: Factor TAMN actual
            
        Returns:
            Monto de intereses moratorios
        """
        if factor_vencimiento == 0:
            raise ValueError("El factor de vencimiento no puede ser 0")
        
        ratio = factor_actual / factor_vencimiento
        interes = monto_deuda * (ratio - Decimal("1"))
        interes = interes.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        logger.debug(
            f"TAMN: Deuda={monto_deuda}, Factor={ratio:.6f}, Interés={interes}"
        )
        
        return max(interes, Decimal("0"))
    
    # ============================================
    # Validaciones SUNAT para Recibos Tipo 14
    # ============================================
    
    @staticmethod
    def validar_serie_correlativo(serie: str, correlativo: int) -> bool:
        """
        Valida formato de serie y correlativo según SUNAT.
        
        Reglas:
        - Serie: 4 caracteres alfanuméricos (ej: F001, B001)
        - Correlativo: Número entero positivo de hasta 8 dígitos
        
        Args:
            serie: Serie del comprobante
            correlativo: Número correlativo
            
        Returns:
            True si es válido
        """
        if len(serie) != 4:
            logger.warning(f"Serie inválida: {serie} (debe tener 4 caracteres)")
            return False
        
        if not serie[0].isalpha():
            logger.warning(f"Serie inválida: {serie} (debe empezar con letra)")
            return False
        
        if correlativo <= 0 or correlativo > 99999999:
            logger.warning(f"Correlativo inválido: {correlativo}")
            return False
        
        return True
    
    @staticmethod
    def validar_tipo_comprobante(tipo_doc: str) -> bool:
        """
        Valida tipo de documento de identidad.
        
        Args:
            tipo_doc: '1' para DNI, '6' para RUC
            
        Returns:
            True si es válido
        """
        return tipo_doc in ("1", "6")
    
    @staticmethod
    def validar_numero_documento(tipo_doc: str, num_doc: str) -> bool:
        """
        Valida número de documento según tipo.
        
        - DNI: 8 dígitos
        - RUC: 11 dígitos, empieza con 10, 15, 17, 20
        
        Args:
            tipo_doc: Tipo de documento
            num_doc: Número de documento
            
        Returns:
            True si es válido
        """
        if tipo_doc == "1":  # DNI
            return len(num_doc) == 8 and num_doc.isdigit()
        
        if tipo_doc == "6":  # RUC
            if len(num_doc) != 11 or not num_doc.isdigit():
                return False
            return num_doc[:2] in ("10", "15", "17", "20")
        
        return False
    
    # ============================================
    # Retenciones y Detracciones
    # ============================================
    
    RETENCION_IGV_RATE = Decimal("0.03")  # 3% de retención
    
    @staticmethod
    def calcular_retencion_igv(monto_igv: Decimal, aplica_retencion: bool = False) -> Decimal:
        """
        Calcula retención de IGV (aplica para grandes contribuyentes).
        
        Args:
            monto_igv: Monto del IGV
            aplica_retencion: Si aplica retención
            
        Returns:
            Monto de retención
        """
        if not aplica_retencion:
            return Decimal("0")
        
        retencion = monto_igv * TaxationEngine.RETENCION_IGV_RATE
        return retencion.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    # ============================================
    # Redondeo SUNAT
    # ============================================
    
    @staticmethod
    def redondear_sunat(monto: Decimal) -> Decimal:
        """
        Redondea según reglas SUNAT:
        - 2 decimales
        - Redondeo simétrico (HALF_UP)
        
        Args:
            monto: Monto a redondear
            
        Returns:
            Monto redondeado
        """
        return monto.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# Singleton
taxation_engine = TaxationEngine()