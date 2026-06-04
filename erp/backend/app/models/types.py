"""
Tipos agnósticos de banco de dados.
Em produção (PostgreSQL) usa JSONB e INET.
Em testes (SQLite) usa JSON e String.
"""
import os

from sqlalchemy import JSON, String
from sqlalchemy.dialects.postgresql import INET as PG_INET, JSONB as PG_JSONB

# Detecta se está em ambiente de teste
_TESTING = "sqlite" in os.environ.get("DATABASE_URL", "sqlite")


def JSONB_COMPAT():
    """JSONB em PostgreSQL, JSON em SQLite (testes)."""
    return JSON if _TESTING else PG_JSONB


def INET_COMPAT():
    """INET em PostgreSQL, String(45) em SQLite (testes)."""
    return String(45) if _TESTING else PG_INET
