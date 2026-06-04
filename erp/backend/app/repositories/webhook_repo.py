"""Repositório de acesso a dados para Webhooks."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.webhook import Webhook, WebhookEntrega


class WebhookRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def listar(self) -> list[Webhook]:
        result = await self.db.execute(select(Webhook).order_by(Webhook.criado_em.desc()))
        return result.scalars().all()

    async def buscar_por_id(self, webhook_id: UUID) -> Optional[Webhook]:
        return await self.db.get(Webhook, webhook_id)

    async def criar(self, webhook: Webhook) -> Webhook:
        self.db.add(webhook)
        await self.db.flush()
        await self.db.refresh(webhook)
        return webhook

    async def deletar(self, webhook: Webhook) -> None:
        webhook.ativo = False
        await self.db.flush()
