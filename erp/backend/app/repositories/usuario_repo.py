"""Repositório de acesso a dados para Usuários."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usuario import Usuario


class UsuarioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def buscar_por_email(self, email: str) -> Optional[Usuario]:
        result = await self.db.execute(
            select(Usuario).where(Usuario.email == email, Usuario.ativo == True)
        )
        return result.scalar_one_or_none()

    async def buscar_por_id(self, usuario_id) -> Optional[Usuario]:
        # Aceita tanto UUID quanto string (JWT retorna string)
        if isinstance(usuario_id, str):
            usuario_id = UUID(usuario_id)
        result = await self.db.execute(
            select(Usuario).where(Usuario.id == usuario_id, Usuario.ativo == True)
        )
        return result.scalar_one_or_none()

    async def criar(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        await self.db.flush()
        await self.db.refresh(usuario)
        return usuario
