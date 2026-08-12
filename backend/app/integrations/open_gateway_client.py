"""
Cliente asíncrono para Open Gateway (Movistar / Telefónica).

Consume las APIs CAMARA expuestas por Open Gateway:
1. SIM Swap API      -> detecta si la SIM fue cambiada recientemente (fraude)
2. Number Verification API -> verifica que el número coincide con el dispositivo
3. Device Status API -> comprueba si el dispositivo está en roaming

Autenticación: OAuth 2.0 (grant_type=client_credentials) con caché del token
y renovación automática ante respuestas 401.
"""

import time
from typing import Any, Dict, Optional

import httpx
import structlog

from app.config.settings import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class OpenGatewayClient:
    """
    Cliente HTTP asíncrono para las APIs de Open Gateway.

    Se inicializa con las credenciales desde variables de entorno
    (o valores explícitos) y maneja de forma centralizada:
    - Obtención/caché del access_token (client_credentials).
    - Renovación automática del token si expira (reintento ante 401).
    - Timeouts, errores 4xx/5xx y respuestas estructuradas {success, error}.
    """

    # Paths CAMARA bajo el API Gateway de Telefónica
    SIM_SWAP_PATH = "/apigateway/sim-swap/v0/retrieve"
    NUMBER_VERIFICATION_PATH = "/apigateway/number-verification/v0/verify"
    DEVICE_STATUS_PATH = "/apigateway/device-status/v0/retrieve"

    TOKEN_TIMEOUT = 15.0
    API_TIMEOUT = 30.0

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token_url: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        # Credenciales desde parámetros o variables de entorno
        self.client_id = client_id or settings.OPEN_GATEWAY_CLIENT_ID
        self.client_secret = client_secret or settings.OPEN_GATEWAY_CLIENT_SECRET
        self.token_url = token_url or settings.OPEN_GATEWAY_TOKEN_URL
        self.base_url = (base_url or settings.OPEN_GATEWAY_BASE_URL).rstrip("/")

        # Caché del token OAuth
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0.0

    # ============================================================
    # Autenticación (OAuth 2.0 client_credentials)
    # ============================================================

    def _is_token_valid(self) -> bool:
        """
        Verifica si el token en caché sigue vigente.

        Se resta un margen de 30s para evitar usarlo justo antes de expirar.
        """
        return bool(self._access_token) and time.time() < (self._token_expires_at - 30)

    async def _get_access_token(self) -> str:
        """
        Obtiene (y cachea) el access_token usando grant_type=client_credentials.

        Si el token en caché es válido lo reutiliza; en caso contrario
        solicita uno nuevo y guarda su expiración (expires_in).
        """
        if self._is_token_valid():
            return self._access_token  # type: ignore[return-value]

        logger.info("🔑 Open Gateway: solicitando nuevo access_token")
        async with httpx.AsyncClient(timeout=self.TOKEN_TIMEOUT) as client:
            response = await client.post(
                self.token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )
            response.raise_for_status()
            payload = response.json()

        token = payload.get("access_token", "")
        if not token:
            raise ValueError("La respuesta del token no incluye access_token")

        expires_in = float(payload.get("expires_in", 3600))
        self._access_token = token
        self._token_expires_at = time.time() + expires_in
        logger.info("🔑 Open Gateway: access_token obtenido", expires_in_seconds=expires_in)
        return token

    # ============================================================
    # Core HTTP
    # ============================================================

    async def _api_post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía un POST autenticado a una API de Open Gateway.

        Reintenta UNA vez si el servidor responde 401, forzando la
        renovación del token antes del segundo intento.
        """
        url = f"{self.base_url}{path}"

        for attempt in (1, 2):
            token = await self._get_access_token()
            headers = {"Authorization": f"Bearer {token}"}

            async with httpx.AsyncClient(timeout=self.API_TIMEOUT) as client:
                response = await client.post(url, headers=headers, json=payload)

            if response.status_code == 401 and attempt == 1:
                # Token expirado o revocado: invalidar caché y reintentar
                logger.warning("⚠️ Open Gateway: 401, renovando token")
                self._access_token = None
                self._token_expires_at = 0.0
                continue

            response.raise_for_status()
            return response.json()

        raise RuntimeError("Open Gateway: autenticación fallida tras dos intentos")

    def _error_response(self, operation: str, error: Exception) -> Dict[str, Any]:
        """Devuelve una respuesta estructurada de error, sin lanzar excepciones."""
        logger.error(f"❌ Open Gateway: falló {operation}", error=str(error), error_type=type(error).__name__)
        return {
            "success": False,
            "operation": operation,
            "error": str(error),
            "error_type": type(error).__name__,
        }

    # ============================================================
    # Métodos públicos
    # ============================================================

    async def verify_sim_swap(self, phone_number: str, hours: int = 24) -> Dict[str, Any]:
        """
        Detecta si la SIM del cliente fue cambiada en las últimas `hours` horas.

        Regla de negocio:
        - `swapped=True` indica un posible fraude (cambio de SIM reciente).

        Returns:
            {"success": bool, "swapped": bool, "latest_sim_change_at": str, "data": {...}}
        """
        operation = "verify_sim_swap"
        logger.info("🛡️ Open Gateway: consultando SIM Swap", phone_number=phone_number, hours=hours)
        try:
            data = await self._api_post(
                self.SIM_SWAP_PATH,
                {"phoneNumber": phone_number, "maxAge": hours * 3600},
            )
            sim_change = data.get("latestSimChange", {})
            return {
                "success": True,
                "operation": operation,
                "swapped": bool(data.get("swapped", False)),
                "latest_sim_change_at": sim_change.get("latestSimChangeAt"),
                "data": data,
            }
        except (httpx.HTTPError, ValueError, TimeoutError, RuntimeError) as exc:
            return self._error_response(operation, exc)

    async def verify_number(self, phone_number: str) -> Dict[str, Any]:
        """
        Verifica que el número del cliente coincide con el dispositivo
        que realiza la solicitud (Number Verification API).

        Returns:
            {"success": bool, "verified": bool, "data": {...}}
        """
        operation = "verify_number"
        logger.info("🔐 Open Gateway: verificando número", phone_number=phone_number)
        try:
            data = await self._api_post(
                self.NUMBER_VERIFICATION_PATH,
                {"phoneNumber": phone_number},
            )
            return {
                "success": True,
                "operation": operation,
                "verified": bool(data.get("devicePhoneNumberVerified", False)),
                "data": data,
            }
        except (httpx.HTTPError, ValueError, TimeoutError, RuntimeError) as exc:
            return self._error_response(operation, exc)

    async def check_device_status(self, phone_number: str) -> Dict[str, Any]:
        """
        Comprueba si el dispositivo del cliente está en roaming
        (para alertas de seguridad).

        Returns:
            {"success": bool, "roaming": bool, "last_status_change_at": str, "data": {...}}
        """
        operation = "check_device_status"
        logger.info("📡 Open Gateway: consultando estado del dispositivo", phone_number=phone_number)
        try:
            data = await self._api_post(
                self.DEVICE_STATUS_PATH,
                {
                    "phoneNumber": phone_number,
                    "deviceStatus": {"roaming": True},  # solicitamos solo roaming
                },
            )
            roaming = data.get("deviceStatus", {}).get("roaming", {})
            return {
                "success": True,
                "operation": operation,
                "roaming": bool(roaming.get("status", False)),
                "last_status_change_at": roaming.get("lastStatusChangeAt"),
                "data": data,
            }
        except (httpx.HTTPError, ValueError, TimeoutError, RuntimeError) as exc:
            return self._error_response(operation, exc)


# Singleton
open_gateway_client = OpenGatewayClient()