"""Modelo de usuário do sistema."""
import uuid

from sqlalchemy import Boolean, Column, DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import PerfilUsuario


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True, index=True)
    senha_hash = Column(String(255), nullable=False)
    perfil = Column(Enum(PerfilUsuario, name="perfil_usuario"), nullable=False, default=PerfilUsuario.caixa)
    ativo = Column(Boolean, nullable=False, default=True)
    criado_em = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    vendas = relationship("Venda", foreign_keys="Venda.usuario_id", back_populates="usuario")
    sessoes_caixa = relationship("SessaoCaixa", back_populates="usuario")
    movimentacoes_estoque = relationship("MovimentacaoEstoque", back_populates="usuario")
