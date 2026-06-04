"""Modelos de Categoria e Produto."""
from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey,
    Integer, Numeric, String, func,
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import UnidadeEnum


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False, unique=True)
    ativo = Column(Boolean, nullable=False, default=True)

    produtos = relationship("Produto", back_populates="categoria")


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo_barras = Column(String(50), unique=True, nullable=True, index=True)
    descricao = Column(String(100), nullable=False)
    descricao_adicional = Column(String(200), nullable=True)
    unidade = Column(Enum(UnidadeEnum, name="unidade_enum"), nullable=False, default=UnidadeEnum.UN)
    # NUMERIC(10,2) para preço — nunca float
    preco_venda = Column(Numeric(10, 2), nullable=False)
    tributado = Column(Boolean, nullable=False, default=True)
    perc_icms = Column(Numeric(5, 2), nullable=False, default=18.00)
    perc_reducao_bc = Column(Numeric(5, 2), nullable=False, default=0.00)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    ativo = Column(Boolean, nullable=False, default=True)
    criado_em = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    categoria = relationship("Categoria", back_populates="produtos")
    estoque = relationship("Estoque", back_populates="produto", uselist=False)
    itens_venda = relationship("ItemVenda", back_populates="produto")
    movimentacoes_estoque = relationship("MovimentacaoEstoque", back_populates="produto")
