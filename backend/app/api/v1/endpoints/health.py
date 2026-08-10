"""
Endpoints de Health Check
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database.connection import get_db

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """
    Health check básico para monitoreo y balanceadores de carga
    """
    return {
        "status": "ok",
        "app": "SON-IA",
        "version": "0.1.0",
    }


@router.get("/health/detailed")
async def health_detailed(db: AsyncSession = Depends(get_db)):
    """
    Health check detallado que verifica conexión a BD
    """
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"
    
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "components": {
            "api": "ok",
            "database": db_status,
        },
    }