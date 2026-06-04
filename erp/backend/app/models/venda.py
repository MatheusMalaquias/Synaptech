"""Modelos de Venda, ItemVenda e PagamentoVenda."""
import uuid

from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Enum, ForeignKey,
    Integer, Numeric, String, Text, UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import (
    FormaPagamento, StatusNfce, StatusPagamento,
    StatusVenda, UnidadeEnum,
)


class Venda(Base):
    __tablename__ = "vendas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero = Column(BigInteger, nullable=False)
    serie = Column(String(5), nullable=False, default="01")
    sessao_caixa_id = Column(UUID(as_uuid=True), ForeignKey("sessoes_caixa.id"), nullable=False, index=True)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=True)
    vendedor_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    status = Column(Enum(StatusVenda, name="status_venda"), nullable=False, default=StatusVenda.aberta, index=True)
    subtotal = Column(Numeric(10, 2), nullable=False, default=0.00)
    desconto_nota = Column(Numeric(10, 2), nullable=False, default=0.00)
    acrescimo_nota = Column(Numeric(10, 2), nullable=False, default=0.00)
    total_final = Column(Numeric(10, 2), nullable=False, default=0.00)
    # NFC-e
    nfce_status = Column(Enum(StatusNfce, name="status_nfce"), nullable=False, default=StatusNfce.pendente)
    nfce_numero = Column(Integer, nullable=True)
    nfce_serie = Column(String(5), nullable=True)
    nfce_chave = Column(String(50), nullable=True)
    nfce_xml = Column(Text, nullable=True)
    nfce_qrcode = Column(Text, nullable=True)
    # Datas
    criado_em = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    finalizado_em = Column(DateTime(timezone=True), nullable=True)
    cancelado_em = Column(DateTime(timezone=True), nullable=True)
    motivo_cancelamento = Column(String(200), nullable=True)

    __table_args__ = (UniqueConstraint("numero", "serie", name="uq_vendas_numero_serie"),)

    sessao_caixa = relationship("SessaoCaixa", back_populates="vendas")
    usuario = relationship("Usuario", foreign_keys=[usuario_id], back_populates="vendas")
    cliente = relationship("Cliente", back_populates="vendas")
    itens = relationship("ItemVenda", back_populates="venda", cascade="all, delete-orphan")
    pagamentos = relationship("PagamentoVenda", back_populates="venda")


class ItemVenda(Base):
    __tablename__ = "itens_venda"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    venda_id = Column(UUID(as_uuid=True), ForeignKey("vendas.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    sequencia = Column(Integer, nullable=False)
    # NUMERIC(12,3) para quantidade KG
    quantidade = Column(Numeric(12, 3), nullable=False)
    preco_unitario = Column(Numeric(10, 2), nullable=False)
    desconto_item = Column(Numeric(10, 2), nullable=False, default=0.00)
    subtotal = Column(Numeric(10, 2), nullable=False)
    # Snapshot fiscal imutável após finalização
    unidade = Column(Enum(UnidadeEnum, name="unidade_enum"), nullable=False)
    tributado = Column(Boolean, nullable=False)
    perc_icms = Column(Numeric(5, 2), nullable=False)

    __table_args__ = (UniqueConstraint("venda_id", "sequencia", name="uq_itens_venda_seq"),)

    venda = relationship("Venda", back_populates="itens")
    produto = relationship("Produto", back_populates="itens_venda")


class PagamentoVenda(Base):
    __tablename__ = "pagamentos_venda"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    venda_id = Column(UUID(as_uuid=True), ForeignKey("vendas.id"), nullable=False, index=True)
    forma = Column(Enum(FormaPagamento, name="forma_pagamento"), nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(StatusPagamento, name="status_pagamento"), nullable=False, default=StatusPagamento.pendente)
    referencia_externa = Column(String(200), nullable=True)
    dados_extras = Column("dados_extras", Text, nullable=True)  # JSON serializado
    criado_em = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    confirmado_em = Column(DateTime(timezone=True), nullable=True)

    venda = relationship("Venda", back_populates="pagamentos")
