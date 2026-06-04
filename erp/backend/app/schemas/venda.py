"""Schemas Pydantic v2 para Vendas, Itens e Pagamentos."""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.base import FormaPagamento, StatusNfce, StatusVenda


class PagamentoInput(BaseModel):
    forma: FormaPagamento
    valor: Decimal = Field(..., gt=0)


class DescontoInput(BaseModel):
    tipo: str = Field(..., pattern="^(nota|item)$")
    valor: Optional[Decimal] = Field(None, ge=0)
    percentual: Optional[float] = Field(None, ge=0, le=100)


class AdicionarItemRequest(BaseModel):
    produto_id: int
    quantidade: Decimal = Field(..., gt=0)
    preco_unitario: Optional[Decimal] = Field(None, ge=0)  # se None, usa o preço do cadastro


class AtualizarItemRequest(BaseModel):
    quantidade: Optional[Decimal] = Field(None, gt=0)
    preco_unitario: Optional[Decimal] = Field(None, ge=0)


class FinalizarVendaRequest(BaseModel):
    pagamentos: List[PagamentoInput] = Field(..., min_length=1)


class CancelarVendaRequest(BaseModel):
    motivo: str = Field(..., min_length=1, max_length=200)


class ItemVendaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    sequencia: int
    produto_id: int
    descricao: Optional[str] = None
    unidade: str
    quantidade: Decimal
    preco_unitario: Decimal
    desconto_item: Decimal
    subtotal: Decimal
    tributado: bool
    perc_icms: Decimal


class PagamentoVendaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    forma: str
    valor: Decimal
    status: str
    referencia_externa: Optional[str]
    criado_em: datetime


class VendaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    numero: int
    serie: str
    sessao_caixa_id: UUID
    usuario_id: UUID
    cliente_id: Optional[UUID]
    status: StatusVenda
    subtotal: Decimal
    desconto_nota: Decimal
    acrescimo_nota: Decimal
    total_final: Decimal
    nfce_status: StatusNfce
    nfce_chave: Optional[str]
    nfce_qrcode: Optional[str]
    criado_em: datetime
    finalizado_em: Optional[datetime]
    itens: List[ItemVendaOut] = []
    pagamentos: List[PagamentoVendaOut] = []
    troco: Optional[Decimal] = None


class VendaListResponse(BaseModel):
    items: List[VendaOut]
    total: int
    page: int
    limit: int
