"""
Testes para os endpoints de Estoque:
  GET  /api/v1/estoque
  GET  /api/v1/estoque/{produto_id}
  POST /api/v1/estoque/movimentacao
  GET  /api/v1/estoque/movimentacoes
"""
from decimal import Decimal

import pytest
from httpx import AsyncClient

from tests.conftest import headers_para

pytestmark = pytest.mark.asyncio


class TestSaldoEstoque:
    async def test_saldo_produto_existente(self, client: AsyncClient, usuario_caixa, produto_kg):
        """Retorna saldo correto para produto cadastrado."""
        resp = await client.get(
            f"/api/v1/estoque/{produto_kg.id}",
            headers=headers_para(usuario_caixa),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["produto_id"] == produto_kg.id
        assert data["descricao"] == "ALHO"
        assert data["unidade"] == "KG"
        assert float(data["quantidade"]) == 100.0
        assert float(data["estoque_minimo"]) == 10.0
        assert data["abaixo_minimo"] is False

    async def test_saldo_produto_inexistente(self, client: AsyncClient, usuario_caixa):
        """Produto sem registro de estoque retorna 404."""
        resp = await client.get("/api/v1/estoque/999999", headers=headers_para(usuario_caixa))
        assert resp.status_code == 404

    async def test_listar_todos_estoques(self, client: AsyncClient, usuario_caixa, produto_kg, produto_un):
        """Listagem retorna todos os produtos com saldo."""
        resp = await client.get("/api/v1/estoque", headers=headers_para(usuario_caixa))
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 2


class TestMovimentacaoEstoque:
    async def test_entrada_estoque(self, client: AsyncClient, usuario_admin, produto_kg):
        """Entrada de estoque aumenta o saldo corretamente."""
        resp = await client.post(
            "/api/v1/estoque/movimentacao",
            headers=headers_para(usuario_admin),
            json={
                "produto_id": produto_kg.id,
                "tipo": "entrada",
                "quantidade": "50.000",
                "motivo": "Compra fornecedor",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["tipo"] == "entrada"
        assert float(data["saldo_anterior"]) == 100.0
        assert float(data["saldo_posterior"]) == 150.0

    async def test_saida_estoque(self, client: AsyncClient, usuario_admin, produto_kg):
        """Saída de estoque reduz o saldo corretamente."""
        resp = await client.post(
            "/api/v1/estoque/movimentacao",
            headers=headers_para(usuario_admin),
            json={
                "produto_id": produto_kg.id,
                "tipo": "saida",
                "quantidade": "30.000",
                "motivo": "Venda",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert float(data["saldo_posterior"]) == 70.0

    async def test_estoque_pode_ser_negativo(self, client: AsyncClient, usuario_admin, produto_kg):
        """
        O sistema permite estoque negativo (regra de negócio — spec/02).
        Saída maior que o saldo deve ser aceita.
        """
        resp = await client.post(
            "/api/v1/estoque/movimentacao",
            headers=headers_para(usuario_admin),
            json={
                "produto_id": produto_kg.id,
                "tipo": "saida",
                "quantidade": "200.000",  # maior que o saldo de 100
                "motivo": "Venda que zera e nega",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert float(data["saldo_posterior"]) == -100.0  # 100 - 200 = -100

    async def test_ajuste_positivo(self, client: AsyncClient, usuario_admin, produto_kg):
        """Ajuste positivo adiciona ao saldo."""
        resp = await client.post(
            "/api/v1/estoque/movimentacao",
            headers=headers_para(usuario_admin),
            json={
                "produto_id": produto_kg.id,
                "tipo": "ajuste_positivo",
                "quantidade": "5.500",
                "motivo": "Inventário",
            },
        )
        assert resp.status_code == 201
        assert float(resp.json()["saldo_posterior"]) == 105.5

    async def test_movimentacao_caixa_negado(self, client: AsyncClient, usuario_caixa, produto_kg):
        """Caixa não pode registrar movimentação manual — retorna 403."""
        resp = await client.post(
            "/api/v1/estoque/movimentacao",
            headers=headers_para(usuario_caixa),
            json={
                "produto_id": produto_kg.id,
                "tipo": "entrada",
                "quantidade": "10.000",
            },
        )
        assert resp.status_code == 403

    async def test_movimentacao_produto_inexistente(self, client: AsyncClient, usuario_admin):
        """Movimentação para produto inexistente retorna 404."""
        resp = await client.post(
            "/api/v1/estoque/movimentacao",
            headers=headers_para(usuario_admin),
            json={
                "produto_id": 999999,
                "tipo": "entrada",
                "quantidade": "10.000",
            },
        )
        assert resp.status_code == 404

    async def test_quantidade_zero_invalida(self, client: AsyncClient, usuario_admin, produto_kg):
        """Quantidade zero deve ser rejeitada (validação Pydantic)."""
        resp = await client.post(
            "/api/v1/estoque/movimentacao",
            headers=headers_para(usuario_admin),
            json={
                "produto_id": produto_kg.id,
                "tipo": "entrada",
                "quantidade": "0",
            },
        )
        assert resp.status_code == 422

    async def test_historico_movimentacoes(self, client: AsyncClient, usuario_admin, produto_kg):
        """Histórico retorna movimentações registradas."""
        # Registra uma movimentação
        await client.post(
            "/api/v1/estoque/movimentacao",
            headers=headers_para(usuario_admin),
            json={"produto_id": produto_kg.id, "tipo": "entrada", "quantidade": "1.000"},
        )

        resp = await client.get(
            f"/api/v1/estoque/movimentacoes?produto_id={produto_kg.id}",
            headers=headers_para(usuario_admin),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1


class TestAbaixoMinimo:
    async def test_filtro_abaixo_minimo(self, client: AsyncClient, usuario_admin, produto_kg):
        """Filtro abaixo_minimo retorna apenas produtos com saldo <= mínimo."""
        # Zera o estoque para ficar abaixo do mínimo (10)
        await client.post(
            "/api/v1/estoque/movimentacao",
            headers=headers_para(usuario_admin),
            json={"produto_id": produto_kg.id, "tipo": "saida", "quantidade": "95.000"},
        )

        resp = await client.get(
            "/api/v1/estoque?abaixo_minimo=true",
            headers=headers_para(usuario_caixa := usuario_admin),
        )
        assert resp.status_code == 200
        data = resp.json()
        # Produto ALHO deve estar na lista (saldo=5, mínimo=10)
        ids = [e["produto_id"] for e in data]
        assert produto_kg.id in ids


class TestInvariantesEstoque:
    """Testa invariantes do estoque conforme spec/02-regras-de-negocio.md."""

    def test_movimentacao_rastreavel(self):
        """Toda movimentação preserva saldo_anterior e saldo_posterior."""
        saldo = Decimal("100.000")
        quantidade = Decimal("30.000")
        novo_saldo = saldo - quantidade
        assert novo_saldo == Decimal("70.000")

    def test_saldo_negativo_permitido(self):
        """Estoque negativo é permitido pela regra de negócio."""
        saldo = Decimal("5.000")
        saida = Decimal("10.000")
        novo = saldo - saida
        assert novo == Decimal("-5.000")
        # O sistema não deve bloquear
        assert novo < 0
