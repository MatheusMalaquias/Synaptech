"""Schemas Pydantic v2 para Caixa e Sessões de Caixa."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CaixaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str
    serie_nfce: str
    impressora: Optional[str]
    ativo: bool


class AbrirCaixaRequest(BaseModel):
    caixa_id: UUID
    valor_abertura: Decimal = Field(default=Decimal("0.00"), ge=0)


class FecharCaixaRequest(BaseModel):
    valor_fechamento: Decimal = Field(..., ge=0)
    observacao: Optional[str] = None


class SangriaSuprimentoRequest(BaseModel):
    valor: Decimal = Field(..., gt=0)
    motivo: str = Field(..., min_length=1, max_length=200)


class TotaisPorForma(BaseModel):
    dinheiro: Decimal = Decimal("0.00")
    pix: Decimal = Decimal("0.00")
    credito: Decimal = Decimal("0.00")
    debito: Decimal = Decimal("0.00")
    cheque: Decimal = Decimal("0.00")
    voucher: Decimal = Decimal("0.00")
    troca: Decimal = Decimal("0.00")
    caderneta: Decimal = Decimal("0.00")


class SessaoCaixaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    caixa_id: UUID
    usuario_id: UUID
    status: str
    valor_abertura: Decimal
    valor_fechamento: Optional[Decimal]
    observacao: Optional[str]
    abertura_em: datetime
    fechamento_em: Optional[datetime]
    total_vendas: Optional[Decimal] = None
    total_por_forma: Optional[TotaisPorForma] = None
