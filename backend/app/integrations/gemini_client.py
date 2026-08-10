"""
Cliente para Gemini API (Google)
"""

from typing import Dict, Any, Optional, List
import structlog

from app.config.settings import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class GeminiClient:
    """
    Cliente para interactuar con Gemini (Google).
    
    Modelos:
    - gemini-1.5-pro: NLP, generación de texto, RAG
    - gemini-1.5-flash: Clasificación rápida, bajo costo
    """
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_pro = settings.GEMINI_MODEL_PRO
        self.model_flash = settings.GEMINI_MODEL_FLASH
    
    async def generate_text(
        self,
        prompt: str,
        use_pro: bool = True,
    ) -> Dict[str, Any]:
        """
        Genera texto usando Gemini.
        
        Args:
            prompt: Prompt para el modelo
            use_pro: True para Gemini Pro, False para Flash
        
        Returns:
            Respuesta del modelo
        """
        model = self.model_pro if use_pro else self.model_flash
        logger.info(f"🌐 Gemini ({model}): Generando texto")
        
        # Simulación para MVP
        return {
            "text": f"Respuesta de {model}: {prompt[:100]}...",
            "model": model,
        }
    
    async def classify_text(
        self,
        text: str,
        categories: List[str],
    ) -> Dict[str, Any]:
        """
        Clasifica texto en categorías predefinidas.
        Usa Gemini Flash por velocidad y costo.
        """
        logger.info(f"🏷️ Gemini Flash: Clasificando texto")
        
        # Simulación
        return {
            "category": categories[0] if categories else "otro",
            "confidence": 0.95,
            "model": self.model_flash,
        }
    
    async def generate_embeddings(
        self,
        text: str,
    ) -> List[float]:
        """
        Genera embeddings para un texto.
        Usado para RAG y búsqueda semántica.
        """
        logger.info(f"🔢 Gemini: Generando embeddings ({len(text)} chars)")
        
        # Simulación - retorna vector de 768 dimensiones
        import hashlib
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()[:768 // 8]
        
        # Convertir a lista de floats normalizados
        import struct
        floats = []
        for i in range(0, len(hash_bytes), 4):
            if len(hash_bytes[i:i+4]) == 4:
                val = struct.unpack('f', hash_bytes[i:i+4])[0]
                floats.append(val)
        
        # Normalizar
        import math
        norm = math.sqrt(sum(f * f for f in floats))
        if norm > 0:
            floats = [f / norm for f in floats]
        
        return floats[:768]
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Chat contextual con Gemini Pro.
        Usado por el Agente de Atención al Cliente.
        """
        logger.info(f"💬 Gemini Pro: Chat con {len(messages)} mensajes")
        
        last_message = messages[-1]["content"] if messages else ""
        
        return {
            "response": f"Respuesta de Gemini a: {last_message[:100]}...",
            "model": self.model_pro,
        }


# Singleton
gemini_client = GeminiClient()