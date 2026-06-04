"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-02 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _x(sql: str) -> None:
    """Executa um único comando SQL via Alembic."""
    op.execute(sql.strip())


def upgrade() -> None:
    # Extensões
    _x('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    _x('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')

    # ENUMs — cada DO separado para o asyncpg aceitar
    for ddl in [
        "DO $$ BEGIN CREATE TYPE unidade_enum AS ENUM ('KG','UN','L','CX','PC','DZ'); EXCEPTION WHEN duplicate_object THEN NULL; END $$",
        "DO $$ BEGIN CREATE TYPE perfil_usuario AS ENUM ('admin','gerente','caixa'); EXCEPTION WHEN duplicate_object THEN NULL; END $$",
        "DO $$ BEGIN CREATE TYPE status_venda AS ENUM ('aberta','finalizada','cancelada'); EXCEPTION WHEN duplicate_object THEN NULL; END $$",
        "DO $$ BEGIN CREATE TYPE status_nfce AS ENUM ('pendente','emitida','rejeitada','cancelada'); EXCEPTION WHEN duplicate_object THEN NULL; END $$",
        "DO $$ BEGIN CREATE TYPE forma_pagamento AS ENUM ('dinheiro','credito','debito','pix','cheque','voucher','troca','caderneta'); EXCEPTION WHEN duplicate_object THEN NULL; END $$",
        "DO $$ BEGIN CREATE TYPE status_pagamento AS ENUM ('pendente','confirmado','rejeitado','estornado'); EXCEPTION WHEN duplicate_object THEN NULL; END $$",
        "DO $$ BEGIN CREATE TYPE tipo_movimentacao AS ENUM ('entrada','saida','ajuste_positivo','ajuste_negativo','cancelamento'); EXCEPTION WHEN duplicate_object THEN NULL; END $$",
        "DO $$ BEGIN CREATE TYPE status_sessao_caixa AS ENUM ('aberta','fechada'); EXCEPTION WHEN duplicate_object THEN NULL; END $$",
        "DO $$ BEGIN CREATE TYPE webhook_status AS ENUM ('pendente','enviando','entregue','falhou'); EXCEPTION WHEN duplicate_object THEN NULL; END $$",
    ]:
        _x(ddl)

    # Tabelas
    _x("""CREATE TABLE IF NOT EXISTS usuarios (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        nome VARCHAR(100) NOT NULL,
        email VARCHAR(150) NOT NULL UNIQUE,
        senha_hash VARCHAR(255) NOT NULL,
        perfil perfil_usuario NOT NULL DEFAULT 'caixa',
        ativo BOOLEAN NOT NULL DEFAULT true,
        criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )""")

    _x("""CREATE TABLE IF NOT EXISTS categorias (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(100) NOT NULL UNIQUE,
        ativo BOOLEAN NOT NULL DEFAULT true
    )""")

    _x("""CREATE TABLE IF NOT EXISTS produtos (
        id SERIAL PRIMARY KEY,
        codigo_barras VARCHAR(50) UNIQUE,
        descricao VARCHAR(100) NOT NULL,
        descricao_adicional VARCHAR(200),
        unidade unidade_enum NOT NULL DEFAULT 'UN',
        preco_venda NUMERIC(10,2) NOT NULL CHECK (preco_venda >= 0),
        tributado BOOLEAN NOT NULL DEFAULT true,
        perc_icms NUMERIC(5,2) NOT NULL DEFAULT 18.00,
        perc_reducao_bc NUMERIC(5,2) NOT NULL DEFAULT 0.00,
        categoria_id INT REFERENCES categorias(id),
        ativo BOOLEAN NOT NULL DEFAULT true,
        criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )""")
    _x("CREATE INDEX IF NOT EXISTS idx_produtos_barcode ON produtos(codigo_barras) WHERE codigo_barras IS NOT NULL")
    _x("CREATE INDEX IF NOT EXISTS idx_produtos_descricao ON produtos USING gin(descricao gin_trgm_ops)")

    _x("""CREATE TABLE IF NOT EXISTS estoque (
        id SERIAL PRIMARY KEY,
        produto_id INT NOT NULL REFERENCES produtos(id) UNIQUE,
        quantidade NUMERIC(12,3) NOT NULL DEFAULT 0,
        estoque_minimo NUMERIC(12,3) NOT NULL DEFAULT 0,
        atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )""")

    _x("""CREATE TABLE IF NOT EXISTS movimentacoes_estoque (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        produto_id INT NOT NULL REFERENCES produtos(id),
        tipo tipo_movimentacao NOT NULL,
        quantidade NUMERIC(12,3) NOT NULL,
        saldo_anterior NUMERIC(12,3) NOT NULL,
        saldo_posterior NUMERIC(12,3) NOT NULL,
        motivo VARCHAR(200),
        referencia_id UUID,
        referencia_tipo VARCHAR(50),
        usuario_id UUID NOT NULL REFERENCES usuarios(id),
        criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )""")
    _x("CREATE INDEX IF NOT EXISTS idx_movest_produto ON movimentacoes_estoque(produto_id)")
    _x("CREATE INDEX IF NOT EXISTS idx_movest_referencia ON movimentacoes_estoque(referencia_id) WHERE referencia_id IS NOT NULL")

    _x("""CREATE TABLE IF NOT EXISTS clientes (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        nome VARCHAR(150) NOT NULL,
        cpf_cnpj VARCHAR(20) UNIQUE,
        telefone VARCHAR(20),
        email VARCHAR(150),
        endereco JSONB,
        credito_troca NUMERIC(10,2) NOT NULL DEFAULT 0.00,
        saldo_caderneta NUMERIC(10,2) NOT NULL DEFAULT 0.00,
        ativo BOOLEAN NOT NULL DEFAULT true,
        criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )""")
    _x("CREATE INDEX IF NOT EXISTS idx_clientes_cpf ON clientes(cpf_cnpj) WHERE cpf_cnpj IS NOT NULL")
    _x("CREATE INDEX IF NOT EXISTS idx_clientes_nome ON clientes USING gin(nome gin_trgm_ops)")

    _x("""CREATE TABLE IF NOT EXISTS caixas (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        nome VARCHAR(50) NOT NULL,
        serie_nfce VARCHAR(5) NOT NULL DEFAULT '01',
        impressora VARCHAR(100),
        ativo BOOLEAN NOT NULL DEFAULT true
    )""")

    _x("""CREATE TABLE IF NOT EXISTS sessoes_caixa (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        caixa_id UUID NOT NULL REFERENCES caixas(id),
        usuario_id UUID NOT NULL REFERENCES usuarios(id),
        status status_sessao_caixa NOT NULL DEFAULT 'aberta',
        valor_abertura NUMERIC(10,2) NOT NULL DEFAULT 0.00,
        valor_fechamento NUMERIC(10,2),
        observacao TEXT,
        abertura_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        fechamento_em TIMESTAMPTZ
    )""")

    _x("""CREATE TABLE IF NOT EXISTS vendas (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        numero BIGINT NOT NULL,
        serie VARCHAR(5) NOT NULL DEFAULT '01',
        sessao_caixa_id UUID NOT NULL REFERENCES sessoes_caixa(id),
        usuario_id UUID NOT NULL REFERENCES usuarios(id),
        cliente_id UUID REFERENCES clientes(id),
        vendedor_id UUID REFERENCES usuarios(id),
        status status_venda NOT NULL DEFAULT 'aberta',
        subtotal NUMERIC(10,2) NOT NULL DEFAULT 0.00,
        desconto_nota NUMERIC(10,2) NOT NULL DEFAULT 0.00,
        acrescimo_nota NUMERIC(10,2) NOT NULL DEFAULT 0.00,
        total_final NUMERIC(10,2) NOT NULL DEFAULT 0.00 CHECK (total_final >= 0),
        nfce_status status_nfce NOT NULL DEFAULT 'pendente',
        nfce_numero INT,
        nfce_serie VARCHAR(5),
        nfce_chave VARCHAR(50),
        nfce_xml TEXT,
        nfce_qrcode TEXT,
        criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        finalizado_em TIMESTAMPTZ,
        cancelado_em TIMESTAMPTZ,
        motivo_cancelamento VARCHAR(200),
        UNIQUE(numero, serie)
    )""")
    _x("CREATE INDEX IF NOT EXISTS idx_vendas_sessao ON vendas(sessao_caixa_id)")
    _x("CREATE INDEX IF NOT EXISTS idx_vendas_criado ON vendas(criado_em)")
    _x("CREATE INDEX IF NOT EXISTS idx_vendas_status ON vendas(status)")
    # Sequence para número de venda — evita race condition em inserções paralelas
    _x("CREATE SEQUENCE IF NOT EXISTS vendas_numero_seq START 1")

    _x("""CREATE TABLE IF NOT EXISTS itens_venda (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        venda_id UUID NOT NULL REFERENCES vendas(id),
        produto_id INT NOT NULL REFERENCES produtos(id),
        sequencia INT NOT NULL,
        quantidade NUMERIC(12,3) NOT NULL CHECK (quantidade > 0),
        preco_unitario NUMERIC(10,2) NOT NULL CHECK (preco_unitario >= 0),
        desconto_item NUMERIC(10,2) NOT NULL DEFAULT 0.00,
        subtotal NUMERIC(10,2) NOT NULL,
        unidade unidade_enum NOT NULL,
        tributado BOOLEAN NOT NULL,
        perc_icms NUMERIC(5,2) NOT NULL,
        UNIQUE(venda_id, sequencia)
    )""")

    _x("""CREATE TABLE IF NOT EXISTS pagamentos_venda (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        venda_id UUID NOT NULL REFERENCES vendas(id),
        forma forma_pagamento NOT NULL,
        valor NUMERIC(10,2) NOT NULL CHECK (valor > 0),
        status status_pagamento NOT NULL DEFAULT 'pendente',
        referencia_externa VARCHAR(200),
        dados_extras TEXT,
        criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        confirmado_em TIMESTAMPTZ
    )""")
    _x("CREATE INDEX IF NOT EXISTS idx_pagamentos_venda ON pagamentos_venda(venda_id)")

    _x("""CREATE TABLE IF NOT EXISTS webhooks (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        nome VARCHAR(100) NOT NULL,
        url VARCHAR(500) NOT NULL,
        eventos TEXT[] NOT NULL,
        ativo BOOLEAN NOT NULL DEFAULT true,
        secret VARCHAR(200),
        criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )""")

    _x("""CREATE TABLE IF NOT EXISTS webhook_entregas (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        webhook_id UUID NOT NULL REFERENCES webhooks(id),
        evento VARCHAR(100) NOT NULL,
        payload JSONB NOT NULL,
        status webhook_status NOT NULL DEFAULT 'pendente',
        tentativas INT NOT NULL DEFAULT 0,
        proxima_tentativa TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        ultimo_erro TEXT,
        entregue_em TIMESTAMPTZ,
        criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )""")
    _x("""CREATE INDEX IF NOT EXISTS idx_webhook_entregas_pendentes
        ON webhook_entregas(proxima_tentativa)
        WHERE status IN ('pendente','falhou') AND tentativas < 4""")

    _x("""CREATE TABLE IF NOT EXISTS auditoria_log (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        usuario_id UUID REFERENCES usuarios(id),
        acao VARCHAR(100) NOT NULL,
        tabela VARCHAR(50),
        registro_id VARCHAR(100),
        dados_antes JSONB,
        dados_depois JSONB,
        ip VARCHAR(45),
        user_agent VARCHAR(500),
        criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )""")
    _x("CREATE INDEX IF NOT EXISTS idx_auditoria_usuario ON auditoria_log(usuario_id)")
    _x("CREATE INDEX IF NOT EXISTS idx_auditoria_tabela  ON auditoria_log(tabela, registro_id)")
    _x("CREATE INDEX IF NOT EXISTS idx_auditoria_criado  ON auditoria_log(criado_em)")

    _x("""CREATE TABLE IF NOT EXISTS configuracoes (
        chave VARCHAR(100) PRIMARY KEY,
        valor TEXT NOT NULL,
        descricao VARCHAR(200),
        atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )""")

    for chave, valor, desc in [
        ("empresa_razao_social",    "",      "Razão social da empresa"),
        ("empresa_cnpj",            "",      "CNPJ da empresa"),
        ("empresa_ie",              "",      "Inscrição Estadual"),
        ("empresa_regime_tributario","1",    "1=Simples Nacional"),
        ("nfce_serie_padrao",       "01",    "Série padrão NFC-e"),
        ("nfce_ambiente",           "2",     "1=Produção, 2=Homologação"),
        ("estoque_permite_negativo","true",  "Permite estoque negativo"),
        ("moeda",                   "BRL",   "Moeda padrão"),
    ]:
        _x(f"INSERT INTO configuracoes (chave, valor, descricao) VALUES ('{chave}', '{valor}', '{desc}') ON CONFLICT (chave) DO NOTHING")

    _x("""CREATE OR REPLACE FUNCTION audit_vendas() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO auditoria_log (acao, tabela, registro_id, dados_antes, dados_depois)
    VALUES (TG_OP, 'vendas',
        COALESCE(NEW.id::text, OLD.id::text),
        CASE WHEN TG_OP IN ('DELETE','UPDATE') THEN to_jsonb(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT','UPDATE') THEN to_jsonb(NEW) ELSE NULL END);
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql""")

    _x("DROP TRIGGER IF EXISTS trg_audit_vendas ON vendas")
    _x("""CREATE TRIGGER trg_audit_vendas
        AFTER INSERT OR UPDATE OR DELETE ON vendas
        FOR EACH ROW EXECUTE FUNCTION audit_vendas()""")


def downgrade() -> None:
    for sql in [
        "DROP TRIGGER IF EXISTS trg_audit_vendas ON vendas",
        "DROP FUNCTION IF EXISTS audit_vendas()",
        "DROP TABLE IF EXISTS configuracoes, auditoria_log, webhook_entregas, webhooks, pagamentos_venda, itens_venda, vendas, sessoes_caixa, caixas, clientes, movimentacoes_estoque, estoque, produtos, categorias, usuarios CASCADE",
        "DROP TYPE IF EXISTS webhook_status, status_sessao_caixa, tipo_movimentacao, status_pagamento, forma_pagamento, status_nfce, status_venda, perfil_usuario, unidade_enum CASCADE",
    ]:
        _x(sql)
