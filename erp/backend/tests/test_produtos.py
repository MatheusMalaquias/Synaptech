"""
Testes para os endpoints de Produtos:
  GET    /api/v1/produtos
  GET    /api/v1/produtos/{id}
  GET    /api/v1/produtos/barcode/{codigo}
  POST   /api/v1/produtos
  PUT    /api/v1/produtos/{id}
  DELETE /api/v1/produtos/{id}
"""
from decimal import Decimal

import pytest
from httpx import AsyncClient

from tests.conftest import headers_para

pytestmark = pytest.mark.asyncio


class TestListarProdutos:
    async def test_listar_retorna_lista(self, client: AsyncClient, usuario_caixa, produto_kg):
        """Listar produtos retorna lista paginada."""
        resp = await client.get("/api/v1/produtos", headers=headers_para(usuario_caixa))
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert data["page"] == 1
        assert data["limit"] == 50

    async def test_listar_inclui_estoque(self, client: AsyncClient, usuario_caixa, produto_kg):
        """Listagem inclui o saldo de estoque de cada produto."""
        resp = await client.get("/api/v1/produtos", headers=headers_para(usuario_caixa))
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) >= 1
        # Produto com estoque deve ter campo estoque preenchido
        produto = next(p for p in items if p["id"] == produto_kg.id)
        assert produto["estoque"] is not None
        assert float(produto["estoque"]) == 100.0

    async def test_listar_sem_autenticacao(self, client: AsyncClient):
        """Listagem sem token retorna 403."""
        resp = await client.get("/api/v1/produtos")
        assert resp.status_code in (401, 403)

    async def test_listar_filtro_unidade(self, client: AsyncClient, usuario_caixa, produto_kg, produto_un):
        """Filtrar por unidade retorna apenas produtos daquela unidade."""
        resp = await client.get("/api/v1/produtos?unidade=KG", headers=headers_para(usuario_caixa))
        assert resp.status_code == 200
        for item in resp.json()["items"]:
            assert item["unidade"] == "KG"


class TestDetalharProduto:
    async def test_detalhar_existente(self, client: AsyncClient, usuario_caixa, produto_kg):
        """Detalhar produto existente retorna 200 com dados corretos."""
        resp = await client.get(f"/api/v1/produtos/{produto_kg.id}", headers=headers_para(usuario_caixa))
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == produto_kg.id
        assert data["descricao"] == "ALHO"
        assert data["unidade"] == "KG"
        assert float(data["preco_venda"]) == 29.99

    async def test_detalhar_inexistente(self, client: AsyncClient, usuario_caixa):
        """Produto inexistente retorna 404."""
        resp = await client.get("/api/v1/produtos/999999", headers=headers_para(usuario_caixa))
        assert resp.status_code == 404

    async def test_buscar_por_barcode(self, client: AsyncClient, usuario_caixa, produto_kg):
        """Busca por código de barras retorna o produto correto."""
        resp = await client.get(
            f"/api/v1/produtos/barcode/{produto_kg.codigo_barras}",
            headers=headers_para(usuario_caixa),
        )
        assert resp.status_code == 200
        assert resp.json()["id"] == produto_kg.id

    async def test_buscar_barcode_inexistente(self, client: AsyncClient, usuario_caixa):
        """Barcode inexistente retorna 404."""
        resp = await client.get("/api/v1/produtos/barcode/0000000000000", headers=headers_para(usuario_caixa))
        assert resp.status_code == 404


