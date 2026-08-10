
# 🏗️ Arquitectura Técnica - SON-IA

## Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Principios Arquitectónicos](#principios-arquitectónicos)
3. [Stack Tecnológico Detallado](#stack-tecnológico-detallado)
4. [Diagrama de Componentes](#diagrama-de-componentes)
5. [Arquitectura de Agentes IA](#arquitectura-de-agentes-ia)
6. [Motor Simbólico Zero-Hallucination](#motor-simbólico-zero-hallucination)
7. [Base de Datos](#base-de-datos)
8. [Integraciones Externas](#integraciones-externas)
9. [Modelos de IA y ML](#modelos-de-ia-y-ml)
10. [Flujos de Datos](#flujos-de-datos)
11. [Seguridad y Gobernanza](#seguridad-y-gobernanza)
12. [Estrategia de Despliegue](#estrategia-de-despliegue)

---

## Visión General

SON-IA implementa una arquitectura de **microservicios con orquestación de agentes IA** basada en el patrón **BSS/OSS separado** requerido por estándares de telecomunicaciones y normativa SUNAT.

### Objetivos Arquitectónicos

| Objetivo | Descripción | Implementación |
|----------|-------------|----------------|
| **Precisión Financiera** | Cero errores en cálculos | Motor Simbólico en Python, LLMs no hacen matemáticas |
| **Alta Disponibilidad** | Sistema crítico para facturación | Multi-proveedor IA, redundancia, circuit breakers |
| **Auditabilidad** | Trazabilidad completa | Logs inmutables de cada acción de cada agente |
| **Cumplimiento SUNAT** | Normativa peruana | Recibos Tipo 14, IGV 18%, TAMN, validaciones fiscales |
| **Soberanía Tecnológica** | Sin vendor lock-in | Groq + Google, modelos intercambiables |
| **Escalabilidad** | Crecimiento en volumen | Arquitectura stateless, workers Celery escalables |

---

## Principios Arquitectónicos

### 1. Separación BSS / OSS

```
┌─────────────────────────────────────────────────────────┐
│              BSS (Business Support System)               │
│                                                          │
│  • Clientes (bss_clientes)                               │
│  • Cuentas de facturación (bss_cuentas)                  │
│  • Facturas (bss_factura_cabecera, bss_factura_detalle)  │
│  • Historial de pagos (bss_historial_pagos)              │
│  • Ofertas de negociación (bss_ofertas_negociacion)      │
│  • Score de confianza                                    │
│                                                          │
│  Responsabilidad: Gestión comercial y financiera         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              OSS (Operations Support System)             │
│                                                          │
│  • Servicios de planta (oss_planta)                      │
│  • Recursos de red (identificador_recurso)               │
│  • Cargos fijos mensuales (cargo_fijo_mensual)           │
│  • Tecnología (tecnologia)                               │
│  • Fechas de alta/baja                                   │
│                                                          │
│  Responsabilidad: Infraestructura técnica y red          │
└─────────────────────────────────────────────────────────┘
```

### 2. Zero-Hallucination

```
┌─────────────────────────────────────────────────────────┐
│                 AGENTE DE IA (LLM)                        │
│                                                          │
│  "Necesito calcular el prorrateo PxQ para el servicio    │
│   3001 con cargo fijo S/ 310.00 del 1 al 15 de octubre"  │
│                                                          │
│  El LLM NUNCA hace: 310 / 31 * 15 = ?                    │
│  El LLM SOLO invoca: call_symbolic_engine(servicio_3001) │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ call_symbolic_engine()
                         ▼
┌─────────────────────────────────────────────────────────┐
│            MOTOR SIMBÓLICO (Python Decimal)              │
│                                                          │
│  def calcular_prorrateo_pxq(cargo, inicio, fin):         │
│      dias_mes = calendar.monthrange(inicio.year,         │
│                                     inicio.month)[1]     │
│      dias_uso = (fin - inicio).days + 1                  │
│      return (Decimal(cargo) / dias_mes * dias_uso)       │
│              .quantize(Decimal("0.01"), ROUND_HALF_UP)   │
│                                                          │
│  ✅ Resultado: S/ 150.00 (exacto, determinista, auditable)│
└─────────────────────────────────────────────────────────┘
```

### 3. Modelo Correcto para Cada Tarea

| Tarea | Modelo | Razón |
|-------|--------|-------|
| Razonamiento financiero | DeepSeek-R1 (Groq) | Optimizado para lógica y matemáticas |
| Decisiones de enrutamiento | DeepSeek-R1 (Groq) | Razonamiento multi-paso |
| Generación de texto natural | Gemini 1.5 Pro | Mejor NLP y generación |
| Clasificación de mensajes | Gemini 1.5 Flash | Más rápido y económico |
| Cálculos matemáticos | Python Decimal | Precisión absoluta, auditable |

### 4. Human-in-the-Loop (HITL)

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────────┐
│   Agente     │────▶│ Detecta excepción│────▶│  Supervisor      │
│   ejecuta    │     │ • Anomalía 5x    │     │  pausa el flujo  │
│   tarea      │     │ • Score crítico  │     │                  │
└──────────────┘     └─────────────────┘     └────────┬─────────┘
                                                       │
                                                       ▼
                                                ┌──────────────────┐
                                                │   Dashboard      │
                                                │   Alerta HITL    │
                                                └────────┬─────────┘
                                                         │
                                            ┌────────────┴────────────┐
                                            │                         │
                                            ▼                         ▼
                                     ┌──────────────┐          ┌──────────────┐
                                     │   Humano     │          │   Humano     │
                                     │   APRUEBA    │          │   RECHAZA    │
                                     └──────┬───────┘          └──────┬───────┘
                                            │                         │
                                            ▼                         ▼
                                     ┌──────────────┐          ┌──────────────┐
                                     │  Continúa    │          │  Rollback    │
                                     │  el flujo    │          │  Automático  │
                                     └──────────────┘          └──────────────┘
```

---

## Stack Tecnológico Detallado

### Backend Core

| Componente | Tecnología | Versión | Justificación |
|------------|-----------|---------|---------------|
| **API Framework** | FastAPI | 0.115.0 | Async nativo, validación Pydantic, OpenAPI automático, alto rendimiento |
| **Lenguaje** | Python | 3.11+ | Tipado fuerte, ecosistema ML/IA, Decimal para precisión financiera |
| **Orquestación IA** | LangGraph | 0.2.43 | State graphs con checkpoints, HITL nativo, streaming |
| **Framework IA** | LangChain | 0.3.4 | Integración con múltiples LLMs, tools, RAG |
| **Validación** | Pydantic | 2.9.2 | Schemas estrictos para datos financieros, validación en runtime |

### Bases de Datos

| Base de Datos | Versión | Uso | Tipo de Datos |
|---------------|---------|-----|---------------|
| **PostgreSQL** | 16 | Datos de agentes, facturación, clientes, auditoría | Relacional (principal) |
| **Redis** | 7 | Caché de sesiones, memoria contextual de agentes, Celery broker | Key-Value en memoria |
| **Pinecone** | - | Embeddings vectoriales para RAG | Vectorial |
| **SQL Server** | - | BSS/OSS Legacy (solo lectura, migración gradual) | Relacional (legacy) |
| **Teradata** | - | Data warehouse legacy (solo lectura) | Relacional (legacy) |

### IA y Machine Learning

| Componente | Proveedor | Modelo | Uso Principal | Latencia Típica |
|------------|-----------|--------|---------------|-----------------|
| **DeepSeek-R1** | Groq (LPU) | deepseek-r1-distill-llama-70b | Razonamiento complejo, decisiones | <500ms |
| **Gemini 1.5 Pro** | Google | gemini-1.5-pro | NLP, RAG, generación de texto | 1-3s |
| **Gemini 1.5 Flash** | Google | gemini-1.5-flash | Clasificación rápida | <500ms |
| **XGBoost** | Local | Classifier | Score confianza, predicción pago | <10ms |
| **Isolation Forest** | Local | Anomaly Detector | Detección anomalías | <5ms |

### Infraestructura y DevOps

| Componente | Tecnología | Propósito |
|------------|-----------|-----------|
| **Contenedores** | Docker 24+ | Empaquetado consistente |
| **Orquestación** | Docker Compose (dev) / Kubernetes (prod) | Gestión de servicios |
| **Tareas Async** | Celery 5.4 | Procesamiento background |
| **Message Broker** | Redis 7 | Colas de tareas Celery |
| **Monitoreo Celery** | Flower 2.0 | Dashboard de workers |
| **CI/CD** | GitHub Actions | Tests automáticos, linting |
| **Métricas** | Prometheus + FastAPI Instrumentator | Monitoreo de API |
| **Logging** | structlog | Logs estructurados en JSON |

---

## Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  CLIENTES                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐     │
│  │ Navegador│  │ WhatsApp │  │  Email   │  │  API Externa (ERP/CRM)   │     │
│  │ (Next.js)│  │ (Twilio) │  │ (SMTP)   │  │  (REST/GraphQL)          │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────────┬─────────────┘     │
└───────┼─────────────┼─────────────┼────────────────────┼───────────────────┘
        │             │             │                    │
        ▼             ▼             ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             CAPA DE ENTRADA                                  │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐   │
│  │   Next.js 14     │  │   Twilio API     │  │   SMTP Server (Gmail)    │   │
│  │   (Frontend SPA) │  │   (WhatsApp/SMS) │  │   (Notificaciones)       │   │
│  │                  │  │                  │  │                          │   │
│  │ • Dashboard      │  │ • Webhook inbound│  │  • Recordatorios pago    │   │
│  │ • Portal Cliente │  │ • Envío outbound │  │  • Ofertas negociación   │   │
│  │ • Chat Widget    │  │                  │  │  • Alertas vencimiento   │   │
│  └────────┬─────────┘  └────────┬─────────┘  └───────────┬──────────────┘   │
└───────────┼─────────────────────┼────────────────────────┼──────────────────┘
            │                     │                        │
            ▼                     ▼                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          API GATEWAY (FastAPI)                               │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        MIDDLEWARE LAYER                               │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────┐ ┌────────────────────┐   │   │
│  │  │   CORS   │ │  JWT     │ │ Rate Limiting│ │  Prometheus        │   │   │
│  │  │          │ │  Auth    │ │              │ │  Metrics           │   │   │
│  │  └──────────┘ └──────────┘ └──────────────┘ └────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌───────────────────────────┐  ┌──────────────────────────────────────┐   │
│  │     REST API v1           │  │        WebSockets                     │   │
│  │                           │  │                                       │   │
│  │  • /health                │  │  • /ws/dashboard                      │   │
│  │  • /billing/*             │  │    - Métricas en tiempo real          │   │
│  │  • /clients/*             │  │    - Estado de agentes                │   │
│  │  • /dashboard/*           │  │    - Alertas HITL                     │   │
│  │  • /collections/*         │  │                                       │   │
│  │  • /negotiations/*        │  │  • /ws/cliente/{id}                   │   │
│  │  • /audit/*               │  │    - Notificaciones personalizadas    │   │
│  │                           │  │    - Estado de facturas               │   │
│  └─────────────┬─────────────┘  └─────────────────┬────────────────────┘   │
└────────────────┼──────────────────────────────────┼────────────────────────┘
                 │                                  │
                 ▼                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      ORQUESTADOR DE AGENTES (LangGraph)                      │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    AGENTE SUPERVISOR                                   │   │
│  │                    Modelo: DeepSeek-R1 (Groq LPU)                      │   │
│  │                                                                        │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────────────┐   │   │
│  │  │  Task Router   │  │ HITL Manager   │  │  System Health Check   │   │   │
│  │  │                │  │                │  │                        │   │   │
│  │  │ • Analiza      │  │ • Evalúa       │  │ • Monitorea agentes    │   │   │
│  │  │   trigger      │  │   criticidad   │  │ • Circuit breaker     │   │   │
│  │  │ • Selecciona   │  │ • Pausa flujo  │  │ • Alertas fallos      │   │   │
│  │  │   agente       │  │ • Notifica     │  │ • Failover            │   │   │
│  │  └───────┬────────┘  └───────┬────────┘  └───────────┬────────────┘   │   │
│  └──────────┼───────────────────┼───────────────────────┼───────────────┘   │
│             │                   │                       │                    │
│  ┌──────────┼───────────────────┼───────────────────────┼───────────────┐   │
│  │          ▼                   ▼                       ▼               │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐│   │
│  │  │   BILLING    │ │ COLLECTIONS  │ │ NEGOTIATION  │ │  CUSTOMER    ││   │
│  │  │   AGENT      │ │   AGENT      │ │   AGENT      │ │  AGENT       ││   │
│  │  │              │ │              │ │              │ │              ││   │
│  │  │ DeepSeek-R1  │ │ DeepSeek-R1  │ │ DeepSeek-R1  │ │ Gemini Pro   ││   │
│  │  │              │ │              │ │              │ │              ││   │
│  │  │ Skills:      │ │ Skills:      │ │ Skills:      │ │ Skills:      ││   │
│  │  │ • PxQ, IGV   │ │ • TAMN       │ │ • Descuentos │ │ • Chat RAG   ││   │
│  │  │ • Validación │ │ • Conciliar  │ │ • Predicción │ │ • Explicar   ││   │
│  │  │ • Emisión    │ │ • Priorizar  │ │ • Simular    │ │ • Soportar   ││   │
│  │  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘│   │
│  │         │                │                │                │        │   │
│  │  ┌──────┴────────────────┴────────────────┴────────────────┴──────┐ │   │
│  │  │                    AGENTES AUXILIARES                           │ │   │
│  │  │                                                                │ │   │
│  │  │  ┌──────────────────┐  ┌──────────────────────────────────┐   │ │   │
│  │  │  │    LEARNING      │  │        CLASSIFIER                │   │ │   │
│  │  │  │    AGENT         │  │        AGENT                     │   │ │   │
│  │  │  │                  │  │                                  │   │ │   │
│  │  │  │ DeepSeek + Gemini│  │     Gemini Flash                 │   │ │   │
│  │  │  │                  │  │                                  │   │ │   │
│  │  │  │ • Patrones       │  │  • Clasifica correos             │   │ │   │
│  │  │  │ • Mejora scores  │  │  • Clasifica WhatsApp            │   │ │   │
│  │  │  │ • Reportes       │  │  • Extrae entidades              │   │ │   │
│  │  │  │ • Re-entrenar    │  │  • Enruta al agente              │   │ │   │
│  │  │  └──────────────────┘  └──────────────────────────────────┘   │ │   │
│  │  └────────────────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CAPA DE SERVICIOS                                  │
│                                                                              │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌──────────────┐ │
│  │    Billing     │ │  Collections   │ │  Notification  │ │    Audit     │ │
│  │    Service     │ │    Service     │ │    Service     │ │   Service    │ │
│  │                │ │                │ │                │ │              │ │
│  │ • get_facturas │ │ • get_vencidas │ │ • send_email   │ │ • log_action │ │
│  │ • get_cliente  │ │ • calcular_tamn│ │ • send_whatsapp│ │ • get_log    │ │
│  │ • validar      │ │ • procesar_pago│ │ • send_sms     │ │ • get_detail │ │
│  │ • get_ofertas  │ │                │ │ • reminder     │ │              │ │
│  └───────┬────────┘ └───────┬────────┘ └───────┬────────┘ └──────┬───────┘ │
└──────────┼──────────────────┼──────────────────┼─────────────────┼─────────┘
           │                  │                  │                 │
           ▼                  ▼                  ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CAPA DE DATOS Y EXTERNAL                              │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      ALMACENAMIENTO PRINCIPAL                         │   │
│  │                                                                       │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │   │
│  │  │  PostgreSQL  │ │    Redis     │ │   Pinecone   │ │  SQL Server  │ │   │
│  │  │    16        │ │      7       │ │   (Vector)   │ │   (Legacy)   │ │   │
│  │  │              │ │              │ │              │ │              │ │   │
│  │  │ • Clientes   │ │ • Caché      │ │ • Embeddings │ │ • BSS legacy │ │   │
│  │  │ • Facturas   │ │ • Sesiones   │ │ • RAG docs   │ │ • OSS legacy │ │   │
│  │  │ • Auditoría  │ │ • Celery     │ │ • Historial  │ │ • Histórico  │ │   │
│  │  │ • Agentes    │ │ • Rate limit │ │ • SUNAT      │ │ • Solo read  │ │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      SERVICIOS EXTERNOS                               │   │
│  │                                                                       │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │   │
│  │  │    Groq      │ │   Google     │ │   Twilio     │ │  RPA Bridge  │ │   │
│  │  │  (DeepSeek)  │ │  (Gemini)    │ │  (SMS/WA)    │ │              │ │   │
│  │  │              │ │              │ │              │ │ • UiPath     │ │   │
│  │  │ • Chat       │ │ • Chat       │ │ • WhatsApp   │ │ • Automation │ │   │
│  │  │ • Reasoning  │ │ • Embeddings │ │ • SMS        │ │   Anywhere   │ │   │
│  │  │ • Decisions  │ │ • Classify   │ │ • Voice      │ │ • Mainframes │ │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Arquitectura de Agentes IA

### Diseño de Agentes con LangGraph

Cada agente es un **nodo** en un **StateGraph** de LangGraph. El **Agente Supervisor** actúa como router que decide qué nodo ejecutar a continuación basado en el estado actual.

```python
# Representación conceptual del StateGraph
from langgraph.graph import StateGraph, END

class SupervisorState(TypedDict):
    task_type: str
    next_agent: str
    result: dict
    requires_human_review: bool
    audit_log: list

graph = StateGraph(SupervisorState)

# Nodos
graph.add_node("supervisor", supervisor_node)      # DeepSeek-R1
graph.add_node("billing", billing_node)            # DeepSeek-R1
graph.add_node("collections", collections_node)    # DeepSeek-R1
graph.add_node("negotiation", negotiation_node)    # DeepSeek-R1
graph.add_node("customer", customer_node)          # Gemini Pro
graph.add_node("classifier", classifier_node)      # Gemini Flash
graph.add_node("learning", learning_node)          # Híbrido
graph.add_node("human_review", human_review_node)  # HITL

# Aristas condicionales
graph.add_conditional_edges("supervisor", route_to_agent)
graph.add_conditional_edges("billing", check_for_human_review)
```

### Comunicación entre Agentes

```
┌─────────────┐         State Update          ┌─────────────────┐
│   Agent A   │ ─────────────────────────────▶ │  LangGraph       │
│  (Producer) │                                │  State           │
└─────────────┘                                │                  │
                                               │  {               │
                                               │   task_type: ..,  │
                                               │   result: {..},  │
                                               │   next_agent: .., │
                                               │   audit_log: [..] │
                                               │  }               │
                                               └────────┬─────────┘
                                                        │
                                                 State Read
                                                        │
                                                        ▼
                                               ┌─────────────┐
                                               │   Agent B   │
                                               │  (Consumer) │
                                               └─────────────┘
```

### Ciclo de Vida de un Agente

```
┌─────────────────────────────────────────────────────────────────┐
│                    CICLO DE VIDA DEL AGENTE                       │
│                                                                  │
│  1. INIT                                                         │
│     └─▶ Agente recibe task del Supervisor                        │
│                                                                  │
│  2. VALIDATE                                                      │
│     └─▶ Valida inputs (Pydantic schemas)                         │
│                                                                  │
│  3. EXECUTE                                                       │
│     └─▶ Ejecuta lógica principal                                 │
│         • Si necesita cálculo → call_symbolic_engine()           │
│         • Si necesita IA → call_llm()                            │
│         • Si necesita datos → query_database()                   │
│                                                                  │
│  4. VALIDATE OUTPUT                                               │
│     └─▶ Verifica consistencia del resultado                      │
│                                                                  │
│  5. LOG                                                           │
│     └─▶ Registra acción en audit_log                             │
│                                                                  │
│  6. RETURN                                                        │
│     └─▶ Devuelve resultado al StateGraph                         │
│                                                                  │
│  7. ERROR HANDLING                                                │
│     └─▶ Si error → handle_error() → retry o alertar HITL         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Motor Simbólico Zero-Hallucination

### Principio Fundamental

> **Los LLMs nunca realizan cálculos matemáticos. Solo invocan funciones del Motor Simbólico.**

### Arquitectura del Motor

```
┌─────────────────────────────────────────────────────────────┐
│                  MOTOR SIMBÓLICO                              │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              CalculationEngine                        │   │
│  │                                                       │   │
│  │  • calcular_prorrateo_pxq(cargo, inicio, fin)         │   │
│  │    → (Cargo / DíasMes) * DíasUso                     │   │
│  │    → Redondeo SUNAT: 2 decimales, ROUND_HALF_UP       │   │
│  │                                                       │   │
│  │  • calcular_igv(monto_total)                          │   │
│  │    → Base = Total / 1.18                              │   │
│  │    → IGV = Base * 0.18                                │   │
│  │                                                       │   │
│  │  • calcular_igv_desde_base(base)                      │   │
│  │    → IGV = Base * 0.18                                │   │
│  │                                                       │   │
│  │  • calcular_interes_tamn(deuda, dias, factor_v,       │   │
│  │                          factor_a)                    │   │
│  │    → Interés = Deuda * (Factor_A/Factor_V - 1)        │   │
│  │                                                       │   │
│  │  • calcular_total_factura(subtotal, igv)              │   │
│  │    → Total = Subtotal + IGV                           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              TaxationEngine                           │   │
│  │                                                       │   │
│  │  • calcular_base_imponible(total)                     │   │
│  │  • calcular_retencion_igv(igv, aplica)                │   │
│  │  • validar_serie_correlativo(serie, correlativo)      │   │
│  │  • validar_numero_documento(tipo, numero)             │   │
│  │  • redondear_sunat(monto)                             │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              ConfidenceScorer                         │   │
│  │                                                       │   │
│  │  • calcular_score(antiguedad, mora, disputas,         │   │
│  │                   pagos_tarde, monto, segmento)       │   │
│  │  • es_cliente_confiable(score) → bool                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Tipos de Datos para Precisión

| Dato | Tipo Python | Razón |
|------|-------------|-------|
| Montos monetarios | `Decimal` | Precisión exacta, sin errores de punto flotante |
| Fechas | `date` | Sin ambigüedad de zona horaria |
| Scores | `Decimal` (0-1) | 2 decimales de precisión |
| Porcentajes | `Decimal` | Cálculos exactos de IGV, descuentos |

---

## Base de Datos

### Esquema Relacional

```sql
-- ============================================
-- BSS (Business Support System)
-- ============================================

-- 1. Maestra de Clientes
CREATE TABLE bss_clientes (
    id_cliente BIGINT PRIMARY KEY,
    tipo_doc VARCHAR(2) NOT NULL,           -- '1'=DNI, '6'=RUC
    num_doc VARCHAR(20) UNIQUE NOT NULL,
    nombre_razon_social VARCHAR(255) NOT NULL,
    segmento VARCHAR(50),                   -- B2B, B2C, Gobierno
    email_contacto VARCHAR(100),
    telefono_contacto VARCHAR(20),
    score_confianza DECIMAL(5,2) DEFAULT 0.80, -- Perfil de confianza (0-1)
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Cuentas de Facturación
CREATE TABLE bss_cuentas (
    id_cuenta BIGINT PRIMARY KEY,
    id_cliente BIGINT REFERENCES bss_clientes(id_cliente),
    ciclo_facturacion INT NOT NULL,         -- Día del mes (5,10,15,20,25,30)
    metodo_pago VARCHAR(50),
    estado_cuenta VARCHAR(20),
    limite_credito DECIMAL(14,2),
    dias_plazo_estandar INT DEFAULT 8,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. Facturación - Cabecera
CREATE TABLE bss_factura_cabecera (
    id_factura BIGINT PRIMARY KEY,
    id_cuenta BIGINT REFERENCES bss_cuentas(id_cuenta),
    serie VARCHAR(4) NOT NULL,
    correlativo BIGINT NOT NULL,
    f_emision DATE NOT NULL,
    f_vencimiento DATE NOT NULL,
    subtotal_gravado DECIMAL(14,2),
    igv_total DECIMAL(14,2),
    importe_total DECIMAL(14,2),
    estado_pago VARCHAR(20),
    validacion_automatica BOOLEAN DEFAULT FALSE,
    UNIQUE(serie, correlativo),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 4. Facturación - Detalle
CREATE TABLE bss_factura_detalle (
    id_detalle SERIAL PRIMARY KEY,
    id_factura BIGINT REFERENCES bss_factura_cabecera(id_factura),
    id_servicio BIGINT REFERENCES oss_planta(id_servicio),
    concepto VARCHAR(100),
    periodo_inicio DATE,
    periodo_fin DATE,
    monto_linea DECIMAL(14,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 5. Ofertas de Negociación
CREATE TABLE bss_ofertas_negociacion (
    id_oferta SERIAL PRIMARY KEY,
    id_factura BIGINT REFERENCES bss_factura_cabecera(id_factura),
    fecha_oferta DATE,
    descuento_ofrecido DECIMAL(5,2),
    nuevo_plazo_dias INT,
    fecha_limite_aceptacion DATE,
    estado VARCHAR(20),                    -- pendiente, aceptada, rechazada, expirada
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 6. Historial de Pagos
CREATE TABLE bss_historial_pagos (
    id_historial SERIAL PRIMARY KEY,
    id_cliente BIGINT REFERENCES bss_clientes(id_cliente),
    fecha_vencimiento DATE NOT NULL,
    fecha_pago DATE,
    dias_mora INT,
    monto_pagado DECIMAL(14,2),
    fue_disputado BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- OSS (Operations Support System)
-- ============================================

-- 7. Planta - Servicios Técnicos
CREATE TABLE oss_planta (
    id_servicio BIGINT PRIMARY KEY,
    id_cuenta BIGINT REFERENCES bss_cuentas(id_cuenta),
    tecnologia VARCHAR(20),                -- Fibra Óptica, ADSL, Cloud, etc.
    identificador_recurso VARCHAR(50) UNIQUE NOT NULL,
    cargo_fijo_mensual DECIMAL(14,2) NOT NULL,
    fecha_alta DATE NOT NULL,
    estado_servicio VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Diagrama de Relaciones

```
bss_clientes (1) ──────────< (N) bss_cuentas
bss_cuentas (1) ───────────< (N) oss_planta
bss_cuentas (1) ───────────< (N) bss_factura_cabecera
bss_factura_cabecera (1) ──< (N) bss_factura_detalle
bss_factura_cabecera (1) ──< (N) bss_ofertas_negociacion
bss_clientes (1) ──────────< (N) bss_historial_pagos
oss_planta (1) ────────────< (N) bss_factura_detalle
```

### Índices para Rendimiento

```sql
-- Índices principales
CREATE INDEX idx_cliente_segmento ON bss_clientes(segmento);
CREATE INDEX idx_cuenta_cliente ON bss_cuentas(id_cliente);
CREATE INDEX idx_factura_cuenta ON bss_factura_cabecera(id_cuenta);
CREATE INDEX idx_factura_fechas ON bss_factura_cabecera(f_emision, f_vencimiento);
CREATE INDEX idx_factura_estado ON bss_factura_cabecera(estado_pago);
CREATE INDEX idx_historial_cliente ON bss_historial_pagos(id_cliente);
CREATE INDEX idx_oferta_factura ON bss_ofertas_negociacion(id_factura);
CREATE INDEX idx_oferta_estado ON bss_ofertas_negociacion(estado);
```

---

## Integraciones Externas

### Groq API (DeepSeek-R1)

```
┌─────────────────────────────────────────────────────────────┐
│                    GROQ API CONFIGURATION                     │
│                                                              │
│  Base URL: https://api.groq.com/openai/v1                    │
│  Auth: Bearer {GROQ_API_KEY}                                 │
│  Model: deepseek-r1-distill-llama-70b                        │
│                                                              │
│  Endpoints Usados:                                           │
│  • POST /chat/completions - Generación de texto              │
│                                                              │
│  Parámetros:                                                 │
│  • temperature: 0.0-0.1 (decisiones financieras)             │
│  • max_tokens: 1000-4096                                     │
│  • response_format: { "type": "json_object" } (opcional)     │
│                                                              │
│  Límites:                                                    │
│  • Rate: Depende del plan (gratuito: 30 req/min)             │
│  • Contexto: 8K tokens                                       │
└─────────────────────────────────────────────────────────────┘
```

### Google Gemini API

```
┌─────────────────────────────────────────────────────────────┐
│                  GEMINI API CONFIGURATION                     │
│                                                              │
│  Auth: API Key en header                                     │
│                                                              │
│  Modelos:                                                    │
│  • gemini-1.5-pro  → Customer Agent (NLP, RAG)              │
│  • gemini-1.5-flash → Classifier Agent (rápido, económico)   │
│                                                              │
│  Endpoints:                                                  │
│  • generateContent - Generación de texto                     │
│  • embedContent - Generación de embeddings                   │
│                                                              │
│  Límites (cuota gratuita):                                   │
│  • Pro: 2 RPM, 32K TPM                                      │
│  • Flash: 15 RPM, 1M TPM                                    │
│  • Embeddings: 1500 RPM                                     │
└─────────────────────────────────────────────────────────────┘
```

### SQL Server (Legacy BSS/OSS)

```
┌─────────────────────────────────────────────────────────────┐
│              SQL SERVER CONNECTOR (Solo Lectura)              │
│                                                              │
│  Driver: pymssql                                             │
│  Conexión: mssql+pymssql://user:pass@host:1433/db            │
│                                                              │
│  Tablas Legacy:                                              │
│  • clientes_históricos                                       │
│  • facturación_anterior                                      │
│  • servicios_planta                                          │
│                                                              │
│  Uso:                                                        │
│  • Migración gradual a PostgreSQL                            │
│  • Consultas históricas para modelos ML                      │
│  • Validación cruzada de datos                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Modelos de IA y ML

### Asignación de Modelos por Agente

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA HÍBRIDA DE IA                     │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              DEEPSEEK-R1 (Groq LPU)                       │    │
│  │                                                           │    │
│  │  Agentes:                                                 │    │
│  │  • Supervisor Agent    → Razonamiento + Enrutamiento      │    │
│  │  • Billing Agent       → Análisis datos estructurados     │    │
│  │  • Collections Agent   → Predicción + Priorización        │    │
│  │  • Negotiation Agent   → Optimización de ofertas          │    │
│  │                                                           │    │
│  │  Características:                                         │    │
│  │  • Razonamiento multi-paso                                │    │
│  │  • Chain-of-thought                                      │    │
│  │  • Decisiones deterministas (temperature=0.0-0.1)         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              GEMINI 1.5 PRO (Google)                      │    │
│  │                                                           │    │
│  │  Agentes:                                                 │    │
│  │  • Customer Agent      → Chat contextual + RAG            │    │
│  │  • Learning Agent      → Análisis de textos               │    │
│  │                                                           │    │
│  │  Características:                                         │    │
│  │  • Excelente NLP en español                               │    │
│  │  • Generación de texto natural y empático                 │    │
│  │  • Ventana de contexto 1M tokens                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              GEMINI 1.5 FLASH (Google)                    │    │
│  │                                                           │    │
│  │  Agentes:                                                 │    │
│  │  • Classifier Agent    → Clasificación de mensajes        │    │
│  │                                                           │    │
│  │  Características:                                         │    │
│  │  • Ultra-rápido (<500ms)                                  │    │
│  │  • Bajo costo por request                                 │    │
│  │  • Ideal para clasificación en tiempo real                │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              MODELOS LOCALES (Python)                     │    │
│  │                                                           │    │
│  │  • XGBoost Classifier → Score de Confianza               │    │
│  │  • XGBoost Classifier → Predicción de Pago               │    │
│  │  • Isolation Forest   → Detección de Anomalías           │    │
│  │                                                           │    │
│  │  Características:                                         │    │
│  │  • Inferencia <10ms (local, sin API call)                 │    │
│  │  • Re-entrenamiento mensual con datos históricos          │    │
│  │  • Features: antigüedad, mora, disputas, segmento         │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Flujos de Datos

### Ciclo de Facturación Completo (Secuencia)

```
Cliente    Dashboard    Supervisor    BillingAgent    MotorSim    PostgreSQL
  │            │            │              │              │            │
  │            │  POST      │              │              │            │
  │            │ /billing/  │              │              │            │
  │            │ ciclos/    │              │              │            │
  │            │ ejecutar   │              │              │            │
  │            │───────────▶│              │              │            │
  │            │            │              │              │            │
  │            │            │  execute()   │              │            │
  │            │            │─────────────▶│              │            │
  │            │            │              │              │            │
  │            │            │              │ SELECT *     │            │
  │            │            │              │ FROM oss_    │            │
  │            │            │              │ planta       │            │
  │            │            │              │─────────────▶│            │
  │            │            │              │◀─────────────│            │
  │            │            │              │              │            │
  │            │            │              │ SELECT score │            │
  │            │            │              │ FROM bss_    │            │
  │            │            │              │ clientes     │            │
  │            │            │              │─────────────▶│            │
  │            │            │              │◀─────────────│            │
  │            │            │              │              │            │
  │            │            │              │ calcular_    │            │
  │            │            │              │ prorrateo_   │            │
  │            │            │              │ pxq()        │            │
  │            │            │              │─────────────▶│            │
  │            │            │              │◀───S/ 150.00─│            │
  │            │            │              │              │            │
  │            │            │              │ calcular_    │            │
  │            │            │              │ igv()        │            │
  │            │            │              │─────────────▶│            │
  │            │            │              │◀───S/ 27.00──│            │
  │            │            │              │              │            │
  │            │            │              │ Score ≥ 0.80?│            │
  │            │            │              │ → validación │            │
  │            │            │              │   automática │            │
  │            │            │              │              │            │
  │            │            │              │ INSERT INTO  │            │
  │            │            │              │ bss_factura_ │            │
  │            │            │              │ cabecera +   │            │
  │            │            │              │ detalle      │            │
  │            │            │              │─────────────▶│            │
  │            │            │              │◀───OK────────│            │
  │            │            │              │              │            │
  │            │            │◀──Factura────│              │            │
  │            │            │   generada   │              │            │
  │            │            │              │              │            │
  │            │◀──Métricas─│              │              │            │
  │            │   actualiz │              │              │            │
  │            │            │              │              │            │
  │◀─Notif.───│            │              │              │            │
  │  (email/  │            │              │              │            │
  │  WhatsApp)│            │              │              │            │
```

---

## Seguridad y Gobernanza

### Capas de Seguridad

| Capa | Medida | Implementación |
|------|--------|----------------|
| **API** | JWT Authentication | Tokens con expiración, refresh tokens |
| **API** | Rate Limiting | 100 req/min por IP, 1000 req/min por usuario |
| **API** | CORS | Orígenes permitidos configurados |
| **Datos** | Anonimización en logs | Números de documento enmascarados |
| **Datos** | Encriptación en tránsito | HTTPS/TLS 1.3 |
| **Datos** | Secrets Management | Variables de entorno, nunca en código |
| **IA** | Prompt Injection Prevention | Sanitización de inputs de usuario |
| **IA** | Output Validation | Validación Pydantic de respuestas de LLM |
| **Negocio** | Human-in-the-Loop | Excepciones requieren aprobación |
| **Negocio** | Audit Log Inmutable | Registro de cada acción de cada agente |
| **Infra** | Network Isolation | Redes Docker separadas |
| **Infra** | Health Checks | Monitoreo continuo de todos los servicios |

---

## Estrategia de Despliegue

### Ambiente de Desarrollo

```yaml
# docker-compose.yml (Desarrollo)
services:
  backend:     # FastAPI con --reload, puerto 8000
  frontend:    # Next.js con hot reload, puerto 3000
  postgres:    # PostgreSQL 16, puerto 5432
  redis:       # Redis 7, puerto 6379
  celery:      # Worker Celery
  flower:      # Monitoreo Celery, puerto 5555
```

### Ambiente de Producción

```yaml
# Consideraciones producción:
servicios:
  backend:
    - Gunicorn + Uvicorn workers (4-8 procesos)
    - Health checks para load balancer
    - Logs a stdout para ELK/CloudWatch
  
  postgres:
    - Replicación streaming (primary + 1 replica)
    - Backups automáticos cada 6 horas
    - Point-in-time recovery habilitado
  
  redis:
    - Redis Sentinel para alta disponibilidad
    - Persistencia RDB + AOF
  
  frontend:
    - Static export o SSR con caching
    - CDN para assets estáticos
  
  monitoreo:
    - Prometheus + Grafana para métricas
    - ELK Stack para logs centralizados
    - Sentry para error tracking
    - Uptime monitoring externo
```

### Estrategia de Rollback

```
┌─────────────────────────────────────────────────────────────┐
│                  PLAN DE CONTINGENCIA                         │
│                                                              │
│  Fase 1: Shadow Mode (Mes 1)                                 │
│  └─▶ IA ejecuta en paralelo con proceso humano               │
│      • No afecta operación real                              │
│      • Comparación de resultados                             │
│      • Ajuste de modelos                                     │
│                                                              │
│  Fase 2: Despliegue Controlado (Mes 2-3)                     │
│  └─▶ 20% → 50% → 100% de facturas                           │
│      • Monitoreo constante                                   │
│      • Rollback instantáneo si error                         │
│                                                              │
│  Fase 3: Operación Completa (Mes 4+)                         │
│  └─▶ Sistema en producción                                   │
│      • Rollback automático si Supervisor detecta anomalía    │
│      • Equipo de respuesta 24/7 primeros 3 meses             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Diagrama de Infraestructura

```
                          ┌──────────────┐
                          │   Internet   │
                          └──────┬───────┘
                                 │
                                 ▼
                          ┌──────────────┐
                          │ Load Balancer│
                          │  (Nginx)     │
                          └──────┬───────┘
                                 │
                 ┌───────────────┼───────────────┐
                 │               │               │
                 ▼               ▼               ▼
          ┌────────────┐ ┌────────────┐ ┌────────────┐
          │ Frontend   │ │ Frontend   │ │ Frontend   │
          │ Instance 1 │ │ Instance 2 │ │ Instance N │
          └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
                 │               │               │
                 └───────────────┼───────────────┘
                                 │
                                 ▼
                          ┌──────────────┐
                          │ API Gateway  │
                          │  (FastAPI)   │
                          └──────┬───────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
  ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
  │  Backend     │       │  Celery      │       │  Celery      │
  │  Instance 1  │       │  Worker 1    │       │  Worker 2    │
  └──────┬───────┘       └──────┬───────┘       └──────┬───────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
         ┌────────────┐ ┌────────────┐ ┌────────────┐
         │ PostgreSQL │ │   Redis    │ │  Pinecone  │
         │  Primary   │ │  Sentinel  │ │  (Vector)  │
         └─────┬──────┘ └────────────┘ └────────────┘
               │
               ▼
         ┌────────────┐
         │ PostgreSQL │
         │  Replica   │
         └────────────┘
```

