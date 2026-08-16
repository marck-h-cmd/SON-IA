# SON-IA: Sistema Operativo de Negociación e Inteligencia Artificial para Facturación y Cobranzas B2B
## Documentación Integral de Arquitectura, Tecnologías, Enjambre de Agentes e Impacto de Negocio

---

## 📌 1. Resumen Ejecutivo y Ficha Técnica

| Parámetro | Detalle |
| :--- | :--- |
| **Nombre del Proyecto** | **SON-IA** (*Sistema Operativo de Negociación e Inteligencia Artificial*) |
| **Entidad / Caso de Uso** | **Movistar Empresas / Integratel Perú S.A.C.** (Telecomunicaciones B2B) |
| **Versión** | `1.0.0-MVP (Enterprise Ready)` |
| **Propósito** | Orquestación inteligente de ciclos de facturación masiva, cobranza predictiva, negociación empática asistida por IA y emisión electrónica conforme a SUNAT UBL 2.1. |
| **Paradigma Clave** | **Zero-Hallucination**: Separación estricta entre motor matemático determinista y capa de lenguaje/negociación con LLMs. |
| **Modo Operativo** | Multi-Agente Asíncrono (Swarm) con **Human-in-the-Loop (HITL)** para control de riesgo y compliance. |

---

## 🚨 2. El Problema de Negocio (Problem Statement)

En el sector de telecomunicaciones corporativas (B2B), la gestión financiera enfrenta retos operativos críticos:

1. **Complejidad y Dispersión de Datos BSS/OSS**:
   - Millones de registros fragmentados entre Planta Fija (enlaces de datos, PBX), Planta Móvil (líneas corporativas, bolsas de datos), Facturas emitidas, Pagos parciales y Notas de Crédito.
2. **Alta Morosidad y Procesos Rígidos de Cobranza**:
   - Las empresas clientes caen en morosidad (días mora variables) y las operadoras aplican cobranzas genéricas, frías y no personalizadas, perdiendo clientes o elevando incobrables.
   - Falta de cálculo dinámico de intereses moratorios (Tasa Activa en Moneda Nacional - **TAMN**) en tiempo real.
3. **Fricción en la Emisión y Cumplimiento Regulatorio (SUNAT)**:
   - Emisión manual de comprobantes electrónicos Tipo 14 (Recibos de Telecomunicaciones) y necesidad de generar archivos XML bajo estándar UBL 2.1 con código Hash SHA-256 y códigos QR oficiales.
4. **Canales de Atención Lentos y Mecánicos**:
   - Mensajes automáticos robotizados que generan rechazo en los clientes y retrasan la recaudación.
5. **Riesgo de Alucinaciones en IA Convencional**:
   - Los modelos de lenguaje puros (LLMs) cometen errores de cálculo aritmético si intentan sumar, calcular IGV o liquidar deudas directamente en el texto.

---

## 💡 3. La Solución Propuesta (Solution Architecture)

**SON-IA** resuelve estos desafíos combinando un motor transaccional determinista con un enjambre de agentes de Inteligencia Artificial especializados:

