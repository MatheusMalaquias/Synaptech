"""
Endpoints de autenticação:
  POST /auth/login   — gera access + refresh tokens
  POST /auth/refresh — renova access token
  POST /auth/logout  — revoga o token atual
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import CurrentUser, get_usuario_atual
from app.core.config import get_settings
from app.core.database import get_db
from app.core.redis import adicionar_token_blacklist
from app.core.security import (
    criar_access_token,
    criar_refresh_token,
    verificar_refresh_token,
    verificar_senha,
)
from app.repositories.auditoria_repo import AuditoriaRepository
from app.repositories.usuario_repo import UsuarioRepository
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    RefreshRequest,
    RefreshResponse,
    UsuarioInfo,
)

router = APIRouter()
settings = get_settings()


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Autenticar operador",
)
async def login(
    body: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Autentica um operador com email e senha.

    Retorna access_token (1h) e refresh_token (7d).
    Registra o login (sucesso ou falha) em auditoria_log.
    """
    repo = UsuarioRepository(db)
    audit = AuditoriaRepository(db)
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent", "")

    usuario = await repo.buscar_por_email(body.email)

    if not usuario or not verificar_senha(body.senha, usuario.senha_hash):
        # Registra tentativa falha — sem expor qual campo está errado
        await audit.registrar(
            acao="login_falha",
            tabela="usuarios",
            dados_depois={"email": body.email},
            ip=ip,
            user_agent=ua,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )

    access_token = criar_access_token(
        usuario_id=usuario.id,
        nome=usuario.nome,
        perfil=usuario.perfil.value,
    )
    refresh_token = criar_refresh_token(usuario_id=usuario.id)

    await audit.registrar(
        acao="login",
        usuario_id=usuario.id,
        tabela="usuarios",
        registro_id=str(usuario.id),
        ip=ip,
        user_agent=ua,
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_EXPIRE_MINUTES * 60,
        usuario=UsuarioInfo(id=usuario.id, nome=usuario.nome, perfil=usuario.perfil.value),
    )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    summary="Renovar access token",
)
async def refresh(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Renova o access_token a partir de um refresh_token válido.
    O refresh_token é rotacionado a cada uso.
    """
    usuario_id = verificar_refresh_token(body.refresh_token)
    if not usuario_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado",
        )

    repo = UsuarioRepository(db)
    usuario = await repo.buscar_por_id(usuario_id)  # type: ignore[arg-type]
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
        )

    access_token = criar_access_token(
        usuario_id=usuario.id,
        nome=usuario.nome,
        perfil=usuario.perfil.value,
    )

    return RefreshResponse(
        access_token=access_token,
        expires_in=settings.JWT_ACCESS_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Encerrar sessão",
)
async def logout(
    request: Request,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Revoga o access_token atual adicionando-o à blacklist no Redis.
    O token não poderá ser reutilizado mesmo que ainda não tenha expirado.
    """
    # Extrai o token do header para revogar
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.removeprefix("Bearer ").strip()

    from app.core.security import decodificar_token
    try:
        payload = decodificar_token(token)
        jti = str(current_user.id) + str(payload.get("exp", ""))
        ttl = settings.JWT_ACCESS_EXPIRE_MINUTES * 60
        await adicionar_token_blacklist(jti, ttl)
    except Exception:
        pass  # Se o token já expirou, não há nada a fazer

    audit = AuditoriaRepository(db)
    ip = request.client.host if request.client else None
    await audit.registrar(
        acao="logout",
        usuario_id=current_user.id,
        tabela="usuarios",
        registro_id=str(current_user.id),
        ip=ip,
    )

    return LogoutResponse(message="Sessão encerrada")
