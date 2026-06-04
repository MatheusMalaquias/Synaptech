"""Repositório de acesso a dados para Vendas, Itens e Pagamentos."""
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import StatusPagamento, StatusVenda
from app.models.venda import ItemVenda, PagamentoVenda, Venda


class VendaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def proximo_numero(self, serie: str = "01") -> int:
        """
        Gera o próximo número sequencial de venda usando PostgreSQL sequence.
        Evita race condition quando múltiplas vendas são criadas simultaneamente.
        """
        result = await self.db.execute(text("SELECT nextval('vendas_numero_seq')"))
        return result.scalar_one()

    async def criar(self, venda: Venda) -> Venda:
        self.db.add(venda)
        await self.db.flush()
        return venda

    async def buscar_por_id(self, venda_id: UUID) -> Optional[Venda]:
        result = await self.db.execute(
            select(Venda).where(Venda.id == venda_id)
        )
        return result.scalar_one_or_none()

    async def listar(
        self,
        sessao_caixa_id: Optional[UUID] = None,
        usuario_id: Optional[UUID] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[Venda], int]:
        query = select(Venda)
        if sessao_caixa_id:
            query = query.where(Venda.sessao_caixa_id == sessao_caixa_id)
        if usuario_id:
            query = query.where(Venda.usuario_id == usuario_id)
        if status:
            query = query.where(Venda.status == status)
        query = query.order_by(Venda.criado_em.desc())

        count_q = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_q)).scalar_one()
        result = await self.db.execute(query.offset((page - 1) * limit).limit(limit))
        return result.scalars().all(), total

    async def buscar_item(self, item_id: UUID) -> Optional[ItemVenda]:
        result = await self.db.execute(select(ItemVenda).where(ItemVenda.id == item_id))
        return result.scalar_one_or_none()

    async def listar_itens(self, venda_id: UUID) -> list[ItemVenda]:
        result = await self.db.execute(
            select(ItemVenda).where(ItemVenda.venda_id == venda_id).order_by(ItemVenda.sequencia)
        )
        return result.scalars().all()

    async def proximo_sequencia(self, venda_id: UUID) -> int:
        result = await self.db.execute(
            select(func.coalesce(func.max(ItemVenda.sequencia), 0) + 1)
            .where(ItemVenda.venda_id == venda_id)
        )
        return result.scalar_one()

    async def adicionar_item(self, item: ItemVenda) -> ItemVenda:
        self.db.add(item)
        await self.db.flush()
        return item

    async def remover_item(self, item: ItemVenda) -> None:
        await self.db.delete(item)
        await self.db.flush()

    async def adicionar_pagamento(self, pagamento: PagamentoVenda) -> PagamentoVenda:
        self.db.add(pagamento)
        await self.db.flush()
        return pagamento

    async def listar_pagamentos(self, venda_id: UUID) -> list[PagamentoVenda]:
        result = await self.db.execute(
            select(PagamentoVenda).where(PagamentoVenda.venda_id == venda_id)
        )
        return result.scalars().all()

    async def recalcular_total(self, venda: Venda) -> None:
        """Recalcula subtotal e total_final com base nos itens."""
        result = await self.db.execute(
            select(func.coalesce(func.sum(ItemVenda.subtotal), 0))
            .where(ItemVenda.venda_id == venda.id)
        )
        subtotal = result.scalar_one()
        venda.subtotal = subtotal
        venda.total_final = max(Decimal("0"), subtotal - venda.desconto_nota + venda.acrescimo_nota)
        await self.db.flush()
