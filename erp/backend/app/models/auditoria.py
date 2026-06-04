"""Modelo de log de auditoria — registra todo INSERT/UPDATE/DELETE em tabelas críticas."""
import uuid

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class AuditoriaLog(Base):
    __tablename__ = "auditoria_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True, index=True)
    acao = Column(String(100), nullable=False)       # 'create', 'update', 'delete', 'login'
    tabela = Column(String(50), nullable=True, index=True)
    registro_id = Column(String(100), nullable=True)
    dados_antes = Column(JSON, nullable=True)
    dados_depois = Column(JSON, nullable=True)
    ip = Column(String(45), nullable=True)           # INET no PostgreSQL, String nos testes
    user_agent = Column(String(500), nullable=True)
    criado_em = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    usuario = relationship("Usuario")
