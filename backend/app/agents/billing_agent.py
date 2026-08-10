"""
Agente de Facturación (Billing Specialist Agent)
Modelo: Llama-3.3
Rol: Estructurar documentos de cobro, cruzar OSS con BSS
"""

from typing import Any, Dict, List, Optional
from decimal import Decimal
from datetime import date, datetime
import structlog
import time

from app.agents.base_agent import BaseAgent
from app.core.calculation_engine import calculation_engine
from app.core.confidence_scorer import confidence_scorer

logger = structlog.get_logger(__name__)


class BillingAgent(BaseAgent):
    """
    Agente de Facturación
    
    Responsable de:
    1. Recopilar datos de OSS_Planta y BSS_Clientes
    2. Ejecutar cálculos en motor simbólico (NO hace matemáticas)
    3. Validar facturas según score de confianza
    4. Generar estructura JSON para factura
    
    Modelo: Llama-3.3 (análisis de datos estructurados)
    """
    
    def __init__(self):
        super().__init__(
            name="Billing Agent",
            model="Llama-3.3",
            version="1.0.0"
        )
        self.auto_validation_threshold = Decimal("0.80")
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el ciclo de facturación para una cuenta.
        
        Args:
            task: {
                "cuenta_id": 2001,
                "periodo": "2024-10",
                "servicios": [...],
                "cliente_score": 0.85
            }
        
        Returns:
            Factura generada con detalle
        """
        start_time = time.time()
        
        try:
            cuenta_id = task.get("cuenta_id")
            periodo = task.get("periodo")
            servicios = task.get("servicios", [])
            cliente_score = Decimal(str(task.get("cliente_score", 0.80)))
            
            logger.info(f"📄 Billing Agent: Iniciando facturación cuenta {cuenta_id}")
            
            # 1. Validar datos de entrada
            self._validate_inputs(cuenta_id, periodo, servicios)
            
            # 2. Calcular líneas de factura usando motor simbólico
            lineas_factura = []
            subtotal = Decimal("0")
            
            for servicio in servicios:
                cargo_fijo = Decimal(str(servicio["cargo_fijo_mensual"]))
                fecha_inicio = servicio.get("fecha_inicio", date.today())
                fecha_fin = servicio.get("fecha_fin", date.today())
                
                # Cálculo simbólico (NO lo hace el LLM)
                monto_linea = calculation_engine.calcular_prorrateo_pxq(
                    cargo_fijo_mensual=cargo_fijo,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                )
                
                lineas_factura.append({
                    "servicio_id": servicio["id_servicio"],
                    "concepto": servicio.get("concepto", "Servicio"),
                    "periodo_inicio": fecha_inicio.isoformat(),
                    "periodo_fin": fecha_fin.isoformat(),
                    "monto_linea": float(monto_linea),
                })
                
                subtotal += monto_linea
            
            # 3. Calcular IGV
            igv = calculation_engine.calcular_igv_desde_base(subtotal)
            total = calculation_engine.calcular_total_factura(subtotal, igv)
            
            # 4. Validación dinámica según score
            validacion_automatica = confidence_scorer.es_cliente_confiable(cliente_score)
            
            # 5. Armar factura
            factura = {
                "cuenta_id": cuenta_id,
                "periodo": periodo,
                "f_emision": date.today().isoformat(),
                "f_vencimiento": self._calcular_vencimiento(date.today()),
                "subtotal_gravado": float(subtotal),
                "igv_total": float(igv),
                "importe_total": float(total),
                "validacion_automatica": validacion_automatica,
                "score_confianza": float(cliente_score),
                "lineas": lineas_factura,
            }
            
            execution_time = (time.time() - start_time) * 1000
            
            result = {
                "status": "success",
                "factura": factura,
                "execution_time_ms": execution_time,
            }
            
            await self.log_execution(task, result)
            return result
            
        except Exception as e:
            return await self.handle_error(e, task)
    
    def _validate_inputs(self, cuenta_id: int, periodo: str, servicios: List[Dict]) -> None:
        """Valida los datos de entrada para facturación"""
        if not cuenta_id:
            raise ValueError("cuenta_id es requerido")
        if not servicios:
            raise ValueError("Se requiere al menos un servicio para facturar")
        logger.debug(f"✅ Inputs validados para cuenta {cuenta_id}")
    
    def _calcular_vencimiento(self, fecha_emision: date, dias_plazo: int = 8) -> str:
        """Calcula la fecha de vencimiento"""
        from datetime import timedelta
        vencimiento = fecha_emision + timedelta(days=dias_plazo)
        return vencimiento.isoformat()
    
    def validate_anomalies(self, factura: Dict[str, Any], historico_promedio: Decimal) -> bool:
        """
        Detecta anomalías en la factura.
        Si el monto es 5x el promedio histórico, requiere revisión humana.
        
        Args:
            factura: Factura generada
            historico_promedio: Promedio histórico del cliente
            
        Returns:
            True si hay anomalía, False si es normal
        """
        monto_actual = Decimal(str(factura["importe_total"]))
        if historico_promedio > 0:
            ratio = monto_actual / historico_promedio
            if ratio > 5:
                logger.warning(f"⚠️ Anomalía detectada: factura {ratio}x el promedio")
                return True
        return False


# Singleton
billing_agent = BillingAgent()
