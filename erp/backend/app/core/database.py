"""
Configuração do SQLAlchemy async com PostgreSQL.
Usa asyncpg como driver. Nunca usar conexões síncronas neste projeto.
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()

# Engine assíncrono — pool padrão (5 conexões, max_overflow 10)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    """Base para todos os modelos ORM do projeto."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency FastAPI que fornece uma sessão de banco por request.
    A sessão é fechada automaticamente ao final do request.
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
