"""
Servicio de recuperación de información para RAG (Retrieval-Augmented Generation)
"""

from typing import Any, Dict, List, Optional
import structlog

from app.rag.embeddings import embedding_generator
from app.rag.vector_store import vector_store
from app.rag.knowledge_base import KNOWLEDGE_DOCUMENTS

logger = structlog.get_logger(__name__)


class RetrievalService:
    """
    Servicio integral de recuperación de información contextual.
    
    Flujo RAG:
    1. Asegurar indexación de la base de conocimiento institucional (Planes, TAMN, SUNAT, Pagos).
    2. Generar embedding vectorial de la consulta del usuario.
    3. Buscar documentos más relevantes en el Vector Store (con fallback léxico).
    4. Formatear el contexto recuperado para enriquecer prompts de LLMs.
    """
    
    def __init__(self):
        self.embedding_generator = embedding_generator
        self.vector_store = vector_store
        self._is_initialized = False

    async def initialize_knowledge_base(self, force_reindex: bool = False) -> int:
        """
        Indexa automáticamente todos los documentos de la base de conocimiento institucional.
        
        Args:
            force_reindex: Si es True, re-genera los embeddings aunque ya existan.
            
        Returns:
            Cantidad de documentos indexados
        """
        indexed_count = 0
        current_stats = await self.vector_store.get_stats()
        
        for doc in KNOWLEDGE_DOCUMENTS:
            doc_id = doc["id"]
            
            # Si ya está indexado y no se fuerza reindexación, solo verificar metadatos
            if doc_id in self.vector_store.store and not force_reindex:
                continue
            
            content_to_embed = f"{doc['title']}. {doc['content']}"
            try:
                embedding = await self.embedding_generator.generate_embedding(content_to_embed)
                metadata = {
                    "title": doc["title"],
                    "category": doc["category"],
                    "content": doc["content"],
                    **doc.get("metadata", {})
                }
                await self.vector_store.add_vector(doc_id, embedding, metadata, persist=False)
                indexed_count += 1
            except Exception as e:
                logger.warning(f"⚠️ Error generando embedding para {doc_id}, guardando con vector sintético: {e}")
                # En caso de no tener API key activa de embeddings, indexar con vector normalizado simulado
                # para que el fallback léxico/híbrido funcione sin interrupción
                synth_vector = [0.01 * (i % 10) for i in range(128)]
                metadata = {
                    "title": doc["title"],
                    "category": doc["category"],
                    "content": doc["content"],
                    **doc.get("metadata", {})
                }
                await self.vector_store.add_vector(doc_id, synth_vector, metadata, persist=False)
                indexed_count += 1
        
        if indexed_count > 0:
            self.vector_store.save_to_disk()
            logger.info(f"📚 Base de conocimiento RAG inicializada: {indexed_count} documentos actualizados")
        
        self._is_initialized = True
        return indexed_count
    
    async def index_document(
        self,
        doc_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Indexa un documento dinámico adicional en el Vector Store.
        """
        metadata = metadata or {}
        try:
            embedding = await self.embedding_generator.generate_embedding(content)
        except Exception as e:
            logger.warning(f"⚠️ Fallo en embedding de {doc_id}: {e}")
            embedding = [0.01 * (i % 10) for i in range(128)]
            
        full_metadata = {"content": content, **metadata}
        await self.vector_store.add_vector(doc_id, embedding, full_metadata, persist=True)
        logger.info(f"📄 Documento dinámico indexado: {doc_id}")
    
    async def retrieve_context(
        self,
        query: str,
        top_k: int = 4,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Recupera los documentos más relevantes para una consulta.
        
        Args:
            query: Consulta o pregunta del usuario
            top_k: Número de fragmentos a recuperar
            category: Categoría opcional (e.g. 'planes_servicios', 'politicas_cobranza')
            
        Returns:
            Lista de documentos relevantes con scores y contenido
        """
        if not self._is_initialized or len(self.vector_store.store) == 0:
            await self.initialize_knowledge_base()
        
        # 1. Intentar búsqueda semántica vectorial
        results = []
        try:
            query_embedding = await self.embedding_generator.generate_embedding(query)
            results = await self.vector_store.search_similar(
                query_vector=query_embedding,
                top_k=top_k,
                filter_category=category
            )
        except Exception as e:
            logger.debug(f"ℹ️ Fallback a búsqueda léxica RAG: {e}")
        
        # 2. Si no hay resultados o la similitud fue baja, complementar con búsqueda léxica
        if not results or (results and results[0]["score"] < 0.1):
            keyword_results = await self.vector_store.search_by_keywords(query, top_k=top_k)
            if keyword_results:
                results = keyword_results
        
        logger.info(f"🔍 RAG: Recuperados {len(results)} fragmentos de conocimiento para query='{query[:40]}...'")
        return results
    
    async def format_context_for_llm(
        self,
        query: str,
        top_k: int = 3,
        category: Optional[str] = None,
    ) -> str:
        """
        Formatea el contexto recuperado en un bloque de texto claro para inyectar en el prompt del LLM.
        """
        results = await self.retrieve_context(query, top_k, category)
        
        if not results:
            return "No se encontró documentación específica en la base de conocimiento."
        
        context_lines = ["--- BASE DE CONOCIMIENTO INSTITUCIONAL (SON-IA / INTEGRATEL) ---"]
        
        for i, result in enumerate(results, 1):
            meta = result.get("metadata", {})
            title = meta.get("title", meta.get("id", f"Documento #{i}"))
            content = meta.get("content", "")
            score = result.get("score", 0.0)
            
            context_lines.append(f"\n[{i}] {title} (Relevancia: {score:.2f})")
            context_lines.append(content)
        
        context_lines.append("\n-------------------------------------------------------------")
        return "\n".join(context_lines)


# Singleton
retrieval_service = RetrievalService()