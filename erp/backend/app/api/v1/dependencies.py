"""
Dependências compartilhadas dos endpoints FastAPI.
Inclui autenticação JWT e controle de acesso por perfil.
"""
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.redis import token_esta_revogado
from app.core.security import verificar_access_token

security = HTTPBearer()


class UsuarioAutenticado:
    """Dados do usuário extraídos do JWT."""

    def __init__(self, id: UUID, nome: str, perfil: str, sessao_id: str | None = None):
        self.id = id
        self.nome = nome
        self.perfil = perfil
        self.sessao_id = sessao_id

    @property
    def is_admin(self) -> bool:
        return self.perfil == "admin"

    @property
    def is_gerente_ou_admin(self) -> bool:
        return self.perfil in ("admin", "gerente")


async def get_usuario_atual(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> UsuarioAutenticado:
    """
    Dependency que valida o JWT do header Authorization e retorna o usuário.
    Verifica também se o token foi revogado (blacklist no Redis).
    """
    token = credentials.credentials
    payload = verificar_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verifica blacklist (logout)
    jti = payload.get("sub", "") + str(payload.get("exp", ""))
    if await token_esta_revogado(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revogado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UsuarioAutenticado(
        id=UUID(payload["sub"]),
        nome=payload.get("nome", ""),
        perfil=payload.get("perfil", "caixa"),
        sessao_id=payload.get("sessao_id"),
    )


def require_perfil(*perfis: str):
    """
    Factory de dependency para controle de acesso por perfil.

    Uso:
        @router.post("/", dependencies=[Depends(require_perfil("admin", "gerente"))])
    """
    async def _check(usuario: Annotated[UsuarioAutenticado, Depends(get_usuario_atual)]):
        if usuario.perfil not in perfis:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Perfil requerido: {', '.join(perfis)}",
            )
        return usuario

    return _check


# Aliases convenientes
CurrentUser = Annotated[UsuarioAutenticado, Depends(get_usuario_atual)]
RequireAdmin = Depends(require_perfil("admin"))
RequireGerente = Depends(require_perfil("admin", "gerente"))
