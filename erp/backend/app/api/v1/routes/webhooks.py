"""
Endpoints de Webhooks (integração n8n):
  GET    /webhooks           — listar configurações
  POST   /webhooks           — criar novo webhook
  DELETE /webhooks/{id}      — desativar webhook (soft delete)
  POST   /webhooks/test/{id} — disparar evento de teste
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import CurrentUser, RequireAdmin
from app.core.database import get_db
from app.integrations.n8n.webhook_worker import enfileirar_evento
from app.models.webhook import Webhook
from app.repositories.webhook_repo import WebhookRepository
from app.schemas.webhook import WebhookCreate, WebhookOut

router = APIRouter()


@router.get(
    "",
    response_model=list[WebhookOut],
    summary="Listar webhooks configurados",
    dependencies=[RequireAdmin],
)
async def listar_webhooks(
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Lista todos os webhooks cadastrados (ativos e inativos). Requer admin."""
    repo = WebhookRepository(db)
    return [WebhookOut.model_validate(wh) for wh in await repo.listar()]


@router.post(
    "",
    response_model=WebhookOut,
    status_code=status.HTTP_201_CREATED,
    summary="Criar webhook",
    dependencies=[RequireAdmin],
)
async def criar_webhook(
    body: WebhookCreate,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Cria uma nova configuração de webhook para integração com n8n.
    O secret é usado para assinar cada entrega via HMAC-SHA256.
    Requer perfil admin.
    """
    repo = WebhookRepository(db)
    webhook = Webhook(
        nome=body.nome,
        url=body.url,
        eventos=body.eventos,
        secret=body.secret,
    )
    webhook = await repo.criar(webhook)
    return WebhookOut.model_validate(webhook)


@router.delete(
    "/{webhook_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desativar webhook",
    dependencies=[RequireAdmin],
)
async def deletar_webhook(
    webhook_id: UUID,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """Soft delete: marca o webhook como inativo. Requer admin."""
    repo = WebhookRepository(db)
    webhook = await repo.buscar_por_id(webhook_id)
    if not webhook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook não encontrado")
    await repo.deletar(webhook)


@router.post(
    "/test/{webhook_id}",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Disparar evento de teste",
    dependencies=[RequireAdmin],
)
async def testar_webhook(
    webhook_id: UUID,
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Enfileira um payload de teste para validar a configuração do webhook.
    Útil para verificar se o n8n está recebendo e processando corretamente.
    """
    repo = WebhookRepository(db)
    webhook = await repo.buscar_por_id(webhook_id)
    if not webhook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook não encontrado")

    payload_teste = {
        "evento": "teste",
        "timestamp": "2026-06-02T00:00:00Z",
        "mensagem": "Evento de teste do ERP FLV",
        "webhook_id": str(webhook_id),
    }

    count = await enfileirar_evento(db, "teste", payload_teste)
    return {"message": f"Evento de teste enfileirado ({count} entrega(s))"}
