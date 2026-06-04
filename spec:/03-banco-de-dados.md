# 03 — Banco de Dados (PostgreSQL)

## Convenções

- UUIDs para tabelas de domínio (vendas, usuários, clientes, movimentações)
- SERIAL para tabelas de cadastro estável (produtos, categorias) — compatibilidade com legado
- Timestamps sempre em UTC, tipo `TIMESTAMPTZ`
- Soft delete via campo `ativo BOOLEAN` — nunca DELETE físico em tabelas de domínio
- `NUMERIC(10,2)` para moeda — nunca FLOAT
- `NUMERIC(12,3)` para quantidades em KG — três casas decimais
- Schema único: `public` (pode ser separado por `erp` futuramente)

---

## DDL Completo

```sql
-- ============================================================
-- EXTENSÕES
-- ============================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- busca textual eficiente

-- ============================================================
-- ENUMS
-- ============================================================
CREATE TYPE unidade_enum AS ENUM ('KG', 'UN', 'L', 'CX', 'PC', 'DZ');
CREATE TYPE perfil_usuario AS ENUM ('admin', 'gerente', 'caixa');
CREATE TYPE status_venda AS ENUM ('aberta', 'finalizada', 'cancelada');
CREATE TYPE status_nfce AS ENUM ('pendente', 'emitida', 'rejeitada', 'cancelada');
CREATE TYPE forma_pagamento AS ENUM (
    'dinheiro', 'credito', 'debito', 'pix',
    'cheque', 'voucher', 'troca', 'caderneta'
);
CREATE TYPE status_pagamento AS ENUM ('pendente', 'confirmado', 'rejeitado', 'estornado');
CREATE TYPE tipo_movimentacao AS ENUM ('entrada', 'saida', 'ajuste_positivo', 'ajuste_negativo', 'cancelamento');
CREATE TYPE status_sessao_caixa AS ENUM ('aberta', 'fechada');

-- ============================================================
-- USUÁRIOS
-- ============================================================
CREATE TABLE usuarios (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome            VARCHAR(100) NOT NULL,
    email           VARCHAR(150) NOT NULL UNIQUE,
    senha_hash      VARCHAR(255) NOT NULL,
    perfil          perfil_usuario NOT NULL DEFAULT 'caixa',
    ativo           BOOLEAN NOT NULL DEFAULT true,
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- CATEGORIAS
-- ============================================================
CREATE TABLE categorias (
    id              SERIAL PRIMARY KEY,
    nome            VARCHAR(100) NOT NULL UNIQUE,
    ativo           BOOLEAN NOT NULL DEFAULT true
);

-- ============================================================
-- PRODUTOS
-- ============================================================
CREATE TABLE produtos (
    id              SERIAL PRIMARY KEY,
    codigo_barras   VARCHAR(50) UNIQUE,
    descricao       VARCHAR(100) NOT NULL,
    descricao_adicional VARCHAR(200),
    unidade         unidade_enum NOT NULL DEFAULT 'UN',
    preco_venda     NUMERIC(10,2) NOT NULL CHECK (preco_venda >= 0),
    tributado       BOOLEAN NOT NULL DEFAULT true,
    perc_icms       NUMERIC(5,2) NOT NULL DEFAULT 18.00 CHECK (perc_icms >= 0 AND perc_icms <= 100),
    perc_reducao_bc NUMERIC(5,2) NOT NULL DEFAULT 0.00,
    categoria_id    INT REFERENCES categorias(id),
    ativo           BOOLEAN NOT NULL DEFAULT true,
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index para busca por nome (trigram para busca parcial)
CREATE INDEX idx_produtos_descricao ON produtos USING gin(descricao gin_trgm_ops);
CREATE INDEX idx_produtos_barcode ON produtos(codigo_barras) WHERE codigo_barras IS NOT NULL;

-- ============================================================
-- ESTOQUE
-- ============================================================
CREATE TABLE estoque (
    id              SERIAL PRIMARY KEY,
    produto_id      INT NOT NULL REFERENCES produtos(id),
    quantidade      NUMERIC(12,3) NOT NULL DEFAULT 0,
    -- Nota: pode ser negativo por regra de negócio
    estoque_minimo  NUMERIC(12,3) NOT NULL DEFAULT 0,
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(produto_id)
);

CREATE TABLE movimentacoes_estoque (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    produto_id      INT NOT NULL REFERENCES produtos(id),
    tipo            tipo_movimentacao NOT NULL,
    quantidade      NUMERIC(12,3) NOT NULL,  -- sempre positivo; tipo define sinal
    saldo_anterior  NUMERIC(12,3) NOT NULL,
    saldo_posterior NUMERIC(12,3) NOT NULL,
    motivo          VARCHAR(200),
    referencia_id   UUID,                    -- venda_id, compra_id, etc.
    referencia_tipo VARCHAR(50),             -- 'venda', 'compra', 'ajuste'
    usuario_id      UUID NOT NULL REFERENCES usuarios(id),
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_movest_produto ON movimentacoes_estoque(produto_id);
CREATE INDEX idx_movest_referencia ON movimentacoes_estoque(referencia_id) WHERE referencia_id IS NOT NULL;

-- ============================================================
-- CLIENTES
-- ============================================================
CREATE TABLE clientes (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome            VARCHAR(150) NOT NULL,
    cpf_cnpj        VARCHAR(20) UNIQUE,
    telefone        VARCHAR(20),
    email           VARCHAR(150),
    endereco        JSONB,              -- {logradouro, numero, bairro, cidade, uf, cep}
    credito_troca   NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (credito_troca >= 0),
    saldo_caderneta NUMERIC(10,2) NOT NULL DEFAULT 0.00,  -- positivo = deve para a loja
    ativo           BOOLEAN NOT NULL DEFAULT true,
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_clientes_cpf ON clientes(cpf_cnpj) WHERE cpf_cnpj IS NOT NULL;
CREATE INDEX idx_clientes_nome ON clientes USING gin(nome gin_trgm_ops);

-- ============================================================
-- CAIXAS (equipamentos físicos)
-- ============================================================
CREATE TABLE caixas (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome            VARCHAR(50) NOT NULL,
    serie_nfce      VARCHAR(5) NOT NULL DEFAULT '01',
    impressora      VARCHAR(100),
    ativo           BOOLEAN NOT NULL DEFAULT true
);

-- ============================================================
-- SESSÕES DE CAIXA (turno de trabalho)
-- ============================================================
CREATE TABLE sessoes_caixa (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    caixa_id        UUID NOT NULL REFERENCES caixas(id),
    usuario_id      UUID NOT NULL REFERENCES usuarios(id),
    status          status_sessao_caixa NOT NULL DEFAULT 'aberta',
    valor_abertura  NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    valor_fechamento NUMERIC(10,2),
    observacao      TEXT,
    abertura_em     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fechamento_em   TIMESTAMPTZ
);

-- ============================================================
-- VENDAS
-- ============================================================
CREATE TABLE vendas (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    numero          BIGINT NOT NULL,          -- sequencial por série
    serie           VARCHAR(5) NOT NULL DEFAULT '01',
    sessao_caixa_id UUID NOT NULL REFERENCES sessoes_caixa(id),
    usuario_id      UUID NOT NULL REFERENCES usuarios(id),
    cliente_id      UUID REFERENCES clientes(id),
    vendedor_id     UUID REFERENCES usuarios(id),
    status          status_venda NOT NULL DEFAULT 'aberta',
    subtotal        NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    desconto_nota   NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    acrescimo_nota  NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    total_final     NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    -- NFC-e
    nfce_status     status_nfce NOT NULL DEFAULT 'pendente',
    nfce_numero     INT,
    nfce_serie      VARCHAR(5),
    nfce_chave      VARCHAR(50),
    nfce_xml        TEXT,
    nfce_qrcode     TEXT,
    -- Datas
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finalizado_em   TIMESTAMPTZ,
    cancelado_em    TIMESTAMPTZ,
    motivo_cancelamento VARCHAR(200),
    -- Constraint: total_final = subtotal - desconto + acrescimo
    CONSTRAINT chk_total CHECK (total_final >= 0)
);

CREATE UNIQUE INDEX idx_vendas_numero_serie ON vendas(numero, serie);
CREATE INDEX idx_vendas_sessao ON vendas(sessao_caixa_id);
CREATE INDEX idx_vendas_criado ON vendas(criado_em);
CREATE INDEX idx_vendas_status ON vendas(status);

-- ============================================================
-- ITENS DA VENDA
-- ============================================================
CREATE TABLE itens_venda (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    venda_id        UUID NOT NULL REFERENCES vendas(id) ON DELETE RESTRICT,
    produto_id      INT NOT NULL REFERENCES produtos(id),
    sequencia       INT NOT NULL,
    quantidade      NUMERIC(12,3) NOT NULL CHECK (quantidade > 0),
    preco_unitario  NUMERIC(10,2) NOT NULL CHECK (preco_unitario >= 0),
    desconto_item   NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    subtotal        NUMERIC(10,2) NOT NULL,
    -- Snapshot fiscal no momento da venda (imutável após finalização)
    unidade         unidade_enum NOT NULL,
    tributado       BOOLEAN NOT NULL,
    perc_icms       NUMERIC(5,2) NOT NULL,
    UNIQUE(venda_id, sequencia)
);

-- ============================================================
-- PAGAMENTOS DA VENDA
-- ============================================================
CREATE TABLE pagamentos_venda (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    venda_id        UUID NOT NULL REFERENCES vendas(id) ON DELETE RESTRICT,
    forma           forma_pagamento NOT NULL,
    valor           NUMERIC(10,2) NOT NULL CHECK (valor > 0),
    status          status_pagamento NOT NULL DEFAULT 'pendente',
    referencia_externa VARCHAR(200),  -- ID da transação TEF, txid PIX, etc.
    dados_extras    JSONB,            -- metadados da transação
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    confirmado_em   TIMESTAMPTZ
);

CREATE INDEX idx_pagamentos_venda ON pagamentos_venda(venda_id);

-- ============================================================
-- WEBHOOKS (configuração de integrações n8n)
-- ============================================================
CREATE TABLE webhooks (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome            VARCHAR(100) NOT NULL,
    url             VARCHAR(500) NOT NULL,
    eventos         TEXT[] NOT NULL,   -- ['venda_finalizada', 'estoque_alterado', etc.]
    ativo           BOOLEAN NOT NULL DEFAULT true,
    secret          VARCHAR(200),      -- HMAC secret para validação
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- LOG DE AUDITORIA
-- ============================================================
CREATE TABLE auditoria_log (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id      UUID REFERENCES usuarios(id),
    acao            VARCHAR(100) NOT NULL,   -- 'create', 'update', 'delete', 'login', etc.
    tabela          VARCHAR(50),
    registro_id     VARCHAR(100),
    dados_antes     JSONB,
    dados_depois    JSONB,
    ip              INET,
    user_agent      VARCHAR(500),
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_auditoria_usuario ON auditoria_log(usuario_id);
CREATE INDEX idx_auditoria_tabela ON auditoria_log(tabela, registro_id);
CREATE INDEX idx_auditoria_criado ON auditoria_log(criado_em);

-- ============================================================
-- CONFIGURAÇÕES DO SISTEMA
-- ============================================================
CREATE TABLE configuracoes (
    chave           VARCHAR(100) PRIMARY KEY,
    valor           TEXT NOT NULL,
    descricao       VARCHAR(200),
    atualizado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Dados iniciais de configuração
INSERT INTO configuracoes (chave, valor, descricao) VALUES
    ('empresa_razao_social', '', 'Razão social da empresa'),
    ('empresa_cnpj', '', 'CNPJ da empresa'),
    ('empresa_ie', '', 'Inscrição Estadual'),
    ('empresa_regime_tributario', '1', '1=Simples Nacional, 2=Simples Excesso, 3=Normal'),
    ('nfce_serie_padrao', '01', 'Série padrão das NFC-e'),
    ('nfce_ambiente', '2', '1=Produção, 2=Homologação'),
    ('estoque_permite_negativo', 'true', 'Permite estoque negativo'),
    ('moeda', 'BRL', 'Moeda padrão');
```