```mermaid
flowchart TB
    subgraph "Capas de Entrada y Canales"
        WA["📱 WhatsApp Gateway (OpenWA)"]
        MAIL["✉️ Gmail / SMTP Corporativo"]
        WEB["💻 Dashboard Web (Next.js 14)"]
    end

    subgraph "Orquestación y Agentes IA (Swarm)"
        SA["🛡️ Supervisor Agent\n(Enrutamiento y Control de Salud)"]
        BA["📄 Billing Agent\n(Detección de Anomalías en Facturación)"]
        CA["💰 Collections Agent\n(TAMN, Días Mora y Segmentación)"]
        NA["🤝 Negotiation Agent\n(Ofertas Predictivas y Descuentos)"]
        CUST["💬 Customer Agent\n(Conversación Empática 100% Humana)"]
        HITL["👤 Supervisor Humano (HITL Dashboard)\n(Aprobación de Casos Críticos)"]
    end

    subgraph "Motor Determinista y Servicios de Negocio (Zero-Hallucination)"
        CALC["⚙️ Motor Matemático Determinista (Python / Pandas / Decimal)"]
        SUNAT["🏛️ Servicio SUNAT UBL 2.1 (XML, SHA-256 Digest, QR)"]
        PDF["📑 Generador de Recibos Oficiales Movistar (3 Páginas PDF)"]
        AUDIT["📋 Servicio de Auditoría e Inmutabilidad"]
    end

    subgraph "Persistencia y Colas Asíncronas"
        PG[("🐘 PostgreSQL 16 (BSS/OSS Data)")]
        REDIS[("⚡ Redis 7 (Caché & Broker)")]
        CELERY["⚙️ Celery Workers (Procesamiento Distribuido)"]
    end

    WA <--> CUST
    MAIL <-- PDF
    WEB <--> SA
    SA <--> BA & CA & NA & CUST
    SA --> HITL
    BA & CA & NA --> CALC
    CALC --> SUNAT & PDF & PG
    SA & HITL --> AUDIT
    CELERY <--> REDIS <--> PG
```

### Pilares Fundamentales:
* **Zero-Hallucination**: Todos los montos, IGV (18%), intereses TAMN, subtotales y redondeos son procesados por el motor matemático de precisión en Python (`Decimal`). La IA solo interpreta, negocia y redacta.
* **Human-in-the-Loop (HITL)**: Facturas que superen umbrales de riesgo (descuentos > 15%, score de confianza < 0.80, montos retenidos) se congelan en la bandeja de Aprobaciones para autorización humana con 1 clic.
* **Comprobantes Oficiales Movistar**: Emisión de recibos digitales idénticos a los físicos en PDF de 3 páginas (Pág 1: Resumen de Cuenta; Pág 2: Detalle de Consumo y Tarifas; Pág 3: Conceptos Facturables y Lugares de Pago) y códigos QR tributarios interactivos.
* **Atención Empática y Humanizada**: El chatbot de WhatsApp responde con calidez, sin tecnicismos ni frialdad robótica, identificando al cliente y resolviendo consultas de pago al instante.

---

## 🛠️ 4. Stack Tecnológico y Herramientas Utilizadas

### 🔹 Backend & Servicios Core
* **Python 3.11+**: Lenguaje principal de backend y computación matemática.
* **FastAPI**: Framework web asíncrono de alto rendimiento con generación automática de especificaciones OpenAPI / Swagger.
* **Pydantic v2**: Validación de esquemas de datos y serialización tipada.
* **SQLAlchemy 2.0 (Async Engine)**: ORM asíncrono para consultas de alta velocidad y concurrencia.
* **ReportLab**: Motor de generación programática de comprobantes PDF vectoriales de 3 páginas con layout oficial Movistar.
* **XML UBL 2.1 & SHA-256**: Generación de documentos tributarios estándar SUNAT con cálculo de `DigestValue` y cadenas QR oficiales.
* **Structlog**: Logging estructurado en formato JSON para trazabilidad y auditoría.

### 🔹 Inteligencia Artificial & Enjambre de Agentes
* **LangChain Core & Community**: Framework para gestión de cadenas de razonamiento, prompts modulares y herramientas.
* **Groq API (LPU Inference)**:
  * `llama-3.3-70b-versatile`: Modelo principal para razonamiento estratégico de negociación y orquestación.
  * `llama-3.1-8b-instant`: Modelo ultrarrápido para atención al cliente y clasificación semántica en tiempo real.
* **Google Gemini & OpenAI GPT-4o**: Proveedores alternativos y de respaldo integrados en la arquitectura multi-modelo.
* **Técnicas de Promp Engineering**: In-Context Learning, Few-Shot prompting, Guardrails de cumplimiento y humanización conversacional.

