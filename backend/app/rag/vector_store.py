"""
Almacenamiento vectorial para RAG
"""

import structlog
from typing import List, Dict, Any

logger = structlog.get_logger(__name__)


class VectorStore:
    """
    Almacén de vectores para búsqueda semántica.
    
    Backends:
    - Pinecone (producción)
    - PGVector (PostgreSQL, desarrollo)
    - In-Memory (MVP/testing)
    """
    
    def __init__(self):
        self.store: Dict[str, List[float]] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
        logger.info("📚 Vector Store inicializado (in-memory)")
    
    async def add_vector(
        self,
        id: str,
        vector: List[float],
        metadata: Dict[str, Any] = {},
    ) -> None:
        """
        Agrega un vector al almacén.
        
        Args:
            id: Identificador único
            vector: Vector de embedding
            metadata: Metadatos asociados
        """
        self.store[id] = vector
        self.metadata[id] = metadata
        logger.debug(f"Vector agregado: {id}")
    
    async def search_similar(
        self,
        query_vector: List[float],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Busca vectores más similares usando cosine similarity.
        
        Args:
            query_vector: Vector de consulta
            top_k: Número de resultados
            
        Returns:
            Lista de resultados con scores
        """
        import math
        
        results = []
        
        for id, vector in self.store.items():
            # Cosine similarity
            dot_product = sum(a * b for a, b in zip(query_vector, vector))
            norm_a = math.sqrt(sum(a * a for a in query_vector))
            norm_b = math.sqrt(sum(b * b for b in vector))
            
            if norm_a > 0 and norm_b > 0:
                similarity = dot_product / (norm_a * norm_b)
            else:
                similarity = 0
            
            results.append({
                "id": id,
                "score": similarity,
                "metadata": self.metadata.get(id, {}),
            })
        
        # Ordenar por score descendente
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:top_k]
    
    async def delete_vector(self, id: str) -> None:
        """Elimina un vector del almacén"""
        self.store.pop(id, None)
        self.metadata.pop(id, None)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Estadísticas del almacén"""
        return {
            "total_vectors": len(self.store),
            "backend": "in-memory",
        }


# Singleton
vector_store = VectorStore()