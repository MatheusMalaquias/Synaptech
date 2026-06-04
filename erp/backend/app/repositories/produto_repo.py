"""Repositório de acesso a dados para Produtos."""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, outerjoin, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.estoque import Estoque
from app.models.produto import Produto


@dataclass
class ProdutoComEstoque:
    """DTO de produto com saldo de estoque embutido (evita lazy loading)."""
    id: int
    codigo_barras: Optional[str]
    descricao: str
    descricao_adicional: Optional[str]
    unidade: str
    preco_venda: Decimal
    tributado: bool
    perc_icms: Decimal
    perc_reducao_bc: Decimal
    categoria_id: Optional[int]
    ativo: bool
    estoque: Optional[Decimal]


class ProdutoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _row_to_dto(self, row) -> ProdutoComEstoque:
        """Converte uma linha de resultado em DTO."""
        # row pode ter formato (Produto, quantidade) ou apenas Produto
        if hasattr(row, 'Produto'):
            p = row.Produto
            qty = row.quantidade
        else:
            p = row
            qty = None

        unidade = p.unidade.value if hasattr(p.unidade, 'value') else str(p.unidade)
        return ProdutoComEstoque(
            id=p.id,
            codigo_barras=p.codigo_barras,
            descricao=p.descricao,
            descricao_adicional=p.descricao_adicional,
            unidade=unidade,
            preco_venda=p.preco_venda,
            tributado=p.tributado,
            perc_icms=p.perc_icms,
            perc_reducao_bc=p.perc_reducao_bc,
            categoria_id=p.categoria_id,
            ativo=p.ativo,
            estoque=qty,
        )

    async def listar(
        self,
        busca: Optional[str] = None,
        unidade: Optional[str] = None,
        ativo: Optional[bool] = True,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[ProdutoComEstoque], int]:
        """Lista produtos com saldo de estoque via LEFT JOIN."""
        query = (
            select(Produto, Estoque.quantidade)
            .outerjoin(Estoque, Produto.id == Estoque.produto_id)
        )

        if ativo is not None:
            query = query.where(Produto.ativo == ativo)
        if unidade:
            query = query.where(Produto.unidade == unidade)
        if busca:
            query = query.where(Produto.descricao.ilike(f"%{busca.upper()}%"))
            query = query.order_by(Produto.descricao)
        else:
            query = query.order_by(Produto.descricao)

        # Contagem total
        count_q = select(func.count(Produto.id))
        if ativo is not None:
            count_q = count_q.where(Produto.ativo == ativo)
        if unidade:
            count_q = count_q.where(Produto.unidade == unidade)
        if busca:
            count_q = count_q.where(Produto.descricao.ilike(f"%{busca.upper()}%"))
        total = (await self.db.execute(count_q)).scalar_one()

        query = query.offset((page - 1) * limit).limit(limit)
        result = await self.db.execute(query)
        rows = result.all()
        return [self._row_to_dto(r) for r in rows], total

    async def buscar_por_id(self, produto_id: int) -> Optional[ProdutoComEstoque]:
        result = await self.db.execute(
            select(Produto, Estoque.quantidade)
            .outerjoin(Estoque, Produto.id == Estoque.produto_id)
            .where(Produto.id == produto_id)
        )
        row = result.one_or_none()
        return self._row_to_dto(row) if row else None

    async def buscar_por_id_orm(self, produto_id: int) -> Optional[Produto]:
        """Retorna o ORM Produto para atualização."""
        result = await self.db.execute(select(Produto).where(Produto.id == produto_id))
        return result.scalar_one_or_none()

    async def buscar_por_barcode(self, codigo: str) -> Optional[ProdutoComEstoque]:
        result = await self.db.execute(
            select(Produto, Estoque.quantidade)
            .outerjoin(Estoque, Produto.id == Estoque.produto_id)
            .where(Produto.codigo_barras == codigo)
        )
        row = result.one_or_none()
        return self._row_to_dto(row) if row else None

    async def criar(self, produto: Produto, estoque_inicial: Decimal = Decimal("0")) -> ProdutoComEstoque:
        self.db.add(produto)
        await self.db.flush()

        estoque = Estoque(produto_id=produto.id, quantidade=estoque_inicial)
        self.db.add(estoque)
        await self.db.flush()

        # Retorna DTO sem lazy loading
        unidade = produto.unidade.value if hasattr(produto.unidade, 'value') else str(produto.unidade)
        return ProdutoComEstoque(
            id=produto.id,
            codigo_barras=produto.codigo_barras,
            descricao=produto.descricao,
            descricao_adicional=produto.descricao_adicional,
            unidade=unidade,
            preco_venda=produto.preco_venda,
            tributado=produto.tributado,
            perc_icms=produto.perc_icms,
            perc_reducao_bc=produto.perc_reducao_bc,
            categoria_id=produto.categoria_id,
            ativo=produto.ativo,
            estoque=estoque_inicial,
        )

    async def atualizar(self, produto_id: int, dados: dict) -> Optional[ProdutoComEstoque]:
        produto = await self.buscar_por_id_orm(produto_id)
        if not produto:
            return None
        for campo, valor in dados.items():
            setattr(produto, campo, valor)
        await self.db.flush()
        return await self.buscar_por_id(produto_id)
