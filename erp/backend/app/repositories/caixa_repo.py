"""Repositório de acesso a dados para Caixa e Sessões."""
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import FormaPagamento, StatusSessaoCaixa
from app.models.caixa import Caixa, SessaoCaixa
from app.models.venda import PagamentoVenda, Venda


class CaixaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def listar_caixas(self) -> list[Caixa]:
        result = await self.db.execute(select(Caixa).where(Caixa.ativo == True))
        return result.scalars().all()

    async def buscar_caixa(self, caixa_id: UUID) -> Optional[Caixa]:
        return await self.db.get(Caixa, caixa_id)

    async def criar_caixa(self, caixa: Caixa) -> Caixa:
        self.db.add(caixa)
        await self.db.flush()
        return caixa

    async def sessao_aberta_do_usuario(self, usuario_id: UUID) -> Optional[SessaoCaixa]:
        """Retorna a sessão aberta do usuário, se existir."""
        result = await self.db.execute(
            select(SessaoCaixa).where(
                SessaoCaixa.usuario_id == usuario_id,
                SessaoCaixa.status == StatusSessaoCaixa.aberta,
            )
        )
        return result.scalar_one_or_none()

    async def sessao_aberta_qualquer(self) -> Optional[SessaoCaixa]:
        """Retorna qualquer sessão aberta (usado pela integração n8n)."""
        result = await self.db.execute(
            select(SessaoCaixa).where(SessaoCaixa.status == StatusSessaoCaixa.aberta).limit(1)
        )
        return result.scalar_one_or_none()

    async def buscar_sessao(self, sessao_id: UUID) -> Optional[SessaoCaixa]:
        return await self.db.get(SessaoCaixa, sessao_id)

    async def abrir_sessao(self, sessao: SessaoCaixa) -> SessaoCaixa:
        self.db.add(sessao)
        await self.db.flush()
        return sessao

    async def fechar_sessao(
        self,
        sessao: SessaoCaixa,
        valor_fechamento: Decimal,
        observacao: Optional[str] = None,
    ) -> SessaoCaixa:
        from datetime import datetime, timezone
        sessao.status = StatusSessaoCaixa.fechada
        sessao.valor_fechamento = valor_fechamento
        sessao.observacao = observacao
        sessao.fechamento_em = datetime.now(timezone.utc)
        await self.db.flush()
        return sessao

    async def total_vendas_sessao(self, sessao_id: UUID) -> Decimal:
        """Soma total_final de todas as vendas finalizadas da sessão."""
        from app.models.base import StatusVenda
        result = await self.db.execute(
            select(func.coalesce(func.sum(Venda.total_final), 0))
            .where(
                Venda.sessao_caixa_id == sessao_id,
                Venda.status == StatusVenda.finalizada,
            )
        )
        return result.scalar_one()

    async def totais_por_forma(self, sessao_id: UUID) -> dict:
        """Soma pagamentos por forma para o resumo de fechamento."""
        from app.models.base import StatusVenda, StatusPagamento
        result = await self.db.execute(
            select(PagamentoVenda.forma, func.sum(PagamentoVenda.valor))
            .join(Venda, PagamentoVenda.venda_id == Venda.id)
            .where(
                Venda.sessao_caixa_id == sessao_id,
                Venda.status == StatusVenda.finalizada,
                PagamentoVenda.status == StatusPagamento.confirmado,
            )
            .group_by(PagamentoVenda.forma)
        )
        return {str(row[0].value if hasattr(row[0], 'value') else row[0]): row[1] for row in result.all()}
