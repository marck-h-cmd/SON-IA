"""
Dependencias reutilizables para endpoints FastAPI
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency para obtener sesión de base de datos.
    
    Uso:
    @router.get("/items")
    async def get_items(db: AsyncSession = Depends(get_db)):
        ...
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