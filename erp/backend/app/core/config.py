"""
Configurações centrais do ERP via pydantic-settings.
Todos os valores sensíveis são carregados do .env — nunca hard-coded.
"""
from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Ambiente ──────────────────────────────────────────────
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # ── Banco de dados ────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://erp:erp_secret@localhost:5432/erp"

    # ── Redis ─────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── JWT ───────────────────────────────────────────────────
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    # ── CORS ──────────────────────────────────────────────────
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    # ── N8N ───────────────────────────────────────────────────
    N8N_WEBHOOK_SECRET: str = ""

    # ── MinIO ─────────────────────────────────────────────────
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = ""
    MINIO_BUCKET_NFCE: str = "nfce-xml"

    # ── PIX ───────────────────────────────────────────────────
    PIX_BASE_URL: str = ""
    PIX_CLIENT_ID: str = ""
    PIX_CLIENT_SECRET: str = ""
    PIX_CERT_PATH: str = ""

    # ── NFC-e (Fase 5) ────────────────────────────────────────
    NFCE_AMBIENTE: int = 2  # 2 = Homologação
    NFCE_UF: int = 35
    NFCE_CERTIFICADO_PATH: str = ""
    NFCE_CERTIFICADO_SENHA: str = ""

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def jwt_secret_must_be_strong(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY deve ter pelo menos 32 caracteres")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
