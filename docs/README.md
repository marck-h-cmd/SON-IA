
# SON-IA: Sinergia Operativa del Negocio - Integratel Agéntica

<div align="center">

![SON-IA](https://img.shields.io/badge/SON--IA-v0.1.0-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![Groq](https://img.shields.io/badge/Groq-DeepSeek--R1-orange)
![Gemini](https://img.shields.io/badge/Google-Gemini%201.5-blue)

**Ecosistema de Agentes IA para Automatización de Facturación, Recaudación y Cobranzas**

</div>

---

## 📋 Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Problema que Resuelve](#problema-que-resuelve)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Inicio Rápido](#inicio-rápido)
5. [Estructura del Proyecto](#estructura-del-proyecto)
6. [Agentes IA](#agentes-ia)
7. [Modelos de IA](#modelos-de-ia)
8. [Métricas e Impacto](#métricas-e-impacto)
9. [Documentación Adicional](#documentación-adicional)

---

## 🎯 Visión General

**SON-IA** (Sinergia Operativa del Negocio – Integratel Agéntica) es un ecosistema de agentes de Inteligencia Artificial diseñado para revolucionar los procesos de facturación, recaudación y cobranzas de Integratel.

El sistema despliega **7 agentes especializados** que trabajan de forma coordinada bajo un **Agente Supervisor** con supervisión humana en excepciones (Human-in-the-Loop), garantizando eficiencia operativa, precisión financiera y cumplimiento normativo.

### 🚀 Características Principales

| Característica | Descripción |
|----------------|-------------|
| 🤖 **7 Agentes Especializados** | Supervisor, Facturación, Cobranzas, Negociación, Atención al Cliente, Aprendizaje y Clasificación |
| 🧠 **IA Híbrida Multi-Proveedor** | DeepSeek-R1 (vía Groq LPU) para razonamiento + Gemini 1.5 Pro/Flash para NLP |
| 📊 **Motor Simbólico Zero-Hallucination** | Cálculos exactos PxQ, IGV, TAMN en Python - Los LLMs nunca hacen matemáticas |
| 🔒 **Human-in-the-Loop (HITL)** | Supervisión humana obligatoria en excepciones críticas y anomalías |
| 💬 **RAG con Gemini Embeddings** | Chat contextual que explica facturas usando historial real del cliente |
| ⚡ **Tiempo Real** | WebSockets para dashboard en vivo y notificaciones push |
| 📈 **Modelos Predictivos Locales** | XGBoost para score de confianza y predicción de pago |
| 🏦 **Cumplimiento SUNAT** | Normativa peruana completa: IGV 18%, TAMN, Recibos Tipo 14, Prorrateos PxQ |

### 🎯 Enfoque Predictivo y de Micro-Negociación

SON-IA incorpora un enfoque **proactivo** que permite:

- **Anticipar** comportamientos de pago antes del vencimiento
- **Validar** clientes de forma dinámica según su perfil de confianza
- **Negociar** condiciones en tiempo real antes de que se generen moras
- **Aprender** de cada interacción para mejorar continuamente

---

## 🎯 Problema que Resuelve

### Situación Actual en Integratel

| Problema | Impacto |
|----------|---------|
| **Procesos Manuales de Facturación** | Validaciones manuales, revisión cruzada de archivos, coordinación entre áreas (postventa, implantación, ingeniería, comercial) |
| **Información Dispersa** | Datos en SQL Server, Teradata y plataformas propias sin integración |
| **Cobranzas Externalizadas** | Gestión tradicional con correos y llamadas, buzones no centralizados ni automatizados |
| **Cobranza Reactiva** | Se activa cuando el cliente ya está en mora (30+ días), perdiendo oportunidad de negociación temprana |
| **Riesgo de Errores** | Cálculos PxQ con errores, servicios no facturados, fuga de ingresos |
| **Sin Trazabilidad** | Deficiente registro de decisiones y cambios en facturación |

### Cómo SON-IA lo Resuelve

| Problema | Solución SON-IA | Impacto Esperado |
|----------|-----------------|------------------|
| ❌ Procesos Manuales | ✅ Automatización E2E con agentes especializados | 80% ahorro en horas-hombre |
| ❌ Información Dispersa | ✅ Integración con SQL Server, Teradata y sistemas legacy vía RPA | Fuente única de verdad |
| ❌ Cobranzas Reactivas | ✅ Negociación Predictiva 5 días antes del vencimiento | +20% recupero de cartera |
| ❌ Errores de Cálculo | ✅ Motor Simbólico determinista (Python Decimal) | 99.9% exactitud |
| ❌ Comunicaciones No Centralizadas | ✅ Buzón Único con Clasificación IA (Gemini Flash) | +30% resolución en primer contacto |
| ❌ Sin Trazabilidad | ✅ Auditoría Inmutable de cada acción de cada agente | Cumplimiento normativo total |

---

## 🏗️ Arquitectura del Sistema

### Diagrama de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js 14)                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐ │
│  │ Dashboard  │  │   Portal   │  │    Chat    │  │  Reportes  │ │
│  │  Interno   │  │  Cliente   │  │ Contextual │  │     BI     │ │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘ │
└────────┼───────────────┼───────────────┼───────────────┼────────┘
         │               │               │               │
         ▼               ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                   API GATEWAY (FastAPI)                           │
│  • REST API v1  • WebSockets  • JWT Auth  • Rate Limiting       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                ORQUESTADOR (LangGraph)                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │           AGENTE SUPERVISOR (DeepSeek-R1 vía Groq)         │  │
│  │           • Router de Tareas  • HITL  • Auditoría          │  │
│  └──┬────────┬────────┬────────┬────────┬────────┬──────────┘  │
│     │        │        │        │        │        │              │
│     ▼        ▼        ▼        ▼        ▼        ▼              │
│  ┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────────┐        │
│  │Bill. ││Collec││Negot ││Custom││Learn ││Classif   │        │
│  │Agent ││Agent ││Agent ││Agent ││Agent ││Agent     │        │
│  └──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘└────┬─────┘        │
└─────┼───────┼───────┼───────┼───────┼───────┼──────────────┘
      │       │       │       │       │       │
      ▼       ▼       ▼       ▼       ▼       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CAPA DE DATOS                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │PostgreSQL│ │  Redis   │ │ Pinecone │ │  SQL Server      │   │
│  │(Agentes) │ │ (Caché)  │ │ (Vector) │ │  (Legacy BSS)    │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Modelos de IA por Proveedor

| Modelo | Proveedor | Agentes Asignados | Función Principal |
|--------|-----------|-------------------|-------------------|
| **DeepSeek-R1** | Groq (LPU) | Supervisor, Billing, Collections, Negotiation | Razonamiento complejo, decisiones críticas, análisis financiero |
| **Gemini 1.5 Pro** | Google | Customer Agent | NLP, generación de texto, RAG, chat contextual |
| **Gemini 1.5 Flash** | Google | Classifier Agent | Clasificación rápida de mensajes (bajo costo, alta velocidad) |
| **XGBoost** | Local | Inference Service | Score de confianza, predicción de pago |
| **Isolation Forest** | Local | Inference Service | Detección de anomalías en facturación |

### ¿Por qué Groq para DeepSeek-R1?

| Ventaja | Descripción |
|---------|-------------|
| ⚡ **Velocidad** | LPU (Language Processing Unit) - Inferencia en <500ms |
| 🔌 **API OpenAI-Compatible** | Mismo formato que OpenAI, integración sin fricción |
| 💰 **Costo Competitivo** | Precios por token accesibles para uso empresarial |
| 🎯 **Precisión** | DeepSeek-R1 optimizado para razonamiento matemático y lógico |
| 🔒 **Soberanía Tecnológica** | Sin dependencia de un único proveedor de IA |

---

## 🚀 Inicio Rápido

### Prerrequisitos

| Herramienta | Versión Mínima | Descarga |
|-------------|---------------|----------|
| Python | 3.11+ | [python.org](https://python.org) |
| Node.js | 20+ | [nodejs.org](https://nodejs.org) |
| PostgreSQL | 16 | [postgresql.org](https://postgresql.org) |
| Redis | 7 | [redis.io](https://redis.io) |
| Docker | 24+ | [docker.com](https://docker.com) |
| Git | 2.40+ | [git-scm.com](https://git-scm.com) |

### APIs Externas (Claves Gratuitas Disponibles)

| API | Registro | Cuota Gratuita |
|-----|----------|----------------|
| **Groq** (DeepSeek-R1) | [console.groq.com](https://console.groq.com) | Créditos iniciales gratuitos |
| **Google Gemini** | [aistudio.google.com](https://aistudio.google.com) | 60 requests/minuto gratis |
| **Pinecone** (Vector DB) | [pinecone.io](https://pinecone.io) | 1 índice gratis (hasta 100K vectores) |

### 🐳 Instalación con Docker (Recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/integratel/son-ia-mvp.git
cd son-ia-mvp

# 2. Configurar variables de entorno
cp backend/.env.example backend/.env
# Editar backend/.env con tus claves API:
#   GROQ_API_KEY=gsk_xxxxxxxx
#   GEMINI_API_KEY=xxxxxxxx

# 3. Iniciar todos los servicios
docker-compose up -d

# 4. Verificar que todo está corriendo
docker-compose ps

# 5. Sembrar datos de prueba
docker-compose exec backend python scripts/seed-database.py

# 6. Acceder a los servicios
# API Docs:   http://localhost:8000/api/docs
# Frontend:   http://localhost:3000
# Flower:     http://localhost:5555
```

### 💻 Instalación para Desarrollo

```bash
# ========== BACKEND ==========
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Editar con tus claves API

# Inicializar base de datos
python ../scripts/seed-database.py

# Iniciar servidor
uvicorn app.main:app --reload --port 8000


# ========== FRONTEND (Nueva Terminal) ==========
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### ✅ Verificación de Instalación

```bash
# Health Check del Backend
curl http://localhost:8000/api/v1/health
# Respuesta esperada:
# {"status":"ok","app":"SON-IA","version":"0.1.0"}

# Health Check Detallado
curl http://localhost:8000/api/v1/health/detailed
# Respuesta esperada:
# {"status":"ok","components":{"api":"ok","database":"ok"}}

# Métricas del Dashboard
curl http://localhost:8000/api/v1/dashboard/metrics

# Estado de los Agentes
curl http://localhost:8000/api/v1/dashboard/agentes/estado

# Listar Clientes de Prueba
curl http://localhost:8000/api/v1/clients/
```

---

## 📁 Estructura del Proyecto

```
son-ia-mvp/
│
├── 📁 backend/                          # API FastAPI + Lógica de Negocio
│   ├── app/
│   │   ├── agents/                     # 7 Agentes IA orquestados con LangGraph
│   │   │   ├── base_agent.py           # Clase base abstracta para todos los agentes
│   │   │   ├── supervisor_agent.py     # Orquestador central (DeepSeek-R1)
│   │   │   ├── billing_agent.py        # Facturación y validación (DeepSeek-R1)
│   │   │   ├── collections_agent.py    # Cobranzas y TAMN (DeepSeek-R1)
│   │   │   ├── negotiation_agent.py    # Negociación predictiva (DeepSeek-R1)
│   │   │   ├── customer_agent.py       # Atención al cliente (Gemini Pro)
│   │   │   ├── learning_agent.py       # Aprendizaje continuo (Híbrido)
│   │   │   └── classifier_agent.py     # Clasificación mensajes (Gemini Flash)
│   │   │
│   │   ├── api/v1/                     # Endpoints REST + WebSockets
│   │   │   ├── router.py               # Router principal v1
│   │   │   ├── endpoints/              # Endpoints por módulo
│   │   │   │   ├── health.py           # Health checks
│   │   │   │   ├── billing.py          # Facturación
│   │   │   │   ├── clients.py          # Clientes
│   │   │   │   ├── dashboard.py        # Dashboard métricas
│   │   │   │   ├── collections.py      # Cobranzas
│   │   │   │   ├── negotiations.py     # Negociaciones
│   │   │   │   └── audit.py            # Auditoría
│   │   │   └── websockets/             # WebSockets tiempo real
│   │   │
│   │   ├── core/                       # Motor Simbólico Zero-Hallucination
│   │   │   ├── calculation_engine.py   # Cálculos PxQ, IGV, TAMN
│   │   │   ├── confidence_scorer.py    # Score de confianza (reglas)
│   │   │   ├── taxation.py             # Normativa SUNAT Perú
│   │   │   ├── validators.py           # Validaciones (RUC, DNI, montos)
│   │   │   └── constants.py            # Constantes del negocio
│   │   │
│   │   ├── database/                   # Modelos SQLAlchemy + Migraciones Alembic
│   │   │   ├── models.py               # 7 tablas: clientes, cuentas, facturas, etc.
│   │   │   ├── connection.py           # Conexiones PostgreSQL y SQL Server
│   │   │   ├── schemas.py              # Schemas Pydantic para validación
│   │   │   └── migrations/             # Migraciones Alembic
│   │   │
│   │   ├── integrations/               # Clientes para servicios externos
│   │   │   ├── deepseek_client.py      # Groq API (DeepSeek-R1)
│   │   │   ├── gemini_client.py        # Google Gemini API
│   │   │   ├── teradata_connector.py   # Conector Teradata Legacy
│   │   │   ├── sqlserver_connector.py  # Conector SQL Server Legacy
│   │   │   └── rpa_bridge.py           # Puente RPA (UiPath/Automation Anywhere)
│   │   │
│   │   ├── models/                     # Modelos ML entrenados
│   │   │   ├── trained/                # Archivos .pkl
│   │   │   ├── inference.py            # Servicio de inferencia
│   │   │   └── model_loader.py         # Carga de modelos
│   │   │
│   │   ├── rag/                        # Retrieval Augmented Generation
│   │   │   ├── embeddings.py           # Gemini Embeddings
│   │   │   ├── vector_store.py         # Pinecone / PGVector
│   │   │   └── retrieval.py            # Servicio de recuperación
│   │   │
│   │   ├── services/                   # Lógica de negocio
│   │   │   ├── billing_service.py      # Servicio de facturación
│   │   │   ├── collections_service.py  # Servicio de cobranzas
│   │   │   ├── notification_service.py # Notificaciones (email, WhatsApp, SMS)
│   │   │   └── audit_service.py        # Servicio de auditoría
│   │   │
│   │   ├── tasks/                      # Tareas asíncronas Celery
│   │   │   ├── celery_app.py           # Configuración Celery
│   │   │   ├── billing_tasks.py        # Tareas de facturación
│   │   │   └── notification_tasks.py   # Tareas de notificación
│   │   │
│   │   ├── training/                   # Scripts de entrenamiento ML
│   │   │   ├── train_score_confianza.py
│   │   │   └── train_prediccion_pago.py
│   │   │
│   │   └── utils/                      # Utilidades generales
│   │       ├── date_utils.py           # Manejo de fechas
│   │       ├── number_utils.py         # Manejo de números y Decimal
│   │       └── security.py             # Hash, tokens, sanitización
│   │
│   ├── tests/                          # Tests unitarios e integración
│   │   ├── conftest.py                 # Fixtures compartidas
│   │   ├── unit/                       # Tests unitarios
│   │   └── integration/                # Tests de integración
│   │
│   ├── .env.example                    # Template de variables de entorno
│   ├── requirements.txt                # Dependencias Python
│   ├── Dockerfile                      # Imagen Docker
│   └── pyproject.toml                  # Configuración del proyecto
│
├── 📁 frontend/                        # Next.js 14 + Tailwind CSS
│   └── src/
│       ├── app/                        # App Router (Next.js 14)
│       ├── components/                 # Componentes React reutilizables
│       ├── hooks/                      # Custom hooks (useMetrics, useInvoices, etc.)
│       ├── services/                   # Cliente API (axios)
│       ├── types/                      # TypeScript types
│       └── styles/                     # Estilos globales
│
├── 📁 docs/                            # Documentación ← ESTÁS AQUÍ
│   ├── README.md                       # Este archivo
│   ├── architecture.md                 # Arquitectura técnica detallada
│   ├── api-reference.md                # Referencia completa de API
│   ├── deployment.md                   # Guía de despliegue
│   └── contribution-guide.md           # Guía de contribución
│
├── 📁 scripts/                         # Scripts de utilidad
│   ├── setup-dev.sh                    # Configuración automática de desarrollo
│   ├── seed-database.py                # Datos de prueba
│   └── run-tests.sh                    # Ejecutar tests
│
├── 📁 .github/workflows/               # CI/CD
│   ├── backend-tests.yml               # Tests automáticos backend
│   └── frontend-tests.yml              # Tests automáticos frontend
│
├── docker-compose.yml                  # Orquestación de servicios
├── Makefile                            # Comandos de desarrollo
└── .gitignore                          # Archivos ignorados por Git
```

---

## 🤖 Agentes IA

### Arquitectura de Agentes

El corazón de SON-IA es su ecosistema de **7 agentes especializados** orquestados con **LangGraph**:

```
                         ┌─────────────────────────┐
                         │    AGENTE SUPERVISOR     │
                         │    Modelo: DeepSeek-R1   │
                         │    (Groq LPU)            │
                         │                         │
                         │    • Router de Tareas    │
                         │    • HITL Manager        │
                         │    • System Health       │
                         └────────────┬────────────┘
                                      │
          ┌───────────────┬───────────┼───────────┬───────────────┐
          │               │           │           │               │
          ▼               ▼           ▼           ▼               ▼
┌─────────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐
│   FACTURACIÓN   │ │  COBRANZAS  │ │ NEGOCIACIÓN │ │   ATENCIÓN  │ │  CLASIFICACIÓN  │
│   DeepSeek-R1   │ │ DeepSeek-R1 │ │ DeepSeek-R1 │ │  Gemini Pro │ │  Gemini Flash   │
│                 │ │             │ │             │ │             │ │                 │
│ • PxQ, IGV      │ │ • TAMN      │ │ • Descuentos│ │ • Chat RAG  │ │ • Correos       │
│ • Validación    │ │ • Conciliar │ │ • Predicción│ │ • Explicar  │ │ • WhatsApp      │
│ • Emisión       │ │ • Notificar │ │ • Ofertas   │ │ • Soporte   │ │ • Enrutar       │
└─────────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────┘
          │               │           │           │               │
          └───────────────┴───────────┼───────────┴───────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │      APRENDIZAJE        │
                         │   DeepSeek + Gemini     │
                         │                         │
                         │   • Patrones de error   │
                         │   • Mejora continua     │
                         │   • Reportes mensuales  │
                         └─────────────────────────┘
```

### Descripción de Agentes

| Agente | Modelo | Función Principal | Principales Habilidades |
|--------|--------|-------------------|------------------------|
| **Supervisor** | DeepSeek-R1 | Orquestador central del ecosistema | `delegate_task()`, `check_system_health()`, `trigger_human_review()`, `log_audit()` |
| **Billing** | DeepSeek-R1 | Estructurar documentos de cobro | `call_symbolic_engine()`, lectura OSS/BSS, `validate_anomalies()` |
| **Collections** | DeepSeek-R1 | Gestionar cartera morosa | `calculate_tamn()`, `prioritize_accounts()`, `get_mora_stage()` |
| **Negotiation** | DeepSeek-R1 | Ofertas predictivas pre-vencimiento | `optimize_discount()`, `simulate_scenarios()`, `generar_oferta()` |
| **Customer** | Gemini Pro | Atención y explicación al cliente | RAG, `explain_invoice()`, `answer_question()` |
| **Learning** | Híbrido | Análisis de patrones y mejora | `analyze_patterns()`, `generate_report()`, `optimize_scores()` |
| **Classifier** | Gemini Flash | Clasificar mensajes entrantes | `classify_message()`, `extract_entities()`, enrutamiento |

### Flujo de Trabajo End-to-End

```
ETAPA 0: PREDICCIÓN PROACTIVA (T-7 días antes del cierre)
┌─────────────────────────────────────────────────────────┐
│  • Agente Predictivo estima facturación del ciclo       │
│  • Detecta quiebres potenciales (consumo anómalo)       │
│  • Envía alertas tempranas al equipo de facturación     │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
ETAPA 1: PREPARACIÓN Y VALIDACIÓN DINÁMICA
┌─────────────────────────────────────────────────────────┐
│  • Supervisor inicia el ciclo de facturación            │
│  • Billing Agent recopila OSS_Planta + BSS_Clientes     │
│  • Motor Simbólico calcula PxQ, IGV (NO el LLM)        │
│  • Score ≥ 0.80 → Validación Automática                 │
│  • Score < 0.80 → Envío a Portal para aprobación manual │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
ETAPA 2: EMISIÓN Y NOTIFICACIÓN
┌─────────────────────────────────────────────────────────┐
│  • Emisión en momento óptimo (calendario tributario)    │
│  • Publicación en Dashboard Interno                     │
│  • Notificación al cliente vía canal preferido          │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
ETAPA 3: NEGOCIACIÓN PREDICTIVA (T-5 días antes del vencimiento)
┌─────────────────────────────────────────────────────────┐
│  • Negotiation Agent evalúa perfil del cliente          │
│  • Modelo XGBoost predice probabilidad de pago          │
│                                                         │
│  Happy Path (>75%):    No ofrecer descuento             │
│  Warning Path (40-75%): Descuento moderado (5-10%)      │
│  Unhappy Path (<40%):   Facilidades agresivas (15-20%)  │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
ETAPA 4: CONCILIACIÓN Y COBRANZA
┌─────────────────────────────────────────────────────────┐
│  • Collections Agent detecta pagos (integración banco)  │
│  • Conciliación automática con facturas pendientes      │
│  • Cálculo TAMN para facturas vencidas                  │
│  • Gemini Flash clasifica todas las comunicaciones      │
│  • Cliente recibe respuesta del agente correspondiente  │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
ETAPA 5: APRENDIZAJE Y MEJORA CONTINUA
┌─────────────────────────────────────────────────────────┐
│  • Learning Agent analiza patrones de error y disputas  │
│  • Propone ajustes a scores, umbrales y descuentos      │
│  • Genera reportes ejecutivos mensuales                 │
│  • Re-entrena modelos XGBoost con nuevos datos          │
│  • Cambios revisados por comité Finanzas + TI           │
└─────────────────────────────────────────────────────────┘
```

---

## 🧠 Modelos de IA

### Asignación por Agente

| Modelo | Proveedor | Agentes | Ventaja Competitiva |
|--------|-----------|---------|---------------------|
| **DeepSeek-R1** | Groq (LPU) | Supervisor, Billing, Collections, Negotiation | Razonamiento complejo, decisiones críticas, análisis financiero |
| **Gemini 1.5 Pro** | Google | Customer Agent | NLP avanzado, generación de texto natural, RAG contextual |
| **Gemini 1.5 Flash** | Google | Classifier Agent | Clasificación ultra-rápida, bajo costo por request |
| **XGBoost** | Local | Score de Confianza, Predicción de Pago | Modelos entrenados con datos históricos, alta precisión |
| **Isolation Forest** | Local | Detección de Anomalías | Identificación de facturas atípicas sin supervisión |

### Modelos Predictivos (Entrenados Localmente)

| Modelo | Algoritmo | Propósito | Features Principales | Re-entrenamiento |
|--------|-----------|-----------|---------------------|------------------|
| **Score de Confianza** | XGBoost Classifier | Clasificar clientes confiables (0-1) | Antigüedad, mora promedio, disputas, pagos tarde | Mensual |
| **Predicción de Pago** | XGBoost Classifier | Predecir probabilidad de pago en 15 días | Score confianza, días al vencimiento, recordatorios | Mensual |
| **Detección de Anomalías** | Isolation Forest | Detectar facturas atípicas | Monto, desviación del promedio, frecuencia | Trimestral |

### Estrategia de Modelos

- **LLMs vía API**: Usados en modo inferencia con prompts especializados y RAG, evitando costos de fine-tuning
- **Modelos ML locales**: Entrenados con datos ficticios para MVP, re-entrenados mensualmente en producción
- **Motor Simbólico**: Todos los cálculos financieros (PxQ, IGV, TAMN) en Python, garantizando precisión absoluta

---

## 📈 Métricas e Impacto

### KPIs Operativos

| KPI | Baseline Actual | Proyección SON-IA | Mejora |
|-----|-----------------|-------------------|--------|
| **DSO (Días Promedio de Cobro)** | 45 días | 40 días | -11% |
| **Exactitud de Facturación** | Con errores manuales | 99.9% | Zero-Hallucination |
| **Resolución en Primer Contacto (FCR)** | Call Center saturado | +30% digital | Chat RAG |
| **Recupero de Cartera Morosa** | Cobranza reactiva | +15-20% | Negociación predictiva |
| **Ahorro en Horas-Hombre (FTE)** | 30 personas | 6 personas | -80% |
| **Churn Involuntario** | 5% anual | <1.5% anual | -70% |
| **Tasa de Aceptación de Ofertas** | No existía | 30-40% | Nuevo canal |

### Impacto Financiero Estimado

| Concepto | Ahorro Anual Estimado (S/) |
|----------|---------------------------|
| Reducción de FTE (30 → 6 personas) | S/ 2,400,000 |
| Reducción de fuga de ingresos | S/ 1,200,000 |
| Mejora de DSO (5 días) | S/ 4,500,000 |
| Recupero de cartera morosa (+15%) | S/ 3,000,000 |
| **Total Ahorro Anual** | **S/ 11,100,000** |
| **Costo de Implementación** | S/ 1,800,000 |
| **ROI Año 1** | **516%** |
| **Payback** | **< 3 meses** |

---

## 📚 Documentación Adicional

| Documento | Descripción | Cuándo Leerlo |
|-----------|-------------|---------------|
| [🏗️ Arquitectura Detallada](architecture.md) | Diseño técnico completo, diagramas de secuencia, stack detallado | Para entender el diseño interno |
| [🔌 API Reference](api-reference.md) | Todos los endpoints REST, WebSockets, modelos de datos | Para integrar con el backend |
| [🚀 Guía de Despliegue](deployment.md) | Instrucciones para producción, cloud, CI/CD | Para poner en producción |
| [🤝 Guía de Contribución](contribution-guide.md) | Estándares de código, flujo de trabajo, convenciones | Para contribuir al proyecto |

---

## 🛠️ Stack Tecnológico Completo

| Capa | Tecnología | Versión | Propósito |
|------|-----------|---------|-----------|
| **Backend Framework** | FastAPI | 0.115 | API REST de alto rendimiento |
| **Lenguaje** | Python | 3.11+ | Tipado fuerte, ecosistema ML/IA |
| **Orquestación IA** | LangGraph | 0.2+ | State graphs con HITL nativo |
| **Validación** | Pydantic | 2.9+ | Esquemas estrictos para datos financieros |
| **Tareas Async** | Celery | 5.4 | Procesamiento background |
| **Broker** | Redis | 7 | Caché + message broker |
| **Base de Datos** | PostgreSQL | 16 | Datos de agentes y facturación |
| **Vector DB** | Pinecone | - | Embeddings para RAG |
| **Frontend** | Next.js | 14 | React framework con SSR |
| **Estilos** | Tailwind CSS | 3.4 | Utility-first CSS |
| **Gráficos** | Chart.js | 4.4 | Visualizaciones interactivas |
| **Estado** | TanStack Query | 5.59 | Server state management |
| **Container** | Docker | 24+ | Contenedores |
| **CI/CD** | GitHub Actions | - | Tests automáticos |

---

## 📞 Contacto y Soporte

- **Equipo**: SON-IA Development Team @ Integratel
- **Email**: sonia@integratel.com
- **Documentación**: [docs/](.)
- **Issues**: [GitHub Issues](https://github.com/integratel/son-ia-mvp/issues)

---

**SON-IA**: Transformando la facturación con Inteligencia Artificial 🚀

