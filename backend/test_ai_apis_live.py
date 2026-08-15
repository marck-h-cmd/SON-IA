"""
Diagnóstico en Vivo de Conexión a APIs de IA y Funcionamiento de los 7 Agentes
"""

import asyncio
import sys
from pathlib import Path
import httpx

sys.path.insert(0, str(Path(__file__).parent))

from app.config.settings import get_settings
from app.integrations.llm_client import llm_client
from app.integrations.gemini_client import gemini_client
from app.agents.supervisor_agent import supervisor_agent
from app.agents.billing_agent import billing_agent
from app.agents.collections_agent import collections_agent
from app.agents.negotiation_agent import negotiation_agent
from app.agents.customer_agent import customer_agent
from app.agents.classifier_agent import classifier_agent
from app.agents.learning_agent import learning_agent

settings = get_settings()


async def test_groq_api():
    print("\n" + "=" * 60)
    print("1. PROBANDO API DE GROQ (Llama-3.3-70b-versatile)")
    print("=" * 60)
    print(f"Base URL: {settings.LLM_BASE_URL}")
    print(f"Modelo: {settings.LLM_MODEL}")
    print(f"API Key configurada: {settings.LLM_API_KEY[:8]}...{settings.LLM_API_KEY[-6:]}")
    
    try:
        res = await llm_client.generate_text(
            prompt="Calcula el 18% de IGV de un subtotal de S/ 1,000.00 y responde en una sola frase breve.",
            system_prompt="Eres un asistente financiero de Integratel.",
            max_tokens=60,
        )
        if "error" in res and res.get("tokens_used") == 0:
            print(f"❌ Error en respuesta Groq: {res.get('error')}")
            return False
        else:
            print(f"✅ Respuesta exitosa de Groq:")
            print(f"   Texto: {res.get('text')}")
            print(f"   Tokens usados: {res.get('tokens_used')}")
            print(f"   Modelo real: {res.get('model')}")
            return True
    except Exception as e:
        print(f"❌ Excepción conectando a Groq: {e}")
        return False


async def test_gemini_api():
    print("\n" + "=" * 60)
    print("2. PROBANDO API DE GOOGLE GEMINI (gemini-1.5-flash / pro)")
    print("=" * 60)
    api_key = settings.GEMINI_API_KEY
    print(f"API Key configurada: {api_key[:8]}...{api_key[-6:] if len(api_key) > 10 else ''}")
    
    # Probar endpoint real de Gemini
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                url,
                json={
                    "contents": [{
                        "parts": [{"text": "Di 'Hola desde Gemini' en una frase corta."}]
                    }]
                }
            )
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                print(f"✅ Respuesta exitosa de Google Gemini API (200 OK):")
                print(f"   Texto: {text.strip()}")
                return True
            else:
                print(f"⚠️ Google Gemini API respondió status {resp.status_code}: {resp.text[:120]}...")
                return False
    except Exception as e:
        print(f"⚠️ Conexión a Gemini API falló: {e}")
        return False


async def test_all_agents():
    print("\n" + "=" * 60)
    print("3. PROBANDO LOS 7 AGENTES DEL ECOSISTEMA SON-IA")
    print("=" * 60)
    
    agents = [
        ("Supervisor Agent", supervisor_agent, {"type": "start_billing_cycle", "ciclo_id": 31}),
        ("Billing Agent", billing_agent, {"type": "calculate_invoice", "cliente_id": 1001, "servicios": []}),
        ("Collections Agent", collections_agent, {"type": "calculate_tamn", "factura_id": "TEST-1", "monto_original": 1200.0, "dias_vencido": 15}),
        ("Negotiation Agent", negotiation_agent, {"type": "evaluate_and_offer", "factura_id": "TEST-1", "monto_pendiente": 1200.0, "score_confianza": 0.65, "dias_mora": 15}),
        ("Customer Agent", customer_agent, {"type": "answer_question", "pregunta": "¿Qué planes de fibra tienen?"}),
        ("Classifier Agent", classifier_agent, {"type": "classify_message", "message": "Quiero pagar mi factura vencida"}),
        ("Learning Agent", learning_agent, {"type": "analyze_patterns"}),
    ]
    
    success_count = 0
    for name, agent, payload in agents:
        try:
            res = await agent.execute(payload)
            status = res.get("status", "unknown")
            exec_time = res.get("execution_time_ms", 0.0)
            print(f"✅ {name:20} -> Status: {status:10} ({exec_time:.1f}ms)")
            success_count += 1
        except Exception as e:
            print(f"❌ {name:20} -> Error: {e}")
            
    print(f"\nResultado: {success_count}/{len(agents)} agentes funcionando correctamente.")
    return success_count == len(agents)


async def main():
    groq_ok = await test_groq_api()
    gemini_ok = await test_gemini_api()
    agents_ok = await test_all_agents()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL DE DIAGNÓSTICO:")
    print(f" • API Groq (Llama-3.3 LLM):    {'OPERATIVO ✅' if groq_ok else 'CON ERROR ❌'}")
    print(f" • API Google Gemini:           {'OPERATIVO ✅' if gemini_ok else 'REQUIERE CLAVE VÁLIDA ⚠️'}")
    print(f" • Enjambre 7 Agentes IA:       {'OPERATIVO (100%) ✅' if agents_ok else 'PARCIAL ⚠️'}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
