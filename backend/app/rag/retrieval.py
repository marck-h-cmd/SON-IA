"""
Servicio de recuperación de información para RAG
"""

import structlog
from typing import List, Dict, Any

from app.rag.embeddings import embedding_generator
from app.rag.vector_store import vector_store

logger = structlog.get_logger(__name__)


class RetrievalService:
    """
    Servicio de recuperación de información contextual.
    
    Flujo RAG:
    1. Generar embedding de la consulta
    2. Buscar documentos similares en Vector Store
    3. Retornar contexto relevante para el LLM
    """
    
    def __init__(self):
        self.embedding_generator = embedding_generator
        self.vector_store = vector_store
    
    async def index_document(
        self,
        doc_id: str,
        content: str,
        metadata: Dict[str, Any] = {},
    ) -> None:
        """
        Indexa un documento en el Vector Store.
        
        Args:
            doc_id: Identificador del documento
            content: Contenido del documento
            metadata: Metadatos (tipo, fecha, cliente_id, etc.)
        """
        embedding = await self.embedding_generator.generate_embedding(content)
        await self.vector_store.add_vector(doc_id, embedding, metadata)
        logger.info(f"📄 Documento indexado: {doc_id}")
    
    async def retrieve_context(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Recupera contexto relevante para una consulta.
        
        Args:
            query: Consulta del usuario
            top_k: Número de documentos a recuperar
            
        Returns:
            Lista de documentos relevantes con scores
        """
        # 1. Generar embedding de la consulta
        query_embedding = await self.embedding_generator.generate_embedding(query)
        
        # 2. Buscar documentos similares
        results = await self.vector_store.search_similar(query_embedding, top_k)
        
        logger.info(f"🔍 Recuperados {len(results)} documentos para query")
        
        return results
    
    async def format_context_for_llm(
        self,
        query: str,
        top_k: int = 3,
    ) -> str:
        """
        Formatea el contexto recuperado para incluirlo en el prompt del LLM.
        
        Args:
            query: Consulta del usuario
            top_k: Número de documentos
            
        Returns:
            String con contexto formateado
        """
        results = await self.retrieve_context(query, top_k)
        
        if not results:
            return "No se encontró información relevante."
        
        context_parts = ["Información relevante encontrada:\n"]
        
        for i, result in enumerate(results, 1):
            meta = result.get("metadata", {})
            context_parts.append(
                f"{i}. {meta.get('titulo', 'Documento sin título')} "
                f"(relevancia: {result['score']:.2f})"
            )
        
        return "\n".join(context_parts)


# Singleton
retrieval_service = RetrievalService()