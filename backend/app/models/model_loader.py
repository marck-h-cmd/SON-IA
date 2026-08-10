"""
Carga de modelos ML entrenados
"""

import structlog
from pathlib import Path
from typing import Optional
import pickle

logger = structlog.get_logger(__name__)


class ModelLoader:
    """
    Carga modelos ML desde archivos .pkl
    
    Modelos:
    - score_confianza.pkl: XGBoost para score de confianza
    - prediccion_pago.pkl: XGBoost para predicción de pago
    - anomaly_detector.pkl: Isolation Forest para anomalías
    """
    
    def __init__(self):
        self.models_dir = Path(__file__).parent / "trained"
        self.loaded_models = {}
    
    def load_model(self, model_name: str) -> Optional[object]:
        """
        Carga un modelo desde disco.
        
        Args:
            model_name: Nombre del modelo (sin .pkl)
            
        Returns:
            Modelo cargado o None
        """
        model_path = self.models_dir / f"{model_name}.pkl"
        
        if not model_path.exists():
            logger.warning(f"⚠️ Modelo no encontrado: {model_path}")
            return None
        
        if model_name in self.loaded_models:
            return self.loaded_models[model_name]
        
        try:
            with open(model_path, "rb") as f:
                model = pickle.load(f)
            self.loaded_models[model_name] = model
            logger.info(f"✅ Modelo cargado: {model_name}")
            return model
        except Exception as e:
            logger.error(f"❌ Error cargando modelo {model_name}: {e}")
            return None
    
    def load_all_models(self) -> dict:
        """Carga todos los modelos disponibles"""
        models = {}
        for model_file in self.models_dir.glob("*.pkl"):
            model_name = model_file.stem
            model = self.load_model(model_name)
            if model:
                models[model_name] = model
        return models


# Singleton
model_loader = ModelLoader()