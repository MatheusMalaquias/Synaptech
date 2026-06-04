#!/bin/bash
# ============================================================
# ERP FLV — Script de inicialização
# Uso: ./start.sh [start|stop|restart|status|logs|test]
# ============================================================

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

banner() {
  echo -e "${BLUE}${BOLD}"
  echo "  ╔══════════════════════════════════╗"
  echo "  ║        ERP FLV — Sistema         ║"
  echo "  ╚══════════════════════════════════╝"
  echo -e "${NC}"
}

ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
warn() { echo -e "  ${YELLOW}⚠${NC}  $1"; }
err()  { echo -e "  ${RED}✗${NC} $1"; }
info() { echo -e "  ${BLUE}→${NC} $1"; }

# ── Verificação do .env ───────────────────────────────────────
check_env() {
  if [ ! -f ".env" ]; then
    warn ".env não encontrado. Criando a partir do exemplo..."
    cp .env.example .env
    echo ""
    err "AÇÃO NECESSÁRIA: Edite o arquivo .env antes de continuar."
    err "Especialmente: JWT_SECRET_KEY, POSTGRES_PASSWORD, REDIS_PASSWORD"
    echo ""
    info "Gerando JWT_SECRET_KEY automático para desenvolvimento..."
    SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)
    # Substitui o placeholder pelo secret gerado
    if [[ "$OSTYPE" == "darwin"* ]]; then
      sed -i '' "s/gere_um_secret_de_64_chars_aqui_nunca_use_este_valor/$SECRET/" .env
    else
      sed -i "s/gere_um_secret_de_64_chars_aqui_nunca_use_este_valor/$SECRET/" .env
    fi
    ok "JWT_SECRET_KEY gerado automaticamente"
    warn "Altere as senhas do banco em .env antes de usar em produção!"
    echo ""
  fi
}

# ── Aguardar serviço ficar saudável ──────────────────────────
wait_for() {
  local name="$1"
  local url="$2"
  local max=30
  local i=0
  printf "  Aguardando %-20s" "$name..."
  while ! curl -sf "$url" > /dev/null 2>&1; do
    sleep 2
    i=$((i+1))
    printf "."
    if [ $i -ge $max ]; then
      echo ""
      err "$name não respondeu em tempo hábil"
      return 1
    fi
  done
  echo ""
  ok "$name pronto"
}

# ── Criar usuário admin padrão ────────────────────────────────
criar_admin() {
  info "Verificando usuário admin..."
  docker-compose exec -T backend python3 - <<'PYEOF' 2>/dev/null || true
import asyncio, sys
sys.path.insert(0, '/app')

async def main():
    from app.core.database import AsyncSessionLocal
    from app.core.security import hash_senha
    from app.models.usuario import Usuario
    from app.models.base import PerfilUsuario
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Usuario).where(Usuario.email == "admin@loja.com"))
        if result.scalar_one_or_none():
            print("EXISTE")
            return
        admin = Usuario(
            nome="Administrador",
            email="admin@loja.com",
            senha_hash=hash_senha("admin123"),
            perfil=PerfilUsuario.admin,
        )
        db.add(admin)
        await db.commit()
        print("CRIADO")

asyncio.run(main())
PYEOF
}

# ── Abrir no browser ──────────────────────────────────────────
abrir_browser() {
  sleep 2
  # URL direta no backend (evita problema de HTTPS-Only do Safari)
  local URL="http://localhost:8000"
  if [[ "$OSTYPE" == "darwin"* ]]; then
    # Tenta Chrome primeiro, depois Firefox, depois navegador padrão
    if open -a "Google Chrome" "$URL" 2>/dev/null; then
      :
    elif open -a "Firefox" "$URL" 2>/dev/null; then
      :
    elif open -a "Brave Browser" "$URL" 2>/dev/null; then
      :
    else
      open "$URL" 2>/dev/null || true
    fi
  elif command -v xdg-open &> /dev/null; then
    xdg-open "$URL" 2>/dev/null || true
  fi
}

# ══════════════════════════════════════════════════════════════
# COMANDOS
# ══════════════════════════════════════════════════════════════

check_docker() {
  if ! docker info > /dev/null 2>&1; then
    echo ""
    err "Docker não está rodando!"
    echo ""
    echo -e "  ${YELLOW}Por favor:${NC}"
    echo -e "  1. Abra o ${BOLD}Docker Desktop${NC} (procure no Launchpad ou Spotlight)"
    echo -e "  2. Aguarde o ícone da baleia aparecer na barra de menu"
    echo -e "  3. Execute este script novamente"
    echo ""

    # Tenta abrir o Docker Desktop automaticamente no macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
      info "Tentando abrir o Docker Desktop automaticamente..."
      open -a Docker 2>/dev/null && echo -e "  ${YELLOW}Aguarde o Docker iniciar (~30s) e execute novamente${NC}" || true
    fi
    echo ""
    exit 1
  fi
}

