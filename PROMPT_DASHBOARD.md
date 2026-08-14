# Crear Dashboard Administrativo en Next.js para SON-IA

## Contexto General

Estoy construyendo un dashboard administrativo interno para **SON-IA** (Sinergia Operativa del Negocio - Integratel Agéntica), un ecosistema de agentes IA para automatización de facturación, recaudación y cobranzas.

El backend es una **API FastAPI** que expone múltiples endpoints organizados en estas secciones:

### Endpoints Disponibles

#### 🏥 Health
- `GET /api/v1/health` - Health check básico
- `GET /api/v1/health/detailed` - Estado de componentes (DB, Redis, Groq, Gemini)

#### 📊 Dashboard (Home)
- `GET /api/v1/dashboard/metrics` - Métricas principales en tarjetas
  - `facturas_procesadas_hoy`: int
  - `monto_total_recaudado`: float (S/)
  - `indice_morosidad`: float (%)
  - `ofertas_activas`: int
  - `facturas_pendientes_revision`: int (HITL)
  - `tasa_aceptacion_ofertas`: float (%)
  - `tiempo_promedio_emision_seg`: float
  - `agentes_activos`: int
  - `timestamp`: ISO 8601

- `GET /api/v1/dashboard/agentes/estado` - Estado del enjambre de agentes IA
  - Agentes: supervisor, billing, collections, negotiation, customer, classifier, learning
  - Por agente: estado, modelo, proveedor, última_ejecución, tareas_procesadas, tasa_error

#### 💰 Facturación
- `GET /api/v1/billing/facturas` - Lista paginada de facturas
  - Query: skip, limit, estado (Pendiente|Pagado|Vencido)
- `GET /api/v1/billing/facturas/{factura_id}` - Detalle de factura (cabecera + líneas + ofertas)
- `POST /api/v1/billing/ciclos/ejecutar` - Ejecutar ciclo de facturación
  - Query: ciclo_id, force_review

#### 👥 Clientes
- `GET /api/v1/clients` - Lista paginada de clientes
  - Query: skip, limit, segmento (B2B|B2C|Gobierno)
- `GET /api/v1/clients/{cliente_id}` - Detalle de cliente (datos, score, cuentas, servicios)
- `GET /api/v1/clients/{cliente_id}/historial-facturas` - Historial de facturas
- `GET /api/v1/clients/{cliente_id}/score` - Score de confianza del cliente

#### 📈 Cobranzas
- `GET /api/v1/collections/facturas-vencidas` - Cartera de vencidas
  - Query: skip, limit, etapa (temprana|media|tardia|critica)
- `POST /api/v1/collections/calcular-tamn/{factura_id}` - Calcular intereses moratorios
- `POST /api/v1/collections/procesar-pago` - Registrar pago
  - Query: factura_id, monto_pagado, fecha_pago

#### 🤝 Negociación
- `GET /api/v1/negotiations/ofertas` - Lista de ofertas de negociación
  - Query: skip, limit, estado (pendiente|aceptada|rechazada|expirada)
- `POST /api/v1/negotiations/ofertas/{oferta_id}/aceptar` - Cliente acepta oferta
- `POST /api/v1/negotiations/ofertas/{oferta_id}/rechazar` - Cliente rechaza oferta

#### 📋 Auditoría
- Endpoints para logs de acciones y rastrabilidad de cada operación

---

## Requisitos de Diseño

### 1. **Estructura y Layout**
- **Sidebar Navigation**: Menú colapsible con secciones (Dashboard, Facturación, Clientes, Cobranzas, Negociación, Auditoría)
- **Header**: Logo SON-IA, breadcrumbs, usuario logueado, notificaciones, perfil
- **Responsive**: Funcione en desktop, tablet y mobile
- **Tema**: Modo claro (default) y modo oscuro (toggle)
- **Paleta de colores**: Profesional, azul/gris como colores primarios, rojo para alertas/morosidad, verde para éxito/pagos

### 2. **Página de Inicio (Dashboard)**

#### Sección Superior: Métricas en Tarjetas
- 4 tarjetas grandes con indicadores principales:
  1. **Facturas Procesadas Hoy** (contador + icon)
  2. **Monto Recaudado** (S/ con formato de dinero + sparkline/trend)
  3. **Índice de Morosidad** (% en rojo si > 5%, amarillo si 2-5%, verde si < 2%)
  4. **Facturas Pendientes Revisión HITL** (alerta si > 0)

