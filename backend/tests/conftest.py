"""
Fixtures compartidas para tests de SON-IA
"""

import pytest
import asyncio
from typing import AsyncGenerator


@pytest.fixture(scope="session")
def event_loop():
    """Crea un event loop para tests asíncronos"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session():
    """Fixture para sesión de base de datos en tests"""
    # Usar SQLite en memoria para tests
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    
    async with engine.begin() as conn:
        from app.database.models import Base
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine) as session:
        yield session
    
    await engine.dispose()


@pytest.fixture
def sample_cliente_data():
    """Datos de cliente de prueba"""
    return {
        "id_cliente": 1001,
        "tipo_doc": "6",
        "num_doc": "20100000001",
        "nombre_razon_social": "Empresa Test S.A.C.",
        "segmento": "B2B",
        "email_contacto": "test@empresa.com",
        "score_confianza": 0.85,
    }


@pytest.fixture
def sample_servicio_data():
    """Datos de servicio de prueba"""
    return {
        "id_servicio": 3001,
        "tecnologia": "Fibra Óptica",
        "cargo_fijo_mensual": 2500.00,
        "estado_servicio": "Activo",
    }