# 🚀 SON-IA Dashboard - Quick Start Guide

**Comienza con el dashboard en 5 minutos**

## Prerequisitos
- Node.js 18+
- Backend FastAPI corriendo en http://localhost:8000

## 1️⃣ Instalación (2 minutos)

```bash
# Ir a carpeta del frontend
cd frontend

# Instalar dependencias
npm install
```

## 2️⃣ Configuración (1 minuto)

```bash
# Crear archivo de entorno (copia del ejemplo)
cp .env.local.example .env.local
```

El archivo `.env.local` por defecto ya tiene la URL correcta:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## 3️⃣ Ejecutar en Desarrollo (2 minutos)

```bash
# Iniciar servidor de desarrollo
npm run dev
```

✅ Dashboard disponible en: **http://localhost:3000**

Se redirige automáticamente a `/dashboard-interno`

## 📍 URLs de las Secciones

| Sección | URL | Iconos |
|---------|-----|--------|
| Dashboard | `/dashboard-interno` | 📊 |
| Facturación | `/facturacion` | 📄 |
| Clientes | `/clientes` | 👥 |
| Cobranzas | `/cobranzas` | 💰 |
| Negociación | `/negociacion` | 🤝 |
| Auditoría | `/auditoria` | 📋 |

## 🎮 Primeros Pasos en la UI

### Header
- 🌙 **Modo Oscuro**: Click en icon de luna para activar dark mode
- 🔔 **Notificaciones**: Bell icon (preparado para fase 2)
- 👤 **Perfil**: Avatar en esquina superior derecha

### Sidebar
- 📌 Colapsible: Click en flecha para contraer/expandir
- 🔗 Links a todas las secciones
- ✨ Resaltado de página actual

### Buscar Datos
Todas las páginas tienen:
- **Filtros**: Ajusta parámetros de búsqueda
- **Tabla**: Scroll horizontal en móvil
- **Paginación**: Anterior/Siguiente en footer

### Modales/Detalles
- 👁️ Botón "Ver" en tablas → Abre modal con detalles
- ✏️ Formularios: Completa y envía
- ❌ Click en fondo oscuro para cerrar

## 📝 Datos de Prueba

El dashboard consume datos del backend. Para testing:

### 1. Dashboard Home
```
GET /api/v1/dashboard/metrics
GET /api/v1/dashboard/agentes/estado
```

### 2. Facturación
```
GET /api/v1/billing/facturas?skip=0&limit=10
GET /api/v1/billing/facturas/{id}
```

### 3. Clientes
```
GET /api/v1/clients?skip=0&limit=10
GET /api/v1/clients/{id}
```

### 4. Cobranzas
```
GET /api/v1/collections/facturas-vencidas
GET /api/v1/collections/cartera-metricas
POST /api/v1/collections/procesar-pago
```

### 5. Negociación
```
GET /api/v1/negotiations/ofertas
GET /api/v1/negotiations/tasa-aceptacion
POST /api/v1/negotiations/ofertas/{id}/aceptar
```

### 6. Auditoría
```
GET /api/v1/audit/logs
```

## 🎨 Personalización Rápida

### Cambiar Colores
Archivo: `src/utils/colors.ts`

```typescript
export const colors = {
  primary: "#2563EB",      // Cambiar color primario
  success: "#10B981",      // Verde
  danger: "#EF4444",       // Rojo
  warning: "#F59E0B",      // Ámbar
};
```

### Cambiar Logo/Branding
Archivo: `src/components/layout/Sidebar.tsx` (línea ~25)

```tsx
<h1 className="text-xl font-bold text-blue-600">SON-IA</h1>
// Cambiar "SON-IA" por tu texto
```

### Cambiar Items del Menú
Archivo: `src/components/layout/Sidebar.tsx` (línea ~35)

```tsx
const menuItems = [
  {
    label: 'Dashboard',
    icon: '📊',
    href: '/dashboard-interno',
  },
  // Agregar o modificar aquí
];
```

## 🔍 Debugging

