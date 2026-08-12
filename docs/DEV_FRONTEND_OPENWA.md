# Guía para el Dev de Frontend: Conexión Backend ↔ OpenWA

Esta guía explica cómo levantar el backend de SON-IA y conectarlo con el
gateway de WhatsApp (OpenWA) en TU máquina local, incluyendo cómo registrar
una sesión propia con tu propio WhatsApp si no usas la de integración.

---

## 1. Levantar el backend (FastAPI + Postgres + Redis)

```bash
# Desde la raíz del proyecto (donde está docker-compose.yml)
make up
# o equivalentemente:
UID=$(id -u) GID=$(id -g) docker compose up -d
```

Verificar que los 5 servicios estén arriba:

```bash
docker compose ps
```

Servicios esperados: `son-ia-db`, `son-ia-redis`, `son-ia-backend`,
`son-ia-celery`, `son-ia-flower`, `son-ia-frontend`.

El backend queda escuchando en `http://localhost:8000`.

- Documentación Swagger de la API (para ver cada endpoint y su respuesta):
  `http://localhost:8000/api/docs`
- Ejemplo de ruta: `GET http://localhost:8000/api/v1/dashboard/metrics`

---

## 2. El frontend NO necesita config de la API

El frontend consume el backend mediante el **proxy de Next.js** (ya configurado
en `frontend/next.config.js`):

```js
/api/proxy/:path*  ->  http://backend:8000/api/v1/:path*
```

Es decir: dentro del frontend NO se llama a `http://localhost:8000/api/v1/...`;
se llama a `http://localhost:3000/api/proxy/...` (rutas relativas, sin dominio).

Ejemplo dentro de componentes React:

```ts
const res = await fetch('/api/proxy/dashboard/metrics');
const data = await res.json(); // { status, metrics: {...} }
```

Regla: **siempre rutas relativas `/api/proxy/...`**, nunca `localhost:8000`
(ni hardcodear el host; además el proxy resuelve el hostname interno `backend`).

---

## 3. Conexión Backend ↔ OpenWA (WhatsApp)

El flujo es:

```
Cliente escribe a tu WhatsApp
        │
        ▼
OpenWA (gateway externo, publica puerto 2785)
        │  "message.received" -> hace POST al webhook
        ▼
URL pública del backend (túnel localtunnel)
        ▼
GET/POST http://localhost:8000/api/v1/whatsapp/webhook
        │  identifica al cliente por teléfono, arma respuesta
        ▼
OpenWA -> /api/sessions/{SESSION_ID}/messages/send-text
        ▼
Respuesta al cliente por WhatsApp
```

### 3.1 Requisitos de red

El backend (contenedor Docker `son-ia-backend`) y el contenedor de OpenWA
(`openwa-api`) deben **compartir una red Docker** llamada `openwa-network`.

Esto ya está declarado en `docker-compose.yml` como red externa:

```yaml
networks:
  openwa:
    external: true
    name: openwa-network
```

Para que funcione, la red `openwa-network` **debe existir** en tu máquina.
La crea el stack de OpenWA. Si tu OpenWA usa otra red/stack, ajusta el nombre
en `docker-compose.yml` (y el `OPENWA_BASE_URL` del `.env`).

### 3.2 Configuración en `backend/.env`

```bash
# backend/.env
OPENWA_API_KEY=tu_api_key_aquí           # key del OpenWA accesible para TU sesión
OPENWA_BASE_URL=http://openwa-api:2785   # hostname DENTRO de la red Docker de OpenWA
OPENWA_SESSION_NAME=7d71ec12-...         # UUID de TU sesión (ver sección 4)
```

> Importante: `OPENWA_BASE_URL` apunta al hostname interno de la red Docker
> (`openwa-api`), NO a `localhost:2785`. Desde dentro del contenedor backend,
> `localhost` no alcanza a OpenWA.

> Importante: OpenWA identifica la sesión por su **UUID**, no por su nombre.
> Poner aquí el UUID (id) de tu sesión activa.

### 3.3 Exponer el backend públicamente (túnel localtunnel)

OpenWA rechaza llamar a URLs internas; debe llamar a una **URL pública** del
backend. Se usa localtunnel (sin cuenta):

```bash
make tunnel
# genera algo como: your url is: https://XXXX.loca.lt
```

- El túnel NO necesita cuenta/token (a diferencia de ngrok).
- Cambia la URL en cada ejecución; si cambia, hay que re-registrar el webhook.

### 3.4 Registrar el webhook en OpenWA

Con el túnel corriendo, registra en OpenWA hacia dónde enviar los mensajes
entrantes (evento `message.received`):

> La URL del webhook SIEMPRE debe terminar en
> `/api/v1/whatsapp/webhook`. Solo cambia la parte del dominio (el subdominio
> generado por el túnel). Verificarla siempre es:
> `https://<DominioDelTúnel>.loca.lt/api/v1/whatsapp/webhook`.

