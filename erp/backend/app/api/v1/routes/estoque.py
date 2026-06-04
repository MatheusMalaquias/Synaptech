"""
Endpoints de Estoque:
  GET  /estoque                    — lista saldos de todos os produtos
  GET  /estoque/{produto_id}       — saldo de um produto específico
  POST /estoque/movimentacao       — registrar entrada/saída/ajuste
  GET  /estoque/movimentacoes      — histórico de movimentações
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import CurrentUser, RequireGerente
from app.core.database import get_db
from app.repositories.auditoria_repo import AuditoriaRepository
from app.repositories.estoque_repo import EstoqueRepository
from app.repositories.produto_repo import ProdutoRepository
from app.schemas.estoque import (
    EstoqueOut,
    MovimentacaoCreate,
    MovimentacaoListResponse,
    MovimentacaoOut,
)

router = APIRouter()


def _estoque_to_out(estoque) -> EstoqueOut:
    return EstoqueOut(
        produto_id=estoque.produto_id,
        descricao=estoque.descricao,
        unidade=estoque.unidade,
        quantidade=estoque.quantidade,
        estoque_minimo=estoque.estoque_minimo,
        abaixo_minimo=estoque.quantidade <= estoque.estoque_minimo,
    )


@router.get(
    "",
    response_model=list[EstoqueOut],
    summary="Listar saldos de estoque",
)
async def listar_estoque(
    produto_id: Optional[int] = Query(None),
    abaixo_minimo: Optional[bool] = Query(None, description="Filtrar apenas produtos abaixo do mínimo"),
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Lista os saldos atuais de estoque de todos os produtos.
    Aceita filtro por produto_id ou por produtos abaixo do estoque mínimo.
    """
    repo = EstoqueRepository(db)
    estoques = await repo.listar(produto_id=produto_id, abaixo_minimo=abaixo_minimo)
    return [_estoque_to_out(e) for e in estoques]


@router.get(
    "/movimentacoes",
    response_model=MovimentacaoListResponse,
    summary="Histórico de movimentações",
)
async def listar_movimentacoes(
    produto_id: Optional[int] = Query(None),
    data_inicio: Optional[datetime] = Query(None),
    data_fim: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Retorna o histórico de movimentações de estoque com filtros opcionais
    por produto e período.
    """
    repo = EstoqueRepository(db)
    movs, total = await repo.listar_movimentacoes(
        produto_id=produto_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        page=page,
        limit=limit,
    )
    return MovimentacaoListResponse(
        items=[MovimentacaoOut.model_validate(m) for m in movs],
        total=total,
        page=page,
        limit=limit,
    )


@router.get(
    "/{produto_id}",
    response_model=EstoqueOut,
    summary="Saldo de estoque por produto",
)
async def saldo_produto(
    produto_id: int,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Retorna o saldo atual de estoque de um produto específico."""
    repo = EstoqueRepository(db)
    estoque = await repo.buscar_por_produto(produto_id)
    if not estoque:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado no estoque")
    return _estoque_to_out(estoque)


@router.post(
    "/movimentacao",
    response_model=MovimentacaoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar movimentação de estoque",
    dependencies=[RequireGerente],
)
async def registrar_movimentacao(
    body: MovimentacaoCreate,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Registra uma movimentação de estoque (entrada, saída ou ajuste).
    O saldo pode ficar negativo (regra de negócio permitida).
    Requer perfil gerente ou admin.
    Registra em auditoria_log.
    """
    produto_repo = ProdutoRepository(db)
    produto = await produto_repo.buscar_por_id(body.produto_id)
    if not produto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")

    estoque_repo = EstoqueRepository(db)
    audit = AuditoriaRepository(db)

    try:
        mov = await estoque_repo.registrar_movimentacao(
            produto_id=body.produto_id,
            tipo=body.tipo.value,
            quantidade=body.quantidade,
            usuario_id=current_user.id,
            motivo=body.motivo,
            referencia_id=body.referencia_id,
            referencia_tipo=body.referencia_tipo,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    await audit.registrar(
        acao="estoque_movimentacao",
        usuario_id=current_user.id,
        tabela="movimentacoes_estoque",
        registro_id=str(mov.id),
        dados_depois={
            "produto_id": body.produto_id,
            "tipo": body.tipo.value,
            "quantidade": str(body.quantidade),
            "saldo_anterior": str(mov.saldo_anterior),
            "saldo_posterior": str(mov.saldo_posterior),
        },
    )

    return MovimentacaoOut.model_validate(mov)
