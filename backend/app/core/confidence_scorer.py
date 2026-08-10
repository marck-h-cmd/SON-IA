"""
Calculador de Score de Confianza
Versión basada en reglas para MVP (previa a modelo XGBoost)
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

import structlog

logger = structlog.get_logger(__name__)


class ConfidenceScorer:
    """
    Calcula el score de confianza de un cliente basado en reglas de negocio.
    
    En producción, este score será calculado por un modelo XGBoost entrenado.
    Para el MVP, usamos reglas deterministas.
    
    Score range: 0.0 - 1.0
    Threshold para validación automática: >= 0.80
    """
    
    # Pesos para cada factor
    PESO_ANTIGUEDAD = 0.25
    PESO_MORA_PROMEDIO = 0.30
    PESO_DISPUTAS = 0.20
    PESO_PAGOS_TARDE = 0.15
    PESO_MONTO_PROMEDIO = 0.10
    
    @staticmethod
    def calcular_score(
        antiguedad_meses: int,
        promedio_mora_dias: float,
        num_disputas_ultimo_anio: int,
        num_pagos_tarde: int,
        monto_promedio: Decimal,
        segmento: str,
    ) -> Decimal:
        """
        Calcula el score de confianza (0-1)
        
        Args:
            antiguedad_meses: Meses como cliente
            promedio_mora_dias: Promedio de días de mora
            num_disputas_ultimo_anio: Número de disputas en el último año
            num_pagos_tarde: Número de pagos tarde
            monto_promedio: Monto promedio de facturación
            segmento: B2B, B2C, Gobierno
        
        Returns:
            Score entre 0 y 1
        """
        score = Decimal("0")
        
        # 1. Antigüedad (más antigüedad = más confianza)
        if antiguedad_meses >= 60:  # 5+ años
            score += Decimal(str(ConfidenceScorer.PESO_ANTIGUEDAD))
        elif antiguedad_meses >= 24:  # 2-5 años
            score += Decimal(str(ConfidenceScorer.PESO_ANTIGUEDAD * 0.75))
        elif antiguedad_meses >= 12:  # 1-2 años
            score += Decimal(str(ConfidenceScorer.PESO_ANTIGUEDAD * 0.5))
        elif antiguedad_meses >= 6:  # 6 meses - 1 año
            score += Decimal(str(ConfidenceScorer.PESO_ANTIGUEDAD * 0.25))
        # < 6 meses: 0 puntos
        
        # 2. Promedio de mora (menos mora = más confianza)
        if promedio_mora_dias == 0:
            score += Decimal(str(ConfidenceScorer.PESO_MORA_PROMEDIO))
        elif promedio_mora_dias <= 3:
            score += Decimal(str(ConfidenceScorer.PESO_MORA_PROMEDIO * 0.7))
        elif promedio_mora_dias <= 7:
            score += Decimal(str(ConfidenceScorer.PESO_MORA_PROMEDIO * 0.4))
        elif promedio_mora_dias <= 15:
            score += Decimal(str(ConfidenceScorer.PESO_MORA_PROMEDIO * 0.2))
        # > 15 días: 0 puntos
        
        # 3. Disputas (menos disputas = más confianza)
        if num_disputas_ultimo_anio == 0:
            score += Decimal(str(ConfidenceScorer.PESO_DISPUTAS))
        elif num_disputas_ultimo_anio == 1:
            score += Decimal(str(ConfidenceScorer.PESO_DISPUTAS * 0.5))
        # > 1 disputa: 0 puntos
        
        # 4. Pagos tarde (menos pagos tarde = más confianza)
        if num_pagos_tarde == 0:
            score += Decimal(str(ConfidenceScorer.PESO_PAGOS_TARDE))
        elif num_pagos_tarde <= 2:
            score += Decimal(str(ConfidenceScorer.PESO_PAGOS_TARDE * 0.5))
        elif num_pagos_tarde <= 5:
            score += Decimal(str(ConfidenceScorer.PESO_PAGOS_TARDE * 0.25))
        # > 5 pagos tarde: 0 puntos
        
        # 5. Bonus por segmento
        if segmento == "Gobierno":
            score += Decimal("0.05")  # Gobierno suele pagar, aunque tarde
        elif segmento == "B2B":
            score += Decimal("0.03")  # Empresas más estables
        
        # Normalizar a 0-1
        score = min(max(score, Decimal("0")), Decimal("1"))
        score = score.quantize(Decimal("0.01"))
        
        logger.debug(
            f"Score calculado: {score} "
            f"(antiguedad={antiguedad_meses}m, mora_prom={promedio_mora_dias}d, "
            f"disputas={num_disputas_ultimo_anio}, pagos_tarde={num_pagos_tarde})"
        )
        
        return score
    
    @staticmethod
    def es_cliente_confiable(score: Decimal) -> bool:
        """
        Determina si un cliente es confiable para validación automática
        Threshold: >= 0.80
        """
        return score >= Decimal("0.80")


# Singleton
confidence_scorer = ConfidenceScorer()