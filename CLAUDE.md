# ERP Próprio — Contexto do Projeto para Claude Code

## O que é este projeto

Substituição gradual do ERP **Fantastsoft FantastPDV v10.2** por um sistema próprio.
A empresa é um **FLV (Frutas, Legumes e Verduras)** que opera com PDV físico, impressora térmica Epson, NFC-e, e múltiplas formas de pagamento incluindo PIX dinâmico.

## Stack definida

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.12 + FastAPI |
| Banco de dados | PostgreSQL 16 |
| Cache / Sessões | Redis 7 |
| Frontend | React 18 + TypeScript + Tailwind CSS |
| Automação | n8n (self-hosted) |
| Armazenamento de arquivos | MinIO (S3-compatible) |
| Containerização | Docker + Docker Compose |
| Reverse proxy | Nginx |

## Fases do projeto

```
Fase 1 → Automação de lançamentos via n8n          (meses 0-3)
Fase 2 → Controle de estoque próprio               (meses 3-5)
Fase 3 → PDV próprio em paralelo à Fantastsoft     (meses 5-8)
Fase 4 → Substituição completa da Fantastsoft      (meses 8-10)
Fase 5 → Emissão fiscal NFC-e própria              (meses 10-14)
```

## Fase atual

**FASE 1** — Construindo a base: modelos de banco, APIs core, autenticação e webhook para n8n.

## Regras absolutas para este projeto

- **Nunca** salvar senhas em texto puro — sempre bcrypt
- **Nunca** expor credenciais em logs
- **Nunca** fazer hard-code de secrets — sempre `.env`
- **Sempre** usar UUID como PK em tabelas de domínio (exceto `produtos` e `categorias` que usam SERIAL por compatibilidade com legado)
- **Sempre** registrar na tabela `auditoria_log` qualquer INSERT/UPDATE/DELETE em tabelas críticas
- **Sempre** usar Alembic para migrations — nunca alterar banco manualmente
- **Sempre** escrever testes para toda lógica de negócio em `tests/`
- **Sempre** documentar endpoints com docstrings FastAPI (aparece no /docs automático)
- Estoque pode ser negativo (regra de negócio: o sistema não bloqueia venda sem estoque)
- Quantidade de produtos KG usa `NUMERIC(12,3)` — três casas decimais
- Moeda sempre em `NUMERIC(10,2)` — duas casas decimais, sem float

## Estrutura de pastas

```
erp/
├── CLAUDE.md                    ← este arquivo
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── routes/
│   │   │       │   ├── auth.py
│   │   │       │   ├── produtos.py
│   │   │       │   ├── estoque.py
│   │   │       │   ├── vendas.py
│   │   │       │   ├── caixa.py
│   │   │       │   ├── pagamentos.py
│   │   │       │   ├── clientes.py
│   │   │       │   ├── relatorios.py
│   │   │       │   └── webhooks.py
│   │   │       └── dependencies.py
│   │   ├── core/
│   │   │   ├── config.py        ← Settings via pydantic-settings
│   │   │   ├── security.py      ← JWT, bcrypt
│   │   │   ├── database.py      ← SQLAlchemy async engine
│   │   │   └── redis.py
│   │   ├── models/              ← SQLAlchemy ORM models
│   │   │   ├── usuario.py
│   │   │   ├── produto.py
│   │   │   ├── estoque.py
│   │   │   ├── venda.py
│   │   │   ├── caixa.py
│   │   │   ├── cliente.py
│   │   │   └── auditoria.py
│   │   ├── schemas/             ← Pydantic v2 schemas
│   │   ├── services/            ← Regras de negócio
│   │   ├── repositories/        ← Acesso a dados (repository pattern)
│   │   └── integrations/
│   │       ├── n8n/
│   │       ├── sefaz/           ← NFC-e (fase 5)
│   │       └── pix/
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_produtos.py
│   │   ├── test_vendas.py
│   │   └── test_estoque.py
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── PDV/
    │   │   ├── Produtos/
    │   │   ├── Estoque/
    │   │   ├── Vendas/
    │   │   ├── Caixa/
    │   │   └── Relatorios/
    │   ├── components/
    │   ├── hooks/
    │   ├── services/            ← chamadas à API
    │   ├── store/               ← Zustand
    │   └── types/
    └── package.json
```

## Documentos de referência nesta pasta

| Arquivo | Conteúdo |
|---------|----------|
| `CLAUDE.md` | Este arquivo — leia primeiro |
| `spec/01-analise-sistema-atual.md` | Análise detalhada do Fantastsoft |
| `spec/02-regras-de-negocio.md` | Todas as regras de negócio mapeadas |
| `spec/03-banco-de-dados.md` | Schema completo do PostgreSQL |
| `spec/04-api-endpoints.md` | Todos os endpoints da API |
| `spec/05-integracao-n8n.md` | Fluxos e payloads do n8n |
| `spec/06-plano-migracao.md` | Plano de migração da Fantastsoft |
| `spec/07-seguranca.md` | Regras de segurança e autenticação |
