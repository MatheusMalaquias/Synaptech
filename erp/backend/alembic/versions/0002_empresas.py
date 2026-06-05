"""empresas table

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-05 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _x(sql: str) -> None:
    op.execute(sql.strip())


def upgrade() -> None:
    _x("""CREATE TABLE IF NOT EXISTS empresas (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        nome VARCHAR(150) NOT NULL,
        cnpj VARCHAR(20) UNIQUE,
        telefone VARCHAR(20),
        email VARCHAR(150),
        cidade VARCHAR(100),
        estado VARCHAR(2),
        plano VARCHAR(50) NOT NULL DEFAULT 'basico',
        ativo BOOLEAN NOT NULL DEFAULT true,
        api_key VARCHAR(100) UNIQUE,
        observacao TEXT,
        criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )""")
    _x("CREATE INDEX IF NOT EXISTS idx_empresas_ativo ON empresas(ativo)")
    _x("CREATE INDEX IF NOT EXISTS idx_empresas_api_key ON empresas(api_key) WHERE api_key IS NOT NULL")


def downgrade() -> None:
    _x("DROP TABLE IF EXISTS empresas CASCADE")