### Ver errores de API
Abre **DevTools** (F12) → Console tab

```javascript
// Ver últimas 10 peticiones
console.log(localStorage.getItem('requests'));
```

### Activar modo debug
```javascript
// En console
localStorage.setItem('debug', '*');
// Recargar página
location.reload();
```

### Datos del usuario actual
El dashboard asume usuario "Admin User" por defecto (ver Header.tsx línea ~60)

## ⚙️ Configuración Avanzada

### Cambiar timeout de API
Archivo: `src/services/api.ts` (línea ~10)

```typescript
const apiClient = axios.create({
  timeout: 30000, // Cambiar a 60000 para 60s
});
```

### Cambiar items por página
Cada página tiene estado `limit`:

```typescript
const [filters, setFilters] = useState({
  limit: 10,  // Cambiar a 20, 50, etc.
});
```

### Agregar nueva sección

1. **Crear página**: `src/app/(dashboard)/nueva-seccion/page.tsx`
2. **Crear servicio**: `src/services/nuevaService.ts`
3. **Agregar tipo**: Actualizar `src/types/api.ts`
4. **Agregar link**: Sidebar.tsx menuItems

## 🐛 Troubleshooting

### Puerto 3000 ocupado
```bash
# Linux/Mac
lsof -i :3000
kill -9 <PID>

# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### API no se conecta
```bash
# Verificar URL
echo $NEXT_PUBLIC_API_URL

# Probar conexión
curl http://localhost:8000/api/v1/health
```

### Estilos no se ven
```bash
# Limpiar caché de Next.js
rm -rf .next
npm run dev
```

### Dark mode no funciona
```bash
# Check localStorage
localStorage.getItem('theme')

# Reset
localStorage.removeItem('theme')
```

## 📦 Build para Producción

```bash
# Crear build optimizado
npm run build

# Probar en producción localmente
npm start
```

URL: http://localhost:3000

## 📊 Estructura de Carpetas (Quick Reference)

```
frontend/
├── src/
│   ├── app/              ← Páginas principales
│   ├── components/       ← Componentes reutilizables
│   │   ├── layout/       ← Header, Sidebar, Footer
│   │   ├── ui/          ← Button, Card, Modal, etc.
│   │   └── dashboard/   ← MetricCard, etc.
│   ├── services/         ← Llamadas a API
│   ├── types/           ← Definiciones TypeScript
│   └── utils/           ← Funciones auxiliares
├── public/              ← Archivos estáticos
└── package.json         ← Dependencias
```

## 🔗 Links Útiles

- [Next.js Docs](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com)
- [Recharts](https://recharts.org/)
- [Axios](https://axios-http.com/)

## 💡 Tips y Trucos

### 1. Recargar datos rápidamente
```javascript
// En consola del navegador
location.reload();
```

### 2. Ver estructura de datos
```javascript
// En consola, en cualquier página
// Ver objeto de ambiente
console.log(process.env);
```

### 3. Copiar tabla a Excel
1. Click derecho en tabla → Inspeccionar
2. Copiar HTML de `<table>`
3. Pegar en Excel → Ajustar formato

### 4. Activar todas las validaciones
Todas las páginas validan datos. Para ver qué se envía:

```typescript
// En cualquier servicio
console.log('API Call:', params);
```

## 🎯 Próximos Pasos Recomendados

1. ✅ Instalar y ejecutar en dev
2. ✅ Navegar por todas las secciones
3. ✅ Revisar código base (componentes/tipos)
4. ✅ Conectar con backend real
5. ✅ Agregar autenticación (JWT - Fase 2)
6. ✅ Implementar WebSockets (Fase 3)

## 📞 Soporte Rápido

- **Issue**: Revisar console (F12)
- **Pregunta**: Ver README_FRONTEND.md
- **Error de API**: Verificar que backend esté corriendo
- **Build error**: Ejecutar `rm -rf .next && npm run dev`

---

**¡Listo para usar! 🎉**

Cualquier duda, revisa la documentación completa en `README_FRONTEND.md`
