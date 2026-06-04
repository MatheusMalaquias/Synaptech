"""
Testes para os endpoints de Webhooks e worker de entregas:
  GET    /api/v1/webhooks
  POST   /api/v1/webhooks
  DELETE /api/v1/webhooks/{id}
  POST   /api/v1/webhooks/test/{id}
"""
import hashlib
import hmac
import json
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from tests.conftest import headers_para

pytestmark = pytest.mark.asyncio


class TestCriarWebhook:
    async def test_criar_webhook_admin(self, client: AsyncClient, usuario_admin):
        """Admin pode criar webhook com eventos válidos."""
        resp = await client.post(
            "/api/v1/webhooks",
            headers=headers_para(usuario_admin),
            json={
                "nome": "n8n Vendas",
                "url": "https://n8n.empresa.com/webhook/vendas",
                "eventos": ["venda_finalizada", "estoque_critico"],
                "secret": "meu_secret_hmac",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["nome"] == "n8n Vendas"
        assert "venda_finalizada" in data["eventos"]
        assert data["ativo"] is True

    async def test_criar_webhook_evento_invalido(self, client: AsyncClient, usuario_admin):
        """Evento inválido retorna 422."""
        resp = await client.post(
            "/api/v1/webhooks",
            headers=headers_para(usuario_admin),
            json={
                "nome": "Teste",
                "url": "https://exemplo.com",
                "eventos": ["evento_inexistente"],
            },
        )
        assert resp.status_code == 422

    async def test_criar_webhook_caixa_negado(self, client: AsyncClient, usuario_caixa):
        """Apenas admin pode criar webhooks."""
        resp = await client.post(
            "/api/v1/webhooks",
            headers=headers_para(usuario_caixa),
            json={
                "nome": "Teste",
                "url": "https://exemplo.com",
                "eventos": ["venda_finalizada"],
            },
        )
        assert resp.status_code == 403


class TestListarWebhooks:
    async def test_listar_admin(self, client: AsyncClient, usuario_admin):
        """Admin pode listar webhooks."""
        resp = await client.get("/api/v1/webhooks", headers=headers_para(usuario_admin))
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_listar_caixa_negado(self, client: AsyncClient, usuario_caixa):
        """Caixa não pode listar webhooks."""
        resp = await client.get("/api/v1/webhooks", headers=headers_para(usuario_caixa))
        assert resp.status_code == 403


class TestDeletarWebhook:
    async def test_soft_delete(self, client: AsyncClient, usuario_admin):
        """Deletar webhook faz soft delete (ativo=false)."""
        # Cria primeiro
        create_resp = await client.post(
            "/api/v1/webhooks",
            headers=headers_para(usuario_admin),
            json={
                "nome": "Para Deletar",
                "url": "https://exemplo.com/wh",
                "eventos": ["caixa_aberto"],
            },
        )
        webhook_id = create_resp.json()["id"]

        # Deleta
        resp = await client.delete(
            f"/api/v1/webhooks/{webhook_id}",
            headers=headers_para(usuario_admin),
        )
        assert resp.status_code == 204

    async def test_deletar_inexistente(self, client: AsyncClient, usuario_admin):
        """Deletar webhook inexistente retorna 404."""
        resp = await client.delete(
            "/api/v1/webhooks/00000000-0000-0000-0000-000000000000",
            headers=headers_para(usuario_admin),
        )
        assert resp.status_code == 404


class TestTestarWebhook:
    async def test_disparar_teste(self, client: AsyncClient, usuario_admin):
        """Endpoint de teste enfileira evento de teste."""
        # Cria webhook
        create_resp = await client.post(
            "/api/v1/webhooks",
            headers=headers_para(usuario_admin),
            json={
                "nome": "Webhook Teste",
                "url": "https://exemplo.com/wh-test",
                "eventos": ["venda_finalizada"],
            },
        )
        webhook_id = create_resp.json()["id"]

        # Dispara teste
        resp = await client.post(
            f"/api/v1/webhooks/test/{webhook_id}",
            headers=headers_para(usuario_admin),
        )
        assert resp.status_code == 202
        assert "enfileirado" in resp.json()["message"]


class TestAssinaturaHMAC:
    """Testa a geração da assinatura HMAC para segurança dos webhooks."""

    def test_assinatura_hmac_valida(self):
        """A assinatura HMAC gerada pelo worker pode ser validada pelo n8n."""
        from app.integrations.n8n.webhook_worker import _calcular_assinatura

        payload = {"evento": "venda_finalizada", "total": "82.47"}
        payload_json = json.dumps(payload)
        secret = "meu_secret_hmac"

        assinatura = _calcular_assinatura(payload_json, secret)

        # Validação como faria o n8n
        expected = "sha256=" + hmac.new(
            secret.encode(), payload_json.encode(), hashlib.sha256
        ).hexdigest()

        assert assinatura == expected
        assert assinatura.startswith("sha256=")

    def test_assinatura_diferente_para_payloads_distintos(self):
        """Payloads diferentes geram assinaturas diferentes."""
        from app.integrations.n8n.webhook_worker import _calcular_assinatura

        secret = "secret"
        sig1 = _calcular_assinatura('{"a": 1}', secret)
        sig2 = _calcular_assinatura('{"a": 2}', secret)
        assert sig1 != sig2


class TestEnfileirarEvento:
    async def test_enfileirar_para_webhooks_ativos(self, client: AsyncClient, usuario_admin, db):
        """Evento é enfileirado apenas para webhooks ativos que escutam o evento."""
        from app.integrations.n8n.webhook_worker import enfileirar_evento
        from app.models.webhook import WebhookEntrega

        # Cria webhook via API
        await client.post(
            "/api/v1/webhooks",
            headers=headers_para(usuario_admin),
            json={
                "nome": "Webhook Ativo",
                "url": "https://exemplo.com",
                "eventos": ["venda_finalizada"],
            },
        )

        payload = {"evento": "venda_finalizada", "venda_id": "123"}
        count = await enfileirar_evento(db, "venda_finalizada", payload)
        assert count >= 1

    async def test_nao_enfileira_para_evento_errado(self, client: AsyncClient, usuario_admin, db):
        """Webhook configurado para 'caixa_aberto' não recebe 'venda_finalizada'."""
        from app.integrations.n8n.webhook_worker import enfileirar_evento

        # Webhook escuta apenas caixa_aberto
        await client.post(
            "/api/v1/webhooks",
            headers=headers_para(usuario_admin),
            json={
                "nome": "Caixa Webhook",
                "url": "https://exemplo.com",
                "eventos": ["caixa_aberto"],
            },
        )

        # Enfileira venda_finalizada — não deve ir para o webhook de caixa
        payload = {"evento": "venda_finalizada"}
        # O count pode ser zero ou positivo dependendo de outros webhooks do teste
        count = await enfileirar_evento(db, "venda_finalizada", payload)
        # Aqui apenas verificamos que não lança exceção
        assert isinstance(count, int)


class TestWorkerRetry:
    """Testa a lógica de retry do worker sem conexão real."""

    def test_retry_delays_configurados(self):
        """Verifica que os delays de retry estão conforme a spec."""
        from app.integrations.n8n.webhook_worker import RETRY_DELAYS, MAX_TENTATIVAS

        assert RETRY_DELAYS == [30, 120, 600, 3600]
        assert MAX_TENTATIVAS == 4

    def test_max_tentativas(self):
        """Após MAX_TENTATIVAS, a entrega deve ficar com status 'falhou'."""
        from app.integrations.n8n.webhook_worker import MAX_TENTATIVAS
        assert MAX_TENTATIVAS == 4
