"""
Cliente REST para OpenWA (Gateway de WhatsApp).

Es un servicio externo independiente que corre en http://localhost:2785.
Solo se consume su API REST, no se modifica su código.

Endpoints reales de OpenWA 0.16:
- Envío de texto:    POST /api/sessions/{session}/messages/send-text
                     body: {"chatId": "<pais><numero>@c.us", "text": "..."}
- Config webhook:    POST /api/sessions/{session}/webhooks
                     body: {"url": "...", "events": ["message.received"], ...}

Autenticación vía header "X-API-Key".
"""

import re
from typing import Any, Dict, Optional

import httpx
import structlog

from app.config.settings import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

# Código de país por defecto para números peruanos (movistar)
DEFAULT_COUNTRY_CODE = "51"


def normalize_phone(phone: str | int) -> str:
    """
    Convierte un número al formato nacional peruano de 9 dígitos
    (sin código de país). Ej: "+51901528082" -> "901528082".
    Usado para buscar al cliente en la BD (columna numero_celular).
    """
    digits = re.sub(r"\D", "", str(phone))
    if digits.startswith(DEFAULT_COUNTRY_CODE) and len(digits) == 11:
        return digits[2:]  # quitar 51
    if digits.startswith("00" + DEFAULT_COUNTRY_CODE) and len(digits) == 13:
        return digits[4:]
    return digits


def to_chat_id(phone: str | int) -> str:
    """
    Convierte un número local o group ID al WID de WhatsApp: <pais><numero>@c.us o <id>@g.us.
    Ej: "901528082" -> "51901528082@c.us"
    Ej: "120363024823948293@g.us" -> "120363024823948293@g.us"
    """
    s = str(phone).strip()
    if "@g.us" in s or "@c.us" in s or "@lid" in s or "@s.whatsapp.net" in s:
        return s
    digits = normalize_phone(s)
    if not digits.startswith(DEFAULT_COUNTRY_CODE):
        digits = DEFAULT_COUNTRY_CODE + digits
    return f"{digits}@c.us"


class OpenWAClient:
    """
    Cliente asíncrono para enviar mensajes de WhatsApp vía OpenWA.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        session_name: Optional[str] = None,
    ) -> None:
        self.base_url = (base_url or settings.OPENWA_BASE_URL).rstrip("/")
        self.api_key = api_key or settings.OPENWA_API_KEY
        self.session_name = session_name or settings.OPENWA_SESSION_NAME
        self.timeout = 15.0

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    async def send_message(
        self,
        phone_number: str,
        message: str,
        session_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Envía un mensaje de texto de WhatsApp al número indicado.

        Args:
            phone_number: Número de teléfono de destino (local o internacional)
            message: Texto del mensaje a enviar
            session_name: Sesión de WhatsApp activa en OpenWA (default: env OPENWA_SESSION_NAME)

        Returns:
            {"success": bool, "data": {...}} o {"success": False, "error": ...}
        """
        session = session_name or self.session_name
        # 🛡️ Blindaje de Seguridad Saliente: Solo permitir envío a números/grupos autorizados
        allowed_demo = (getattr(settings, "WHATSAPP_DEMO_ALLOWED_PHONE", "") or "").strip()
        if allowed_demo:
            allowed_items = [n.strip() for n in allowed_demo.split(",") if n.strip()]
            allowed_normalized_phones = [normalize_phone(n) for n in allowed_items if "@g.us" not in n]
            allowed_groups = [n.lower() for n in allowed_items if "@g.us" in n or len(n) > 15]

            target_norm = normalize_phone(phone_number)
            target_lower = str(phone_number).lower()

            matches_phone = bool(target_norm and target_norm in allowed_normalized_phones)
            matches_group = any(g in target_lower for g in allowed_groups)
            matches_lid = "@lid" in target_lower

            if not (matches_phone or matches_group or matches_lid):
                logger.warning(
                    "🛡️ [Sandbox Saliente] Envío bloqueado a destinatario no autorizado",
                    destinatario=phone_number,
                    autorizados=allowed_items,
                )
                return {
                    "success": False,
                    "error": "Destinatario bloqueado por filtro de seguridad (WHATSAPP_DEMO_ALLOWED_PHONE)",
                    "blocked_by_sandbox": True,
                }

        logger.info("📨 OpenWA: enviando mensaje WhatsApp", phone_number=phone_number, session=session)

        url = f"{self.base_url}/api/sessions/{session}/messages/send-text"
        payload = {
            "chatId": to_chat_id(phone_number),
            "text": message,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=self._headers())
                response.raise_for_status()
                return {"success": True, "data": response.json()}
        except (httpx.HTTPError, ValueError, TimeoutError) as exc:
            logger.error("❌ OpenWA: error enviando mensaje", error=str(exc), error_type=type(exc).__name__)
            return {"success": False, "error": str(exc), "error_type": type(exc).__name__}

    async def send_template(
        self,
        phone_number: str,
        template_name: str,
        params: Optional[Dict[str, Any]] = None,
        session_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Envía una plantilla de mensaje (para notificaciones fuera de la ventana de 24h).

        Args:
            phone_number: Número de teléfono de destino
            template_name: Nombre de la plantilla en WhatsApp
            params: Parámetros de la plantilla
            session_name: Sesión de WhatsApp

        Returns:
            {"success": bool, "data": {...}} o {"success": False, "error": ...}
        """
        session = session_name or self.session_name
        url = f"{self.base_url}/api/sessions/{session}/messages/send-template"
        payload = {
            "chatId": to_chat_id(phone_number),
            "template": {"name": template_name, "params": params or {}},
        }

        logger.info("📨 OpenWA: enviando plantilla", phone_number=phone_number, template=template_name)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=self._headers())
                response.raise_for_status()
                return {"success": True, "data": response.json()}
        except (httpx.HTTPError, ValueError, TimeoutError) as exc:
            logger.error("❌ OpenWA: error enviando plantilla", error=str(exc), error_type=type(exc).__name__)
            return {"success": False, "error": str(exc), "error_type": type(exc).__name__}

    async def configure_webhook(
        self,
        webhook_url: str,
        events: Optional[list] = None,
        secret: Optional[str] = None,
        session_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Registra un webhook para la sesión de OpenWA.

        Args:
            webhook_url: URL pública (ngrok) del backend que recibirá los mensajes
            events: Eventos a suscribir (default: ["message.received"])
            secret: Secreto opcional firmado por OpenWA en el header X-OpenWA-Signature
            session_name: Sesión de WhatsApp

        Returns:
            {"success": bool, "data": {...}} o {"success": False, "error": ...}
        """
        session = session_name or self.session_name
        url = f"{self.base_url}/api/sessions/{session}/webhooks"
        payload: Dict[str, Any] = {
            "url": webhook_url,
            "events": events or ["message.received"],
        }
        if secret:
            payload["secret"] = secret

        logger.info("🔗 OpenWA: configurando webhook", url=webhook_url, events=payload["events"])

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=self._headers())
                response.raise_for_status()
                return {"success": True, "data": response.json()}
        except (httpx.HTTPError, ValueError, TimeoutError) as exc:
            logger.error("❌ OpenWA: error configurando webhook", error=str(exc), error_type=type(exc).__name__)
            return {"success": False, "error": str(exc), "error_type": type(exc).__name__}


# Singleton
openwa_client = OpenWAClient()