"""
Endpoints de WhatsApp (OpenWA)

ROL DEL AGENTE DE COBRANZAS/NEGOCIACIÓN VÍA WHATSAPP
-----------------------------------------------------
SON-IA automatiza la cobranza y recaudación end-to-end. El canal WhatsApp
(mediante el gateway externo OpenWA) es el puente hacia el cliente real:

- ENTRADA:  OpenWA reenvía aquí los mensajes que el cliente escribe (webhook).
            SON-IA identifica al cliente por su número de celular, clasifica la
            intención (saldo, factura, negociación, saludo) y responde con datos
            REALES de bss_facturas / bss_pagos.
- SALIDA:   El Agente de Cobranzas o de Negociación genera mensajes estructurados
            (links de pago express, resúmenes de ofertas, confirmaciones de pago)
            y los envía a los números reales de los clientes usando OpenWA.
- CICLO:    el backend NUNCA conversa por WhatsApp directamente; siempre a través
            de OpenWA (POST /api/sessions/{session}/messages/send-text).

Endpoints (para el frontend):
- POST /v1/whatsapp/webhook           -> OpenWA envía mensajes entrantes (NO lo llama el frontend)
- POST /v1/whatsapp/send              -> probar envíos manuales desde el backend
- POST /v1/whatsapp/configure-webhook -> registrar la URL pública del webhook en OpenWA
- GET  /v1/whatsapp/health            -> estado de la conexión con OpenWA
"""

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.integrations.openwa_client import openwa_client
from app.services.whatsapp_webhook_service import whatsapp_webhook_service

router = APIRouter(tags=["WhatsApp"])


class SendMessageRequest(BaseModel):
    """Petición para enviar un mensaje de WhatsApp manualmente"""

    phone_number: str = Field(..., description="Número de destino, ej: 901528082 o +51901528082")
    message: str = Field(..., min_length=1, max_length=4096)
    session_name: Optional[str] = None


class ConfigureWebhookRequest(BaseModel):
    """Petición para registrar el webhook del backend en OpenWA"""

    url: str = Field(..., description="URL pública (ngrok) del backend, ej: https://abc123.ngrok.app/api/v1/whatsapp/webhook")
    session_name: Optional[str] = None
    events: Optional[list] = None


@router.post("/webhook", summary="Recibe mensajes entrantes de OpenWA")
async def whatsapp_webhook(
    payload: dict,
    db: AsyncSession = Depends(get_db),
):
    """
    PUNTO DE ENTRADA DE MENSAJES DE WHATSAPP (lo llama OpenWA, NO el frontend).

    PARA EL FRONTEND:
    - Esta ruta NO se consume desde el frontend; es el destino del webhook
      que OpenWA configura (URL pública del backend + /api/v1/whatsapp/webhook).
    - Los eventos del bot (mensajería del cliente por WhatsApp) NO pasan por
      las pantallas del dashboard; solo se reflejan en el log de auditoría.

    FLUJO INTERNO (Agente de Cobranzas vía WhatsApp):
    1. OpenWA recibe un mensaje del cliente y hace POST aquí.
    2. Se identifica al cliente por su número de celular (bss_clientes.numero_celular).
    3. Se clasifica la intención: consulta_saldo, consulta_factura, negociacion, saludo.
    4. Se arma la respuesta con datos REALES de bss_facturas/bss_pagos
       (ej: "tu saldo pendiente es S/ 466.34 en 9 facturas").
    5. Se envía la respuesta por OpenWA al mismo número.

    Respuesta: { status, success, phone, intent, client_found, reply, send_result }
    """
    return await whatsapp_webhook_service.process_payload(payload, db)


@router.post("/send", summary="Envía un mensaje de WhatsApp manualmente")
async def whatsapp_send(body: SendMessageRequest):
    """
    ENVÍO MANUAL DE WHATSAPP (para pruebas, no lo usa el frontend).

    PARA EL FRONTEND:
    - No es una pantalla del dashboard. Sirve para que el equipo valide
      el canal de salida (Agente de Cobranzas/Negociación) sin esperar un
      mensaje del cliente.
    - El número de destino debe ser un celular real de 9 dígitos y con
      chat previo con la sesión de OpenWA (si no, WhatsApp responde 400).

    Ej:
    {"phone_number": "901528082", "message": "Hola, prueba desde el backend"}
    """
    return await openwa_client.send_message(
        phone_number=body.phone_number,
        message=body.message,
        session_name=body.session_name,
    )


@router.post("/configure-webhook", summary="Registra la URL del webhook en OpenWA")
async def whatsapp_configure_webhook(body: ConfigureWebhookRequest):
    """
    REGISTRA EL WEBHOOK EN OPENWA (tarea de configuración, no del frontend).

    PARA EL FRONTEND:
    - Lo usa el equipo técnico (o un script de despliegue) para decirle a
      OpenWA hacia qué URL pública del backend reenviar los mensajes entrantes.
    - Si el túnel público cambia (ej: localtunnel reinicia su URL), se debe
      re-registrar con la nueva URL.

    Ej:
    {
      "url": "https://XXXXX.loca.lt/api/v1/whatsapp/webhook",
      "session_name": "7d71ec12-907c-448d-9f3a-a859f5737f3c"
    }
    """
    return await openwa_client.configure_webhook(
        webhook_url=body.url,
        events=body.events,
        session_name=body.session_name,
    )


@router.get("/health", summary="Verifica la conexión con OpenWA")
async def whatsapp_health():
    """
    ESTADO DE LA CONEXIÓN CON OPENWA (para monitoreo).

    PARA EL FRONTEND:
    - Puede usarse en el dashboard interno como indicador de disponibilidad
      del canal WhatsApp (badge "WhatsApp conectado / caído").
    - Respuesta: { status, openwa_http, base_url }
      - status:     "ok" | "error"
      - openwa_http: código HTTP de la respuesta de OpenWA (200 = bien)
      - base_url:   URL interna usada (http://openwa-api:2785)
    """
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{openwa_client.base_url}/api/health",
                                    headers=openwa_client._headers())
        return {"status": "ok", "openwa_http": resp.status_code, "base_url": openwa_client.base_url}
    except Exception as exc:
        return {"status": "error", "error": str(exc), "base_url": openwa_client.base_url}