---

## Triggers de auditoria (exemplo para vendas)

```sql
CREATE OR REPLACE FUNCTION audit_vendas()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO auditoria_log (acao, tabela, registro_id, dados_antes, dados_depois)
    VALUES (
        TG_OP,
        'vendas',
        COALESCE(NEW.id::text, OLD.id::text),
        CASE WHEN TG_OP = 'DELETE' OR TG_OP = 'UPDATE' THEN to_jsonb(OLD) ELSE NULL END,
        CASE WHEN TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN to_jsonb(NEW) ELSE NULL END
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_vendas
AFTER INSERT OR UPDATE OR DELETE ON vendas
FOR EACH ROW EXECUTE FUNCTION audit_vendas();
```

---

## Função para calcular total da venda (mantém consistência)

```sql
CREATE OR REPLACE FUNCTION recalcular_total_venda(p_venda_id UUID)
RETURNS VOID AS $$
DECLARE
    v_subtotal NUMERIC(10,2);
    v_desconto NUMERIC(10,2);
    v_acrescimo NUMERIC(10,2);
BEGIN
    SELECT COALESCE(SUM(subtotal), 0) INTO v_subtotal
    FROM itens_venda WHERE venda_id = p_venda_id;

    SELECT desconto_nota, acrescimo_nota INTO v_desconto, v_acrescimo
    FROM vendas WHERE id = p_venda_id;

    UPDATE vendas
    SET subtotal = v_subtotal,
        total_final = GREATEST(0, v_subtotal - v_desconto + v_acrescimo),
        atualizado_em = NOW()
    WHERE id = p_venda_id;
END;
$$ LANGUAGE plpgsql;
```
