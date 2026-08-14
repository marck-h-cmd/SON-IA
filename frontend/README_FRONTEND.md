# SON-IA Dashboard Frontend

Dashboard administrativo interno para **SON-IA** (Sistema de Orquestación del Negocio - Integratel Agéntica), un ecosistema de agentes IA para automatización de facturación, recaudación y cobranzas.

## 🚀 Características

- **Dashboard Operativo**: Visualización en tiempo real de métricas principales y estado de agentes
- **Gestión de Facturación**: Listado, filtrado y detalles de facturas
- **Perfil de Clientes**: Información completa con score de confianza y servicios activos
- **Cobranzas**: Gestión de facturas vencidas con cálculo de TAMN y registro de pagos
- **Negociación**: Ofertas de descuento con aceptación/rechazo de clientes
- **Auditoría**: Registro completo de acciones y rastrabilidad del sistema
- **Modo Oscuro**: Toggle de tema oscuro/claro con persistencia
- **Diseño Responsivo**: Compatible con desktop, tablet y mobile
- **Dark Mode Support**: Tema oscuro integrado con Tailwind CSS

## 📋 Requisitos Previos

- Node.js 18+
- npm o yarn
- Acceso al backend FastAPI en `http://localhost:8000` (configurable)

## 📦 Instalación

### 1. Clonar e instalar dependencias

```bash
cd frontend
cp .env.local.example .env.local
npm install
```

### 2. Configurar variables de entorno

Editar `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 3. Ejecutar el servidor de desarrollo

```bash
npm run dev
```

El dashboard estará disponible en `http://localhost:3000`

## 🏗️ Estructura del Proyecto

```
frontend/
├── src/
│   ├── app/                      # App Router (Next.js 14)
│   │   ├── (dashboard)/         # Layout dashboard
│   │   │   ├── dashboard-interno/   # Dashboard home
│   │   │   ├── facturacion/        # Billing section
│   │   │   ├── clientes/           # Clients section
│   │   │   ├── cobranzas/          # Collections section
│   │   │   ├── negociacion/        # Negotiations section
│   │   │   ├── auditoria/          # Audit section
│   │   │   └── layout.tsx          # Dashboard layout
│   │   ├── layout.tsx            # Root layout
│   │   ├── page.tsx              # Home redirect
│   │   └── globals.css           # Global styles
│   ├── components/               # Componentes reutilizables
│   │   ├── dashboard/            # Dashboard components
│   │   │   └── MetricCard.tsx
│   │   ├── layout/               # Layout components
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── Breadcrumbs.tsx
│   │   └── ui/                   # Base UI components
│   │       ├── Card.tsx
│   │       ├── Button.tsx
│   │       ├── Badge.tsx
│   │       ├── Input.tsx
│   │       ├── Modal.tsx
│   │       ├── Table.tsx
│   │       ├── Skeleton.tsx
│   │       └── Tabs.tsx
│   ├── hooks/                    # Custom React hooks
│   ├── services/                 # API client services
│   │   ├── api.ts               # Axios configuration
│   │   ├── dashboardService.ts
│   │   ├── billingService.ts
│   │   ├── clientsService.ts
│   │   ├── collectionsService.ts
│   │   ├── negotiationService.ts
│   │   └── auditService.ts
│   ├── types/                    # TypeScript types
│   │   └── api.ts               # API type definitions
│   └── utils/                    # Utility functions
│       ├── formatting.ts        # Formatting functions
│       └── colors.ts            # Color mappings
├── public/                       # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
└── README.md
```

## 🎨 Componentes Principales

### Páginas

#### 1. Dashboard (`/dashboard-interno`)
Resumen operativo con:
- Tarjetas de métricas principales
- Estado del enjambre de agentes IA
- Gráficos de tendencias (recaudación, facturas por estado, ofertas)
- Tabla de agentes con detalles técnicos

#### 2. Facturación (`/facturacion`)
Gestión de facturas:
- Listado paginado filtrable
- Detalles completos (líneas, pagos parciales, ofertas)
- Descarga de PDF
- Ejecución de ciclos de facturación

#### 3. Clientes (`/clientes`)
Perfil completo de clientes:
- Búsqueda y filtrado por segmento
- Score de confianza con explicación de factores
- Historial de facturas
- Servicios activos
- Indicadores de morosidad

#### 4. Cobranzas (`/cobranzas`)
Gestión de cartera vencida:
- Listado de facturas vencidas por etapa
- Cálculo de TAMN (intereses moratorios)
- Registro de pagos
- Métricas de cartera

#### 5. Negociación (`/negociacion`)
Ofertas de descuento:
- Listado de ofertas con estados
- Gráfico de tasa de aceptación
- Detalles y justificación de ofertas
- Aceptación/rechazo por cliente

#### 6. Auditoría (`/auditoria`)
Registro de acciones:
- Logs completos con usuario y timestamp
- Filtrado por tipo de acción y fecha
- Detalles de cambios realizados
- Exportación a CSV

### Componentes UI Reutilizables

- **Card**: Contenedor con estilos consistentes
- **Button**: Botones con variantes (primary, secondary, danger, success)
- **Badge**: Etiquetas con colores por estado
- **Input**: Campos de entrada con validación
- **Modal**: Diálogos reutilizables
- **Table**: Tabla con paginación y acciones
- **Skeleton**: Loading placeholders
- **Tabs**: Sistema de pestañas

## 🔌 Integración con Backend

### Endpoints Consumidos

El dashboard se integra con los siguientes endpoints:

