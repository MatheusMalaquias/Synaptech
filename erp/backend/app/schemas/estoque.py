"""Schemas Pydantic v2 para Estoque e Movimentações."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.base import TipoMovimentacao


class EstoqueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    produto_id: int
    descricao: str
    unidade: str
    quantidade: Decimal
    estoque_minimo: Decimal
    abaixo_minimo: bool


class MovimentacaoCreate(BaseModel):
    produto_id: int
    tipo: TipoMovimentacao
    quantidade: Decimal = Field(..., gt=0, decimal_places=3)
    motivo: Optional[str] = Field(None, max_length=200)
    referencia_id: Optional[UUID] = None
    referencia_tipo: Optional[str] = Field(None, max_length=50)


class MovimentacaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    produto_id: int
    tipo: TipoMovimentacao
    quantidade: Decimal
    saldo_anterior: Decimal
    saldo_posterior: Decimal
    motivo: Optional[str]
    referencia_id: Optional[UUID]
    referencia_tipo: Optional[str]
    usuario_id: UUID
    criado_em: datetime


class MovimentacaoListResponse(BaseModel):
    items: list[MovimentacaoOut]
    total: int
    page: int
    limit: int
