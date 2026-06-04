"""Repositório para gravação de auditoria_log."""
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auditoria import AuditoriaLog


class AuditoriaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def registrar(
        self,
        acao: str,
        usuario_id: Optional[UUID] = None,
        tabela: Optional[str] = None,
        registro_id: Optional[str] = None,
        dados_antes: Optional[dict] = None,
        dados_depois: Optional[dict] = None,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditoriaLog:
        """Grava um registro de auditoria. Chamado em todo INSERT/UPDATE/DELETE crítico."""
        log = AuditoriaLog(
            usuario_id=usuario_id,
            acao=acao,
            tabela=tabela,
            registro_id=registro_id,
            dados_antes=dados_antes,
            dados_depois=dados_depois,
            ip=ip,
            user_agent=user_agent,
        )
        self.db.add(log)
        await self.db.flush()
        return log
