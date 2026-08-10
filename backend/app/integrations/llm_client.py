"""
Cliente Principal para Modelos LLM (vía Groq API)
=======================================
Groq proporciona inferencia ultra-rápida para modelos de IA.
El modelo principal se utiliza para:
- Razonamiento complejo
- Análisis financiero
- Toma de decisiones críticas
- Detección de anomalías

Documentación Groq: https://console.groq.com/docs
"""

from typing import Dict, Any, Optional, List
import httpx
import structlog

from app.config.settings import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class MainLLMClient:
    """
    Cliente principal para interactuar con modelos LLM (ej. Llama-3.3) a través de Groq.
    
    Ventajas de Groq:
    - Inferencia ultra-rápida (LPU - Language Processing Unit)
    - API compatible con OpenAI
    - Baja latencia para decisiones en tiempo real
    - Precios competitivos
    
    Modelos disponibles en Groq:
    - llama-3.3-70b-versatile: Alternativa versátil y poderosa para tareas generales
    - Llama-3.3-distill-llama-70b: Para tareas de razonamiento
    - mixtral-8x7b-32768: Para contexto largo
    """
    
    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.base_url = settings.LLM_BASE_URL
        self.model = getattr(settings, 'LLM_MODEL', 'llama-3.3-70b-versatile')
        self.max_tokens = 4096
        self.temperature = 0.1  # Baja temperatura para decisiones deterministas
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )
        
        logger.info(f"🤖 Main LLM Client inicializado (modelo: {self.model})")
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Genera texto usando el modelo LLM principal vía Groq.
        
        Args:
            prompt: Prompt para el modelo
            system_prompt: Prompt de sistema (opcional)
            max_tokens: Máximo de tokens a generar
            temperature: Temperatura (0-1). Default: 0.1 para decisiones financieras
            
        Returns:
            Respuesta del modelo con texto generado y metadata
        """
        temp = temperature if temperature is not None else self.temperature
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        logger.info(
            f"🤖 Groq: Generando texto",
            model=self.model,
            prompt_length=len(prompt),
            temperature=temp,
        )
        
        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temp,
                },
            )
            response.raise_for_status()
            data = response.json()
            
            result = {
                "text": data["choices"][0]["message"]["content"],
                "model": data["model"],
                "tokens_used": data["usage"]["total_tokens"],
                "prompt_tokens": data["usage"]["prompt_tokens"],
                "completion_tokens": data["usage"]["completion_tokens"],
                "provider": "groq",
            }
            
            logger.info(f"✅ Groq: Respuesta generada ({result['tokens_used']} tokens)")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Groq API Error: {e.response.status_code} - {e.response.text}")
            return {
                "text": f"Error en Groq API: {e.response.status_code}",
                "model": self.model,
                "tokens_used": 0,
                "error": str(e),
            }
        except Exception as e:
            logger.error(f"❌ Groq Client Error: {str(e)}")
            return {
                "text": f"Error: {str(e)}",
                "model": self.model,
                "tokens_used": 0,
                "error": str(e),
            }
    
    async def analyze_financial_data(
        self,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Analiza datos financieros para:
        - Detección de anomalías en facturación
        - Validación de consistencia
        - Identificación de patrones de fraude
        
        Args:
            data: Datos financieros a analizar
            
        Returns:
            Análisis con hallazgos y recomendaciones
        """
        system_prompt = """
        Eres un experto analista financiero especializado en telecomunicaciones.
        Tu tarea es analizar datos de facturación y detectar:
        1. Anomalías (facturas con montos 5x superiores al promedio)
        2. Patrones de consumo irregulares
        3. Posibles errores de cálculo
        4. Riesgos de fuga de ingresos
        
        Responde en formato JSON estructurado con:
        {
            "tiene_anomalias": boolean,
            "hallazgos": [lista de hallazgos],
            "recomendaciones": [lista de recomendaciones],
            "nivel_riesgo": "bajo|medio|alto|critico"
        }
        """
        
        prompt = f"Datos a analizar:\n{data}"
        
        return await self.generate_text(prompt, system_prompt, temperature=0.0)
    
    async def make_decision(
        self,
        context: Dict[str, Any],
        options: List[str],
        criteria: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Toma una decisión basada en contexto y opciones.
        Usado por el Agente Supervisor para enrutamiento.
        
        Args:
            context: Contexto de la decisión
            options: Opciones disponibles
            criteria: Criterios de evaluación (opcional)
            
        Returns:
            Decisión con justificación
        """
        system_prompt = """
        Eres un orquestador de agentes IA en un sistema de facturación.
        Debes tomar decisiones óptimas basadas en el contexto proporcionado.
        
        Responde en JSON:
        {
            "decision": "opcion_seleccionada",
            "justificacion": "razón de la decisión",
            "confianza": 0.0-1.0,
            "siguiente_paso": "accion a tomar"
        }
        """
        
        prompt = f"""
        Contexto: {context}
        Opciones disponibles: {options}
        Criterios: {criteria if criteria else 'Eficiencia, precisión y cumplimiento normativo'}
        
        Selecciona la mejor opción y justifica tu decisión.
        """
        
        result = await self.generate_text(prompt, system_prompt, temperature=0.1)
        result["decision"] = options[0] if options else None
        return result
    
    async def validate_billing_consistency(
        self,
        factura_data: Dict[str, Any],
        historico_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Valida la consistencia de una factura contra datos históricos.
        
        Args:
            factura_data: Datos de la factura actual
            historico_data: Datos históricos del cliente
            
        Returns:
            Resultado de validación
        """
        system_prompt = """
        Eres un validador de facturación para una empresa de telecomunicaciones.
        Compara la factura actual con el histórico y detecta inconsistencias.
        
        Criterios de validación:
        - Variación de monto > 50% requiere justificación
        - Servicios nuevos deben tener fecha de alta
        - Servicios cancelados no deben aparecer
        - Cálculos de prorrateo deben ser correctos
        """
        
        prompt = f"""
        Factura actual: {factura_data}
        Histórico: {historico_data}
        
        ¿La factura es consistente con el histórico?
        """
        
        return await self.generate_text(prompt, system_prompt, temperature=0.0)
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica la conexión con Groq API.
        
        Returns:
            Estado de la conexión
        """
        try:
            result = await self.generate_text(
                "Responde 'OK' si puedes leer esto.",
                max_tokens=10,
                temperature=0.0,
            )
            return {
                "status": "healthy",
                "provider": "groq",
                "model": self.model,
                "response": result.get("text", "").strip(),
            }
        except Exception as e:
            return {
                "status": "error",
                "provider": "groq",
                "error": str(e),
            }


# Singleton
llm_client = MainLLMClient()
