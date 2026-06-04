"""
Testes para Caixa, Vendas e integração n8n:
  POST /api/v1/caixa/criar
  POST /api/v1/caixa/abrir
  POST /api/v1/caixa/fechar
  POST /api/v1/vendas
  POST /api/v1/vendas/{id}/item
  POST /api/v1/vendas/{id}/finalizar
  POST /api/v1/vendas/{id}/cancelar
  POST /api/v1/n8n/registrar-venda
"""
from decimal import Decimal

import pytest
from httpx import AsyncClient

from tests.conftest import headers_para

pytestmark = pytest.mark.asyncio


# ── Fixtures de Caixa ─────────────────────────────────────────────────────────

async def criar_caixa_e_sessao(client, usuario_admin):
    """Helper: cria caixa e abre sessão, retorna sessao."""
    resp = await client.post(
        "/api/v1/caixa/criar?nome=Caixa+Teste&serie_nfce=01",
        headers=headers_para(usuario_admin),
    )
    assert resp.status_code == 201, resp.text
    caixa_id = resp.json()["id"]

    resp = await client.post(
        "/api/v1/caixa/abrir",
        headers=headers_para(usuario_admin),
        json={"caixa_id": caixa_id, "valor_abertura": "100.00"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


class TestCaixa:
    async def test_criar_caixa(self, client: AsyncClient, usuario_admin):
        """Admin pode criar caixa."""
        resp = await client.post(
            "/api/v1/caixa/criar?nome=Caixa+01",
            headers=headers_para(usuario_admin),
        )
        assert resp.status_code == 201
        assert resp.json()["nome"] == "Caixa 01"

    async def test_abrir_sessao(self, client: AsyncClient, usuario_admin):
        """Abre sessão de caixa com sucesso."""
        sessao = await criar_caixa_e_sessao(client, usuario_admin)
        assert sessao["status"] == "aberta"
        assert float(sessao["valor_abertura"]) == 100.0

    async def test_nao_pode_abrir_duas_sessoes(self, client: AsyncClient, usuario_admin):
        """Não pode abrir duas sessões simultâneas."""
        await criar_caixa_e_sessao(client, usuario_admin)

        # Segunda tentativa deve falhar
        resp2 = await client.post(
            "/api/v1/caixa/criar?nome=Caixa+Extra",
            headers=headers_para(usuario_admin),
        )
        caixa_id2 = resp2.json()["id"]

        resp = await client.post(
            "/api/v1/caixa/abrir",
            headers=headers_para(usuario_admin),
            json={"caixa_id": caixa_id2, "valor_abertura": "0.00"},
        )
        assert resp.status_code == 409

    async def test_fechar_sessao(self, client: AsyncClient, usuario_admin):
        """Fecha sessão de caixa e retorna totais."""
        await criar_caixa_e_sessao(client, usuario_admin)

        resp = await client.post(
            "/api/v1/caixa/fechar",
            headers=headers_para(usuario_admin),
            json={"valor_fechamento": "150.00"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "fechada"
        assert float(data["valor_fechamento"]) == 150.0

    async def test_sessao_atual(self, client: AsyncClient, usuario_admin):
        """Retorna sessão atual do operador."""
        await criar_caixa_e_sessao(client, usuario_admin)
        resp = await client.get("/api/v1/caixa/sessao-atual", headers=headers_para(usuario_admin))
        assert resp.status_code == 200
        assert resp.json()["status"] == "aberta"


class TestVendas:
    async def test_criar_venda_sem_sessao(self, client: AsyncClient, usuario_admin):
        """Criar venda sem caixa aberto retorna 400."""
        resp = await client.post("/api/v1/vendas", headers=headers_para(usuario_admin))
        assert resp.status_code == 400

    async def test_criar_venda_com_sessao(self, client: AsyncClient, usuario_admin):
        """Cria venda com sessão aberta."""
        await criar_caixa_e_sessao(client, usuario_admin)
        resp = await client.post("/api/v1/vendas", headers=headers_para(usuario_admin))
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "aberta"
        assert data["numero"] >= 1

    async def test_adicionar_item(self, client: AsyncClient, usuario_admin, produto_kg):
        """Adiciona produto à venda com subtotal calculado corretamente."""
        await criar_caixa_e_sessao(client, usuario_admin)
        venda_resp = await client.post("/api/v1/vendas", headers=headers_para(usuario_admin))
        venda_id = venda_resp.json()["id"]

        resp = await client.post(
            f"/api/v1/vendas/{venda_id}/item",
            headers=headers_para(usuario_admin),
            json={"produto_id": produto_kg.id, "quantidade": "2.750"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["produto_id"] == produto_kg.id
        # 2.750 × 29.99 = 82.47
        assert float(data["subtotal"]) == 82.47
        assert float(data["quantidade"]) == 2.750

    async def test_calculo_subtotal_invariante(self, client: AsyncClient, usuario_admin, produto_kg):
        """Verifica a invariante: subtotal = ROUND(qtd × preco, 2)."""
        await criar_caixa_e_sessao(client, usuario_admin)
        venda_resp = await client.post("/api/v1/vendas", headers=headers_para(usuario_admin))
        venda_id = venda_resp.json()["id"]

        resp = await client.post(
            f"/api/v1/vendas/{venda_id}/item",
            headers=headers_para(usuario_admin),
            json={"produto_id": produto_kg.id, "quantidade": "2.750"},
        )
        subtotal = Decimal(resp.json()["subtotal"])
        assert subtotal == round(Decimal("2.750") * Decimal("29.99"), 2)
        assert subtotal == Decimal("82.47")

    async def test_remover_item(self, client: AsyncClient, usuario_admin, produto_kg):
        """Remove item da venda."""
        await criar_caixa_e_sessao(client, usuario_admin)
        venda_resp = await client.post("/api/v1/vendas", headers=headers_para(usuario_admin))
        venda_id = venda_resp.json()["id"]

        item_resp = await client.post(
            f"/api/v1/vendas/{venda_id}/item",
            headers=headers_para(usuario_admin),
            json={"produto_id": produto_kg.id, "quantidade": "1.000"},
        )
        item_id = item_resp.json()["id"]

        del_resp = await client.delete(
            f"/api/v1/vendas/{venda_id}/item/{item_id}",
            headers=headers_para(usuario_admin),
        )
        assert del_resp.status_code == 204

    async def test_finalizar_venda(self, client: AsyncClient, usuario_admin, produto_kg):
        """Finaliza venda com pagamento PIX."""
        await criar_caixa_e_sessao(client, usuario_admin)
        venda_resp = await client.post("/api/v1/vendas", headers=headers_para(usuario_admin))
        venda_id = venda_resp.json()["id"]

        await client.post(
            f"/api/v1/vendas/{venda_id}/item",
            headers=headers_para(usuario_admin),
            json={"produto_id": produto_kg.id, "quantidade": "2.750"},
        )

        resp = await client.post(
            f"/api/v1/vendas/{venda_id}/finalizar",
            headers=headers_para(usuario_admin),
            json={"pagamentos": [{"forma": "pix", "valor": "82.47"}]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "finalizada"
        assert float(data["total_final"]) == 82.47
        assert len(data["pagamentos"]) == 1
        assert data["pagamentos"][0]["forma"] == "pix"

    async def test_finalizar_venda_multiplos_pagamentos(self, client: AsyncClient, usuario_admin, produto_kg):
        """Venda pode ter múltiplas formas de pagamento."""
        await criar_caixa_e_sessao(client, usuario_admin)
        venda_resp = await client.post("/api/v1/vendas", headers=headers_para(usuario_admin))
        venda_id = venda_resp.json()["id"]

        await client.post(
            f"/api/v1/vendas/{venda_id}/item",
            headers=headers_para(usuario_admin),
            json={"produto_id": produto_kg.id, "quantidade": "2.750"},
        )

        resp = await client.post(
            f"/api/v1/vendas/{venda_id}/finalizar",
            headers=headers_para(usuario_admin),
            json={"pagamentos": [
                {"forma": "pix", "valor": "50.00"},
                {"forma": "dinheiro", "valor": "32.47"},
            ]},
        )
        assert resp.status_code == 200
        assert len(resp.json()["pagamentos"]) == 2

    async def test_finalizar_venda_sem_itens(self, client: AsyncClient, usuario_admin):
        """Não pode finalizar venda sem itens."""
        await criar_caixa_e_sessao(client, usuario_admin)
        venda_resp = await client.post("/api/v1/vendas", headers=headers_para(usuario_admin))
        venda_id = venda_resp.json()["id"]

        resp = await client.post(
            f"/api/v1/vendas/{venda_id}/finalizar",
            headers=headers_para(usuario_admin),
            json={"pagamentos": [{"forma": "pix", "valor": "10.00"}]},
        )
        assert resp.status_code == 400

    async def test_cancelar_venda(self, client: AsyncClient, usuario_admin):
        """Cancela venda em andamento."""
        await criar_caixa_e_sessao(client, usuario_admin)
        venda_resp = await client.post("/api/v1/vendas", headers=headers_para(usuario_admin))
        venda_id = venda_resp.json()["id"]

        resp = await client.post(
            f"/api/v1/vendas/{venda_id}/cancelar",
            headers=headers_para(usuario_admin),
            json={"motivo": "Cancelado a pedido do cliente"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelada"

    async def test_desconto_nota(self, client: AsyncClient, usuario_admin, produto_kg):
        """Aplica desconto fixo na venda."""
        await criar_caixa_e_sessao(client, usuario_admin)
        venda_resp = await client.post("/api/v1/vendas", headers=headers_para(usuario_admin))
        venda_id = venda_resp.json()["id"]

        await client.post(
            f"/api/v1/vendas/{venda_id}/item",
            headers=headers_para(usuario_admin),
            json={"produto_id": produto_kg.id, "quantidade": "2.750"},
        )

        resp = await client.post(
            f"/api/v1/vendas/{venda_id}/desconto",
            headers=headers_para(usuario_admin),
            json={"tipo": "nota", "valor": "5.00"},
        )
        assert resp.status_code == 200
        data = resp.json()
        # 82.47 - 5.00 = 77.47
        assert float(data["total_final"]) == 77.47


class TestIntegracaoN8N:
    """Testa o endpoint dedicado para o workflow n8n."""

    async def test_registrar_venda_n8n(self, client: AsyncClient, produto_kg):
        """n8n registra venda completa em uma única chamada."""
        resp = await client.post(
            "/api/v1/n8n/registrar-venda",
            headers={"X-N8N-Secret": ""},  # secret vazio = dev mode
            json={
                "Produto": "ALHO",
                "Preco_Unit": 29.99,
                "Quantidade": 2.750,
                "Valor_Total": 82.47,
                "Forma_Pagamento": "Pix",
            },
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["sucesso"] is True
        assert data["produto"] == "ALHO"
        assert data["forma_pagamento"] == "pix"
        assert float(data["subtotal"]) == 82.47

    async def test_n8n_cria_produto_automaticamente(self, client: AsyncClient):
        """n8n cria produto automaticamente se não existir."""
        resp = await client.post(
            "/api/v1/n8n/registrar-venda",
            headers={"X-N8N-Secret": ""},
            json={
                "Produto": "PRODUTO NOVO DO N8N",
                "Preco_Unit": 15.99,
                "Quantidade": 1.000,
                "Valor_Total": 15.99,
                "Forma_Pagamento": "Dinheiro",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["sucesso"] is True
        assert data["produto"] == "PRODUTO NOVO DO N8N"
        assert data["forma_pagamento"] == "dinheiro"

    async def test_n8n_mapeamento_formas_pagamento(self, client: AsyncClient, produto_kg):
        """Verifica mapeamento de formas de pagamento do n8n."""
        formas = [
            ("Pix", "pix"),
            ("Dinheiro", "dinheiro"),
            ("Crédito", "credito"),
            ("Débito", "debito"),
            ("pix dinâmico", "pix"),
            ("espécie", "dinheiro"),
        ]
        for forma_n8n, forma_erp in formas:
            resp = await client.post(
                "/api/v1/n8n/registrar-venda",
                headers={"X-N8N-Secret": ""},
                json={
                    "Produto": "ABACAXI",
                    "Preco_Unit": 4.99,
                    "Quantidade": 1.0,
                    "Valor_Total": 4.99,
                    "Forma_Pagamento": forma_n8n,
                },
            )
            assert resp.status_code == 201, f"Falhou para forma: {forma_n8n}"
            assert resp.json()["forma_pagamento"] == forma_erp

    async def test_n8n_secret_invalido(self, client: AsyncClient, produto_kg):
        """Secret inválido retorna 401."""
        # Configura settings com secret para este teste
        from unittest.mock import patch
        with patch("app.api.v1.routes.n8n_integration.settings") as mock_settings:
            mock_settings.N8N_WEBHOOK_SECRET = "secret_correto"
            resp = await client.post(
                "/api/v1/n8n/registrar-venda",
                headers={"X-N8N-Secret": "secret_errado"},
                json={
                    "Produto": "ALHO",
                    "Preco_Unit": 29.99,
                    "Quantidade": 1.0,
                    "Valor_Total": 29.99,
                    "Forma_Pagamento": "Pix",
                },
            )
            assert resp.status_code == 401

    async def test_n8n_calculo_correto(self, client: AsyncClient):
        """Subtotal calculado corretamente pelo ERP (não usa Valor_Total)."""
        resp = await client.post(
            "/api/v1/n8n/registrar-venda",
            headers={"X-N8N-Secret": ""},
            json={
                "Produto": "ALHO KG TESTE",
                "Preco_Unit": 29.99,
                "Quantidade": 2.750,  # 2.750 × 29.99 = 82.47
                "Valor_Total": 82.47,
                "Forma_Pagamento": "Pix",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        # Verifica invariante de cálculo
        subtotal = Decimal(data["subtotal"])
        qtd = Decimal("2.750")
        preco = Decimal("29.99")
        assert subtotal == round(qtd * preco, 2)
        assert subtotal == Decimal("82.47")

    async def test_n8n_multiples_vendas_sequenciais(self, client: AsyncClient):
        """Múltiplas vendas do n8n recebem números sequenciais."""
        numeros = []
        for i in range(3):
            resp = await client.post(
                "/api/v1/n8n/registrar-venda",
                headers={"X-N8N-Secret": ""},
                json={
                    "Produto": f"PRODUTO {i}",
                    "Preco_Unit": 10.00 + i,
                    "Quantidade": 1.0,
                    "Valor_Total": 10.00 + i,
                    "Forma_Pagamento": "Pix",
                },
            )
            assert resp.status_code == 201
            numeros.append(resp.json()["numero"])

        # Números devem ser sequenciais crescentes
        assert numeros == sorted(numeros)
        assert len(set(numeros)) == 3  # todos diferentes
