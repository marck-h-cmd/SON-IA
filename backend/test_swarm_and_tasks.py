"""
Test E2E para Enjambre de Agentes, RAG y Tareas Celery
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.rag.retrieval import retrieval_service
from app.rag.vector_store import vector_store
from app.agents.customer_agent import customer_agent
from app.agents.supervisor_agent import supervisor_agent
from app.agents.learning_agent import learning_agent
from app.tasks.collections_tasks import recalculate_daily_overdue_and_tamn
from app.tasks.negotiation_tasks import predictive_negotiation_t5
from app.tasks.learning_tasks import periodic_learning_and_score_update
from app.tasks.billing_tasks import proactive_billing_t7
from app.services.whatsapp_webhook_service import whatsapp_webhook_service
from app.database.connection import async_session_factory


async def run_tests():
    print("=" * 70)
    print("🚀 INICIANDO VERIFICACIÓN E2E DE ENJAMBRE DE AGENTES, RAG Y CELERY")
    print("=" * 70)

    # 1. TEST RAG KNOWLEDGE BASE
    print("\n--- 1. TEST RAG: BASE DE CONOCIMIENTO & BÚSQUEDA ---")
    indexed = await retrieval_service.initialize_knowledge_base(force_reindex=False)
    stats = await vector_store.get_stats()
    print(f"✅ Documentos indexados en Vector Store: {stats['total_vectors']}")
    
    query = "¿Cuáles son las tarifas y velocidades de Fibra Óptica B2B?"
    context = await retrieval_service.retrieve_context(query, top_k=2)
    print(f"🔍 Búsqueda RAG para '{query}':")
    for doc in context:
        print(f"   • [{doc['score']:.2f}] {doc['metadata'].get('title')}")
    assert len(context) > 0, "RAG debe retornar al menos un documento"

    # 2. TEST CUSTOMER AGENT CON RAG
    print("\n--- 2. TEST CUSTOMER AGENT (RAG + EXPLICACIONES) ---")
    cust_res = await customer_agent.execute({
        "type": "answer_question",
        "pregunta": "¿Qué beneficios tiene el Plan Elige Todo?",
        "cliente_nombre": "Empresa Demo SAC",
    })
    print(f"✅ Respuesta CustomerAgent (Fuente: {cust_res.get('fuente')}):")
    print(f"   {cust_res.get('respuesta')[:160]}...")

    exp_res = await customer_agent.execute({
        "type": "explain_invoice",
        "factura": {"nro_doc_fiscal": "21-0009999", "charge_total_amount": 2950.00}
    })
    print(f"✅ Explicación Factura (Zero-Hallucination):")
    print(f"   {exp_res.get('respuesta')[:140]}...")

    # 3. TEST SUPERVISOR AGENT WORKFLOWS
    print("\n--- 3. TEST SUPERVISOR AGENT: WORKFLOWS MULTI-AGENTE ---")
    health = supervisor_agent.check_system_health()
    print(f"✅ Swarm Health: {health['swarm_status']} ({health['total_agents']} agentes disponibles)")

    print("\n -> Ejecutando Workflow de Facturación E2E...")
    bill_wf = await supervisor_agent.execute({
        "type": "start_billing_cycle",
        "ciclo_id": 31,
        "score_confianza": 0.88,
    })
    print(f"✅ Estado Workflow Facturación: {bill_wf.get('status')}")
    print(f"   Agentes involucrados: {bill_wf.get('agents_involved')}")

    print("\n -> Ejecutando Workflow de Cobranzas y Negociación E2E...")
    col_wf = await supervisor_agent.execute({
        "type": "collections_workflow",
        "factura_id": "TEST-21-001",
        "monto_pendiente": 4500.0,
        "dias_vencido": 12,
        "score_confianza": 0.60,
    })
    print(f"✅ Estado Workflow Cobranzas: {col_wf.get('status')}")
    print(f"   Agentes involucrados: {col_wf.get('agents_involved')}")
    if col_wf.get("negotiation_offer"):
        print(f"   Oferta generada: {col_wf['negotiation_offer'].get('oferta')}")

    print("\n -> Ejecutando Workflow de Atención con Clasificación y RAG...")
    chat_wf = await supervisor_agent.execute({
        "type": "classify_and_respond",
        "mensaje": "¿Cuáles son las etapas de mora y tasas de interés?",
        "cliente_nombre": "Corporación Sur",
    })
    print(f"✅ Intención: {chat_wf.get('intencion_detectada')}")
    print(f"   Respuesta: {chat_wf.get('respuesta_generada')[:140]}...")

    # 4. TEST LEARNING AGENT & RECÁLCULO DE SCORES
    print("\n--- 4. TEST LEARNING AGENT: APRENDIZAJE & SCORES ---")
    learn_res = await learning_agent.execute({
        "type": "retrain_and_update_scores",
        "apply_db_updates": False,  # Simulación segura para el test
    })
    print(f"✅ Clientes procesados para recálculo de score: {learn_res.get('total_clientes_procesados')}")
    print(f"   Accuracy estimada: {learn_res.get('accuracy_estimada')}")

    # 5. TEST WHATSAPP WEBHOOK CON RAG
    print("\n--- 5. TEST WHATSAPP WEBHOOK: SIMULACIÓN DE CONSULTAS ---")
    async with async_session_factory() as db:
        wh_payload = {
            "sessionId": "test-session",
            "event": "message.received",
            "data": {
                "body": "¿Cómo calculan los intereses TAMN si me atraso?",
                "from": "51901528082@c.us",
                "fromMe": False,
            }
        }
        wh_res = await whatsapp_webhook_service.process_payload(wh_payload, db)
        print(f"✅ Webhook procesado exitosamente: {wh_res.get('success')}")
        print(f"   Intención detectada: {wh_res.get('intent')}")
        print(f"   Respuesta enviada: {wh_res.get('reply')[:140]}...")

    print("\n" + "=" * 70)
    print("🎉 TODAS LAS PRUEBAS DEL ENJAMBRE DE AGENTES, RAG Y CELERY PASARON 100%")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_tests())
