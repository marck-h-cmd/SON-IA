"""
Generación de embeddings con Gemini
"""

import structlog
from typing import List

from app.integrations.gemini_client import gemini_client

logger = structlog.get_logger(__name__)


class EmbeddingGenerator:
    """
    Genera embeddings para documentos usando Gemini Embeddings.
    
    Usos:
    - Historial de facturas
    - Documentos legales
    - Normativas SUNAT
    """
    
    def __init__(self):
        self.client = gemini_client
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Genera embedding para un texto.
        
        Args:
            text: Texto a embeber
            
        Returns:
            Vector de embedding
        """
        logger.debug(f"Generando embedding para texto de {len(text)} caracteres")
        return await self.client.generate_embeddings(text)
    
    async def generate_embeddings_batch(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        """
        Genera embeddings para múltiples textos.
        
        Args:
            texts: Lista de textos
            
        Returns:
            Lista de vectores de embedding
        """
        embeddings = []
        for text in texts:
            embedding = await self.generate_embedding(text)
            embeddings.append(embedding)
        
        logger.info(f"✅ {len(embeddings)} embeddings generados")
        return embeddings


# Singleton
embedding_generator = EmbeddingGenerator()