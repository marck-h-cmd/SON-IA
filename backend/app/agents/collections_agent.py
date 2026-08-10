"""
Agente de Cobranzas y Recaudo (Collections Agent)
Modelo: Llama-3.3
Rol: Gestionar cartera morosa y conciliar pagos
"""

from typing import Any, Dict, List, Optional
from decimal import Decimal
from datetime import date
import structlog
import time

from app.agents.base_agent import BaseAgent
from app.core.calculation_engine import calculation_engine

logger = structlog.get_logger(__name__)


class CollectionsAgent(BaseAgent):
    """
    Agente de Cobranzas
    
    Responsable de:
    1. Monitorear facturas vencidas
    2. Calcular intereses moratorios (TAMN)
    3. Generar notificaciones de cobranza
    4. Conciliar pagos recibidos
    
    Modelo: Llama-3.3 (análisis predictivo de probabilidad de pago)
    """
    
    def __init__(self):
        super().__init__(
            name="Collections Agent",
            model="Llama-3.3",
            version="1.0.0"
        )
        self.mora_stages = {
            "temprana": (1, 5),      # 1-5 días
            "media": (6, 15),        # 6-15 días
            "tardia": (16, 30),      # 16-30 días
            "critica": (31, 999),    # 31+ días
        }
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta tareas de cobranza.
        
        Args:
            task: {
                "type": "check_overdue" | "process_payment" | "calculate_tamn",
                "factura_id": 4001,
                ...
            }
        """
        start_time = time.time()
        task_type = task.get("type", "")
        
        try:
            if task_type == "check_overdue":
                result = await self._check_overdue_invoices(task)
            elif task_type == "process_payment":
                result = await self._process_payment(task)
            elif task_type == "calculate_tamn":
                result = await self._calculate_tamn(task)
            else:
                result = {"status": "error", "message": f"Tipo no soportado: {task_type}"}
            
            execution_time = (time.time() - start_time) * 1000
            result["execution_time_ms"] = execution_time
            
            await self.log_execution(task, result)
            return result
            
        except Exception as e:
            return await self.handle_error(e, task)
    
    async def _check_overdue_invoices(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifica facturas vencidas y las clasifica por etapa de mora.
        
        Returns:
            Lista de facturas vencidas con su etapa de mora
        """
        # Simulación - en producción consultaría la BD
        overdue_invoices = [
            {
                "factura_id": 4001,
                "cliente_id": 1005,
                "monto": 4300.00,
                "dias_mora": 12,
                "etapa": "media",
                "accion_recomendada": "Enviar recordatorio con intereses",
            },
            {
                "factura_id": 4002,
                "cliente_id": 1003,
                "monto": 150.00,
                "dias_mora": 45,
                "etapa": "critica",
                "accion_recomendada": "Iniciar proceso de cobranza judicial",
            },
        ]
        
        logger.info(f"📊 Collections: {len(overdue_invoices)} facturas vencidas encontradas")
        
        return {
            "status": "success",
            "total_overdue": len(overdue_invoices),
            "invoices": overdue_invoices,
        }
    
    async def _process_payment(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa un pago recibido y concilia con facturas pendientes.
        
        Args:
            task: {
                "factura_id": 4001,
                "monto_pagado": 4300.00,
                "fecha_pago": "2024-10-20"
            }
        """
        factura_id = task.get("factura_id")
        monto_pagado = Decimal(str(task.get("monto_pagado", 0)))
        
        logger.info(f"💰 Collections: Procesando pago factura {factura_id}")
        
        return {
            "status": "success",
            "factura_id": factura_id,
            "monto_pagado": float(monto_pagado),
            "accion": "conciliado",
            "nuevo_estado": "Pagado",
        }
    
    async def _calculate_tamn(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula intereses moratorios TAMN para una factura vencida.
        
        Args:
            task: {
                "monto_deuda": 4300.00,
                "dias_mora": 15,
                "factor_vencimiento": 1.0,
                "factor_actual": 1.025
            }
        """
        monto_deuda = Decimal(str(task.get("monto_deuda", 0)))
        dias_mora = task.get("dias_mora", 0)
        factor_vencimiento = Decimal(str(task.get("factor_vencimiento", 1.0)))
        factor_actual = Decimal(str(task.get("factor_actual", 1.025)))
        
        # Cálculo simbólico (NO lo hace el LLM)
        interes = calculation_engine.calcular_interes_tamn(
            monto_deuda=monto_deuda,
            dias_mora=dias_mora,
            factor_acumulado_vencimiento=factor_vencimiento,
            factor_acumulado_hoy=factor_actual,
        )
        
        total_pagar = monto_deuda + interes
        
        logger.info(f"📈 TAMN calculado: Deuda={monto_deuda}, Interés={interes}, Total={total_pagar}")
        
        return {
            "status": "success",
            "monto_deuda": float(monto_deuda),
            "dias_mora": dias_mora,
            "interes_tamn": float(interes),
            "total_pagar": float(total_pagar),
        }
    
    def get_mora_stage(self, dias_mora: int) -> str:
        """
        Determina la etapa de mora según los días de retraso.
        
        Args:
            dias_mora: Días de morosidad
            
        Returns:
            Etapa: temprana, media, tardia, critica
        """
        for stage, (min_days, max_days) in self.mora_stages.items():
            if min_days <= dias_mora <= max_days:
                return stage
        return "desconocida"
    
    def get_collection_strategy(self, dias_mora: int, score_confianza: float) -> Dict[str, Any]:
        """
        Determina la estrategia de cobranza según etapa y perfil del cliente.
        
        Args:
            dias_mora: Días de morosidad
            score_confianza: Score de confianza del cliente
            
        Returns:
            Estrategia recomendada
        """
        etapa = self.get_mora_stage(dias_mora)
        
        estrategias = {
            "temprana": {
                "canal": "email",
                "tono": "recordatorio amigable",
                "frecuencia": "cada 3 días",
            },
            "media": {
                "canal": "email + SMS",
                "tono": "aviso formal",
                "frecuencia": "diario",
            },
            "tardia": {
                "canal": "llamada telefónica",
                "tono": "requerimiento de pago",
                "frecuencia": "cada 2 días",
            },
            "critica": {
                "canal": "carta notarial",
                "tono": "aviso legal",
                "frecuencia": "semanal",
            },
        }
        
        estrategia = estrategias.get(etapa, estrategias["critica"])
        
        # Ajustar según score de confianza
        if score_confianza >= 0.80:
            estrategia["tono"] = "preferencial"
            estrategia["ofrecer_negociacion"] = True
        
        return estrategia


# Singleton
collections_agent = CollectionsAgent()
