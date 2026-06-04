"""Modelo de configurações do sistema (chave-valor)."""
from sqlalchemy import Column, DateTime, String, func

from app.core.database import Base


class Configuracao(Base):
    __tablename__ = "configuracoes"

    chave = Column(String(100), primary_key=True)
    valor = Column(String, nullable=False)
    descricao = Column(String(200), nullable=True)
    atualizado_em = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