### 🔹 Frontend & Experiencia de Usuario (UI/UX)
* **Next.js 14 (App Router)**: Framework de React con Server Components, Server-Side Rendering (SSR) y optimización de carga.
* **React 18 & TypeScript 5**: Tipado estricto de extremo a extremo entre Backend y Frontend.
* **Tailwind CSS (Paleta Oficial Movistar Cyan `#00A9E0`)**:
  * Diseño corporativo con fondos suaves (`#EBF7FC`), bordes (`#BAE6FD`), modo oscuro y transiciones suaves.
* **Recharts**: Gráficos interactivos de evolución financiera, morosidad y rendimiento de agentes.
* **Generador Autónomo de Código QR (SVG)**: Componente en TypeScript puro que genera códigos QR estándar ISO/IEC 18004 sin dependencias externas.

### 🔹 Bases de Datos, Colas y Caché
* **PostgreSQL 16**: Base de datos relacional para el almacenamiento de 6 datasets masivos B2B:
  * `001_TBL_CLIENTES_B2B.csv` (`bss_clientes`)
  * `002_TBL_PLANTA_FIJA_B2B.csv` (`oss_planta_fija`)
  * `003_TBL_PLANTA_MOVIL_B2B.csv` (`oss_planta_movil`)
  * `004_TBL_PAGOS_B2B.csv` (`bss_pagos`)
  * `005_TBL_FACTURAS_B2B.csv` (`bss_facturas`)
  * `006_TBL_NOTAS_CREDITO_B2B.csv` (`bss_notas_credito`)
* **Redis 7**: Broker de mensajería asíncrona y caché de baja latencia para el estado de los agentes.
* **Celery & Flower**: Ejecución de tareas pesadas en segundo plano (emisión masiva de ciclos y despacho de campañas) con interfaz de monitoreo en tiempo real.

### 🔹 Integraciones Externas & Despliegue
* **OpenWA (WhatsApp Web Gateway)**: Pasarela de mensajería instantánea para interacción directa con clientes, soporte para grupos y lista blanca de seguridad para demos.
* **Gmail SMTP**: Pasarela de despacho de comprobantes oficiales con adjuntos PDF.
* **Docker & Docker Compose**: Orquestación de 6 contenedores (`backend`, `frontend`, `db`, `redis`, `celery_worker`, `flower`).

---

## 📁 5. Estructura del Código y Organización del Proyecto

