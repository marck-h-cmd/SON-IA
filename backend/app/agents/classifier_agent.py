"""
Agente de Clasificación de Comunicaciones
Modelo: Gemini 1.5 Flash
Rol: Clasificar mensajes entrantes y enrutarlos
"""

from typing import Any, Dict, List, Optional
from enum import Enum
import structlog
import time

from app.agents.base_agent import BaseAgent

logger = structlog.get_logger(__name__)


class MessageCategory(str, Enum):
    """Categorías de mensajes de clientes"""
    PAYMENT = "pago"
    CLAIM = "reclamo"
    INQUIRY = "consulta"
    CANCELLATION = "cancelacion"
    COMPLAINT = "queja"
    OTHER = "otro"


class ClassifierAgent(BaseAgent):
    """
    Agente de Clasificación de Comunicaciones
    
    Procesa mensajes de clientes (correos, WhatsApp, llamadas)
    y los clasifica para enrutar al agente correspondiente.
    
    Modelo: Gemini 1.5 Flash (rápido, bajo costo, excelente clasificación)
    """
    
    def __init__(self):
        super().__init__(
            name="Classifier Agent",
            model="gemini-1.5-flash",
            version="1.0.0"
        )
        self.routing_rules = {
            MessageCategory.PAYMENT: "collections_agent",
            MessageCategory.CLAIM: "customer_agent",
            MessageCategory.INQUIRY: "customer_agent",
            MessageCategory.CANCELLATION: "supervisor_agent",
            MessageCategory.COMPLAINT: "supervisor_agent",
            MessageCategory.OTHER: "customer_agent",
        }
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clasifica un mensaje entrante.
        
        Args:
            task: {
                "type": "classify_message",
                "message": "Quiero pagar mi factura 4001",
                "canal": "whatsapp" | "email" | "llamada",
                "cliente_id": 1001
            }
        """
        start_time = time.time()
        
        try:
            mensaje = task.get("message", "")
            canal = task.get("canal", "email")
            cliente_id = task.get("cliente_id")
            
            logger.info(f"🏷️ Classifier: Clasificando mensaje de cliente {cliente_id}")
            
            # Clasificar mensaje (simulación - en producción usaría Gemini Flash)
            categoria = self._classify_message(mensaje)
            
            # Extraer entidades clave
            entidades = self._extract_entities(mensaje)
            
            # Determinar agente destino
            agente_destino = self.routing_rules.get(categoria, "customer_agent")
            
            execution_time = (time.time() - start_time) * 1000
            
            result = {
                "status": "success",
                "categoria": categoria.value,
                "confianza_clasificacion": 0.95,
                "entidades": entidades,
                "agente_destino": agente_destino,
                "canal": canal,
                "execution_time_ms": execution_time,
            }
            
            await self.log_execution(task, result)
            return result
            
        except Exception as e:
            return await self.handle_error(e, task)
    
    def _classify_message(self, message: str) -> MessageCategory:
        """
        Clasifica un mensaje según su contenido.
        
        En producción, esto usaría Gemini Flash API.
        Para MVP, usamos reglas simples.
        """
        message_lower = message.lower()
        
        # Palabras clave por categoría
        keywords = {
            MessageCategory.PAYMENT: ["pagar", "pago", "factura", "cancelar deuda", "abonar"],
            MessageCategory.CLAIM: ["reclamo", "queja", "mal servicio", "no funciona"],
            MessageCategory.INQUIRY: ["consulta", "duda", "pregunta", "información", "cómo"],
            MessageCategory.CANCELLATION: ["cancelar", "dar de baja", "terminar contrato"],
            MessageCategory.COMPLAINT: ["queja formal", "supervisor", "gerente"],
        }
        
        # Contar coincidencias
        scores = {}
        for category, words in keywords.items():
            score = sum(1 for word in words if word in message_lower)
            scores[category] = score
        
        # Categoría con mayor score
        best_category = max(scores, key=scores.get)
        
        if scores[best_category] == 0:
            return MessageCategory.OTHER
        
        logger.debug(f"Clasificación: {best_category.value} (score: {scores[best_category]})")
        return best_category
    
    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """
        Extrae entidades clave del mensaje (número de factura, monto, etc.)
        
        En producción usaría Gemini Flash para NER.
        """
        import re
        
        entidades = {}
        
        # Buscar número de factura (4 dígitos)
        factura_match = re.search(r'factura\s*#?\s*(\d{4})', message, re.IGNORECASE)
        if factura_match:
            entidades["factura_id"] = int(factura_match.group(1))
        
        # Buscar montos (S/ XXXX.XX)
        monto_match = re.search(r'S/\s*(\d+\.?\d*)', message, re.IGNORECASE)
        if monto_match:
            entidades["monto"] = float(monto_match.group(1))
        
        return entidades


# Singleton
classifier_agent = ClassifierAgent()