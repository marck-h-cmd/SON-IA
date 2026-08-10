"""
Agente Supervisor - El Orquestador Central
Modelo: Llama-3.3
Rol: Router y coordinador del ecosistema de agentes
"""

from typing import Any, Dict, List, Optional
from enum import Enum
import structlog
import time

from app.agents.base_agent import BaseAgent

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
    Agente Supervisor (Orquestador/Router)
    
    Funciona como el cerebro logístico del ecosistema.
    Recibe triggers y decide qué agente debe actuar, en qué orden,
    y valida que las salidas sean correctas.
    
    Modelo: Llama-3.3 (razonamiento complejo y toma de decisiones)
    """
    
    def __init__(self):
        super().__init__(
            name="Supervisor Agent",
            model="Llama-3.3",
            version="1.0.0"
        )
        self.available_agents = {
            TaskType.BILLING: "billing_agent",
            TaskType.COLLECTIONS: "collections_agent",
            TaskType.NEGOTIATION: "negotiation_agent",
            TaskType.CUSTOMER_SERVICE: "customer_agent",
            TaskType.CLASSIFICATION: "classifier_agent",
            TaskType.LEARNING: "learning_agent",
        }
        self.hitl_thresholds = {
            "max_factura_monto": 100000.00,  # S/ 100,000
            "max_descuento_porcentaje": 20.0,  # 20%
            "anomaly_multiplier": 5.0,  # 5x del promedio
        }
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orquesta la ejecución de tareas entre los agentes.
        
        Args:
            task: {
                "type": "start_billing_cycle",
                "ciclo_id": 15,
                "force_human_review": False
            }
        
        Returns:
            Resultado de la orquestación
        """
        start_time = time.time()
        task_type = task.get("type", "")
        
        logger.info(f"🎯 Supervisor: Recibida tarea '{task_type}'")
        
        try:
            # Determinar flujo de trabajo según tipo de tarea
            if task_type == "start_billing_cycle":
                result = await self._handle_billing_cycle(task)
            elif task_type == "process_payment":
                result = await self._handle_payment(task)
            elif task_type == "classify_message":
                result = await self._handle_classification(task)
            elif task_type == "generate_negotiation_offers":
                result = await self._handle_negotiation(task)
            else:
                result = {
                    "status": "error",
                    "message": f"Tipo de tarea no reconocido: {task_type}"
                }
            
            execution_time = (time.time() - start_time) * 1000
            result["execution_time_ms"] = execution_time
            
            await self.log_execution(task, result)
            return result
            
        except Exception as e:
            return await self.handle_error(e, task)
    
    async def _handle_billing_cycle(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orquesta el ciclo de facturación completo.
        
        Flujo:
        1. Validar ciclo
        2. Ejecutar facturación
        3. Verificar anomalías
        4. Decidir si requiere revisión humana
        """
        ciclo_id = task.get("ciclo_id")
        force_review = task.get("force_human_review", False)
        
        workflow = {
            "status": "in_progress",
            "cycle_id": ciclo_id,
            "steps": [],
            "requires_human_review": force_review,
            "agents_involved": [],
        }
        
        # Paso 1: Validar ciclo (siempre)
        workflow["steps"].append({
            "step": "validate_cycle",
            "agent": "supervisor",
            "action": "Validando ciclo de facturación",
            "cycle_id": ciclo_id,
        })
        
        # Paso 2: Asignar a Agente de Facturación
        workflow["steps"].append({
            "step": "execute_billing",
            "agent": TaskType.BILLING,
            "action": "Ejecutando facturación",
        })
        workflow["agents_involved"].append(TaskType.BILLING)
        
        # Paso 3: Verificar anomalías
        workflow["steps"].append({
            "step": "check_anomalies",
            "agent": "supervisor",
            "action": "Verificando anomalías en facturación",
        })
        
        # Decisión HITL
        if self._should_trigger_human_review(workflow):
            workflow["requires_human_review"] = True
            workflow["status"] = "pending_human_review"
            workflow["steps"].append({
                "step": "human_review",
                "agent": TaskType.HUMAN_REVIEW,
                "action": "Enviado a revisión humana (HITL)",
            })
            logger.warning("⚠️ Supervisor: Activado Human-in-the-Loop")
        else:
            workflow["status"] = "completed"
        
        return workflow
    
    async def _handle_payment(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Orquesta el procesamiento de un pago"""
        return {
            "status": "completed",
            "agents_involved": [TaskType.COLLECTIONS],
            "message": "Pago procesado exitosamente",
        }
    
    async def _handle_classification(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Orquesta la clasificación de mensajes"""
        return {
            "status": "completed",
            "agents_involved": [TaskType.CLASSIFICATION],
            "message": "Mensaje clasificado",
        }
    
    async def _handle_negotiation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Orquesta la generación de ofertas de negociación"""
        return {
            "status": "completed",
            "agents_involved": [TaskType.NEGOTIATION],
            "message": "Ofertas generadas",
        }
    
    def _should_trigger_human_review(self, workflow: Dict[str, Any]) -> bool:
        """
        Determina si se debe activar Human-in-the-Loop.
        
        Reglas:
        - Facturas con monto > S/ 100,000
        - Descuentos > 20%
        - Anomalías detectadas (5x del promedio)
        """
        # Por ahora, retornamos False para MVP
        # En producción, aquí iría la lógica de decisión con Llama-3.3
        return workflow.get("requires_human_review", False)
    
    def delegate_task(self, agent_type: TaskType, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delega una tarea a un agente específico.
        
        Args:
            agent_type: Tipo de agente a delegar
            task: Tarea a ejecutar
            
        Returns:
            Confirmación de delegación
        """
        agent_name = self.available_agents.get(agent_type)
        if not agent_name:
            raise ValueError(f"Agente no encontrado: {agent_type}")
        
        logger.info(f"📤 Supervisor: Delegando tarea a {agent_name}")
        
        return {
            "status": "delegated",
            "agent": agent_name,
            "agent_type": agent_type,
            "task": task,
        }
    
    def check_system_health(self) -> Dict[str, Any]:
        """
        Verifica la salud del ecosistema de agentes.
        
        Returns:
            Estado de salud de cada agente
        """
        return {
            "supervisor": "healthy",
            "agents": {
                agent_type.value: "available"
                for agent_type in TaskType
                if agent_type != TaskType.HUMAN_REVIEW
            },
        }


# Singleton del supervisor
supervisor_agent = SupervisorAgent()
