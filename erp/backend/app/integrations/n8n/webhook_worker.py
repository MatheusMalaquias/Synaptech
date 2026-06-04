"""
Worker de envio de webhooks com retry e backoff exponencial.

Fluxo:
  1. Evento ocorre → payload gravado em webhook_entregas (status=pendente)
  2. Worker assíncrono processa pendentes em loop
  3. Em caso de falha: agenda próxima tentativa com backoff
  4. Após MAX_TENTATIVAS: status=falhou (payload preservado para auditoria)

Retry delays (spec/05-integracao-n8n.md):
  30s → 2min → 10min → 1h
"""
import asyncio
import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.database import engine
from app.models.base import WebhookStatus
from app.models.webhook import Webhook, WebhookEntrega

logger = logging.getLogger(__name__)

# Configuração de retry conforme spec
RETRY_DELAYS = [30, 120, 600, 3600]  # segundos: 30s, 2min, 10min, 1h
MAX_TENTATIVAS = 4
WORKER_INTERVAL = 10  # segundos entre cada varredura do worker


def _calcular_assinatura(payload_json: str, secret: str) -> str:
    """Calcula HMAC-SHA256 do payload para o header X-ERP-Signature."""
    mac = hmac.new(secret.encode(), payload_json.encode(), hashlib.sha256)
    return f"sha256={mac.hexdigest()}"


async def enfileirar_evento(
    db: AsyncSession,
    evento: str,
    payload: dict,
) -> int:
    """
    Enfileira o payload em webhook_entregas para todos os webhooks ativos
    que escutam o evento informado.
    Retorna o número de entregas enfileiradas.
    """
    # Busca todos os webhooks ativos e filtra em Python (compatível com SQLite e PostgreSQL)
    result = await db.execute(select(Webhook).where(Webhook.ativo == True))
    webhooks = [wh for wh in result.scalars().all() if evento in (wh.eventos or [])]

    count = 0
    for wh in webhooks:
        entrega = WebhookEntrega(
            webhook_id=wh.id,
            evento=evento,
            payload=payload,
            status=WebhookStatus.pendente,
        )
        db.add(entrega)
        count += 1

    if count:
        await db.flush()

    return count


async def _processar_entrega(
    session_factory: async_sessionmaker,
    entrega_id: UUID,
) -> None:
    """Tenta enviar uma entrega pendente via HTTP POST."""
    async with session_factory() as db:
        result = await db.execute(
            select(WebhookEntrega)
            .join(Webhook)
            .where(WebhookEntrega.id == entrega_id)
        )
        entrega = result.scalar_one_or_none()
        if not entrega:
            return

        webhook = await db.get(Webhook, entrega.webhook_id)
        if not webhook:
            return

        # Marca como "enviando"
        entrega.status = WebhookStatus.enviando
        entrega.tentativas += 1
        await db.commit()

        payload_json = json.dumps(entrega.payload, ensure_ascii=False, default=str)
        headers = {
            "Content-Type": "application/json",
            "X-ERP-Event": entrega.evento,
            "X-ERP-Delivery": str(entrega.id),
        }
        if webhook.secret:
            headers["X-ERP-Signature"] = _calcular_assinatura(payload_json, webhook.secret)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(webhook.url, content=payload_json, headers=headers)
                resp.raise_for_status()

            entrega.status = WebhookStatus.entregue
            entrega.entregue_em = datetime.now(timezone.utc)
            entrega.ultimo_erro = None
            logger.info("Webhook entregue: entrega_id=%s evento=%s", entrega.id, entrega.evento)

        except Exception as exc:
            erro = str(exc)[:1000]
            entrega.ultimo_erro = erro

            if entrega.tentativas >= MAX_TENTATIVAS:
                entrega.status = WebhookStatus.falhou
                logger.error(
                    "Webhook falhou após %d tentativas: entrega_id=%s erro=%s",
                    MAX_TENTATIVAS, entrega.id, erro,
                )
            else:
                delay = RETRY_DELAYS[min(entrega.tentativas - 1, len(RETRY_DELAYS) - 1)]
                entrega.status = WebhookStatus.pendente
                entrega.proxima_tentativa = datetime.now(timezone.utc) + timedelta(seconds=delay)
                logger.warning(
                    "Webhook falhou (tentativa %d/%d), retry em %ds: entrega_id=%s",
                    entrega.tentativas, MAX_TENTATIVAS, delay, entrega.id,
                )

        await db.commit()


async def executar_worker() -> None:
    """
    Loop principal do worker de webhooks.
    Roda indefinidamente em background, varrendo entregas pendentes.
    """
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    logger.info("Webhook worker iniciado.")

    while True:
        try:
            async with session_factory() as db:
                agora = datetime.now(timezone.utc)
                result = await db.execute(
                    select(WebhookEntrega.id).where(
                        WebhookEntrega.status.in_([WebhookStatus.pendente]),
                        WebhookEntrega.tentativas < MAX_TENTATIVAS,
                        WebhookEntrega.proxima_tentativa <= agora,
                    ).limit(20)
                )
                ids = result.scalars().all()

            for entrega_id in ids:
                asyncio.create_task(_processar_entrega(session_factory, entrega_id))

        except Exception as exc:
            logger.error("Erro no webhook worker: %s", exc)

        await asyncio.sleep(WORKER_INTERVAL)
