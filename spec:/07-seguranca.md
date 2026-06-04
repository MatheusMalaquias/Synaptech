# 07 — Segurança e Autenticação

## Autenticação

- **JWT (JSON Web Tokens)** com dois tokens:
  - `access_token`: expira em 1 hora
  - `refresh_token`: expira em 7 dias, rotacionado a cada uso
- Algoritmo: **HS256** (pode migrar para RS256 com chave pública futuramente)
- Payload do JWT:
  ```json
  {
    "sub": "uuid_do_usuario",
    "nome": "João",
    "perfil": "caixa",
    "sessao_id": "uuid_da_sessao",
    "exp": 1748909260,
    "iat": 1748905660
  }
  ```

## Hashing de senhas

- **bcrypt** com fator de custo 12
- Nunca armazenar senha em texto puro
- Nunca logar senha — nem em erro

## Controle de acesso por perfil

| Recurso | caixa | gerente | admin |
|---------|-------|---------|-------|
| Vender | ✅ | ✅ | ✅ |
| Cancelar venda própria | ✅ | ✅ | ✅ |
| Cancelar venda de outro | ❌ | ✅ | ✅ |
| Dar desconto | ✅ | ✅ | ✅ |
| Alterar preço na venda | ❌ | ✅ | ✅ |
| Cadastrar produto | ❌ | ✅ | ✅ |
| Alterar produto | ❌ | ✅ | ✅ |
| Ajustar estoque | ❌ | ✅ | ✅ |
| Ver relatórios | ❌ | ✅ | ✅ |
| Gerenciar usuários | ❌ | ❌ | ✅ |
| Configurações fiscais | ❌ | ❌ | ✅ |
| Ver auditoria | ❌ | ✅ | ✅ |

## Variáveis de ambiente (.env.example)

```bash
# Banco de dados
DATABASE_URL=postgresql+asyncpg://erp:senha@localhost:5432/erp

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=gere_um_secret_de_64_chars_aqui
JWT_ALGORITHM=HS256
JWT_ACCESS_EXPIRE_MINUTES=60
JWT_REFRESH_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://erp.empresa.com

# N8N
N8N_WEBHOOK_SECRET=secret_compartilhado_com_n8n

# PIX (a definir conforme banco)
PIX_BASE_URL=
PIX_CLIENT_ID=
PIX_CLIENT_SECRET=
PIX_CERT_PATH=

# NFC-e (fase 5)
NFCE_AMBIENTE=2
NFCE_UF=35
NFCE_CERTIFICADO_PATH=
NFCE_CERTIFICADO_SENHA=

# MinIO (armazenamento)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=
MINIO_SECRET_KEY=
MINIO_BUCKET_NFCE=nfce-xml
```

## Rate limiting

- Login: máximo 10 tentativas por minuto por IP → bloqueio de 15 minutos
- API geral: 1000 requests/hora por token
- Endpoints de relatório: 10 requests/minuto (queries pesadas)

## CORS

- Lista branca explícita de origens (nunca `*` em produção)
- Configurar via variável `ALLOWED_ORIGINS`

## HTTPS

- Obrigatório em produção
- Nginx com certificado Let's Encrypt (Certbot)
- Redirect automático HTTP → HTTPS

## Logs de segurança

Registrar sempre em `auditoria_log`:
- Login bem-sucedido (com IP)
- Login com falha (com IP e email tentado)
- Logout
- Travar/destravar caixa
- Cancelamento de venda (com motivo)
- Ajuste manual de estoque
- Alteração de preço de produto
- Criação/alteração de usuário

## O que NUNCA fazer

```python
# ❌ NUNCA
print(f"Senha recebida: {senha}")
logger.info(f"JWT secret: {settings.JWT_SECRET_KEY}")
password = "hardcoded_senha"

# ✅ SEMPRE
logger.info(f"Login do usuário {usuario_id} do IP {ip}")
settings = Settings()  # carrega do .env via pydantic-settings
```
