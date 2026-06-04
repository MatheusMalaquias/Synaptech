"""Repositório de acesso a dados para Estoque e Movimentações."""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.estoque import Estoque, MovimentacaoEstoque
from app.models.produto import Produto


@dataclass
class EstoqueComProduto:
    """DTO com dados de estoque + info do produto (evita lazy loading)."""
    produto_id: int
    descricao: str
    unidade: str
    quantidade: Decimal
    estoque_minimo: Decimal


class EstoqueRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def buscar_por_produto(self, produto_id: int) -> Optional[EstoqueComProduto]:
        """Retorna saldo + info do produto via JOIN explícito (sem lazy loading)."""
        result = await self.db.execute(
            select(
                Estoque.produto_id,
                Produto.descricao,
                Produto.unidade,
                Estoque.quantidade,
                Estoque.estoque_minimo,
            )
            .join(Produto, Estoque.produto_id == Produto.id)
            .where(Estoque.produto_id == produto_id)
        )
        row = result.one_or_none()
        if not row:
            return None
        return EstoqueComProduto(
            produto_id=row.produto_id,
            descricao=row.descricao,
            unidade=str(row.unidade.value) if hasattr(row.unidade, 'value') else str(row.unidade),
            quantidade=row.quantidade,
            estoque_minimo=row.estoque_minimo,
        )

    async def listar(
        self,
        produto_id: Optional[int] = None,
        abaixo_minimo: Optional[bool] = None,
    ) -> list[EstoqueComProduto]:
        """Lista estoques com JOIN explícito para evitar lazy loading."""
        query = select(
            Estoque.produto_id,
            Produto.descricao,
            Produto.unidade,
            Estoque.quantidade,
            Estoque.estoque_minimo,
        ).join(Produto, Estoque.produto_id == Produto.id)

        if produto_id:
            query = query.where(Estoque.produto_id == produto_id)
        if abaixo_minimo:
            query = query.where(Estoque.quantidade <= Estoque.estoque_minimo)

        result = await self.db.execute(query)
        rows = result.all()
        return [
            EstoqueComProduto(
                produto_id=r.produto_id,
                descricao=r.descricao,
                unidade=str(r.unidade.value) if hasattr(r.unidade, 'value') else str(r.unidade),
                quantidade=r.quantidade,
                estoque_minimo=r.estoque_minimo,
            )
            for r in rows
        ]

    async def buscar_estoque_orm(self, produto_id: int) -> Optional[Estoque]:
        """Busca o ORM Estoque simples (sem join) para atualização de saldo."""
        result = await self.db.execute(
            select(Estoque).where(Estoque.produto_id == produto_id)
        )
        return result.scalar_one_or_none()

    async def registrar_movimentacao(
        self,
        produto_id: int,
        tipo: str,
        quantidade: Decimal,
        usuario_id: UUID,
        motivo: Optional[str] = None,
        referencia_id: Optional[UUID] = None,
        referencia_tipo: Optional[str] = None,
    ) -> MovimentacaoEstoque:
        """
        Atualiza o saldo em estoque e grava a movimentação.
        O saldo pode ficar negativo (regra de negócio permitida).
        """
        estoque = await self.buscar_estoque_orm(produto_id)
        if not estoque:
            raise ValueError(f"Registro de estoque não encontrado para produto_id={produto_id}")

        saldo_anterior = estoque.quantidade

        # Determina o sinal pela direção da movimentação
        tipos_entrada = {"entrada", "ajuste_positivo", "cancelamento"}
        if tipo in tipos_entrada:
            novo_saldo = saldo_anterior + quantidade
        else:  # saida, ajuste_negativo
            novo_saldo = saldo_anterior - quantidade

        estoque.quantidade = novo_saldo

        mov = MovimentacaoEstoque(
            produto_id=produto_id,
            tipo=tipo,
            quantidade=quantidade,
            saldo_anterior=saldo_anterior,
            saldo_posterior=novo_saldo,
            motivo=motivo,
            referencia_id=referencia_id,
            referencia_tipo=referencia_tipo,
            usuario_id=usuario_id,
        )
        self.db.add(mov)
        await self.db.flush()
        return mov

    async def listar_movimentacoes(
        self,
        produto_id: Optional[int] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[MovimentacaoEstoque], int]:
        query = select(MovimentacaoEstoque)

        if produto_id:
            query = query.where(MovimentacaoEstoque.produto_id == produto_id)
        if data_inicio:
            query = query.where(MovimentacaoEstoque.criado_em >= data_inicio)
        if data_fim:
            query = query.where(MovimentacaoEstoque.criado_em <= data_fim)

        query = query.order_by(MovimentacaoEstoque.criado_em.desc())

        count_q = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_q)).scalar_one()

        query = query.offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all(), total
