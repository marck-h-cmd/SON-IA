"""
Gestión de conexiones a bases de datos
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.config.settings import get_settings
from app.database.models import Base
import structlog

logger = structlog.get_logger(__name__)
settings = get_settings()

# Engine asíncrono para PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

# Factory de sesiones
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """
    Inicializa la base de datos creando todas las tablas.
    En producción usar Alembic migrations.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Tablas creadas exitosamente")
    except Exception as e:
        logger.error(f"❌ Error creando tablas: {e}")
        raise


async def get_db() -> AsyncSession:
    """
    Dependency para obtener sesión de BD.
    Uso en FastAPI: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()