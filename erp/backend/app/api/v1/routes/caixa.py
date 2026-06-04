"""
Endpoints de Caixa (sessões de turno):
  GET  /caixa/sessao-atual    — sessão aberta do operador
  POST /caixa/abrir           — abre uma nova sessão
  POST /caixa/fechar          — fecha a sessão atual
  GET  /caixa/listar          — lista todos os caixas cadastrados
  POST /caixa/criar           — cria novo caixa (admin)
"""
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import CurrentUser, RequireAdmin
from app.core.database import get_db
from app.integrations.n8n.webhook_worker import enfileirar_evento
from app.models.caixa import Caixa, SessaoCaixa
from app.repositories.auditoria_repo import AuditoriaRepository
from app.repositories.caixa_repo import CaixaRepository
from app.schemas.caixa import (
    AbrirCaixaRequest,
    CaixaOut,
    FecharCaixaRequest,
    SessaoCaixaOut,
    TotaisPorForma,
)

router = APIRouter()


@router.get(
    "/listar",
    response_model=list[CaixaOut],
    summary="Listar caixas cadastrados",
)
async def listar_caixas(
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Lista todos os caixas físicos cadastrados."""
    repo = CaixaRepository(db)
    return await repo.listar_caixas()


@router.post(
    "/criar",
    response_model=CaixaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Criar caixa",
    dependencies=[RequireAdmin],
)
async def criar_caixa(
    nome: str,
    serie_nfce: str = "01",
    impressora: Optional[str] = None,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Cadastra um novo caixa físico. Requer admin."""
    repo = CaixaRepository(db)
    caixa = Caixa(nome=nome, serie_nfce=serie_nfce, impressora=impressora)
    return await repo.criar_caixa(caixa)


@router.get(
    "/sessao-atual",
    response_model=SessaoCaixaOut,
    summary="Sessão atual do operador",
)
async def sessao_atual(
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Retorna a sessão de caixa aberta do operador autenticado,
    com totais de vendas e por forma de pagamento.
    """
    repo = CaixaRepository(db)
    sessao = await repo.sessao_aberta_do_usuario(current_user.id)
    if not sessao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhuma sessão aberta")

    total_vendas = await repo.total_vendas_sessao(sessao.id)
    totais = await repo.totais_por_forma(sessao.id)

    return SessaoCaixaOut(
        id=sessao.id,
        caixa_id=sessao.caixa_id,
        usuario_id=sessao.usuario_id,
        status=sessao.status.value,
        valor_abertura=sessao.valor_abertura,
        valor_fechamento=sessao.valor_fechamento,
        observacao=sessao.observacao,
        abertura_em=sessao.abertura_em,
        fechamento_em=sessao.fechamento_em,
        total_vendas=total_vendas,
        total_por_forma=TotaisPorForma(**{k: Decimal(str(v or 0)) for k, v in totais.items()}),
    )


@router.post(
    "/abrir",
    response_model=SessaoCaixaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Abrir sessão de caixa",
)
async def abrir_caixa(
    body: AbrirCaixaRequest,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Abre uma nova sessão de caixa para o operador.
    Só pode ter uma sessão aberta por usuário.
    """
    repo = CaixaRepository(db)
    audit = AuditoriaRepository(db)

    # Verifica se já tem sessão aberta
    sessao_existente = await repo.sessao_aberta_do_usuario(current_user.id)
    if sessao_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma sessão aberta. Feche-a antes de abrir nova.",
        )

    caixa = await repo.buscar_caixa(body.caixa_id)
    if not caixa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caixa não encontrado")

    sessao = SessaoCaixa(
        caixa_id=body.caixa_id,
        usuario_id=current_user.id,
        valor_abertura=body.valor_abertura,
    )
    sessao = await repo.abrir_sessao(sessao)

    await audit.registrar(
        acao="caixa_aberto",
        usuario_id=current_user.id,
        tabela="sessoes_caixa",
        registro_id=str(sessao.id),
        dados_depois={"caixa_id": str(body.caixa_id), "valor_abertura": str(body.valor_abertura)},
    )

    # Dispara evento webhook
    await enfileirar_evento(db, "caixa_aberto", {
        "evento": "caixa_aberto",
        "sessao_id": str(sessao.id),
        "caixa_id": str(sessao.caixa_id),
        "usuario_id": str(sessao.usuario_id),
        "valor_abertura": str(body.valor_abertura),
    })

    return SessaoCaixaOut(
        id=sessao.id,
        caixa_id=sessao.caixa_id,
        usuario_id=sessao.usuario_id,
        status=sessao.status.value,
        valor_abertura=sessao.valor_abertura,
        valor_fechamento=None,
        observacao=None,
        abertura_em=sessao.abertura_em,
        fechamento_em=None,
    )


@router.post(
    "/fechar",
    response_model=SessaoCaixaOut,
    summary="Fechar sessão de caixa",
)
async def fechar_caixa(
    body: FecharCaixaRequest,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Fecha a sessão de caixa aberta do operador.
    Registra totais por forma de pagamento para o relatório de fechamento.
    """
    repo = CaixaRepository(db)
    audit = AuditoriaRepository(db)

    sessao = await repo.sessao_aberta_do_usuario(current_user.id)
    if not sessao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhuma sessão aberta")

    total_vendas = await repo.total_vendas_sessao(sessao.id)
    totais = await repo.totais_por_forma(sessao.id)

    sessao = await repo.fechar_sessao(sessao, body.valor_fechamento, body.observacao)

    await audit.registrar(
        acao="caixa_fechado",
        usuario_id=current_user.id,
        tabela="sessoes_caixa",
        registro_id=str(sessao.id),
        dados_depois={
            "valor_fechamento": str(body.valor_fechamento),
            "total_vendas": str(total_vendas),
        },
    )

    # Dispara evento webhook com resumo completo
    await enfileirar_evento(db, "caixa_fechado", {
        "evento": "caixa_fechado",
        "sessao": {
            "id": str(sessao.id),
            "caixa_id": str(sessao.caixa_id),
            "abertura_em": sessao.abertura_em.isoformat(),
            "fechamento_em": sessao.fechamento_em.isoformat() if sessao.fechamento_em else None,
            "valor_abertura": str(sessao.valor_abertura),
            "valor_fechamento": str(body.valor_fechamento),
            "total_vendas": str(total_vendas),
            "por_forma": {k: str(v) for k, v in totais.items()},
        },
    })

    total_por_forma = TotaisPorForma(**{k: Decimal(str(v or 0)) for k, v in totais.items()})
    return SessaoCaixaOut(
        id=sessao.id,
        caixa_id=sessao.caixa_id,
        usuario_id=sessao.usuario_id,
        status=sessao.status.value,
        valor_abertura=sessao.valor_abertura,
        valor_fechamento=sessao.valor_fechamento,
        observacao=sessao.observacao,
        abertura_em=sessao.abertura_em,
        fechamento_em=sessao.fechamento_em,
        total_vendas=total_vendas,
        total_por_forma=total_por_forma,
    )
