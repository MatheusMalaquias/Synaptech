# ERP FLV — Guia de Início Rápido

## 1. Configurar variáveis de ambiente

```bash
cd /Users/matheusmalaquias/Downloads/SmartMind/erp
cp .env.example .env
```

Edite o `.env` e preencha obrigatoriamente:
```bash
# Gere uma chave segura:
python3 -c "import secrets; print(secrets.token_hex(32))"
```

```env
JWT_SECRET_KEY=<chave_gerada_acima>
POSTGRES_PASSWORD=escolha_uma_senha
REDIS_PASSWORD=escolha_outra_senha
N8N_WEBHOOK_SECRET=mesmo_secret_do_n8n   # use em X-N8N-Secret no workflow
```

---

## 2. Subir todos os serviços

```bash
docker-compose up -d
```

Aguarde ~30 segundos e verifique:
```bash
docker-compose ps        # todos devem estar "healthy" ou "Up"
docker-compose logs backend --tail=20
```

---

## 3. Rodar a migration do banco

```bash
docker-compose exec backend alembic upgrade head
```

---

## 4. Criar o primeiro usuário admin

```bash
docker-compose exec backend python3 - <<'EOF'
import asyncio
from app.core.database import AsyncSessionLocal
from app.core.security import hash_senha
from app.models.usuario import Usuario
from app.models.base import PerfilUsuario

async def criar_admin():
    async with AsyncSessionLocal() as db:
        admin = Usuario(
            nome="Administrador",
            email="admin@loja.com",
            senha_hash=hash_senha("admin123"),
            perfil=PerfilUsuario.admin,
        )
        db.add(admin)
        await db.commit()
        print(f"Admin criado! ID: {admin.id}")

asyncio.run(criar_admin())
EOF
```

---

## 5. Testar a API

Acesse: **http://localhost/docs** (Swagger UI)

Ou via curl:
```bash
# Login
curl -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@loja.com", "senha": "admin123"}'

# Salve o access_token retornado:
TOKEN="eyJ..."

# Listar produtos
curl http://localhost/api/v1/produtos \
  -H "Authorization: Bearer $TOKEN"
```

---

## 6. Configurar o workflow n8n

1. Acesse: **http://localhost:5678** (n8n)
   - Usuário: `admin` | Senha: valor de `N8N_PASSWORD` no `.env`

2. Importe o arquivo: `erp/n8n_workflow_com_erp.json`
   - Menu → Workflows → Import from File

3. Configure a variável de ambiente no n8n:
   - Settings → Environment Variables → `N8N_WEBHOOK_SECRET` = mesmo valor do `.env`

4. O nó **"Registrar no ERP"** já está configurado para chamar:
   ```
   POST http://backend:8000/api/v1/n8n/registrar-venda
   Header: X-N8N-Secret: {{ $env.N8N_WEBHOOK_SECRET }}
   ```

---

## 7. Fluxo do workflow n8n

```
Google Sheets "Notas"     → forma de pagamento + valor bruto
Google Sheets "Produtos"  → catálogo com preços
        ↓
Code JS: sorteia produto candidato (preço ≤ valor bruto)
        ↓
Loop por venda:
  Final → Registrar no ERP → Log Resultado → (próxima venda)
        ↓
ERP cria venda + item + pagamento automaticamente
```

---

## 8. Endpoints principais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/auth/login` | Login |
| GET  | `/api/v1/produtos` | Listar produtos |
| POST | `/api/v1/produtos` | Criar produto |
| GET  | `/api/v1/estoque/{produto_id}` | Saldo de estoque |
| POST | `/api/v1/caixa/abrir` | Abrir turno de caixa |
| POST | `/api/v1/vendas` | Iniciar venda |
| POST | `/api/v1/vendas/{id}/item` | Adicionar item |
| POST | `/api/v1/vendas/{id}/finalizar` | Finalizar com pagamento |
| POST | `/api/v1/n8n/registrar-venda` | **Endpoint n8n** |
| GET  | `/api/v1/webhooks` | Listar webhooks |

Documentação completa: **http://localhost/docs**

---

## Serviços disponíveis

| Serviço | URL | Usuário |
|---------|-----|---------|
| API (Swagger) | http://localhost/docs | — |
| n8n | http://localhost:5678 | admin / N8N_PASSWORD |
| MinIO Console | http://localhost:9001 | MINIO_ACCESS_KEY |
| PostgreSQL | localhost:5432 | POSTGRES_USER |
