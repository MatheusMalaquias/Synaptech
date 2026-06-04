"""Modelos de Caixa (equipamento) e Sessão de Caixa (turno)."""
import uuid

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import StatusSessaoCaixa


class Caixa(Base):
    __tablename__ = "caixas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(50), nullable=False)
    serie_nfce = Column(String(5), nullable=False, default="01")
    impressora = Column(String(100), nullable=True)
    ativo = Column(Boolean, nullable=False, default=True)

    sessoes = relationship("SessaoCaixa", back_populates="caixa")


class SessaoCaixa(Base):
    __tablename__ = "sessoes_caixa"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    caixa_id = Column(UUID(as_uuid=True), ForeignKey("caixas.id"), nullable=False)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    status = Column(Enum(StatusSessaoCaixa, name="status_sessao_caixa"), nullable=False, default=StatusSessaoCaixa.aberta)
    valor_abertura = Column(Numeric(10, 2), nullable=False, default=0.00)
    valor_fechamento = Column(Numeric(10, 2), nullable=True)
    observacao = Column(Text, nullable=True)
    abertura_em = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    fechamento_em = Column(DateTime(timezone=True), nullable=True)

    caixa = relationship("Caixa", back_populates="sessoes")
    usuario = relationship("Usuario", back_populates="sessoes_caixa")
    vendas = relationship("Venda", back_populates="sessao_caixa")
