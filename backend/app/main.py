"""
SON-IA: Sinergia Operativa del Negocio - Integratel Agéntica
Aplicación Principal FastAPI
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1.router import api_v1_router
from app.config.settings import get_settings
from app.database.connection import init_db

logger = structlog.get_logger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Maneja el ciclo de vida de la aplicación:
    - Startup: Inicializa conexiones a BD, carga modelos ML
    - Shutdown: Cierra conexiones gracefully
    """
    # STARTUP
    logger.info("🚀 Iniciando SON-IA Backend...")
    
    try:
        await init_db()
        logger.info("✅ Conexión a base de datos establecida")
    except Exception as e:
        logger.error(f"❌ Error conectando a BD: {e}")
        raise
    
    yield  # La aplicación se ejecuta aquí
    
    # SHUTDOWN
    logger.info("👋 Apagando SON-IA Backend...")


def create_app() -> FastAPI:
    """
    Factory function para crear la aplicación FastAPI
    """
    app = FastAPI(
        title="SON-IA API",
        description="""
        ## Sinergia Operativa del Negocio - Integratel Agéntica
        
        Ecosistema de agentes de IA para automatización de facturación,
        recaudación y cobranzas.
        
        ### Características Principales:
        - 🤖 **Agentes Especializados**: Supervisor, Facturación, Cobranzas, Negociación
        - 🧠 **IA Híbrida**: Llama-3.3 + Gemini
        - 📊 **Motor Simbólico**: Cálculos exactos (PxQ, IGV, TAMN)
        - 🔒 **Zero-Hallucination**: IA no hace cálculos matemáticos
        - 👤 **Human-in-the-Loop**: Supervisión humana en excepciones
        """,
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # ============================================
    # Middlewares
    # ============================================
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ============================================
    # Routers
    # ============================================
    app.include_router(api_v1_router, prefix="/api/v1")

    # ============================================
    # Monitoring
    # ============================================
    Instrumentator().instrument(app).expose(app)

    # ============================================
    # Global Exception Handlers
    # ============================================
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Error no manejado: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Error interno del servidor",
                "detail": str(exc) if settings.DEBUG else "Contacte al administrador",
            },
        )

    @app.get("/")
    async def root():
        return {
            "app": "SON-IA API",
            "version": "0.1.0",
            "status": "operational",
            "docs": "/api/docs",
        }

    return app


app = create_app()
