"""
Clase base para todos los agentes del ecosistema SON-IA
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)


class BaseAgent(ABC):
    """
    Clase base abstracta para todos los agentes especializados.
    
    Attributes:
        name: Nombre del agente
        model: Modelo de IA utilizado (Llama-3.3, gemini-pro, gemini-flash)
        version: Versión del agente
    """
    
    def __init__(self, name: str, model: str, version: str = "1.0.0"):
        self.name = name
        self.model = model
        self.version = version
        self.execution_history: list = []
        logger.info(f"🤖 Agente inicializado: {self.name} (v{self.version}) - Modelo: {self.model}")
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta la tarea principal del agente.
        
        Args:
            task: Diccionario con los parámetros de la tarea
            
        Returns:
            Diccionario con el resultado de la ejecución
        """
        pass
    
    async def log_execution(self, task: Dict[str, Any], result: Dict[str, Any]) -> None:
        """
        Registra la ejecución en el historial del agente.
        
        Args:
            task: Tarea ejecutada
            result: Resultado obtenido
        """
        execution_record = {
            "agent": self.name,
            "model": self.model,
            "timestamp": datetime.utcnow().isoformat(),
            "task_type": task.get("type", "unknown"),
            "status": result.get("status", "unknown"),
            "execution_time_ms": result.get("execution_time_ms", 0),
        }
        self.execution_history.append(execution_record)
        logger.info(f"📝 {self.name}: Ejecución registrada - {execution_record['task_type']}")
    
    async def handle_error(self, error: Exception, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maneja errores durante la ejecución del agente.
        
        Args:
            error: Excepción capturada
            task: Tarea que generó el error
            
        Returns:
            Diccionario con información del error
        """
        logger.error(f"❌ {self.name}: Error ejecutando tarea - {str(error)}")
        return {
            "status": "error",
            "agent": self.name,
            "error": str(error),
            "error_type": type(error).__name__,
            "task": task,
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estadísticas del agente.
        
        Returns:
            Diccionario con estadísticas
        """
        return {
            "name": self.name,
            "model": self.model,
            "version": self.version,
            "total_executions": len(self.execution_history),
            "last_execution": self.execution_history[-1] if self.execution_history else None,
        }
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', model='{self.model}')>"
