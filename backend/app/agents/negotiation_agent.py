"""
Agente de Negociación Predictiva
Modelo: Llama-3.3
Rol: Ofrecer descuentos y facilidades antes de la mora
"""

from typing import Any, Dict, List, Optional
from decimal import Decimal
from datetime import date, timedelta
import structlog
import time

from app.agents.base_agent import BaseAgent

logger = structlog.get_logger(__name__)


class NegotiationAgent(BaseAgent):
    """
    Agente de Negociación Predictiva
    
    Actúa proactivamente 5 días antes del vencimiento.
    Ofrece descuentos por pronto pago, facilidades o cambios de fecha.
    
    Modelo: Llama-3.3 (optimización de ofertas)
    """
    
    def __init__(self):
        super().__init__(
            name="Negotiation Agent",
            model="Llama-3.3",
            version="1.0.0"
        )
        # Matriz de descuentos pre-aprobada por Finanzas
        self.descuentos_matriz = {
            "bajo_riesgo": {"max_descuento": 5.0, "plazo_extra": 3},
            "medio_riesgo": {"max_descuento": 10.0, "plazo_extra": 7},
            "alto_riesgo": {"max_descuento": 15.0, "plazo_extra": 15},
        }
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera ofertas de negociación personalizadas.
        
        Args:
            task: {
                "factura_id": 4001,
                "cliente_score": 0.85,
                "probabilidad_pago": 0.65,
                "monto_factura": 4300.00,
                "dias_para_vencimiento": 5
            }
        """
        start_time = time.time()
        
        try:
            factura_id = task.get("factura_id")
            cliente_score = task.get("cliente_score", 0.80)
            probabilidad_pago = task.get("probabilidad_pago", 0.70)
            monto_factura = Decimal(str(task.get("monto_factura", 0)))
            
            logger.info(f"🤝 Negotiation: Evaluando ofertas para factura {factura_id}")
            
            # Determinar estrategia según probabilidad de pago
            oferta = self._generar_oferta(cliente_score, probabilidad_pago, monto_factura)
            
            # Paths de decisión
            if probabilidad_pago > 0.75:
                decision = "happy_path"
                mensaje = "Cliente con alta probabilidad de pago - No ofrecer descuento"
                oferta = None
            elif probabilidad_pago > 0.40:
                decision = "warning_path"
                mensaje = "Ofrecer descuento moderado para incentivar pago"
            else:
                decision = "unhappy_path"
                mensaje = "Alto riesgo - Ofrecer facilidades agresivas"
            
            execution_time = (time.time() - start_time) * 1000
            
            result = {
                "status": "success",
                "factura_id": factura_id,
                "decision": decision,
                "mensaje": mensaje,
                "oferta": oferta,
                "execution_time_ms": execution_time,
            }
            
            await self.log_execution(task, result)
            return result
            
        except Exception as e:
            return await self.handle_error(e, task)
    
    def _generar_oferta(
        self, score: float, prob_pago: float, monto: Decimal
    ) -> Optional[Dict[str, Any]]:
        """
        Genera una oferta personalizada basada en el perfil del cliente.
        
        Args:
            score: Score de confianza (0-1)
            prob_pago: Probabilidad de pago (0-1)
            monto: Monto de la factura
            
        Returns:
            Oferta de negociación o None si no aplica
        """
        # Determinar nivel de riesgo
        if prob_pago > 0.75:
            return None  # Happy path: no ofrecer descuento
        
        if score >= 0.80 and prob_pago > 0.50:
            nivel_riesgo = "bajo_riesgo"
        elif score >= 0.50:
            nivel_riesgo = "medio_riesgo"
        else:
            nivel_riesgo = "alto_riesgo"
        
        params = self.descuentos_matriz[nivel_riesgo]
        
        # Calcular descuento óptimo
        descuento = Decimal(str(params["max_descuento"]))
        
        # Ajustar por monto (facturas grandes = más incentivo)
        if monto > 5000:
            descuento += Decimal("2.0")
        
        descuento = min(descuento, Decimal("20.0"))  # Tope 20%
        
        oferta = {
            "tipo": "descuento_pronto_pago",
            "descuento_porcentaje": float(descuento),
            "descuento_monto": float(monto * descuento / Decimal("100")),
            "nuevo_total": float(monto * (Decimal("1") - descuento / Decimal("100"))),
            "plazo_extra_dias": params["plazo_extra"],
            "fecha_limite": (date.today() + timedelta(days=3)).isoformat(),
            "condiciones": "Descuento válido si paga antes de la fecha límite",
        }
        
        logger.info(f"🎯 Oferta generada: {descuento}% descuento - {nivel_riesgo}")
        
        return oferta
    
    def simular_escenarios(self, monto: Decimal, score: float) -> List[Dict[str, Any]]:
        """
        Simula diferentes escenarios de negociación.
        
        Args:
            monto: Monto de la factura
            score: Score de confianza
            
        Returns:
            Lista de escenarios posibles
        """
        escenarios = []
        
        for prob in [0.90, 0.70, 0.50, 0.30]:
            oferta = self._generar_oferta(score, prob, monto)
            escenarios.append({
                "probabilidad_pago": prob,
                "ofrece_descuento": oferta is not None,
                "oferta": oferta,
            })
        
        return escenarios


# Singleton
negotiation_agent = NegotiationAgent()