#### Sección Media: Estado del Enjambre de Agentes
- **Tabla de agentes** con:
  - Nombre del agente
  - Estado (círculo verde=activo, gris=idle, rojo=error)
  - Modelo de IA usado
  - Proveedor (Groq, Google)
  - Última ejecución (hace X horas)
  - Tareas procesadas (contador acumulado)
  - Tasa de error (% en rojo si > 2%)
- Gráfico radial o barras mostrando distribución de agentes por estado

#### Sección Inferior: Gráficos
- **Gráfico de línea**: Evolución de recaudación últimos 7 días
- **Gráfico de barras**: Facturas por estado (Pendiente, Pagado, Vencido)
- **Gráfico circular (pie)**: Proporción de ofertas (Pendiente, Aceptada, Rechazada, Expirada)

### 3. **Sección Facturación**
- **Filtros**: Estado (todos|Pendiente|Pagado|Vencido), rango de fechas, cliente
- **Tabla paginada** de facturas con:
  - ID de factura (clickeable → detalle)
  - Cliente (RUC / Razón Social)
  - Monto (formato S/)
  - Fecha de emisión
  - Fecha de vencimiento
  - Estado (badge con color)
  - Acciones: Ver detalle, Descargar PDF
- **Modal/Página de Detalle de Factura**:
  - Cabecera (cliente, período, monto total, IGV)
  - Líneas de detalle (servicio, cantidad, precio unitario, subtotal)
  - Ofertas activas de negociación (si existen)
  - Historial de pagos parciales

### 4. **Sección Clientes**
- **Buscador/filtros**: Segmento (B2B|B2C|Gobierno), nombre/RUC
- **Tabla paginada** con:
  - RUC
  - Razón Social
  - Segmento
  - Score de confianza (0-100, visualizado como barrita o número con color)
  - Teléfono
  - Acciones: Ver perfil
- **Modal/Página de Perfil de Cliente**:
  - Datos generales
  - Score de confianza (explicación de cálculo)
  - Cuentas y servicios activos
  - Historial de facturas (tabla con paginación)
  - Facturas vencidas (si las hay)

### 5. **Sección Cobranzas**
- **Filtros**: Etapa de mora (temprana|media|tardia|critica), rango de días vencido
- **Tabla paginada** de facturas vencidas con:
  - ID Factura
  - Cliente
  - Monto original (S/)
  - Días vencido (rojo si > 30)
  - TAMN calculado (intereses moratorios)
  - Etapa de mora (badge con color)
  - Acciones: Calcular TAMN, Registrar pago, Ver detalle
- **Panel rápido de métricas**:
  - Total cartera vencida (S/)
  - Cantidad de facturas vencidas
  - TAMN acumulado
  - Tendencia vs. mes anterior

### 6. **Sección Negociación**
- **Filtros**: Estado de oferta (todos|pendiente|aceptada|rechazada|expirada)
- **Tabla paginada** de ofertas con:
  - ID Oferta
  - Cliente
  - Factura relacionada
  - Descuento ofrecido (%)
  - Nuevo plazo
  - Estado (badge)
  - Fecha de expiración
  - Acciones: Aceptar, Rechazar, Ver detalle
- **Gráfico de tasa de aceptación** (% de ofertas aceptadas vs. totales)

### 7. **Sección Auditoría** (Bonus)
- Tabla de logs de acciones: quién, qué, cuándo, dónde
- Filtros por tipo de acción, usuario, fecha

---

## Requisitos Técnicos

### Frontend
- **Framework**: Next.js 14+ (TypeScript)
- **Styling**: Tailwind CSS + ShadCN UI (componentes reutilizables)
- **State Management**: TanStack Query (React Query) para fetch de datos
- **Charts**: Recharts o Chart.js
- **Forms**: React Hook Form + Zod/Yup para validación
- **HTTP Client**: Axios o fetch (con interceptores para autenticación futura)

