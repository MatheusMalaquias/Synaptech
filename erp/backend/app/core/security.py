"""
Segurança: JWT (access + refresh tokens) e hashing bcrypt.
Nunca logar secrets, senhas ou tokens.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

import bcrypt as _bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()

# ── Hashing de senha ──────────────────────────────────────────────────────────
# bcrypt com custo 12 conforme spec/07-seguranca.md

def hash_senha(senha: str) -> str:
    """Gera hash bcrypt da senha. Nunca armazenar senha em texto puro."""
    salt = _bcrypt.gensalt(rounds=12)
    return _bcrypt.hashpw(senha.encode("utf-8"), salt).decode("utf-8")


def verificar_senha(senha: str, hash_: str) -> bool:
    """Verifica se a senha bate com o hash armazenado."""
    return _bcrypt.checkpw(senha.encode("utf-8"), hash_.encode("utf-8"))


# ── JWT ───────────────────────────────────────────────────────────────────────

def _criar_token(data: dict, expires_delta: timedelta) -> str:
    """Cria um JWT assinado com HS256."""
    payload = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    payload.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def criar_access_token(
    usuario_id: UUID,
    nome: str,
    perfil: str,
    sessao_id: Optional[str] = None,
) -> str:
    """
    Cria access_token JWT com validade de JWT_ACCESS_EXPIRE_MINUTES.
    Payload inclui: sub, nome, perfil, sessao_id.
    """
    data = {
        "sub": str(usuario_id),
        "nome": nome,
        "perfil": perfil,
        "tipo": "access",
    }
    if sessao_id:
        data["sessao_id"] = sessao_id
    return _criar_token(data, timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES))


def criar_refresh_token(usuario_id: UUID) -> str:
    """
    Cria refresh_token JWT com validade de JWT_REFRESH_EXPIRE_DAYS.
    Rotacionado a cada uso.
    """
    data = {"sub": str(usuario_id), "tipo": "refresh"}
    return _criar_token(data, timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS))


def decodificar_token(token: str) -> dict:
    """
    Decodifica e valida um JWT.
    Lança JWTError se inválido ou expirado.
    """
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def verificar_access_token(token: str) -> Optional[dict]:
    """
    Valida um access_token e retorna o payload.
    Retorna None se inválido.
    """
    try:
        payload = decodificar_token(token)
        if payload.get("tipo") != "access":
            return None
        return payload
    except JWTError:
        return None


def verificar_refresh_token(token: str) -> Optional[str]:
    """
    Valida um refresh_token e retorna o usuario_id (sub).
    Retorna None se inválido.
    """
    try:
        payload = decodificar_token(token)
        if payload.get("tipo") != "refresh":
            return None
        return payload.get("sub")
    except JWTError:
        return None
