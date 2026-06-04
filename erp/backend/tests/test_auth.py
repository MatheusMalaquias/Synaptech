"""
Testes para os endpoints de autenticação:
  POST /api/v1/auth/login
  POST /api/v1/auth/refresh
  POST /api/v1/auth/logout
"""
import pytest
from httpx import AsyncClient

from tests.conftest import headers_para

pytestmark = pytest.mark.asyncio


class TestLogin:
    async def test_login_sucesso(self, client: AsyncClient, usuario_admin):
        """Login com credenciais válidas retorna tokens e dados do usuário."""
        resp = await client.post("/api/v1/auth/login", json={
            "email": "admin@teste.com",
            "senha": "senha_admin_123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 3600
        assert data["usuario"]["perfil"] == "admin"

    async def test_login_senha_errada(self, client: AsyncClient, usuario_admin):
        """Login com senha incorreta retorna 401."""
        resp = await client.post("/api/v1/auth/login", json={
            "email": "admin@teste.com",
            "senha": "senha_errada",
        })
        assert resp.status_code == 401
        assert "Credenciais inválidas" in resp.json()["detail"]

    async def test_login_email_inexistente(self, client: AsyncClient):
        """Login com email não cadastrado retorna 401 (não revela qual campo está errado)."""
        resp = await client.post("/api/v1/auth/login", json={
            "email": "naoexiste@teste.com",
            "senha": "qualquer",
        })
        assert resp.status_code == 401

    async def test_login_email_invalido(self, client: AsyncClient):
        """Email inválido retorna 422 (validação Pydantic)."""
        resp = await client.post("/api/v1/auth/login", json={
            "email": "nao-e-email",
            "senha": "qualquer",
        })
        assert resp.status_code == 422

    async def test_login_registra_auditoria(self, client: AsyncClient, db, usuario_admin):
        """Login bem-sucedido deve gravar registro em auditoria_log."""
        from sqlalchemy import select
        from app.models.auditoria import AuditoriaLog

        await client.post("/api/v1/auth/login", json={
            "email": "admin@teste.com",
            "senha": "senha_admin_123",
        })

        result = await db.execute(
            select(AuditoriaLog).where(
                AuditoriaLog.acao == "login",
                AuditoriaLog.registro_id == str(usuario_admin.id),
            )
        )
        log = result.scalar_one_or_none()
        assert log is not None

    async def test_login_falha_registra_auditoria(self, client: AsyncClient, usuario_admin):
        """Login com falha deve gravar registro de login_falha em auditoria_log."""
        resp = await client.post("/api/v1/auth/login", json={
            "email": "admin@teste.com",
            "senha": "errada",
        })
        assert resp.status_code == 401


class TestRefresh:
    async def test_refresh_valido(self, client: AsyncClient, usuario_admin):
        """Refresh token válido retorna novo access_token."""
        # Primeiro faz login para obter refresh_token
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "admin@teste.com",
            "senha": "senha_admin_123",
        })
        refresh_token = login_resp.json()["refresh_token"]

        resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["expires_in"] == 3600

    async def test_refresh_token_invalido(self, client: AsyncClient):
        """Refresh token inválido retorna 401."""
        resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": "token.invalido.aqui"})
        assert resp.status_code == 401

    async def test_refresh_com_access_token(self, client: AsyncClient, usuario_admin):
        """Usar access_token no lugar de refresh_token deve retornar 401."""
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "admin@teste.com",
            "senha": "senha_admin_123",
        })
        access_token = login_resp.json()["access_token"]

        resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": access_token})
        assert resp.status_code == 401


class TestLogout:
    async def test_logout_sucesso(self, client: AsyncClient, usuario_admin):
        """Logout com token válido retorna mensagem de confirmação."""
        resp = await client.post(
            "/api/v1/auth/logout",
            headers=headers_para(usuario_admin),
        )
        assert resp.status_code == 200
        assert "Sessão encerrada" in resp.json()["message"]

    async def test_logout_sem_token(self, client: AsyncClient):
        """Logout sem token retorna 403."""
        resp = await client.post("/api/v1/auth/logout")
        assert resp.status_code in (401, 403)