```text
son-ia-mvp/
├── backend/
│   ├── app/
│   │   ├── agents/                     # Agentes de IA (Swarm)
│   │   │   ├── supervisor_agent.py     # Orquestador y enrutador
│   │   │   ├── billing_agent.py        # Detección y validación de facturación
│   │   │   ├── collections_agent.py    # Segmentación de mora y TAMN
│   │   │   ├── negotiation_agent.py    # Generación de ofertas predictivas
│   │   │   ├── customer_agent.py       # Atención empática humanizada
│   │   │   ├── classifier_agent.py     # Clasificación semántica de mensajes
│   │   │   └── learning_agent.py       # Auto-mejora y ajuste de políticas
│   │   ├── api/v1/endpoints/           # Controladores REST API
│   │   │   ├── billing.py              # Facturas, ciclos, XML y PDF
│   │   │   ├── clients.py              # Búsqueda multi-campo (RUC, celular, razón)
│   │   │   ├── collections.py          # Cálculo TAMN y liquidaciones
│   │   │   ├── negotiation.py          # Gestión y aceptación de ofertas
│   │   │   ├── hitl.py                 # Aprobaciones y rechazos humanos
│   │   │   ├── audit.py                # Logs y exportación CSV de auditoría
│   │   │   ├── dashboard.py            # Métricas ejecutivas en tiempo real
│   │   │   └── whatsapp.py             # Webhook y pasarela OpenWA
│   │   ├── database/                   # Modelos ORM y conexión PostgreSQL
│   │   │   ├── connection.py           # Engine asíncrono
│   │   │   └── models.py               # Tablas BSS y OSS
│   │   ├── integrations/               # Clientes de terceros (OpenWA, etc.)
│   │   │   └── openwa_client.py
│   │   ├── services/                   # Lógica de negocio determinista
│   │   │   ├── billing_service.py      # Cálculos de facturación y correos
│   │   │   ├── collections_service.py  # Algoritmo TAMN según BCRP/SBS
│   │   │   ├── negotiation_service.py  # Políticas comerciales de descuento
│   │   │   ├── hitl_service.py         # Flujo de aprobación humana
│   │   │   ├── sunat_service.py        # Generador UBL 2.1 y Hash SHA-256
│   │   │   ├── pdf_service.py          # Renderizador de recibo Movistar 3 págs
│   │   │   ├── notification_service.py # Despacho multicanal (Email/WA)
│   │   │   └── audit_service.py        # Trazabilidad inmutable
│   │   └── tasks/                      # Tareas asíncronas Celery
│   ├── scripts/
│   │   └── seed-database-csv.py        # Carga masiva de datasets a PostgreSQL
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── (dashboard)/            # Vistas principales del sistema
│   │   │   │   ├── dashboard-interno/  # Métricas generales y salud de agentes
│   │   │   │   ├── facturacion/        # Emisión, XML, PDF y Código QR SUNAT
│   │   │   │   ├── clientes/           # Directorio con búsqueda por celular/RUC
│   │   │   │   ├── cobranzas/          # Liquidación de mora y cálculo TAMN
│   │   │   │   ├── negociacion/        # Ofertas predictivas y tasas de éxito
│   │   │   │   ├── aprobaciones/       # Centro de control HITL
│   │   │   │   └── auditoria/          # Trazabilidad con filtros reactivos
│   │   │   ├── globals.css             # Clases corporativas Movistar Cyan
│   │   │   └── layout.tsx
│   │   ├── components/
│   │   │   ├── billing/
│   │   │   │   ├── MovistarInvoiceModal.tsx # Visor de recibo oficial de 3 págs
│   │   │   │   └── SunatQrModal.tsx         # Modal interactivo con código QR
│   │   │   ├── ui/
│   │   │   │   ├── QrCode.tsx               # Generador nativo SVG sin paquetes
│   │   │   │   ├── Button.tsx               # Botones Movistar Cyan interactivos
│   │   │   │   ├── Badge.tsx, Card.tsx, Table.tsx, Modal.tsx
│   │   │   └── layout/
│   │   │       ├── Sidebar.tsx              # Menú institucional Movistar B2B
│   │   │       └── Header.tsx
│   │   ├── services/                        # Conectores HTTP Axios tipados
│   │   └── utils/                           # Formateadores de moneda y colores
│   ├── tailwind.config.ts                   # Paleta oficial Movistar Cyan (#00A9E0)
│   └── Dockerfile
│
├── DATASET/                            # Fuentes de datos BSS/OSS
├── docs/                               # Documentación técnica y arquitectura
└── docker-compose.yml                  # Orquestación de todos los microservicios
```

---

## 🤖 6. El Enjambre de Inteligencia Artificial (AI Swarm)

```text
                                  ┌───────────────────────┐
                                  │   Supervisor Agent    │
                                  │ (Orquestador Central) │
                                  └──────────┬────────────┘
                   ┌─────────────────────────┼─────────────────────────┐
                   ▼                         ▼                         ▼
        ┌─────────────────────┐   ┌─────────────────────┐   ┌─────────────────────┐
        │    Billing Agent    │   │  Collections Agent  │   │  Negotiation Agent  │
        │(Detección Anomalías)│   │  (TAMN & Días Mora) │   │ (Ofertas Predictiv.)│
        └─────────────────────┘   └─────────────────────┘   └─────────────────────┘
                   │                         │                         │
                   └─────────────────────────┼─────────────────────────┘
                                             ▼
                                  ┌───────────────────────┐
                                  │     Customer Agent    │
                                  │ (WhatsApp Humanizado) │
                                  └───────────────────────┘
```

