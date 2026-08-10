"""
Agente de Atención y Explicación (Customer Success AI)
Modelo: Gemini 1.5 Pro
Rol: Traducir complejidad técnica a lenguaje natural
"""

from typing import Any, Dict, List, Optional
import structlog
import time

from app.agents.base_agent import BaseAgent

logger = structlog.get_logger(__name__)


class CustomerAgent(BaseAgent):
    """
    Agente de Atención al Cliente
    
    Responsable de:
    1. Explicar facturas en lenguaje natural
    2. Responder consultas vía chat contextual
    3. Utilizar RAG para recuperar historial del cliente
    
    Modelo: Gemini 1.5 Pro (NLP, generación de texto, RAG)
    """
    
    def __init__(self):
        super().__init__(
            name="Customer Success Agent",
            model="gemini-1.5-pro",
            version="1.0.0"
        )
        self.greeting_messages = [
            "¡Hola! Soy el asistente virtual de SON-IA. ¿En qué puedo ayudarte?",
            "Puedo explicarte tu factura, ayudarte con tus pagos o resolver tus dudas.",
        ]
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa una consulta del cliente.
        
        Args:
            task: {
                "type": "explain_invoice" | "answer_question",
                "cliente_id": 1001,
                "factura_id": 4001,
                "pregunta": "¿Por qué pagué más este mes?"
            }
        """
        start_time = time.time()
        task_type = task.get("type", "")
        
        try:
            if task_type == "explain_invoice":
                result = await self._explain_invoice(task)
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
    
    async def _explain_invoice(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Explica una factura en lenguaje natural.
        
        Usa RAG para recuperar información contextual del cliente.
        """
        factura_id = task.get("factura_id")
        cliente_id = task.get("cliente_id")
        
        logger.info(f"💬 Customer Agent: Explicando factura {factura_id}")
        
        # Simulación de respuesta - En producción usaría Gemini + RAG
        explicacion = (
            f"Hola, gracias por tu consulta sobre la factura #{factura_id}. "
            f"Este mes tu factura incluye los siguientes conceptos:\n\n"
            f"1. Servicio de Fibra Óptica: S/ 2,500.00 (mes completo)\n"
            f"2. Servicio Cloud: S/ 1,800.00 (mes completo)\n\n"
            f"Subtotal: S/ 3,644.07\n"
            f"IGV (18%): S/ 655.93\n"
            f"Total: S/ 4,300.00\n\n"
            f"El monto es el mismo que el mes anterior porque no hubo cambios en tus servicios. "
            f"¿Hay algo más en lo que pueda ayudarte?"
        )
        
        return {
            "status": "success",
            "factura_id": factura_id,
            "respuesta": explicacion,
            "fuente": "gemini-1.5-pro + RAG",
        }
    
    async def _answer_question(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Responde una pregunta específica del cliente usando RAG.
        """
        pregunta = task.get("pregunta", "")
        
        logger.info(f"❓ Customer Agent: Respondiendo pregunta: {pregunta}")
        
        # Simulación - En producción usaría Gemini para generar respuesta contextual
        respuesta = (
            f"Entiendo tu consulta sobre '{pregunta}'. "
            f"Revisando tu historial, veo que el cargo adicional corresponde "
            f"al prorrateo por la activación de un nuevo servicio a mitad de mes. "
            f"Este cargo es proporcional a los días de uso, como indica la normativa SUNAT."
        )
        
        return {
            "status": "success",
            "pregunta": pregunta,
            "respuesta": respuesta,
        }
    
    async def _handle_general_query(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Maneja consultas generales no categorizadas"""
        return {
            "status": "success",
            "respuesta": (
                "¡Gracias por contactarnos! Puedo ayudarte con:\n"
                "- Explicar tu factura\n"
                "- Información de pagos\n"
                "- Ofertas y descuentos\n"
                "- Actualizar tus datos\n\n"
                "¿Qué te gustaría hacer?"
            ),
        }
    
    def get_welcome_message(self, cliente_nombre: str = "") -> str:
        """Genera mensaje de bienvenida personalizado"""
        if cliente_nombre:
            return f"¡Hola {cliente_nombre}! Soy el asistente de SON-IA. ¿En qué puedo ayudarte hoy?"
        return self.greeting_messages[0]


# Singleton
customer_agent = CustomerAgent()