cmd_start() {
  banner
  check_docker
  check_env

  info "Iniciando serviços Docker..."
  docker-compose up -d

  echo ""
  info "Aguardando serviços ficarem prontos..."
  wait_for "PostgreSQL" "http://localhost:5432" 2>/dev/null || \
    docker-compose exec -T postgres pg_isready -U erp > /dev/null 2>&1 && ok "PostgreSQL pronto" || true
  wait_for "Backend API" "http://localhost:8000/health"
  wait_for "n8n"         "http://localhost:5678/healthz"

  echo ""
  info "Rodando migrations do banco..."
  docker-compose exec -T backend alembic upgrade head 2>&1 | grep -E "(Running|OK|ERROR)" || true
  ok "Migrations aplicadas"

  echo ""
  RESULT=$(criar_admin)
  if echo "$RESULT" | grep -q "CRIADO"; then
    ok "Usuário admin criado: admin@loja.com / admin123"
  else
    ok "Usuário admin já existe"
  fi

  echo ""
  echo -e "${GREEN}${BOLD}  ══════════════════════════════════════${NC}"
  echo -e "${GREEN}${BOLD}  Sistema iniciado com sucesso! 🚀${NC}"
  echo -e "${GREEN}${BOLD}  ══════════════════════════════════════${NC}"
  echo ""
  echo -e "  ${BOLD}🖥️  PDV (Sistema):${NC}  http://localhost:8000"
  echo -e "  ${BOLD}📋 API / Swagger:${NC}  http://localhost:8000/docs"
  echo -e "  ${BOLD}⚙️  n8n:${NC}           http://localhost:5678"
  echo -e "  ${BOLD}🗄️  MinIO:${NC}         http://localhost:9001"
  echo ""
  echo -e "  ${YELLOW}⚠️  Use Chrome ou Firefox (Safari bloqueia HTTP)${NC}"
  echo ""
  echo -e "  ${BOLD}Login padrão da API:${NC}"
  echo -e "    Email: admin@loja.com"
  echo -e "    Senha: admin123"
  echo ""
  echo -e "  ${YELLOW}Altere a senha após o primeiro acesso!${NC}"
  echo ""

  abrir_browser
}

cmd_stop() {
  banner
  info "Parando todos os serviços..."
  docker-compose down
  ok "Serviços parados"
}

cmd_restart() {
  cmd_stop
  echo ""
  cmd_start
}

cmd_status() {
  banner
  echo -e "  ${BOLD}Status dos serviços:${NC}"
  echo ""
  docker-compose ps
  echo ""

  # Testa cada serviço
  if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    ok "Backend API     → http://localhost/docs"
  else
    err "Backend API     → offline"
  fi

  if curl -sf http://localhost:5678/healthz > /dev/null 2>&1; then
    ok "n8n             → http://localhost:5678"
  else
    warn "n8n             → offline ou iniciando"
  fi

  if curl -sf http://localhost:9000/minio/health/live > /dev/null 2>&1; then
    ok "MinIO           → http://localhost:9001"
  else
    warn "MinIO           → offline ou iniciando"
  fi
}

cmd_logs() {
  SERVICE="${2:-backend}"
  info "Logs do serviço: $SERVICE (Ctrl+C para sair)"
  docker-compose logs -f "$SERVICE"
}

cmd_test() {
  banner
  info "Rodando testes..."
  cd backend
  JWT_SECRET_KEY="test_secret_key_that_is_long_enough_for_validation" \
    python -m pytest tests/ -v --tb=short 2>&1
}

cmd_help() {
  banner
  echo -e "  ${BOLD}Uso:${NC} ./start.sh [comando]"
  echo ""
  echo -e "  ${BOLD}Comandos disponíveis:${NC}"
  echo -e "    ${GREEN}start${NC}    — Inicia todos os serviços e abre o browser"
  echo -e "    ${GREEN}stop${NC}     — Para todos os serviços"
  echo -e "    ${GREEN}restart${NC}  — Reinicia todos os serviços"
  echo -e "    ${GREEN}status${NC}   — Mostra status de cada serviço"
  echo -e "    ${GREEN}logs${NC}     — Exibe logs (./start.sh logs [serviço])"
  echo -e "    ${GREEN}test${NC}     — Roda a suíte de testes"
  echo ""
  echo -e "  ${BOLD}Serviços:${NC} backend, postgres, redis, n8n, minio, nginx"
  echo ""
}

# ══════════════════════════════════════════════════════════════
COMMAND="${1:-start}"
case "$COMMAND" in
  start)   cmd_start ;;
  stop)    cmd_stop ;;
  restart) cmd_restart ;;
  status)  cmd_status ;;
  logs)    cmd_logs "$@" ;;
  test)    cmd_test ;;
  help|--help|-h) cmd_help ;;
  *)
    err "Comando desconhecido: $COMMAND"
    cmd_help
    exit 1
    ;;
esac
