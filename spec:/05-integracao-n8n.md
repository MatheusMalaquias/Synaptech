# 05 — Integração com n8n

## Arquitetura

```
[ERP Backend]
     ↓ evento ocorre
[Salva em fila de webhooks (DB)]
     ↓ worker async envia
[HTTP POST → n8n Webhook URL]
     ↓
[n8n processa]
     ↓
[Destinos: WhatsApp, Planilha, Dashboard, outro sistema]
```

**Por que salvar em fila antes de enviar?**
Garante que nenhum evento se perde mesmo que o n8n esteja offline. O worker tenta reenviar com backoff exponencial.

---

## Eventos disponíveis

| Evento | Quando dispara |
|--------|---------------|
| `venda_finalizada` | Venda fechada com pagamento confirmado |
| `venda_cancelada` | Venda cancelada após finalização |
| `item_cancelado` | Item removido de venda em andamento |
| `estoque_alterado` | Qualquer movimentação de estoque |
| `estoque_critico` | Produto fica abaixo do mínimo ou negativo |
| `caixa_aberto` | Sessão de caixa iniciada |
| `caixa_fechado` | Sessão de caixa encerrada |
| `pagamento_pix_confirmado` | Callback PIX recebido |

---

## Payloads

### venda_finalizada
```json
{
  "evento": "venda_finalizada",
  "timestamp": "2026-06-02T21:41:00Z",
  "venda": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "numero": 1234,
    "serie": "01",
    "operador": {"id": "uuid", "nome": "João"},
    "caixa": {"id": "uuid", "nome": "Caixa 01"},
    "cliente": null,
    "itens": [
      {
        "sequencia": 1,
        "produto_id": 77,
        "descricao": "ALHO",
        "unidade": "KG",
        "quantidade": 2.750,
        "preco_unitario": 29.99,
        "subtotal": 82.47
      }
    ],
    "pagamentos": [
      {
        "forma": "pix",
        "valor": 82.47,
        "status": "confirmado"
      }
    ],
    "subtotal": 82.47,
    "desconto": 0.00,
    "total_final": 82.47,
    "nfce_chave": "35260612345678000195650010000012341234567890",
    "finalizado_em": "2026-06-02T21:41:00Z"
  }
}
```

### estoque_critico
```json
{
  "evento": "estoque_critico",
  "timestamp": "2026-06-02T21:41:00Z",
  "produto": {
    "id": 91,
    "descricao": "AGRIÃO",
    "unidade": "UN",
    "quantidade_atual": -1.000,
    "estoque_minimo": 10.000
  },
  "tipo": "negativo"
}
```

### caixa_fechado
```json
{
  "evento": "caixa_fechado",
  "timestamp": "2026-06-02T22:00:00Z",
  "sessao": {
    "id": "uuid",
    "caixa": "Caixa 01",
    "operador": "João",
    "abertura_em": "2026-06-02T08:00:00Z",
    "fechamento_em": "2026-06-02T22:00:00Z",
    "valor_abertura": 200.00,
    "valor_fechamento": 650.00,
    "total_vendas": 45,
    "total_valor": 3250.75,
    "por_forma": {
      "dinheiro": 450.00,
      "pix": 1800.75,
      "debito": 800.00,
      "credito": 200.00
    }
  }
}
```

---

## Segurança dos webhooks

Cada requisição enviada pelo ERP inclui o header:
```
X-ERP-Signature: sha256=<hmac_hex>
X-ERP-Event: venda_finalizada
X-ERP-Delivery: <uuid_da_entrega>
```

O n8n deve validar o HMAC com o secret configurado:
```javascript
// Validação no n8n (Function node)
const crypto = require('crypto');
const secret = 'meu_secret_hmac';
const signature = $headers['x-erp-signature'];
const body = JSON.stringify($body);
const expected = 'sha256=' + crypto
  .createHmac('sha256', secret)
  .update(body)
  .digest('hex');

if (signature !== expected) {
  throw new Error('Assinatura inválida');
}
```

---

## Retry e tolerância a falhas

```python
# backend/app/integrations/n8n/webhook_worker.py
# Configuração de retry

RETRY_DELAYS = [30, 120, 600, 3600]  # segundos: 30s, 2min, 10min, 1h
MAX_TENTATIVAS = 4

# Status possíveis na fila:
# 'pendente' → 'enviando' → 'entregue'
#                         → 'falhou' (após MAX_TENTATIVAS)
```

---

## Tabela de fila de webhooks (adicionar ao schema)

```sql
CREATE TYPE webhook_status AS ENUM ('pendente', 'enviando', 'entregue', 'falhou');

CREATE TABLE webhook_entregas (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    webhook_id      UUID NOT NULL REFERENCES webhooks(id),
    evento          VARCHAR(100) NOT NULL,
    payload         JSONB NOT NULL,
    status          webhook_status NOT NULL DEFAULT 'pendente',
    tentativas      INT NOT NULL DEFAULT 0,
    proxima_tentativa TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ultimo_erro     TEXT,
    entregue_em     TIMESTAMPTZ,
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_webhook_entregas_pendentes
    ON webhook_entregas(proxima_tentativa)
    WHERE status IN ('pendente', 'falhou') AND tentativas < 4;
```

---

## Endpoint de callback PIX (n8n → ERP)

Quando o n8n recebe confirmação do banco e precisa informar o ERP:

```
POST /api/v1/pagamentos/pix/callback

Headers:
  X-N8N-Secret: <secret_compartilhado>

Body:
{
  "txid": "abc123",
  "valor": 82.47,
  "status": "CONCLUIDA",
  "horario": "2026-06-02T21:41:00Z"
}
```

O ERP localiza o pagamento pelo `txid` e atualiza o status para `confirmado`.
