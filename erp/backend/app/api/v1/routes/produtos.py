"""
CRUD completo de Produtos:
  GET    /produtos            — lista com filtros e paginação
  GET    /produtos/{id}       — detalhe por ID
  GET    /produtos/barcode/{codigo} — busca por código de barras
  POST   /produtos            — criar (gerente/admin)
  PUT    /produtos/{id}       — atualizar (gerente/admin)
  DELETE /produtos/{id}       — soft delete (gerente/admin)
"""
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import CurrentUser, RequireGerente
from app.core.database import get_db
from app.models.produto import Produto
from app.repositories.auditoria_repo import AuditoriaRepository
from app.repositories.produto_repo import ProdutoComEstoque, ProdutoRepository
from app.schemas.produto import (
    ProdutoCreate,
    ProdutoListResponse,
    ProdutoOut,
    ProdutoUpdate,
)

router = APIRouter()


def _dto_to_out(dto: ProdutoComEstoque) -> ProdutoOut:
    return ProdutoOut(
        id=dto.id,
        codigo_barras=dto.codigo_barras,
        descricao=dto.descricao,
        descricao_adicional=dto.descricao_adicional,
        unidade=dto.unidade,
        preco_venda=dto.preco_venda,
        tributado=dto.tributado,
        perc_icms=dto.perc_icms,
        perc_reducao_bc=dto.perc_reducao_bc,
        categoria_id=dto.categoria_id,
        ativo=dto.ativo,
        estoque=dto.estoque,
    )


@router.get(
    "",
    response_model=ProdutoListResponse,
    summary="Listar produtos",
)
async def listar_produtos(
    busca: Optional[str] = Query(None, description="Busca parcial por nome"),
    unidade: Optional[str] = Query(None, description="Filtrar por unidade: KG, UN, etc."),
    ativo: Optional[bool] = Query(True),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Lista produtos com busca textual parcial e paginação.
    Retorna o saldo de estoque atual de cada produto via JOIN.
    """
    repo = ProdutoRepository(db)
    produtos, total = await repo.listar(busca=busca, unidade=unidade, ativo=ativo, page=page, limit=limit)
    return ProdutoListResponse(
        items=[_dto_to_out(p) for p in produtos],
        total=total,
        page=page,
        limit=limit,
    )


@router.get(
    "/barcode/{codigo}",
    response_model=ProdutoOut,
    summary="Buscar produto por código de barras",
)
async def buscar_por_barcode(
    codigo: str,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Retorna um produto pelo código de barras. Usado no PDV ao escanear item."""
    repo = ProdutoRepository(db)
    produto = await repo.buscar_por_barcode(codigo)
    if not produto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    return _dto_to_out(produto)


@router.get(
    "/{produto_id}",
    response_model=ProdutoOut,
    summary="Detalhar produto",
)
async def detalhar_produto(
    produto_id: int,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Retorna os dados completos de um produto pelo ID interno."""
    repo = ProdutoRepository(db)
    produto = await repo.buscar_por_id(produto_id)
    if not produto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    return _dto_to_out(produto)


@router.post(
    "",
    response_model=ProdutoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Criar produto",
    dependencies=[RequireGerente],
)
async def criar_produto(
    body: ProdutoCreate,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Cria um novo produto com estoque inicial.
    Requer perfil gerente ou admin.
    Registra criação em auditoria_log.
    """
    repo = ProdutoRepository(db)
    audit = AuditoriaRepository(db)

    produto = Produto(
        codigo_barras=body.codigo_barras,
        descricao=body.descricao.upper(),
        descricao_adicional=body.descricao_adicional,
        unidade=body.unidade,
        preco_venda=body.preco_venda,
        tributado=body.tributado,
        perc_icms=body.perc_icms,
        perc_reducao_bc=body.perc_reducao_bc,
        categoria_id=body.categoria_id,
    )
    dto = await repo.criar(produto, estoque_inicial=body.estoque_inicial)

    await audit.registrar(
        acao="create",
        usuario_id=current_user.id if current_user else None,
        tabela="produtos",
        registro_id=str(dto.id),
        dados_depois={"descricao": dto.descricao, "preco_venda": str(dto.preco_venda)},
    )

    return _dto_to_out(dto)


@router.put(
    "/{produto_id}",
    response_model=ProdutoOut,
    summary="Atualizar produto",
    dependencies=[RequireGerente],
)
async def atualizar_produto(
    produto_id: int,
    body: ProdutoUpdate,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Atualiza dados de um produto. Requer perfil gerente ou admin.
    Registra alteração em auditoria_log com dados antes e depois.
    """
    repo = ProdutoRepository(db)
    audit = AuditoriaRepository(db)

    atual = await repo.buscar_por_id(produto_id)
    if not atual:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")

    dados_antes = {"descricao": atual.descricao, "preco_venda": str(atual.preco_venda)}
    dados = body.model_dump(exclude_none=True, exclude_unset=True)

    if "descricao" in dados:
        dados["descricao"] = dados["descricao"].upper()

    atualizado = await repo.atualizar(produto_id, dados)

    await audit.registrar(
        acao="update",
        usuario_id=current_user.id if current_user else None,
        tabela="produtos",
        registro_id=str(produto_id),
        dados_antes=dados_antes,
        dados_depois={"descricao": atualizado.descricao, "preco_venda": str(atualizado.preco_venda)},
    )

    return _dto_to_out(atualizado)


@router.delete(
    "/{produto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desativar produto (soft delete)",
    dependencies=[RequireGerente],
)
async def deletar_produto(
    produto_id: int,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Soft delete: marca o produto como inativo (ativo=false).
    Nunca deleta fisicamente. Requer perfil gerente ou admin.
    """
    repo = ProdutoRepository(db)
    audit = AuditoriaRepository(db)

    atual = await repo.buscar_por_id(produto_id)
    if not atual:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")

    await repo.atualizar(produto_id, {"ativo": False})

    await audit.registrar(
        acao="delete",
        usuario_id=current_user.id if current_user else None,
        tabela="produtos",
        registro_id=str(produto_id),
        dados_antes={"descricao": atual.descricao, "ativo": True},
        dados_depois={"ativo": False},
    )
