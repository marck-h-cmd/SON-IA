"""
Endpoints de validación de identidad vía Open Gateway (Movistar)
"""

import asyncio
from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.integrations.open_gateway_client import open_gateway_client

router = APIRouter(tags=["Identity"])


class ValidateIdentityRequest(BaseModel):
    """Cuerpo de la petición para validar identidad de un cliente"""

    phone_number: str = Field(..., description="Número de teléfono en formato internacional, ej: +51123456789")


@router.post("", response_model=Dict[str, Any], summary="Valida identidad del cliente contra Open Gateway")
async def validate_identity(body: ValidateIdentityRequest) -> Dict[str, Any]:
    """
    Prueba las tres validaciones de Open Gateway de forma simultánea:

    - **SIM Swap**: detecta si la SIM fue cambiada en las últimas 24h (fraude).
    - **Number Verification**: verifica que el número coincide con el dispositivo.
    - **Device Status**: comprueba si el dispositivo está en roaming.

    Permite probar la integración desde Postman o el frontend.
    """
    phone_number = body.phone_number

    # Ejecutar las tres validaciones en paralelo (no se bloquean entre sí)
    sim_swap, number_verification, device_status = await asyncio.gather(
        open_gateway_client.verify_sim_swap(phone_number),
        open_gateway_client.verify_number(phone_number),
        open_gateway_client.check_device_status(phone_number),
    )

    # Verdict consolidado: todas deben estar OK (sin SIM swap ni roaming)
    all_ok = (
        sim_swap.get("success", False)
        and not sim_swap.get("swapped", False)
        and number_verification.get("success", False)
        and number_verification.get("verified", False)
        and device_status.get("success", False)
        and not device_status.get("roaming", False)
    )

    return {
        "status": "approved" if all_ok else "rejected",
        "phone_number": phone_number,
        "validations": {
            "sim_swap": sim_swap,
            "number_verification": number_verification,
            "device_status": device_status,
        },
    }