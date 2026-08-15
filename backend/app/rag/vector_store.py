"""
Almacenamiento vectorial y búsqueda semántica para RAG
"""

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)

PERSIST_PATH = Path(__file__).parent / "vector_store_data.json"


class VectorStore:
    """
    Almacén de vectores para búsqueda semántica con soporte de persistencia local.
    
    Backends y Capacidades:
    - In-Memory con persistencia JSON local
    - Búsqueda por similitud de coseno
    - Filtrado flexible por metadatos (categoría, producto, etc.)
    - Búsqueda híbrida (semántica + léxica) como fallback
    """
    
    def __init__(self, persist_path: Optional[Path] = None):
        self.store: Dict[str, List[float]] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self.persist_path = persist_path or PERSIST_PATH
        self._load_from_disk()
        logger.info("📚 Vector Store inicializado", total_vectors=len(self.store))

    def _load_from_disk(self) -> None:
        """Carga vectores previamente indexados desde el archivo persistente si existe."""
        if not self.persist_path.exists():
            return
        try:
            with open(self.persist_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.store = data.get("vectors", {})
                self.metadata = data.get("metadata", {})
                logger.info(f"📂 Cargados {len(self.store)} vectores persistidos desde {self.persist_path.name}")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo cargar el almacén de vectores persistido: {e}")

    def save_to_disk(self) -> None:
        """Persiste los vectores y metadatos en disco."""
        try:
            self.persist_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.persist_path, "w", encoding="utf-8") as f:
                json.dump({
                    "vectors": self.store,
                    "metadata": self.metadata
                }, f, ensure_ascii=False, indent=2)
            logger.debug(f"💾 {len(self.store)} vectores guardados en disco")
        except Exception as e:
            logger.error(f"❌ Error al guardar vectores en disco: {e}")
    
    async def add_vector(
        self,
        id: str,
        vector: List[float],
        metadata: Optional[Dict[str, Any]] = None,
        persist: bool = True,
    ) -> None:
        """
        Agrega o actualiza un vector en el almacén.
        
        Args:
            id: Identificador único del documento
            vector: Vector de embedding
            metadata: Metadatos asociados
            persist: Si se debe sincronizar a disco
        """
        self.store[id] = vector
        self.metadata[id] = metadata or {}
        logger.debug(f"Vector agregado/actualizado: {id}")
        if persist:
            self.save_to_disk()
    
    async def add_vectors_batch(
        self,
        items: List[Dict[str, Any]],
    ) -> None:
        """
        Agrega múltiples vectores de forma eficiente.
        
        Args:
            items: Lista de dicts con claves 'id', 'vector', 'metadata'
        """
        for item in items:
            self.store[item["id"]] = item["vector"]
            self.metadata[item["id"]] = item.get("metadata", {})
        self.save_to_disk()
        logger.info(f"✅ Batch de {len(items)} vectores indexados y guardados")
    
    async def search_similar(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter_category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Busca vectores más similares usando cosine similarity con soporte de filtros.
        
        Args:
            query_vector: Vector de consulta
            top_k: Número máximo de resultados
            filter_category: Categoría opcional para restringir la búsqueda
            
        Returns:
            Lista de resultados ordenados por score con metadatos
        """
        if not self.store:
            return []
        
        results = []
        norm_a = math.sqrt(sum(a * a for a in query_vector)) if query_vector else 0
        
        for doc_id, vector in self.store.items():
            meta = self.metadata.get(doc_id, {})
            
            # Aplicar filtro si se especificó
            if filter_category and meta.get("category") != filter_category:
                continue
            
            # Calcular cosine similarity
            if norm_a > 0 and len(vector) == len(query_vector):
                dot_product = sum(a * b for a, b in zip(query_vector, vector))
                norm_b = math.sqrt(sum(b * b for b in vector))
                similarity = (dot_product / (norm_a * norm_b)) if norm_b > 0 else 0.0
            else:
                similarity = 0.0
            
            results.append({
                "id": doc_id,
                "score": float(similarity),
                "metadata": meta,
            })
        
        # Ordenar por score descendente
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    async def search_by_keywords(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Búsqueda léxica directa en los textos de metadatos (útil si los embeddings fallan o están offline).
        """
        terms = query.lower().split()
        results = []
        
        for doc_id, meta in self.metadata.items():
            text_corpus = (
                f"{meta.get('title', '')} {meta.get('content', '')} {meta.get('category', '')}"
            ).lower()
            
            # Puntuación basada en coincidencias de palabras clave
            matches = sum(1 for term in terms if term in text_corpus)
            if matches > 0:
                score = matches / max(len(terms), 1)
                results.append({
                    "id": doc_id,
                    "score": float(score),
                    "metadata": meta,
                })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    async def delete_vector(self, id: str) -> None:
        """Elimina un vector del almacén"""
        self.store.pop(id, None)
        self.metadata.pop(id, None)
        self.save_to_disk()
    
    async def get_stats(self) -> Dict[str, Any]:
        """Estadísticas del almacén"""
        categories = {}
        for meta in self.metadata.values():
            cat = meta.get("category", "sin_categoria")
            categories[cat] = categories.get(cat, 0) + 1
            
        return {
            "total_vectors": len(self.store),
            "backend": "in-memory + json-persistent",
            "categories": categories,
            "persist_file": str(self.persist_path),
        }


# Singleton
vector_store = VectorStore()