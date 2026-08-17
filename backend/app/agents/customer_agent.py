"""
Agente de Atención y Explicación Contextual (Customer Success AI)
Modelo: Gemini 1.5 Pro / LLM Híbrido + RAG
Rol: Traducir complejidad técnica y normativa a lenguaje natural
"""

import time
from typing import Any, Dict, List, Optional
import structlog

from app.agents.base_agent import BaseAgent
from app.rag.retrieval import retrieval_service
from app.integrations.gemini_client import gemini_client
from app.integrations.llm_client import MainLLMClient

logger = structlog.get_logger(__name__)


class CustomerAgent(BaseAgent):
    """
    Agente de Atención y Explicación al Cliente (SON-IA).
    
    Responsabilidades:
    1. Responder preguntas sobre planes, tarifas, servicios y normativas usando RAG.
    2. Explicar el desglose de facturas (PxQ, IGV 18%, cargos prorrateados).
    3. Explicar intereses TAMN, fechas de corte y métodos de pago oficiales.
    4. Generar respuestas en lenguaje natural cordiales, precisas y sin alucinaciones.
    """
    
    def __init__(self):
        super().__init__(
            name="Customer Success Agent",
            model="gemini-1.5-pro + RAG",
            version="2.0.0"
        )
        self.retrieval_service = retrieval_service
        self.gemini = gemini_client
        self.main_llm = MainLLMClient()
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa una consulta del cliente con contexto RAG.
        
        Args:
            task: {
                "type": "answer_question" | "explain_invoice" | "explain_tamn" | "general_query",
                "pregunta": "¿Qué incluye el Plan Elige Todo?",
                "cliente_id": 1001,
                "cliente_nombre": "Empresa SAC",
                "factura": {...}  # Opcional
            }
        """
        start_time = time.time()
        task_type = task.get("type", "answer_question")
        
        try:
            if task_type == "explain_invoice":
                result = await self._explain_invoice(task)
            elif task_type == "explain_tamn":
                result = await self._explain_tamn(task)
            elif task_type == "answer_question":
                result = await self._answer_question(task)
            else:
                result = await self._handle_general_query(task)
            
            execution_time = (time.time() - start_time) * 1000
            result["execution_time_ms"] = execution_time
            
            await self.log_execution(task, result)
            return result
            
        except Exception as e:
            return await self.handle_error(e, task)
    
    async def _answer_question(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Responde una pregunta general sobre servicios o normativas usando RAG contextual.
        """
        pregunta = task.get("pregunta", "").strip()
        cliente_nombre = task.get("cliente_nombre", "Cliente")
        
        logger.info("💬 Customer Agent: Consultando RAG", pregunta=pregunta)
        
        # 1. Recuperar contexto RAG relevante
        rag_context = await self.retrieval_service.format_context_for_llm(pregunta, top_k=3)
        
        # 2. Generar respuesta con LLM o síntesis contextual
        system_prompt = (
            "Eres un asesor de atención al cliente humano, cálido, empático y muy profesional de Movistar Empresas / Integratel Perú. "
            "Responde en español de forma natural, amigable y conversacional (ideal para WhatsApp, usando emojis oportunos y buena claridad). "
            "NUNCA menciones que eres una IA, un bot, un asistente virtual, ni hagas referencia a metadatos, RAG, bases de datos o algoritmos. "
            "Brinda siempre respuestas claras, útiles y transparentes basadas en los planes y servicios de la empresa."
        )
        
        user_prompt = (
            f"Información de servicios y políticas:\n{rag_context}\n\n"
            f"Consulta del cliente: '{pregunta}'\n\n"
            f"Redacta una respuesta amable, directa y profesional para responderle por WhatsApp."
        )
        
        respuesta_texto = ""
        fuente_usada = "rag_contextual"
        
        # Intentar con Gemini
        try:
            gemini_res = await self.gemini.generate_content(f"{system_prompt}\n\n{user_prompt}")
            if gemini_res and len(gemini_res.strip()) > 10:
                respuesta_texto = gemini_res.strip()
                fuente_usada = "gemini-1.5-pro + RAG"
        except Exception as e:
            logger.debug(f"ℹ️ Gemini no disponible, intentando MainLLM: {e}")
        
        # Fallback a MainLLM (Groq)
        if not respuesta_texto:
            try:
                llm_res = await self.main_llm.generate_text(user_prompt, system_prompt=system_prompt, max_tokens=500)
                choices = llm_res.get("choices", [])
                if choices:
                    respuesta_texto = choices[0].get("message", {}).get("content", "").strip()
                    fuente_usada = "llama-3.3 + RAG"
            except Exception as e:
                logger.debug(f"ℹ️ MainLLM no disponible, usando formateador determinista RAG: {e}")
        
        # Fallback determinista seguro
        if not respuesta_texto:
            rag_docs = await self.retrieval_service.retrieve_context(pregunta, top_k=2)
            if rag_docs:
                top_doc = rag_docs[0].get("metadata", {})
                saludo = f"¡Hola {cliente_nombre}! 😊 " if cliente_nombre else "¡Hola! 😊 "
                respuesta_texto = (
                    f"{saludo}Con gusto te brindamos la información sobre tu consulta:\n\n"
                    f"📌 *{top_doc.get('title', 'Detalle')}*:\n"
                    f"{top_doc.get('content', '')}\n\n"
                    f"¿Deseas que te ayudemos con alguna duda adicional o con la contratación de este servicio?"
                )
            else:
                saludo = f"¡Hola {cliente_nombre}! 😊 " if cliente_nombre else "¡Hola! 😊 "
                respuesta_texto = (
                    f"{saludo}Con gusto te ayudamos con información sobre tus recibos, "
                    f"planes de fibra óptica, servicios móviles o facilidades de pago. "
                    f"¿En qué te podemos colaborar hoy?"
                )
            fuente_usada = "motor_simbolico_rag"
        
        return {
            "status": "success",
            "pregunta": pregunta,
            "respuesta": respuesta_texto,
            "fuente": fuente_usada,
            "rag_context_length": len(rag_context),
        }
    
    async def _explain_invoice(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Explica el desglose numérico de una factura en lenguaje claro y sin alucinaciones.
        """
        factura = task.get("factura", {})
        factura_id = task.get("factura_id") or factura.get("nro_doc_fiscal", "N/A")
        monto_total = float(factura.get("charge_total_amount") or factura.get("monto_total") or 0.0)
        subtotal = monto_total / 1.18 if monto_total > 0 else 0.0
        igv = monto_total - subtotal
        
        explicacion = (
            f"📄 *Detalle de tu Recibo #{factura_id}*:\n\n"
            f"• Base del plan (Subtotal): S/ {subtotal:,.2f}\n"
            f"• IGV (18%): S/ {igv:,.2f}\n"
            f"• *Total a pagar*: *S/ {monto_total:,.2f}*\n\n"
            f"Este monto corresponde al ciclo regular de tus servicios contratados. "
            f"Puedes realizar el pago por Yape o desde la app/web de tu banco. ¿Tienes alguna duda puntual sobre tus consumos?"
        )
        
        return {
            "status": "success",
            "factura_id": factura_id,
            "respuesta": explicacion,
            "fuente": "zero_hallucination_engine",
        }
    
    async def _explain_tamn(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Explica de forma transparente el cálculo de intereses moratorios TAMN.
        """
        dias_vencido = task.get("dias_vencido", 0)
        monto_original = float(task.get("monto_original", 0.0))
        monto_interes = float(task.get("monto_interes", 0.0))
        total = monto_original + monto_interes
        
        explicacion = (
            f"⚠️ *Detalle de tu saldo e intereses de mora*:\n\n"
            f"• Saldo original vencido: S/ {monto_original:,.2f}\n"
            f"• Días transcurridos: {dias_vencido} días\n"
            f"• Recargo por mora acumulado: S/ {monto_interes:,.2f}\n"
            f"• *Total actualizado*: *S/ {total:,.2f}*\n\n"
            f"💡 *Te recomendamos*: Si regularizas hoy, puedes acceder a un descuento por pronto pago o fraccionar tu saldo para evitar recargos de reconexión. ¿Deseas ver las opciones?"
        )
        
        return {
            "status": "success",
            "respuesta": explicacion,
            "fuente": "tamn_engine",
        }
    
    async def _handle_general_query(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Menú de asistencia general para clientes"""
        cliente_nombre = task.get("cliente_nombre", "")
        saludo = f"¡Hola {cliente_nombre}! 😊 " if cliente_nombre else "¡Hola! 😊 "
        
        respuesta = (
            f"{saludo}Te damos la bienvenida a Movistar Empresas. ¿En qué te podemos ayudar hoy?\n\n"
            f"• Consultar tu saldo o fecha de vencimiento\n"
            f"• Explicación de consumos o detalle de tu recibo\n"
            f"• Facilidades y acuerdos especiales de pago\n"
            f"• Planes de Fibra Óptica, Voz y Móvil para empresas"
        )
        
        return {
            "status": "success",
            "respuesta": respuesta,
        }


# Singleton
customer_agent = CustomerAgent()