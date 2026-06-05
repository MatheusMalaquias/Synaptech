"""Modelo ORM para Empresas (multi-tenant)."""
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.models.base import Base


class Empresa(Base):
    __tablename__ = "empresas"

    id: Mapped[uuid.UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(sa.String(150), nullable=False)
    cnpj: Mapped[str | None] = mapped_column(sa.String(20), unique=True)
    telefone: Mapped[str | None] = mapped_column(sa.String(20))
    email: Mapped[str | None] = mapped_column(sa.String(150))
    cidade: Mapped[str | None] = mapped_column(sa.String(100))
    estado: Mapped[str | None] = mapped_column(sa.String(2))
    plano: Mapped[str] = mapped_column(sa.String(50), default="basico")
    ativo: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    api_key: Mapped[str | None] = mapped_column(sa.String(100), unique=True)
    observacao: Mapped[str | None] = mapped_column(sa.Text)
    criado_em: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True), default=datetime.utcnow)
    atualizado_em: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
