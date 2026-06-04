#!/bin/bash
# ============================================================
# Script de instalação do ERP FLV no VPS Hostinger
# Execute UMA VEZ via terminal do Hostinger
# ============================================================
set -e

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'; BOLD='\033[1m'
ok()   { echo -e "${GREEN}✓${NC} $1"; }
info() { echo -e "${YELLOW}→${NC} $1"; }
err()  { echo -e "${RED}✗${NC} $1"; exit 1; }

echo -e "${BOLD}"
echo "  ╔══════════════════════════════════════╗"
echo "  ║     ERP FLV — Setup do Servidor      ║"
echo "  ╚══════════════════════════════════════╝"
echo -e "${NC}"

# ── 1. Instala dependências ───────────────────────────────────
info "Instalando dependências..."
apt-get update -qq
apt-get install -y -qq git curl python3 > /dev/null
ok "Dependências instaladas"

# ── 2. Clona o repositório ────────────────────────────────────
info "Clonando repositório..."
if [ -d "/opt/erp" ]; then
  info "Repositório já existe, atualizando..."
  cd /opt/erp && git pull origin main
else
  git clone https://github.com/MatheusMalaquias/erp-flv.git /opt/erp-repo
  # O código fica dentro da pasta erp/ no repositório
  mv /opt/erp-repo/erp /opt/erp
fi
cd /opt/erp
ok "Código clonado em /opt/erp"

# ── 3. Cria o arquivo .env ────────────────────────────────────
if [ ! -f "/opt/erp/.env" ]; then
  info "Criando arquivo de configuração .env..."
  cp /opt/erp/.env.example /opt/erp/.env

  # Gera secrets automáticos
  JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
  PG_PASS=$(python3 -c "import secrets; print(secrets.token_hex(16))")
  REDIS_PASS=$(python3 -c "import secrets; print(secrets.token_hex(16))")
  MINIO_KEY=$(python3 -c "import secrets; print(secrets.token_hex(16))")
  N8N_PASS=$(python3 -c "import secrets; print(secrets.token_hex(12))")
  WEBHOOK_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(24))")

  sed -i "s|JWT_SECRET_KEY=.*|JWT_SECRET_KEY=${JWT_SECRET}|" .env
  sed -i "s|POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${PG_PASS}|" .env
  sed -i "s|REDIS_PASSWORD=.*|REDIS_PASSWORD=${REDIS_PASS}|" .env
  sed -i "s|MINIO_SECRET_KEY=.*|MINIO_SECRET_KEY=${MINIO_KEY}|" .env
  sed -i "s|N8N_PASSWORD=.*|N8N_PASSWORD=${N8N_PASS}|" .env
  sed -i "s|N8N_WEBHOOK_SECRET=.*|N8N_WEBHOOK_SECRET=${WEBHOOK_SECRET}|" .env
  sed -i "s|DATABASE_URL=.*|DATABASE_URL=postgresql+asyncpg://erp:${PG_PASS}@postgres:5432/erp|" .env
  sed -i "s|REDIS_URL=.*|REDIS_URL=redis://:${REDIS_PASS}@redis:6379/0|" .env
  sed -i "s|VPS_IP=.*|VPS_IP=187.127.11.213|" .env
  echo "VPS_IP=187.127.11.213" >> .env

  ok ".env criado com secrets seguros"
else
  ok ".env já existe, mantendo configurações"
fi

# ── 4. Sobe os containers ─────────────────────────────────────
info "Iniciando serviços Docker..."
docker compose -f docker-compose.prod.yml up -d --build
ok "Containers iniciados"

# ── 5. Aguarda o banco ficar pronto ───────────────────────────
info "Aguardando banco de dados..."
sleep 15

# ── 6. Roda migrations ───────────────────────────────────────
info "Rodando migrations do banco..."
docker compose -f docker-compose.prod.yml exec -T backend alembic upgrade head
ok "Migrations aplicadas"

# ── 7. Cria usuário admin ─────────────────────────────────────
info "Criando usuário admin..."
docker compose -f docker-compose.prod.yml exec -T backend python3 - <<'PYEOF'
import asyncio, sys
sys.path.insert(0, '/app')
async def main():
    from app.core.database import AsyncSessionLocal
    from app.core.security import hash_senha
    from app.models.usuario import Usuario
    from app.models.base import PerfilUsuario
    from sqlalchemy import select
    async with AsyncSessionLocal() as db:
        r = await db.execute(select(Usuario).where(Usuario.email == "admin@loja.com"))
        if r.scalar_one_or_none():
            print("Admin já existe")
            return
        u = Usuario(nome="Administrador", email="admin@loja.com",
                    senha_hash=hash_senha("admin123"), perfil=PerfilUsuario.admin)
        db.add(u)
        await db.commit()
        print("Admin criado!")
asyncio.run(main())
PYEOF
ok "Usuário admin criado"

# ── 8. Gera chave SSH para GitHub Actions ─────────────────────
info "Gerando chave SSH para deploy automático..."
if [ ! -f "/root/.ssh/github_deploy" ]; then
  ssh-keygen -t ed25519 -C "github-actions-erp" -f /root/.ssh/github_deploy -N ""
  cat /root/.ssh/github_deploy.pub >> /root/.ssh/authorized_keys
  chmod 600 /root/.ssh/authorized_keys
fi

# ── Resultado final ───────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}══════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}  ✅ ERP instalado com sucesso!            ${NC}"
echo -e "${GREEN}${BOLD}══════════════════════════════════════════${NC}"
echo ""
echo -e "  ${BOLD}🌐 Sistema online:${NC}"
echo -e "     http://187.127.11.213:8000"
echo ""
echo -e "  ${BOLD}🔑 Login padrão:${NC}"
echo -e "     Email: admin@loja.com"
echo -e "     Senha: admin123"
echo ""
echo -e "  ${BOLD}⚙️  n8n:${NC} http://187.127.11.213:5678"
echo ""
echo -e "${YELLOW}${BOLD}  IMPORTANTE — Adicione esta chave no GitHub:${NC}"
echo -e "${YELLOW}  (Configurações → Secrets → VPS_SSH_KEY)${NC}"
echo ""
cat /root/.ssh/github_deploy
echo ""
echo -e "${YELLOW}  Também adicione como Secret: VPS_HOST = 187.127.11.213${NC}"
echo ""

# Mostra o webhook secret para o n8n
WEBHOOK_SECRET=$(grep N8N_WEBHOOK_SECRET /opt/erp/.env | cut -d= -f2)
echo -e "  ${BOLD}🔗 Header para o n8n (X-N8N-Secret):${NC}"
echo -e "  ${GREEN}${WEBHOOK_SECRET}${NC}"
echo ""
