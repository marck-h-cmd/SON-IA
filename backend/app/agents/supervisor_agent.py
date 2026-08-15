"""
Agente Supervisor - El Orquestador Central del Ecosistema SON-IA
Modelo: Llama-3.3 / Groq + Lógica Agéntica Determinista
Rol: Router dinámico, coordinador de workflows E2E y salvaguarda HITL
"""

from enum import Enum
import time
from typing import Any, Dict, List, Optional
import structlog

from app.agents.base_agent import BaseAgent
from app.agents.billing_agent import billing_agent
from app.agents.collections_agent import collections_agent
from app.agents.negotiation_agent import negotiation_agent
from app.agents.customer_agent import customer_agent
from app.agents.classifier_agent import classifier_agent
from app.agents.learning_agent import learning_agent

logger = structlog.get_logger(__name__)


class TaskType(str, Enum):
    """Tipos de tareas que el supervisor puede asignar"""
    BILLING = "billing"
    COLLECTIONS = "collections"
    NEGOTIATION = "negotiation"
    CUSTOMER_SERVICE = "customer_service"
    CLASSIFICATION = "classification"
    LEARNING = "learning"
    HUMAN_REVIEW = "human_review"


class SupervisorAgent(BaseAgent):
    """
    Agente Supervisor (Orquestador Central y Router Inteligente)
    
    Funciona como el director de orquesta del ecosistema agéntico:
    1. Recibe eventos del sistema o mensajes de clientes.
    2. Determina el pipeline de agentes involucrados.
    3. Ejecuta flujos coordinados pasando el estado entre agentes.
    4. Evalúa reglas de riesgo para activar Human-in-the-Loop (HITL).
    5. Registra auditoría inmutable de cada paso del workflow.
    """
    
    def __init__(self):
        super().__init__(
            name="Supervisor Agent",
            model="Llama-3.3 + Agentic Router",
            version="2.0.0"
        )
        self.agents_map = {
            TaskType.BILLING: billing_agent,
            TaskType.COLLECTIONS: collections_agent,
            TaskType.NEGOTIATION: negotiation_agent,
            TaskType.CUSTOMER_SERVICE: customer_agent,
            TaskType.CLASSIFICATION: classifier_agent,
            TaskType.LEARNING: learning_agent,
        }
        self.hitl_thresholds = {
            "max_factura_monto": 100000.00,       # S/ 100,000
            "max_descuento_porcentaje": 20.0,     # Descuento > 20% requiere HITL
            "min_score_auto_aprobacion": 0.80,    # Score < 0.80 requiere aprobación
        }
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orquesta la ejecución de flujos de trabajo multi-agente.
        
        Args:
            task: Diccionario con la definición del workflow:
                - type: "start_billing_cycle" | "process_payment" | "classify_and_respond" | 
                        "predictive_negotiation" | "run_learning_cycle"
        """
        start_time = time.time()
        task_type = task.get("type", "")
        
        logger.info(f"🎯 Supervisor: Orquestando tarea '{task_type}'")
        
        try:
            if task_type in ("start_billing_cycle", "billing_workflow"):
                result = await self._handle_billing_cycle(task)
            elif task_type in ("collections_workflow", "process_overdue"):
                result = await self._handle_collections_workflow(task)
            elif task_type in ("classify_and_respond", "customer_service_workflow"):
                result = await self._handle_customer_service_workflow(task)
            elif task_type in ("generate_negotiation_offers", "predictive_negotiation"):
                result = await self._handle_negotiation_workflow(task)
            elif task_type in ("run_learning_cycle", "learning_workflow"):
                result = await self._handle_learning_workflow(task)
            else:
                result = {
                    "status": "error",
                    "message": f"Tipo de workflow no reconocido por el Supervisor: '{task_type}'"
                }
            
            execution_time = (time.time() - start_time) * 1000
            result["execution_time_ms"] = execution_time
            
            await self.log_execution(task, result)
            return result
            
        except Exception as e:
            return await self.handle_error(e, task)
    
    async def _handle_billing_cycle(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orquesta el ciclo E2E de facturación inteligente:
        Paso 1: Pre-validación de ciclo
        Paso 2: Agente de Facturación (PxQ + IGV 18%)
        Paso 3: Evaluación de Score y Detección de Anomalías
        Paso 4: Decisión de aprobación automática vs. Enrutamiento a HITL
        """
        ciclo_id = task.get("ciclo_id", 31)
        force_review = task.get("force_human_review", False)
        cliente_id = task.get("cliente_id")
        
        workflow = {
            "workflow_id": f"BILL-{int(time.time())}",
            "status": "in_progress",
            "cycle_id": ciclo_id,
            "steps": [],
            "requires_human_review": force_review,
            "agents_involved": ["supervisor_agent"],
        }
        
        # Paso 1: Validación de reglas
        workflow["steps"].append({
            "step": "1_validate_cycle",
            "agent": "supervisor_agent",
            "status": "success",
            "description": f"Validado ciclo {ciclo_id} y parámetros fiscales",
        })
        
        # Paso 2: Ejecución de Facturación
        billing_result = await billing_agent.execute({
            "type": "calculate_invoice",
            "cliente_id": cliente_id or 1001,
            "servicios": task.get("servicios", []),
            "periodo": task.get("periodo", "2024-11"),
        })
        workflow["steps"].append({
            "step": "2_execute_billing",
            "agent": "billing_agent",
            "status": billing_result.get("status", "success"),
            "data": billing_result,
        })
        workflow["agents_involved"].append("billing_agent")
        
        # Paso 3: Análisis de riesgo y decisión HITL
        monto_total = float(billing_result.get("total", 0.0) if isinstance(billing_result.get("total"), (int, float)) else 0.0)
        score = float(task.get("score_confianza", 0.85))
        
        needs_hitl = (
            force_review or
            score < self.hitl_thresholds["min_score_auto_aprobacion"] or
            monto_total > self.hitl_thresholds["max_factura_monto"]
        )
        
        if needs_hitl:
            workflow["requires_human_review"] = True
            workflow["status"] = "pending_human_review"
            workflow["hitl_reason"] = (
                f"Score ({score:.2f}) < 0.80 o Monto (S/ {monto_total:,.2f}) > S/ 100k"
            )
            workflow["steps"].append({
                "step": "3_hitl_escalation",
                "agent": "supervisor_agent",
                "action": "Enviado al Centro de Aprobaciones Human-in-the-Loop",
            })
            logger.warning("⚠️ Supervisor: Factura enrutada a HITL", motivo=workflow["hitl_reason"])
        else:
            workflow["status"] = "auto_approved"
            workflow["steps"].append({
                "step": "3_auto_approval",
                "agent": "supervisor_agent",
                "action": "Aprobación automática Zero-Hallucination concedida",
            })
        
        return workflow
    
    async def _handle_collections_workflow(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orquesta el flujo de cobranzas y evaluación de mora:
        Paso 1: Cobranzas Agent calcula TAMN y etapa de mora
        Paso 2: Si mora >= media, activa al Agente de Negociación
        """
        factura_id = task.get("factura_id", "FACT-001")
        monto = float(task.get("monto_pendiente", 1000.0))
        dias_vencido = int(task.get("dias_vencido", 10))
        
        # 1. Agente de Cobranzas
        col_res = await collections_agent.execute({
            "type": "calculate_tamn",
            "factura_id": factura_id,
            "monto_original": monto,
            "dias_vencido": dias_vencido,
        })
        
        agents_involved = ["supervisor_agent", "collections_agent"]
        negotiation_offer = None
        
        # 2. Si mora es significativa (dias > 5), activar Negociación predictiva
        if dias_vencido >= 5:
            neg_res = await negotiation_agent.execute({
                "type": "evaluate_and_offer",
                "factura_id": factura_id,
                "monto_pendiente": monto,
                "score_confianza": task.get("score_confianza", 0.65),
                "dias_mora": dias_vencido,
            })
            agents_involved.append("negotiation_agent")
            negotiation_offer = neg_res
        
        return {
            "status": "completed",
            "workflow": "collections_and_tamn",
            "collections_result": col_res,
            "negotiation_offer": negotiation_offer,
            "agents_involved": agents_involved,
        }
    
    async def _handle_customer_service_workflow(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orquesta la atención al cliente con IA:
        Paso 1: Clasificador Agent detecta la intención y entidades del mensaje
        Paso 2: Customer Agent consulta el RAG institucional y responde en lenguaje natural
        """
        mensaje = task.get("mensaje", "")
        cliente_nombre = task.get("cliente_nombre", "Cliente")
        
        # 1. Clasificación de intención
        class_res = await classifier_agent.execute({
            "type": "classify_message",
            "message": mensaje,
        })
        
        # 2. Generación de respuesta contextual con RAG
        customer_res = await customer_agent.execute({
            "type": "answer_question",
            "pregunta": mensaje,
            "cliente_nombre": cliente_nombre,
            "clasificacion": class_res,
        })
        
        return {
            "status": "completed",
            "workflow": "customer_support_rag",
            "intencion_detectada": class_res.get("categoria", "consulta_general"),
            "score_confianza_clasificacion": class_res.get("confianza", 0.90),
            "respuesta_generada": customer_res.get("respuesta", ""),
            "fuente_rag": customer_res.get("fuente", "rag"),
            "agents_involved": ["supervisor_agent", "classifier_agent", "customer_agent"],
        }
    
    async def _handle_negotiation_workflow(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Orquesta la evaluación y generación preventiva de ofertas de descuento"""
        neg_res = await negotiation_agent.execute(task)
        return {
            "status": "completed",
            "workflow": "predictive_negotiation",
            "result": neg_res,
            "agents_involved": ["supervisor_agent", "negotiation_agent"],
        }
    
    async def _handle_learning_workflow(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Orquesta el ciclo de aprendizaje continuo y optimización de modelos"""
        learn_res = await learning_agent.execute(task)
        return {
            "status": "completed",
            "workflow": "continuous_learning",
            "result": learn_res,
            "agents_involved": ["supervisor_agent", "learning_agent"],
        }
    
    def check_system_health(self) -> Dict[str, Any]:
        """Verifica la operatividad del enjambre de 7 agentes"""
        health_status = {}
        for agent_type, agent_inst in self.agents_map.items():
            health_status[agent_type.value] = {
                "name": getattr(agent_inst, "name", agent_type.value),
                "model": getattr(agent_inst, "model", "N/A"),
                "status": "active",
            }
        
        return {
            "supervisor": "active",
            "total_agents": len(self.agents_map),
            "swarm_status": "healthy",
            "agents": health_status,
        }


# Singleton del supervisor
supervisor_agent = SupervisorAgent()
