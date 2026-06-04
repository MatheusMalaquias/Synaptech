"""Schemas Pydantic v2 para Webhooks."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models.base import WebhookStatus

EVENTOS_VALIDOS = [
    "venda_finalizada",
    "venda_cancelada",
    "item_cancelado",
    "estoque_alterado",
    "estoque_critico",
    "caixa_aberto",
    "caixa_fechado",
    "pagamento_pix_confirmado",
]


class WebhookCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    url: str = Field(..., max_length=500)
    eventos: List[str] = Field(..., min_length=1)
    secret: Optional[str] = Field(None, max_length=200)

    def model_post_init(self, __context):
        for ev in self.eventos:
            if ev not in EVENTOS_VALIDOS:
                raise ValueError(f"Evento inválido: {ev}. Válidos: {EVENTOS_VALIDOS}")


class WebhookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nome: str
    url: str
    eventos: List[str]
    ativo: bool
    criado_em: datetime


class WebhookEntregaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    webhook_id: UUID
    evento: str
    status: WebhookStatus
    tentativas: int
    proxima_tentativa: datetime
    ultimo_erro: Optional[str]
    entregue_em: Optional[datetime]
    criado_em: datetime