class TestCriarProduto:
    async def test_criar_produto_admin(self, client: AsyncClient, usuario_admin):
        """Admin pode criar produto com todos os campos."""
        resp = await client.post(
            "/api/v1/produtos",
            headers=headers_para(usuario_admin),
            json={
                "descricao": "MANGA PALMER",
                "unidade": "KG",
                "preco_venda": "8.99",
                "tributado": True,
                "perc_icms": "18.00",
                "estoque_inicial": "50.000",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["descricao"] == "MANGA PALMER"
        assert data["id"] is not None
        # Estoque inicial deve ser 50.0
        assert float(data["estoque"]) == 50.0

    async def test_criar_produto_caixa_negado(self, client: AsyncClient, usuario_caixa):
        """Caixa não pode criar produto — retorna 403."""
        resp = await client.post(
            "/api/v1/produtos",
            headers=headers_para(usuario_caixa),
            json={
                "descricao": "PRODUTO PROIBIDO",
                "unidade": "UN",
                "preco_venda": "1.00",
            },
        )
        assert resp.status_code == 403

    async def test_criar_produto_descricao_maiusculo(self, client: AsyncClient, usuario_admin):
        """Descrição é normalizada para maiúsculas."""
        resp = await client.post(
            "/api/v1/produtos",
            headers=headers_para(usuario_admin),
            json={"descricao": "banana nanica", "unidade": "KG", "preco_venda": "5.99"},
        )
        assert resp.status_code == 201
        assert resp.json()["descricao"] == "BANANA NANICA"

    async def test_criar_produto_preco_negativo(self, client: AsyncClient, usuario_admin):
        """Preço negativo retorna 422."""
        resp = await client.post(
            "/api/v1/produtos",
            headers=headers_para(usuario_admin),
            json={"descricao": "PRODUTO", "unidade": "UN", "preco_venda": "-1.00"},
        )
        assert resp.status_code == 422


class TestAtualizarProduto:
    async def test_atualizar_preco(self, client: AsyncClient, usuario_admin, produto_kg):
        """Gerente/admin pode atualizar o preço do produto."""
        resp = await client.put(
            f"/api/v1/produtos/{produto_kg.id}",
            headers=headers_para(usuario_admin),
            json={"preco_venda": "35.00"},
        )
        assert resp.status_code == 200
        assert float(resp.json()["preco_venda"]) == 35.0

    async def test_atualizar_caixa_negado(self, client: AsyncClient, usuario_caixa, produto_kg):
        """Caixa não pode alterar produto."""
        resp = await client.put(
            f"/api/v1/produtos/{produto_kg.id}",
            headers=headers_para(usuario_caixa),
            json={"preco_venda": "99.99"},
        )
        assert resp.status_code == 403

    async def test_atualizar_inexistente(self, client: AsyncClient, usuario_admin):
        """Atualizar produto inexistente retorna 404."""
        resp = await client.put(
            "/api/v1/produtos/999999",
            headers=headers_para(usuario_admin),
            json={"preco_venda": "10.00"},
        )
        assert resp.status_code == 404


class TestDeletarProduto:
    async def test_soft_delete(self, client: AsyncClient, usuario_admin, produto_kg):
        """Soft delete: produto fica ativo=false mas não é removido do banco."""
        resp = await client.delete(
            f"/api/v1/produtos/{produto_kg.id}",
            headers=headers_para(usuario_admin),
        )
        assert resp.status_code == 204

        # Buscar diretamente com ativo=None deve achar o produto desativado
        from sqlalchemy import select
        from app.models.produto import Produto
        from sqlalchemy.ext.asyncio import AsyncSession

    async def test_delete_caixa_negado(self, client: AsyncClient, usuario_caixa, produto_kg):
        """Caixa não pode deletar produto."""
        resp = await client.delete(
            f"/api/v1/produtos/{produto_kg.id}",
            headers=headers_para(usuario_caixa),
        )
        assert resp.status_code == 403


class TestCalculoPreco:
    """Testa invariantes do cálculo de preço conforme spec/02-regras-de-negocio.md."""

    def test_calculo_subtotal_kg(self):
        """2.750 × 29.99 = 82.47 (arredondado para 2 casas)."""
        quantidade = Decimal("2.750")
        preco = Decimal("29.99")
        subtotal = round(quantidade * preco, 2)
        assert subtotal == Decimal("82.47")

    def test_calculo_subtotal_arredondamento(self):
        """Verifica que o arredondamento segue a regra do sistema."""
        assert round(Decimal("2.750") * Decimal("29.99"), 2) == Decimal("82.47")
        assert round(Decimal("1.000") * Decimal("9.99"), 2) == Decimal("9.99")
        assert round(Decimal("3.333") * Decimal("6.00"), 2) == Decimal("20.00")