| Agente de IA | Modelo / Motor | Función Específica en SON-IA |
| :--- | :--- | :--- |
| **Supervisor Agent** | Groq Llama-3.3-70B | Monitorea la salud del enjambre, enruta intenciones complejas, detecta desviaciones de riesgo y delega tareas a la bandeja Human-in-the-Loop. |
| **Billing Agent** | Llama-3.3-70B + Python | Analiza los consumos de Planta Fija y Móvil, detecta picos anormales de consumo y estructura los ciclos de facturación B2B. |
| **Collections Agent** | Llama-3.1-8B + Motor TAMN | Evalúa el perfil de riesgo del cliente, calcula los días de mora e intereses compensatorios/moratorios según tasas oficiales SBS/BCRP. |
| **Negotiation Agent** | Groq Llama-3.3-70B | Genera ofertas de refinanciamiento y descuentos personalizados (5% - 15%) basados en el score de confianza y capacidad de pago histórica. |
| **Customer Agent** | Groq Llama-3.1-8B Instant | Atiende por WhatsApp con un tono **100% natural, cálido y empático** como asesor de Movistar Empresas, sin respuestas robóticas ni tecnicismos. |
| **Classifier Agent** | Llama-3.1-8B | Identifica la intención del mensaje entrante (`CONSULTA_SALDO`, `SOLICITUD_RECIBO`, `NEGOCIAR_DEUDA`, `PROMOCIONES`). |
| **Learning Agent** | Llama-3.3-70B | Registra las decisiones de aprobación/rechazo de los supervisores humanos para calibrar y sugerir nuevos umbrales de negociación. |

---

## 📈 7. Impacto Esperado y Retorno de Inversión (ROI)

La adopción de **SON-IA** genera beneficios cuantificables para la operación:

1. **⚡ Reducción del 85% en Tiempos de Facturación**:
   - Procesamiento masivo de miles de líneas B2B en segundos gracias a la concurrencia de Celery y FastAPI.
2. **📉 Disminución de hasta un 35% en Cartera Vencida**:
   - Las ofertas predictivas y personalizadas de negociación aumentan sustancialmente la tasa de recupero temprano de deuda.
3. **🎯 Cero Alucinaciones Financieras (100% Precisión Tributaria)**:
   - Cálculos matemáticos auditables y generación de comprobantes XML y Códigos QR UBL 2.1 aceptados por SUNAT.
4. **💬 Incremento del 60% en la Tasa de Cobranza Digital**:
   - Recordatorios y recibos interactivos enviados directamente al WhatsApp del tomador de decisiones de la empresa cliente.
5. **🛡️ Cumplimiento y Control Institucional**:
   - Trazabilidad inmutable de cada acción ejecutada por agentes o humanos en la bitácora de auditoría regulatoria.

---

## 🚀 8. Instrucciones de Ejecución Rápida

Para iniciar todo el ecosistema con un solo comando:

```bash
# 1. Clonar el repositorio y acceder
git clone https://github.com/marck-h-cmd/SON-IA.git
cd son-ia-mvp

# 2. Configurar variables de entorno
cp backend/.env.example backend/.env

# 3. Levantar todos los servicios en Docker
docker compose up -d --build

# 4. Sembrar la base de datos con los 6 datasets B2B
docker compose exec backend python scripts/seed-database-csv.py
```

### URLs de Acceso Local:
- 🌐 **Dashboard Web**: `http://localhost:3001` (o `http://localhost:3000`)
- 📄 **API REST & Swagger Docs**: `http://localhost:8000/docs`
- 🌸 **Monitor de Tareas Celery (Flower)**: `http://localhost:5555`

---
*SON-IA MVP - Desarrollado para Movistar Empresas / Integratel Perú S.A.C.*