```bash
curl -X POST http://localhost:8000/api/v1/whatsapp/configure-webhook \
  -H "Content-Type: application/json" \
  -d '{
        "url": "https://XXXX.loca.lt/api/v1/whatsapp/webhook",
        "session_name": "TU_UUID_DE_SESION"
      }'
```

> **Importante:** cada vez que reinicies el túnel (`make tunnel`), la URL
> cambia → re-registra el webhook con la URL nueva. Además abre la lista de
> webhooks de la sesión y **borra los antiguos** (que apuntan a túneles
> muertos), si no OpenWA seguirá intentando POSTear a las URLs viejas:

```bash
# listar (ver IDs y URL de cada webhook registrado)
curl -s -H "X-API-Key: TU_API_KEY" \
  http://localhost:2785/api/sessions/TU_UUID_DE_SESION/webhooks
# borrar uno viejo con su ID (ejemplo)
  curl -s -X DELETE -H "X-API-Key: TU_API_KEY" \
  http://localhost:2785/api/sessions/TU_UUID_DE_SESION/webhooks/<ID_DEL_VEJO>
```

Verifica que quedó activo:

```bash
# desde cualquier lado
curl -s http://localhost:8000/api/v1/whatsapp/health
# -> {"status":"ok","openwa_http":200,...}
```

---

## 4. Usar TU propia sesión de WhatsApp en OpenWA

No es obligatorio usar la sesión de integración; puedes crear la tuya:

1. Abre el panel/admin de OpenWA (`http://localhost:2785` aprox.).
2. Crea una sesión nueva (p. ej. `sesion-dev`).
3. Escanea el **código QR** con tu WhatsApp (WhatsApp Web Linked Devices).
   Espera a que el estado sea `ready`/`connected`.
4. Obten el **UUID (id) de la sesión** — el panel/admin te lo muestra, o vía API:

```bash
# listar sesiones de tu OpenWA
curl -s -H "X-API-Key: TU_API_KEY" http://localhost:2785/api/sessions
# -> [{ "id": "7d71ec12-...", "name": "sesion-dev", "status": "ready", ... }]
```

5. Pega ese `id` (UUID) en `backend/.env`:

```bash
OPENWA_SESSION_NAME=7d71ec12-907c-448d-9f3a-a859f5737f3c   # <- TU uuid
```

6. Reinicia el backend para que tome el nuevo valor:

```bash
make up   # recrea los contenedores con el nuevo .env
```

7. Re-registra el webhook (sección 3.4) con TU UUID.

### 4.1 Probar envío manual con tu sesión

```bash
curl -X POST http://localhost:8000/api/v1/whatsapp/send \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"901528082","message":"Hola 👋, prueba desde el backend"}'
```

- El número debe ser un **celular real de 9 dígitos** (Perú: 9XXXXXXXX).
- La sesión de OpenWA debe tener **chat previo** con ese número (escríbele 1
  mensaje desde el WhatsApp vinculado la primera vez); si no, WhatsApp devuelve
  400.
- Si el mensaje va a TU propio número, responde ahí.

### 4.2 Probar la recepción (webhook end‑to‑end)

1. Túnel corriendo (`make tunnel`) y webhook registrado con la URL del túnel.
2. Desde el WhatsApp vinculado a TU sesión, escribe por ejemplo:
   `"¿cuánto debo?"`
3. Esperas la respuesta automática del backend con datos reales
   (saldo, facturas vencidas, oferta), enviada de vuelta por WhatsApp.

---

## 5. Checklist rápida si "no conecta"

| Síntoma | Causa probable | Fix |
|---|---|---|
| `whatsapp/health` da `error`/timeout | Backend y OpenWA en redes Docker distintas | `OPENWA_BASE_URL=http://openwa-api:2785` + red `openwa-network` compartida (sección 3.1) |
| `send` responde `400 ... is not active` | Estás usando el *nombre* de la sesión | Usar el **UUID** de la sesión (sección 4.4) |
| `send` responde `400 ... could not resolve recipient` | Número no es celular 9 dígitos, o no hay chat previo | Número real de 9 dígitos; mensajearlo 1 vez desde el WhatsApp vinculado |
| `send` responde `401 Unauthorized` | API key incorrecta | Revisar `OPENWA_API_KEY` en `backend/.env` |
| El webhook recibe mensajes pero no responde | El túnel cambió de URL | Re-registrar webhook con la nueva URL (sección 3.4) |
| `/api/proxy/...` da 404 desde el frontend | `next.config.js` sin los rewrites | Copiar el bloque `rewrites` a `frontend/next.config.js` y reiniciar el frontend |

---

## 6. OpenAPI / Swagger

- Swagger UI: `http://localhost:8000/api/docs`
- Spec JSON: `http://localhost:8000/api/openapi.json`

Toda ruta de la API tiene documentado: URL, query params y la forma de la
respuesta (etiqueta `PARA EL FRONTEND`).