"""
Endpoints de gerenciamento de Empresas (visão SaaS — admin only).
  GET    /empresas           — lista todas
  POST   /empresas           — cadastra nova empresa
  GET    /empresas/{id}      — detalhe
  PUT    /empresas/{id}      — atualiza
  DELETE /empresas/{id}      — desativa (soft delete)
  POST   /empresas/{id}/gerar-api-key  — gera nova API key
"""
import secrets
import uuid
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import CurrentUser, require_perfil
from app.core.database import get_db
from app.models.empresa import Empresa

router = APIRouter()
AdminOnly = Depends(require_perfil("admin"))


# ── Schemas ────────────────────────────────────────────────────
class EmpresaCreate(BaseModel):
    nome: str
    cnpj: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    plano: str = "basico"
    observacao: Optional[str] = None


class EmpresaUpdate(BaseModel):
    nome: Optional[str] = None
    cnpj: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    plano: Optional[str] = None
    ativo: Optional[bool] = None
    observacao: Optional[str] = None


class EmpresaOut(BaseModel):
    id: UUID
    nome: str
    cnpj: Optional[str]
    telefone: Optional[str]
    email: Optional[str]
    cidade: Optional[str]
    estado: Optional[str]
    plano: str
    ativo: bool
    api_key: Optional[str]
    observacao: Optional[str]
    criado_em: datetime

    class Config:
        from_attributes = True


# ── Endpoints ──────────────────────────────────────────────────
@router.get("", response_model=list[EmpresaOut], summary="Listar empresas")
async def listar_empresas(
    ativo: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = AdminOnly,
):
    """Lista todas as empresas cadastradas no sistema."""
    q = select(Empresa).order_by(Empresa.criado_em.desc())
    if ativo is not None:
        q = q.where(Empresa.ativo == ativo)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("", response_model=EmpresaOut, status_code=status.HTTP_201_CREATED, summary="Cadastrar empresa")
async def criar_empresa(
    body: EmpresaCreate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = AdminOnly,
):
    """Cadastra uma nova empresa e gera a API key inicial."""
    empresa = Empresa(
        nome=body.nome,
        cnpj=body.cnpj,
        telefone=body.telefone,
        email=body.email,
        cidade=body.cidade,
        estado=body.estado,
        plano=body.plano,
        observacao=body.observacao,
        api_key=secrets.token_hex(24),
    )
    db.add(empresa)
    await db.flush()
    return empresa


@router.get("/{empresa_id}", response_model=EmpresaOut, summary="Detalhar empresa")
async def detalhar_empresa(
    empresa_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = AdminOnly,
):
    empresa = await db.get(Empresa, empresa_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return empresa


@router.put("/{empresa_id}", response_model=EmpresaOut, summary="Atualizar empresa")
async def atualizar_empresa(
    empresa_id: UUID,
    body: EmpresaUpdate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = AdminOnly,
):
    empresa = await db.get(Empresa, empresa_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(empresa, field, value)
    empresa.atualizado_em = datetime.now(timezone.utc)
    await db.flush()
    return empresa


@router.delete("/{empresa_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Desativar empresa")
async def desativar_empresa(
    empresa_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = AdminOnly,
):
    """Desativa a empresa (soft delete — dados preservados)."""
    empresa = await db.get(Empresa, empresa_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    empresa.ativo = False
    empresa.atualizado_em = datetime.now(timezone.utc)
    await db.flush()


@router.post("/{empresa_id}/gerar-api-key", response_model=EmpresaOut, summary="Gerar nova API key")
async def gerar_api_key(
    empresa_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = AdminOnly,
):
    """Gera uma nova API key para a empresa (invalida a anterior)."""
    empresa = await db.get(Empresa, empresa_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    empresa.api_key = secrets.token_hex(24)
    empresa.atualizado_em = datetime.now(timezone.utc)
    await db.flush()
    return empresa
