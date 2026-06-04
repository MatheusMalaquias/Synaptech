# 04 — API Endpoints

## Padrões gerais

- Base URL: `/api/v1`
- Autenticação: `Authorization: Bearer <jwt_token>` em todos os endpoints (exceto `/auth/login`)
- Paginação: `?page=1&limit=50` nos endpoints de listagem
- Filtros: query params específicos por endpoint
- Resposta de erro padrão:
  ```json
  {"detail": "mensagem de erro", "code": "CODIGO_ERRO"}
  ```
- Timestamps sempre em ISO 8601 UTC: `2026-06-02T18:41:00Z`

---

## AUTH

### POST /auth/login
```json
// Request
{"email": "operador@loja.com", "senha": "senha123"}

// Response 200
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600,
  "usuario": {
    "id": "uuid",
    "nome": "João",
    "perfil": "caixa"
  }
}
```

### POST /auth/refresh
```json
// Request
{"refresh_token": "eyJ..."}

// Response 200
{"access_token": "eyJ...", "expires_in": 3600}
```

### POST /auth/logout
```json
// Response 200
{"message": "Sessão encerrada"}
```

---

## PRODUTOS

### GET /produtos
Query params: `?busca=alho&unidade=KG&ativo=true&page=1&limit=50`
```json
// Response 200
{
  "items": [
    {
      "id": 77,
      "codigo_barras": "7891234567890",
      "descricao": "ALHO",
      "unidade": "KG",
      "preco_venda": 29.99,
      "tributado": true,
      "perc_icms": 18.00,
      "estoque": 405.000,
      "ativo": true
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 50
}
```

### GET /produtos/{id}
### GET /produtos/barcode/{codigo}

### POST /produtos
```json
// Request (perfil: gerente ou admin)
{
  "codigo_barras": "7891234567890",
  "descricao": "ALHO",
  "unidade": "KG",
  "preco_venda": 29.99,
  "tributado": true,
  "perc_icms": 18.00,
  "estoque_inicial": 0
}
```

### PUT /produtos/{id}
### DELETE /produtos/{id} → soft delete (ativo = false)

---

## ESTOQUE

### GET /estoque
Query params: `?produto_id=77&abaixo_minimo=true`

### GET /estoque/{produto_id}
```json
// Response 200
{
  "produto_id": 77,
  "descricao": "ALHO",
  "unidade": "KG",
  "quantidade": 405.000,
  "estoque_minimo": 10.000,
  "abaixo_minimo": false
}
```

### POST /estoque/movimentacao
```json
// Request (entrada de estoque)
{
  "produto_id": 77,
  "tipo": "entrada",
  "quantidade": 50.000,
  "motivo": "Compra fornecedor",
  "referencia_id": null
}
```

### GET /estoque/movimentacoes
Query params: `?produto_id=77&data_inicio=2026-06-01&data_fim=2026-06-30`

---

## CAIXA

### GET /caixa/sessao-atual
```json
// Response 200
{
  "id": "uuid",
  "caixa": {"id": "uuid", "nome": "Caixa 01"},
  "usuario": {"id": "uuid", "nome": "João"},
  "status": "aberta",
  "valor_abertura": 200.00,
  "abertura_em": "2026-06-02T08:00:00Z",
  "total_vendas": 1250.50,
  "total_por_forma": {
    "dinheiro": 450.00,
    "pix": 600.00,
    "debito": 200.50
  }
}
```

### POST /caixa/abrir
```json
// Request
{"caixa_id": "uuid", "valor_abertura": 200.00}
```

### POST /caixa/fechar
```json
// Request
{"valor_fechamento": 650.00, "observacao": ""}
```

### POST /caixa/sangria
```json
// Request
{"valor": 500.00, "motivo": "Depósito bancário"}
```

### POST /caixa/suprimento
```json
// Request
{"valor": 100.00, "motivo": "Reposição de troco"}
```

---

## VENDAS

### POST /vendas
```json
// Request — inicia uma nova venda
{}

// Response 201
{
  "id": "uuid",
  "numero": 1234,
  "serie": "01",
  "status": "aberta",
  "itens": [],
  "total_final": 0.00
}
```

### POST /vendas/{id}/item
```json
// Request
{
  "produto_id": 77,
  "quantidade": 2.750
}

// Response 200
{
  "id": "uuid",
  "sequencia": 1,
  "produto_id": 77,
  "descricao": "ALHO",
  "unidade": "KG",
  "quantidade": 2.750,
  "preco_unitario": 29.99,
  "subtotal": 82.47
}
```

### PUT /vendas/{id}/item/{item_id}
```json
// Request (alterar quantidade ou preço)
{"quantidade": 3.000}
```

### DELETE /vendas/{id}/item/{item_id}
### GET /vendas/{id}
### GET /vendas — Query: `?data_inicio&data_fim&status&usuario_id&page&limit`

### POST /vendas/{id}/desconto
```json
{"tipo": "nota", "valor": 5.00}       // desconto fixo
{"tipo": "nota", "percentual": 10.0}  // desconto percentual
```

### POST /vendas/{id}/finalizar
```json
// Request
{
  "pagamentos": [
    {"forma": "pix", "valor": 82.47}
  ]
}

// Response 200
{
  "id": "uuid",
  "numero": 1234,
  "total_final": 82.47,
  "nfce_status": "emitida",
  "nfce_chave": "...",
  "nfce_qrcode": "...",
  "troco": 0.00
}
```

### POST /vendas/{id}/cancelar
```json
// Request
{"motivo": "Solicitação do cliente"}
```

### GET /vendas/{id}/nfce/xml
### GET /vendas/{id}/nfce/danfe → PDF para reimprimir

---

## CLIENTES

### GET /clientes
Query: `?busca=joao&cpf=12345678901`

### POST /clientes
```json
{
  "nome": "João da Silva",
  "cpf_cnpj": "123.456.789-01",
  "telefone": "(11) 99999-9999"
}
```

### GET /clientes/{id}
### PUT /clientes/{id}
### GET /clientes/{id}/caderneta — histórico do fiado
### POST /clientes/{id}/caderneta/receber
```json
{"valor": 50.00, "forma_pagamento": "dinheiro"}
```

---

## RELATÓRIOS

### GET /relatorios/vendas-dia
Query: `?data=2026-06-02`
```json
{
  "data": "2026-06-02",
  "total_vendas": 25,
  "total_itens": 78,
  "total_valor": 1850.45,
  "por_forma_pagamento": {...},
  "por_hora": [...]
}
```

### GET /relatorios/fechamento-caixa
Query: `?sessao_id=uuid`

### GET /relatorios/produtos-mais-vendidos
Query: `?data_inicio&data_fim&limit=20`

### GET /relatorios/estoque-critico
```json
// Produtos abaixo do estoque mínimo ou com estoque negativo
```

---

## WEBHOOKS (integração n8n)

### GET /webhooks
### POST /webhooks
```json
{
  "nome": "n8n Vendas",
  "url": "https://n8n.empresa.com/webhook/vendas",
  "eventos": ["venda_finalizada", "venda_cancelada", "estoque_alterado"],
  "secret": "meu_secret_hmac"
}
```

### DELETE /webhooks/{id}

### POST /webhooks/test/{id}
— Dispara um evento de teste para validar a configuração