```
GET    /health
GET    /health/detailed
GET    /dashboard/metrics
GET    /dashboard/agentes/estado
GET    /billing/facturas
GET    /billing/facturas/{id}
GET    /clients
GET    /clients/{id}
GET    /clients/{id}/historial-facturas
GET    /clients/{id}/score
GET    /collections/facturas-vencidas
GET    /collections/cartera-metricas
POST   /collections/calcular-tamn/{id}
POST   /collections/procesar-pago
GET    /negotiations/ofertas
POST   /negotiations/ofertas/{id}/aceptar
POST   /negotiations/ofertas/{id}/rechazar
GET    /negotiations/tasa-aceptacion
GET    /audit/logs
```

### Configuración de API

El cliente Axios se configura en `src/services/api.ts`:

```typescript
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
});
```

## 🎨 Sistema de Colores

Paleta de colores predefinida en `src/utils/colors.ts`:

| Estado | Color | Hex |
|--------|-------|-----|
| Éxito | Verde | #10B981 |
| Advertencia | Ámbar | #FFC107 |
| Peligro | Rojo | #EF4444 |
| Información | Azul | #2196F3 |
| Primario | Azul Oscuro | #2563EB |

### Asignaciones de Estado

- **Facturas**: Pendiente (ámbar), Pagado (verde), Vencido (rojo)
- **Agentes**: Activo (verde), Idle (gris), Error (rojo)
- **Ofertas**: Pendiente (azul), Aceptada (verde), Rechazada (rojo), Expirada (gris)
- **Mora**: Temprana (amarillo), Media (naranja), Tardía (rojo), Crítica (rojo oscuro)

## 📊 Tipos de Datos

Todas las definiciones de tipos TypeScript están en `src/types/api.ts`:

```typescript
// Ejemplos de tipos principales
interface DashboardMetrics { ... }
interface Factura { ... }
interface Cliente { ... }
interface FacturaVencida { ... }
interface OfertaNegociacion { ... }
interface LogAuditoria { ... }
```

## 🛠️ Funciones Útiles

### Formatting (`src/utils/formatting.ts`)

```typescript
formatCurrency(1500.50)        // "S/ 1,500.50"
formatPercentage(85.5)         // "85.5%"
formatDate('2024-01-15')       // "15/01/2024"
formatDateTime('2024-01-15T10:30:00')  // "15/01/2024 10:30:00"
formatTimeAgo('2024-01-15T10:30:00')   // "hace 2 horas"
formatNumber(1000)             // "1,000"
```

### Colors (`src/utils/colors.ts`)

```typescript
getFacturaStatusColor('Pagado')        // "#10B981"
getAgentStatusColor('activo')          // "#10B981"
getStatusBgClass('Pendiente', 'factura')  // "bg-amber-100"
getMorosidadColor(3.5)                 // "#FCD34D" (ámbar)
```

## 🚀 Scripts

```bash
# Desarrollo
npm run dev

# Build producción
npm run build

# Iniciar servidor producción
npm start

# Lint
npm run lint
```

## 🔐 Autenticación (Fase 2)

Actualmente el dashboard funciona sin JWT. La estructura está preparada para agregarlo:

```typescript
// En api.ts interceptor
if (token) {
  config.headers.Authorization = `Bearer ${token}`;
}
```

## 📱 Responsive Design

Puntos de quiebre utilizados:

- **sm**: 640px - Tablets pequeños
- **md**: 768px - Tablets
- **lg**: 1024px - Desktops pequeños
- **xl**: 1280px - Desktops estándar

Ejemplo:

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
```

## 🌙 Dark Mode

El modo oscuro se implementa con Tailwind CSS:

```tsx
<button onClick={toggleDarkMode}>
  {darkMode ? '☀️' : '🌙'}
</button>

// Clase "dark" se añade a <html>
document.documentElement.classList.toggle('dark');
```

## 📈 Performance

### Optimizaciones implementadas

- **Server Components** en Next.js 14
- **Code Splitting** automático
- **Image Optimization** (si se usan imágenes)
- **CSS Purging** con Tailwind
- **Lazy Loading** de componentes

### Recomendaciones futuras

- Implementar React Query para caché de datos
- WebSockets para actualizaciones en tiempo real
- Service Worker para offline support
- Progressive Web App (PWA)

## 🐛 Debugging

### Logs en navegador

```javascript
// Ver peticiones API
localStorage.setItem('debug', '*');

// Desactivar
localStorage.removeItem('debug');
```

### Environment variables

```bash
# En .env.local
NEXT_PUBLIC_DEBUG=true
```

## 📚 Documentación Adicional

- [Next.js 14 Docs](https://nextjs.org/docs)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Recharts Docs](https://recharts.org/)
- [Axios Docs](https://axios-http.com/)

## 🤝 Contribuciones

1. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
2. Commit cambios: `git commit -am 'Agregar funcionalidad'`
3. Push a rama: `git push origin feature/nueva-funcionalidad`
4. Crear Pull Request

## 📄 Licencia

Este proyecto es propiedad de Integratel. Todos los derechos reservados.

## 📞 Soporte

Para soporte técnico o reportar bugs:

- Email: support@son-ia.local
- Issues: [GitHub Issues]
- Documentación: Ver `docs/` carpeta

## 📝 Changelog

### v1.0.0 (Inicial)
- ✅ Dashboard con métricas
- ✅ Gestión de facturación
- ✅ Perfil de clientes
- ✅ Cobranzas y TAMN
- ✅ Negociación de ofertas
- ✅ Auditoría
- ✅ Modo oscuro
- ✅ Responsive design

### Próximas versiones
- [ ] Autenticación JWT
- [ ] WebSockets en tiempo real
- [ ] Exportación de reportes (PDF/Excel)
- [ ] Búsqueda global
- [ ] Notificaciones push
- [ ] Gráficos avanzados
- [ ] PWA

---

**SON-IA Dashboard** © 2024 Integratel. Todos los derechos reservados.
