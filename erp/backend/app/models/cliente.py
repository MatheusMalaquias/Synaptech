"""Modelo de Cliente."""
import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(150), nullable=False)
    cpf_cnpj = Column(String(20), unique=True, nullable=True, index=True)
    telefone = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True)
    endereco = Column(JSON, nullable=True)  # {logradouro, numero, bairro, cidade, uf, cep}
    credito_troca = Column(Numeric(10, 2), nullable=False, default=0.00)
    saldo_caderneta = Column(Numeric(10, 2), nullable=False, default=0.00)  # positivo = deve
    ativo = Column(Boolean, nullable=False, default=True)
    criado_em = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    vendas = relationship("Venda", back_populates="cliente")
