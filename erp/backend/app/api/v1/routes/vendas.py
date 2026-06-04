"""
Endpoints de Vendas (PDV):
  POST   /vendas                   — inicia nova venda
  GET    /vendas                   — lista vendas
  GET    /vendas/{id}              — detalhe
  POST   /vendas/{id}/item         — adiciona item
  PUT    /vendas/{id}/item/{item_id}
  DELETE /vendas/{id}/item/{item_id}
  POST   /vendas/{id}/desconto     — aplica desconto
  POST   /vendas/{id}/finalizar    — finaliza com pagamentos
  POST   /vendas/{id}/cancelar     — cancela venda
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import CurrentUser
from app.core.database import get_db
from app.integrations.n8n.webhook_worker import enfileirar_evento
from app.models.base import StatusPagamento, StatusVenda
from app.models.venda import ItemVenda, PagamentoVenda, Venda
from app.repositories.auditoria_repo import AuditoriaRepository
from app.repositories.caixa_repo import CaixaRepository
from app.repositories.estoque_repo import EstoqueRepository
from app.repositories.produto_repo import ProdutoRepository
from app.repositories.venda_repo import VendaRepository
from app.schemas.venda import (
    AdicionarItemRequest,
    AtualizarItemRequest,
    CancelarVendaRequest,
    DescontoInput,
    FinalizarVendaRequest,
    ItemVendaOut,
    PagamentoVendaOut,
    VendaListResponse,
    VendaOut,
)

router = APIRouter()


async def _venda_to_out(venda: Venda, db: AsyncSession) -> VendaOut:
    """Monta o DTO de venda com itens e pagamentos (queries explícitas)."""
    from sqlalchemy import select
    from app.models.produto import Produto

    # Busca itens com nome do produto via JOIN
    from sqlalchemy import select as sa_select
    result = await db.execute(
        sa_select(ItemVenda, Produto.descricao)
        .outerjoin(Produto, ItemVenda.produto_id == Produto.id)
        .where(ItemVenda.venda_id == venda.id)
        .order_by(ItemVenda.sequencia)
    )
    rows = result.all()

    itens = []
    for row in rows:
        item = row[0]
        descricao = row[1]
        unidade = item.unidade.value if hasattr(item.unidade, 'value') else str(item.unidade)
        itens.append(ItemVendaOut(
            id=item.id,
            sequencia=item.sequencia,
            produto_id=item.produto_id,
            descricao=descricao,
            unidade=unidade,
            quantidade=item.quantidade,
            preco_unitario=item.preco_unitario,
            desconto_item=item.desconto_item,
            subtotal=item.subtotal,
            tributado=item.tributado,
            perc_icms=item.perc_icms,
        ))

    # Busca pagamentos
    from sqlalchemy import select as sa_select2
    pag_result = await db.execute(
        sa_select2(PagamentoVenda).where(PagamentoVenda.venda_id == venda.id)
    )
    pagamentos_orm = pag_result.scalars().all()
    pagamentos = []
    for p in pagamentos_orm:
        forma = p.forma.value if hasattr(p.forma, 'value') else str(p.forma)
        pstatus = p.status.value if hasattr(p.status, 'value') else str(p.status)
        pagamentos.append(PagamentoVendaOut(
            id=p.id,
            forma=forma,
            valor=p.valor,
            status=pstatus,
            referencia_externa=p.referencia_externa,
            criado_em=p.criado_em,
        ))

    # Calcula troco (apenas para dinheiro)
    total_pago = sum(p.valor for p in pagamentos_orm)
    troco = max(Decimal("0"), total_pago - venda.total_final) if pagamentos_orm else None

    return VendaOut(
        id=venda.id,
        numero=venda.numero,
        serie=venda.serie,
        sessao_caixa_id=venda.sessao_caixa_id,
        usuario_id=venda.usuario_id,
        cliente_id=venda.cliente_id,
        status=venda.status,
        subtotal=venda.subtotal,
        desconto_nota=venda.desconto_nota,
        acrescimo_nota=venda.acrescimo_nota,
        total_final=venda.total_final,
        nfce_status=venda.nfce_status,
        nfce_chave=venda.nfce_chave,
        nfce_qrcode=venda.nfce_qrcode,
        criado_em=venda.criado_em,
        finalizado_em=venda.finalizado_em,
        itens=itens,
        pagamentos=pagamentos,
        troco=troco,
    )


@router.post(
    "",
    response_model=VendaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Iniciar nova venda",
)
async def criar_venda(
    cliente_id: Optional[UUID] = None,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Cria uma nova venda com status 'aberta'.
    Requer sessão de caixa ativa para o operador.
    """
    caixa_repo = CaixaRepository(db)
    sessao = await caixa_repo.sessao_aberta_do_usuario(current_user.id)
    if not sessao:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhuma sessão de caixa aberta. Abra o caixa antes de iniciar venda.",
        )

    venda_repo = VendaRepository(db)
    numero = await venda_repo.proximo_numero()

    venda = Venda(
        numero=numero,
        serie=sessao.caixa_id and "01" or "01",
        sessao_caixa_id=sessao.id,
        usuario_id=current_user.id,
        cliente_id=cliente_id,
    )
    venda = await venda_repo.criar(venda)
    return await _venda_to_out(venda, db)


