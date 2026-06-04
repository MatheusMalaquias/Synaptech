"""Modelos de Webhook e fila de entregas."""
import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import WebhookStatus


class Webhook(Base):
    __tablename__ = "webhooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    eventos = Column(JSON, nullable=False)  # ['venda_finalizada', ...] — ARRAY(String) no PG, JSON no SQLite
    ativo = Column(Boolean, nullable=False, default=True)
    secret = Column(String(200), nullable=True)  # HMAC secret
    criado_em = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    entregas = relationship("WebhookEntrega", back_populates="webhook")


class WebhookEntrega(Base):
    """Fila de entrega de webhooks com suporte a retry com backoff exponencial."""
    __tablename__ = "webhook_entregas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    webhook_id = Column(UUID(as_uuid=True), ForeignKey("webhooks.id"), nullable=False)
    evento = Column(String(100), nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(Enum(WebhookStatus, name="webhook_status"), nullable=False, default=WebhookStatus.pendente)
    tentativas = Column(Integer, nullable=False, default=0)
    proxima_tentativa = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    ultimo_erro = Column(Text, nullable=True)
    entregue_em = Column(DateTime(timezone=True), nullable=True)
    criado_em = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    webhook = relationship("Webhook", back_populates="entregas")
