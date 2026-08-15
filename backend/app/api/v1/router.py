"""
Router principal de la API v1
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    billing,
    clients,
    dashboard,
    collections,
    negotiations,
    audit,
    validate_identity,
    whatsapp,
    hitl,
)

api_v1_router = APIRouter()

# Incluir sub-routers
api_v1_router.include_router(health.router, prefix="/health", tags=["Health"])
api_v1_router.include_router(billing.router, prefix="/billing", tags=["Billing"])
api_v1_router.include_router(clients.router, prefix="/clients", tags=["Clients"])
api_v1_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_v1_router.include_router(collections.router, prefix="/collections", tags=["Collections"])
api_v1_router.include_router(negotiations.router, prefix="/negotiations", tags=["Negotiations"])
api_v1_router.include_router(audit.router, prefix="/audit", tags=["Audit"])
api_v1_router.include_router(validate_identity.router, prefix="/validate-identity", tags=["Identity"])
api_v1_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["WhatsApp"])
api_v1_router.include_router(hitl.router, prefix="/hitl", tags=["Human-in-the-Loop"])