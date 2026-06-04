"""Schemas Pydantic v2 para Produtos e Categorias."""
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.base import UnidadeEnum


class ProdutoCreate(BaseModel):
    codigo_barras: Optional[str] = None
    descricao: str = Field(..., min_length=1, max_length=100)
    descricao_adicional: Optional[str] = Field(None, max_length=200)
    unidade: UnidadeEnum = UnidadeEnum.UN
    # Decimal para nunca usar float em dinheiro
    preco_venda: Decimal = Field(..., ge=0, decimal_places=2)
    tributado: bool = True
    perc_icms: Decimal = Field(default=Decimal("18.00"), ge=0, le=100)
    perc_reducao_bc: Decimal = Field(default=Decimal("0.00"), ge=0)
    categoria_id: Optional[int] = None
    estoque_inicial: Decimal = Field(default=Decimal("0"), ge=0)


class ProdutoUpdate(BaseModel):
    codigo_barras: Optional[str] = None
    descricao: Optional[str] = Field(None, min_length=1, max_length=100)
    descricao_adicional: Optional[str] = None
    unidade: Optional[UnidadeEnum] = None
    preco_venda: Optional[Decimal] = Field(None, ge=0)
    tributado: Optional[bool] = None
    perc_icms: Optional[Decimal] = Field(None, ge=0, le=100)
    perc_reducao_bc: Optional[Decimal] = Field(None, ge=0)
    categoria_id: Optional[int] = None
    ativo: Optional[bool] = None


class EstoqueInfo(BaseModel):
    quantidade: Decimal
    estoque_minimo: Decimal


class ProdutoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo_barras: Optional[str]
    descricao: str
    descricao_adicional: Optional[str]
    unidade: UnidadeEnum
    preco_venda: Decimal
    tributado: bool
    perc_icms: Decimal
    perc_reducao_bc: Decimal
    categoria_id: Optional[int]
    ativo: bool
    # Saldo de estoque embutido na resposta de listagem
    estoque: Optional[Decimal] = None


class ProdutoListResponse(BaseModel):
    items: list[ProdutoOut]
    total: int
    page: int
    limit: int