### Estructura de Carpetas
```
src/
├── app/                      # App router de Next.js
│   ├── dashboard/            # Ruta principal
│   ├── billing/              # Facturación
│   ├── clients/              # Clientes
│   ├── collections/          # Cobranzas
│   ├── negotiations/         # Negociación
│   └── layout.tsx            # Layout principal
├── components/               # Componentes reutilizables
│   ├── Sidebar.tsx
│   ├── Header.tsx
│   ├── MetricCard.tsx
│   ├── DataTable.tsx
│   └── ...
├── hooks/                    # Custom hooks
│   ├── useFetchMetrics.ts
│   ├── useFetchFacturas.ts
│   └── ...
├── services/                 # API clients
│   ├── api.ts                # Configuración de axios
│   ├── dashboard.ts          # Endpoints dashboard
│   ├── billing.ts            # Endpoints facturación
│   ├── clients.ts            # Endpoints clientes
│   └── ...
├── types/                    # TypeScript types/interfaces
│   ├── dashboard.ts
│   ├── billing.ts
│   ├── clients.ts
│   └── ...
└── utils/                    # Funciones auxiliares
    ├── formatting.ts         # Formatear dinero, fechas
    ├── colors.ts             # Mapeo de estados a colores
    └── ...
```

### Features Adicionales
1. **Real-time Updates**: Conectar WebSockets para métricas en vivo (opcional fase 2)
2. **Exportar Reportes**: Botón para descargar tabla como CSV/PDF
3. **Notificaciones**: Toast/Snackbar para confirmar acciones (pago registrado, oferta aceptada)
4. **Dark Mode**: Toggle en header, persistir preferencia en localStorage
5. **Búsqueda Global**: Search bar en header para buscar clientes/facturas
6. **Validación**: Feedback claro en formularios (ej: registrar pago)
7. **Loading States**: Spinners/skeletons mientras se cargan datos
8. **Error Handling**: Mensajes claros si una API falla, retry button

---

## Especificaciones de Diseño UX

### Colores por Estado
- **Factura Pendiente**: Amarillo (#FFC107)
- **Factura Pagada**: Verde (#4CAF50)
- **Factura Vencida**: Rojo (#F44336)
- **Agente Activo**: Verde (#4CAF50)
- **Agente Idle**: Gris (#9E9E9E)
- **Agente Error**: Rojo (#F44336)
- **Oferta Pendiente**: Azul (#2196F3)
- **Oferta Aceptada**: Verde (#4CAF50)
- **Oferta Rechazada**: Rojo (#F44336)
- **Oferta Expirada**: Gris (#9E9E9E)

### Tipografía
- **Títulos**: Tamaño 24-32px, peso 700
- **Subtítulos**: Tamaño 16-18px, peso 600
- **Cuerpo**: Tamaño 14px, peso 400
- **Pequeño**: Tamaño 12px, peso 400

### Espaciado
- Margen estándar: 16px
- Padding en tarjetas: 20px
- Gap entre elementos: 8-16px

---

## Instrucciones de Implementación

1. **Crear estructura base**: Layout, Sidebar, Header
2. **Implementar página Dashboard**: Tarjetas de métricas + gráficos
3. **Crear service layer**: Funciones para consumir APIs
4. **Implementar secciones**: Facturación, Clientes, Cobranzas, Negociación (en ese orden)
5. **Agregar interactividad**: Modales, formularios, paginación
6. **Pulir UI/UX**: Responsive, dark mode, loading states, error handling
7. **Testing**: Unit + integration tests

---

## Notas Importantes

- **Base URL**: `http://localhost:8000/api/v1` (o env var para producción)
- **Autenticación**: Actualmente sin JWT (Fase 2 del MVP), pero preparar estructura para agregarlo
- **Zona Horaria**: America/Lima (UTC-5)
- **Formato de Dinero**: Siempre en Soles Peruanos (S/)
- **Formatos de Fecha**: ISO 8601 (YYYY-MM-DD) para requests, mostrar local en UI
- **Paginación**: Usar skip/limit (no page/pageSize)

---

## Casos de Uso Principales

1. **Admin abre dashboard** → Ve métricas del día y estado de agentes en una ojeada
2. **Admin ejecuta ciclo de facturación** → Botón en sección Facturación → Confirma ciclo_id → Monitorea progreso
3. **Admin revisa cliente** → Busca en tabla de Clientes → Abre perfil → Ve score + historial + facturas vencidas
4. **Admin gestiona morosidad** → Va a Cobranzas → Filtra por etapa crítica → Calcula TAMN → Registra pago
5. **Admin revisa ofertas** → Va a Negociación → Ve ofertas pendientes → Sistema muestra tasa de aceptación

---

**Espero esto te sea útil. Crea el dashboard con esta guía y tendrás un admin super funcional para SON-IA.**
