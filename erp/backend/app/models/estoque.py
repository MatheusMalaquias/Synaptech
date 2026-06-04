"""Modelos de Estoque e Movimentações."""
import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TipoMovimentacao


class Estoque(Base):
    __tablename__ = "estoque"

    id = Column(Integer, primary_key=True, autoincrement=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, unique=True)
    # NUMERIC(12,3) — quantidade KG com 3 casas decimais; pode ser negativo
    quantidade = Column(Numeric(12, 3), nullable=False, default=0)
    estoque_minimo = Column(Numeric(12, 3), nullable=False, default=0)
    atualizado_em = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    produto = relationship("Produto", back_populates="estoque")


class MovimentacaoEstoque(Base):
    __tablename__ = "movimentacoes_estoque"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, index=True)
    tipo = Column(Enum(TipoMovimentacao, name="tipo_movimentacao"), nullable=False)
    # quantidade sempre positiva; o tipo define o sinal
    quantidade = Column(Numeric(12, 3), nullable=False)
    saldo_anterior = Column(Numeric(12, 3), nullable=False)
    saldo_posterior = Column(Numeric(12, 3), nullable=False)
    motivo = Column(String(200), nullable=True)
    referencia_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    referencia_tipo = Column(String(50), nullable=True)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    criado_em = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    produto = relationship("Produto", back_populates="movimentacoes_estoque")
    usuario = relationship("Usuario", back_populates="movimentacoes_estoque")
