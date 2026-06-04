"""
Fixtures compartilhadas entre todos os testes.

Usa SQLite em memória para isolamento e velocidade.
Cada módulo de teste tem seu próprio banco limpo.
"""
import asyncio
from decimal import Decimal
from typing import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.core.security import criar_access_token, hash_senha
from app.main import app
from app.models.base import PerfilUsuario
from app.models.estoque import Estoque
from app.models.produto import Produto
from app.models.usuario import Usuario

# Engine de teste — SQLite async em memória (uma instância por módulo)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


def make_engine():
    return create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )


@pytest.fixture(scope="module")
def event_loop():
    """Loop de eventos compartilhado por módulo de testes."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
async def test_engine():
    """Engine SQLite por módulo de testes."""
    engine = make_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Sessão de banco isolada por teste.
    Usa begin_nested (savepoint) para rollback ao final.
    """
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=True,
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Cliente HTTP de teste com a aplicação FastAPI.
    Substitui a dependency get_db pela sessão de teste.
    """
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with patch("app.api.v1.dependencies.token_esta_revogado", return_value=False), \
         patch("app.core.redis.get_redis", return_value=AsyncMock()):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as ac:
            yield ac

    app.dependency_overrides.clear()


# ── Fixtures de dados ─────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def usuario_admin(db: AsyncSession) -> Usuario:
    """Cria um usuário admin no banco de teste."""
    usuario = Usuario(
        nome="Admin Teste",
        email="admin@teste.com",
        senha_hash=hash_senha("senha_admin_123"),
        perfil=PerfilUsuario.admin,
    )
    db.add(usuario)
    await db.flush()
    return usuario


@pytest_asyncio.fixture
async def usuario_caixa(db: AsyncSession) -> Usuario:
    """Cria um usuário caixa no banco de teste."""
    usuario = Usuario(
        nome="Caixa Teste",
        email="caixa@teste.com",
        senha_hash=hash_senha("senha_caixa_123"),
        perfil=PerfilUsuario.caixa,
    )
    db.add(usuario)
    await db.flush()
    return usuario


@pytest_asyncio.fixture
async def produto_kg(db: AsyncSession) -> Produto:
    """Cria um produto KG com estoque inicial."""
    produto = Produto(
        descricao="ALHO",
        codigo_barras="7891234567890",
        unidade="KG",
        preco_venda=Decimal("29.99"),
        tributado=True,
        perc_icms=Decimal("18.00"),
    )
    db.add(produto)
    await db.flush()
    estoque = Estoque(produto_id=produto.id, quantidade=Decimal("100.000"), estoque_minimo=Decimal("10.000"))
    db.add(estoque)
    await db.flush()
    return produto


@pytest_asyncio.fixture
async def produto_un(db: AsyncSession) -> Produto:
    """Cria um produto UN com estoque inicial."""
    produto = Produto(
        descricao="ABACAXI",
        codigo_barras="7891234567891",
        unidade="UN",
        preco_venda=Decimal("4.99"),
        tributado=True,
        perc_icms=Decimal("18.00"),
    )
    db.add(produto)
    await db.flush()
    estoque = Estoque(produto_id=produto.id, quantidade=Decimal("50.000"), estoque_minimo=Decimal("5.000"))
    db.add(estoque)
    await db.flush()
    return produto


def token_para(usuario: Usuario) -> str:
    """Gera um access token JWT para o usuário fornecido."""
    return criar_access_token(
        usuario_id=usuario.id,
        nome=usuario.nome,
        perfil=usuario.perfil.value,
    )


def headers_para(usuario: Usuario) -> dict:
    """Retorna headers HTTP com Authorization Bearer para o usuário."""
    return {"Authorization": f"Bearer {token_para(usuario)}"}
