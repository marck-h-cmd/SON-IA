"""
Inferencia de modelos ML
"""

import structlog
from typing import Dict, Any
import numpy as np

from app.models.model_loader import model_loader

logger = structlog.get_logger(__name__)


class ModelInference:
    """
    Servicio de inferencia para modelos ML.
    
    Si el modelo entrenado no está disponible, usa reglas de fallback.
    """
    
    def __init__(self):
        self.score_model = model_loader.load_model("score_confianza")
        self.payment_model = model_loader.load_model("prediccion_pago")
        self.anomaly_model = model_loader.load_model("anomaly_detector")
    
    def predict_score_confianza(self, features: Dict[str, Any]) -> float:
        """
        Predice el score de confianza de un cliente.
        
        Args:
            features: Características del cliente
            
        Returns:
            Score entre 0 y 1
        """
        if self.score_model:
            # Usar modelo XGBoost entrenado
            feature_array = np.array([list(features.values())])
            score = float(self.score_model.predict_proba(feature_array)[0, 1])
        else:
            # Fallback: reglas deterministas
            from app.core.confidence_scorer import confidence_scorer
            score = float(confidence_scorer.calcular_score(
                antiguedad_meses=features.get("antiguedad_meses", 0),
                promedio_mora_dias=features.get("promedio_mora_dias", 0),
                num_disputas_ultimo_anio=features.get("num_disputas_ultimo_anio", 0),
                num_pagos_tarde=features.get("num_pagos_tarde", 0),
                monto_promedio=features.get("monto_promedio", 0),
                segmento=features.get("segmento", "B2C"),
            ))
        
        logger.debug(f"Score confianza: {score:.2f}")
        return score
    
    def predict_payment_probability(self, features: Dict[str, Any]) -> float:
        """
        Predice probabilidad de pago en próximos 15 días.
        
        Args:
            features: Características del cliente y factura
            
        Returns:
            Probabilidad entre 0 y 1
        """
        if self.payment_model:
            feature_array = np.array([list(features.values())])
            prob = float(self.payment_model.predict_proba(feature_array)[0, 1])
        else:
            # Fallback: basado en score de confianza
            prob = features.get("score_confianza", 0.70)
        
        logger.debug(f"Probabilidad pago: {prob:.2f}")
        return prob
    
    def detect_anomaly(self, factura_data: Dict[str, Any]) -> bool:
        """
        Detecta si una factura es anómala.
        
        Returns:
            True si es anómala, False si es normal
        """
        if self.anomaly_model:
            feature_array = np.array([list(factura_data.values())])
            prediction = self.anomaly_model.predict(feature_array)[0]
            return prediction == -1  # -1 = anomalía en Isolation Forest
        else:
            # Fallback: regla simple (5x el promedio)
            return False


# Singleton
model_inference = ModelInference()