@router.get(
    "",
    response_model=VendaListResponse,
    summary="Listar vendas",
)
async def listar_vendas(
    status_venda: Optional[str] = Query(None, alias="status"),
    sessao_caixa_id: Optional[UUID] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Lista vendas com filtros opcionais por status e sessão de caixa."""
    repo = VendaRepository(db)
    vendas, total = await repo.listar(
        sessao_caixa_id=sessao_caixa_id,
        status=status_venda,
        page=page,
        limit=limit,
    )
    items = [await _venda_to_out(v, db) for v in vendas]
    return VendaListResponse(items=items, total=total, page=page, limit=limit)


@router.get(
    "/{venda_id}",
    response_model=VendaOut,
    summary="Detalhar venda",
)
async def detalhar_venda(
    venda_id: UUID,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Retorna todos os dados de uma venda, incluindo itens e pagamentos."""
    repo = VendaRepository(db)
    venda = await repo.buscar_por_id(venda_id)
    if not venda:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venda não encontrada")
    return await _venda_to_out(venda, db)


@router.post(
    "/{venda_id}/item",
    response_model=ItemVendaOut,
    status_code=status.HTTP_200_OK,
    summary="Adicionar item à venda",
)
async def adicionar_item(
    venda_id: UUID,
    body: AdicionarItemRequest,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Adiciona um produto à venda em andamento.
    O subtotal é calculado como ROUND(quantidade × preco_unitario, 2).
    """
    venda_repo = VendaRepository(db)
    venda = await venda_repo.buscar_por_id(venda_id)
    if not venda or venda.status != StatusVenda.aberta:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Venda não encontrada ou não está aberta")

    produto_repo = ProdutoRepository(db)
    produto = await produto_repo.buscar_por_id(body.produto_id)
    if not produto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")

    preco = body.preco_unitario if body.preco_unitario is not None else produto.preco_venda
    # Regra de cálculo: ROUND(quantidade × preco, 2)
    subtotal = round(body.quantidade * preco, 2)

    sequencia = await venda_repo.proximo_sequencia(venda_id)
    item = ItemVenda(
        venda_id=venda_id,
        produto_id=body.produto_id,
        sequencia=sequencia,
        quantidade=body.quantidade,
        preco_unitario=preco,
        subtotal=subtotal,
        unidade=produto.unidade,
        tributado=produto.tributado,
        perc_icms=produto.perc_icms,
    )
    item = await venda_repo.adicionar_item(item)
    await venda_repo.recalcular_total(venda)

    unidade = produto.unidade if isinstance(produto.unidade, str) else produto.unidade
    return ItemVendaOut(
        id=item.id,
        sequencia=item.sequencia,
        produto_id=item.produto_id,
        descricao=produto.descricao,
        unidade=unidade,
        quantidade=item.quantidade,
        preco_unitario=item.preco_unitario,
        desconto_item=item.desconto_item,
        subtotal=item.subtotal,
        tributado=item.tributado,
        perc_icms=item.perc_icms,
    )


@router.delete(
    "/{venda_id}/item/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover item da venda",
)
async def remover_item(
    venda_id: UUID,
    item_id: UUID,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Remove um item da venda em andamento e reverte a baixa de estoque.
    Só funciona com venda no status 'aberta'.
    """
    venda_repo = VendaRepository(db)
    venda = await venda_repo.buscar_por_id(venda_id)
    if not venda or venda.status != StatusVenda.aberta:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Venda não está aberta")

    item = await venda_repo.buscar_item(item_id)
    if not item or item.venda_id != venda_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item não encontrado")

    await venda_repo.remover_item(item)
    await venda_repo.recalcular_total(venda)

    await enfileirar_evento(db, "item_cancelado", {
        "evento": "item_cancelado",
        "venda_id": str(venda_id),
        "item_id": str(item_id),
        "produto_id": item.produto_id,
        "quantidade": str(item.quantidade),
    })


@router.post(
    "/{venda_id}/desconto",
    response_model=VendaOut,
    summary="Aplicar desconto na venda",
)
async def aplicar_desconto(
    venda_id: UUID,
    body: DescontoInput,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Aplica desconto fixo ou percentual no total da venda."""
    repo = VendaRepository(db)
    venda = await repo.buscar_por_id(venda_id)
    if not venda or venda.status != StatusVenda.aberta:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Venda não está aberta")

    if body.valor is not None:
        venda.desconto_nota = body.valor
    elif body.percentual is not None:
        venda.desconto_nota = round(venda.subtotal * Decimal(str(body.percentual)) / 100, 2)

    await repo.recalcular_total(venda)
    return await _venda_to_out(venda, db)


@router.post(
    "/{venda_id}/finalizar",
    response_model=VendaOut,
    summary="Finalizar venda com pagamentos",
)
async def finalizar_venda(
    venda_id: UUID,
    body: FinalizarVendaRequest,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Finaliza a venda, registra pagamentos, dá baixa no estoque e dispara webhook.
    A venda muda para status 'finalizada'. NFC-e fica pendente (Fase 5).
    """
    venda_repo = VendaRepository(db)
    venda = await venda_repo.buscar_por_id(venda_id)

    if not venda or venda.status != StatusVenda.aberta:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Venda não está aberta")

    itens = await venda_repo.listar_itens(venda_id)
    if not itens:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A venda não tem itens")

    # Registra pagamentos
    for pag in body.pagamentos:
        pagamento = PagamentoVenda(
            venda_id=venda_id,
            forma=pag.forma,
            valor=pag.valor,
            status=StatusPagamento.confirmado,
            confirmado_em=datetime.now(timezone.utc),
        )
        await venda_repo.adicionar_pagamento(pagamento)

    # Dá baixa no estoque
    estoque_repo = EstoqueRepository(db)
    audit = AuditoriaRepository(db)
    for item in itens:
        try:
            await estoque_repo.registrar_movimentacao(
                produto_id=item.produto_id,
                tipo="saida",
                quantidade=item.quantidade,
                usuario_id=current_user.id,
                motivo=f"Venda #{venda.numero}",
                referencia_id=venda.id,
                referencia_tipo="venda",
            )
        except ValueError:
            pass  # Estoque pode ser negativo (regra de negócio)

    # Finaliza a venda
    venda.status = StatusVenda.finalizada
    venda.finalizado_em = datetime.now(timezone.utc)

    await audit.registrar(
        acao="venda_finalizada",
        usuario_id=current_user.id,
        tabela="vendas",
        registro_id=str(venda.id),
        dados_depois={"numero": venda.numero, "total_final": str(venda.total_final)},
    )

    # Dispara webhook venda_finalizada
    itens_payload = [
        {
            "sequencia": i.sequencia,
            "produto_id": i.produto_id,
            "quantidade": str(i.quantidade),
            "preco_unitario": str(i.preco_unitario),
            "subtotal": str(i.subtotal),
        }
        for i in itens
    ]
    await enfileirar_evento(db, "venda_finalizada", {
        "evento": "venda_finalizada",
        "venda": {
            "id": str(venda.id),
            "numero": venda.numero,
            "serie": venda.serie,
            "itens": itens_payload,
            "pagamentos": [{"forma": p.forma.value, "valor": str(p.valor)} for p in body.pagamentos],
            "subtotal": str(venda.subtotal),
            "desconto": str(venda.desconto_nota),
            "total_final": str(venda.total_final),
            "finalizado_em": venda.finalizado_em.isoformat(),
        },
    })

    return await _venda_to_out(venda, db)


@router.post(
    "/{venda_id}/cancelar",
    response_model=VendaOut,
    summary="Cancelar venda",
)
async def cancelar_venda(
    venda_id: UUID,
    body: CancelarVendaRequest,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Cancela uma venda em andamento (status 'aberta').
    Vendas finalizadas requerem processo diferente (SEFAZ).
    """
    repo = VendaRepository(db)
    audit = AuditoriaRepository(db)
    venda = await repo.buscar_por_id(venda_id)

    if not venda:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venda não encontrada")

    if venda.status == StatusVenda.cancelada:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Venda já cancelada")

    if venda.status == StatusVenda.finalizada and venda.usuario_id != current_user.id:
        if not current_user.is_gerente_ou_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão para cancelar venda de outro operador")

    venda.status = StatusVenda.cancelada
    venda.cancelado_em = datetime.now(timezone.utc)
    venda.motivo_cancelamento = body.motivo

    await audit.registrar(
        acao="venda_cancelada",
        usuario_id=current_user.id,
        tabela="vendas",
        registro_id=str(venda.id),
        dados_depois={"motivo": body.motivo},
    )

    await enfileirar_evento(db, "venda_cancelada", {
        "evento": "venda_cancelada",
        "venda_id": str(venda.id),
        "numero": venda.numero,
        "motivo": body.motivo,
    })

    return await _venda_to_out(venda, db)
