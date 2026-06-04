"""
Cliente Redis assíncrono para cache e gerenciamento de sessões/blacklist de tokens.
"""
from typing import Optional

import redis.asyncio as aioredis

from app.core.config import get_settings

settings = get_settings()

_redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """Retorna o cliente Redis singleton (conexão lazy)."""
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def close_redis() -> None:
    """Fecha a conexão Redis (chamado no shutdown da aplicação)."""
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None


# ── Helpers de blacklist de tokens ────────────────────────────────────────────

async def adicionar_token_blacklist(jti: str, expire_seconds: int) -> None:
    """Adiciona um token revogado à blacklist com TTL automático."""
    redis = await get_redis()
    await redis.setex(f"blacklist:{jti}", expire_seconds, "1")


async def token_esta_revogado(jti: str) -> bool:
    """Verifica se um token está na blacklist."""
    redis = await get_redis()
    return bool(await redis.exists(f"blacklist:{jti}"))
