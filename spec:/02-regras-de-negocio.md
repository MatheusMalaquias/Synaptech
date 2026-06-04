# 02 — Regras de Negócio

## Fluxo de venda (processo atual mapeado)

```
[CAIXA LIVRE]
     ↓
Operador abre pesquisa de produto (F7 ou digita código)
     ↓
Seleciona produto na lista
     ↓
Modal "Quantidade" → operador digita valor (ex: 2.750 para KG)
     ↓
Item aparece na tela de venda com subtotal calculado
     ↓
(loop) Operador pode adicionar mais produtos
     ↓
Operador escolhe forma de pagamento
     ↓
Sistema finaliza a venda e emite NFC-e
     ↓
Impressora Epson imprime cupom fiscal
     ↓
[CAIXA LIVRE]
```

---

## Regras por domínio

### Produtos

- Todo produto tem: código interno (SERIAL), código de barras, descrição, unidade (KG ou UN), preço de venda
- Unidade KG: venda por peso, quantidade com até 3 casas decimais
- Unidade UN: venda por unidade inteira (quantidade inteira)
- Flag `tributado` (T/F): quando F, alíquota ICMS = 0%
- Alíquota padrão quando tributado: 18% ICMS
- Redução de base de cálculo: campo existe mas parece sempre 0
- Campo "Descrição Adicional" existe mas está vazio em todos os produtos visíveis

### Estoque

- Saldo controlado por produto em sua unidade nativa (KG ou UN)
- **O estoque PODE ser negativo** — o sistema não bloqueia venda por falta de estoque
- Baixa automática no momento da finalização da venda
- Entrada de estoque: processo não visível nas imagens (módulo separado)
- Valores altos de estoque (ex: 427.959 KG de abóbora) precisam ser verificados

### Cálculo de valores

```python
# Regra de cálculo de item
subtotal_item = round(quantidade * preco_unitario, 2)

# Total da venda
total_venda = sum(subtotal_item for item in itens)

# Com desconto
total_final = round(total_venda - desconto_nota, 2)

# Com acréscimo
total_final = round(total_venda + acrescimo_nota, 2)
```

Verificação confirmada: 2,750 × 29,99 = 82,4725 → arredondado = **82,47** ✓

### Formas de pagamento

| Forma         | Comportamento |
|---------------|---------------|
| Dinheiro      | Recebe valor, calcula troco |
| Cartão Crédito| Integração TEF — sem troco |
| Cartão Débito | Integração TEF — sem troco |
| PIX Dinâmico  | Gera QR Code — aguarda confirmação |
| Cheque        | Registra cheque — sem validação em tempo real |
| Voucher       | Abate do saldo do voucher |
| Crédito Troca | Abate do crédito do cliente |
| Caderneta     | Venda fiado — lança no débito do cliente |
| Fechamento Rápido | Atalho para dinheiro sem necessidade de digitar valor |

**Regra:** uma venda pode ser paga com múltiplas formas de pagamento (ex: parte cartão, parte PIX).

### Descontos e acréscimos

- **Desconto por nota:** aplicado sobre o total da venda (tecla C)
- **Desconto por item:** aplicado sobre um item específico (Num-)
- **Acréscimo por nota:** adiciona valor ao total
- Descontos e acréscimos são registrados separadamente do preço original

### NFC-e (Nota Fiscal de Consumidor Eletrônica)

- Série padrão: **01**
- Emitida no fechamento de cada venda
- Integração com SEFAZ via Ctrl+Alt+C (modo online)
- Impressão automática na Epson após emissão
- Reimprimir: Ctrl+R

### Cancelamentos

- **Cancelar Item (F9):** remove um item da venda em andamento
- **Cancelar Nota (F10):** cancela toda a venda antes de finalizar
- Cancelamento após emissão NFC-e: processo diferente (requer protocolo SEFAZ)

### Outros fluxos identificados

- **Receber Caderneta (N):** registra pagamento de dívida de fiado
- **Receber Comanda:** integração com comanda (delivery ou mesa?)
- **Receber Pedido (P):** importa pedido já registrado
- **Pesquisa Vendedor:** associa venda a um vendedor específico
- **Travar Caixa (B):** bloqueia o caixa (exige senha para desbloquear)
- **Abrir Gaveta (A):** aciona a gaveta de dinheiro via impressora

---

## Campos obrigatórios por operação

### Nova venda
- Produto (obrigatório)
- Quantidade (obrigatório)
- Forma de pagamento (obrigatório para finalizar)

### Opcionais na venda
- Cliente (F4 — opcional)
- Vendedor (opcional)
- Desconto (opcional)
- Acréscimo (opcional)

---

## Invariantes do sistema (nunca devem ser violadas)

1. `total_item = round(quantidade * preco_unitario, 2)` — sempre
2. `total_venda = sum(total_item)` — sempre
3. `total_final >= 0` — nunca negativo
4. Toda venda finalizada gera uma NFC-e (ou fica pendente se SEFAZ offline)
5. Toda baixa de estoque tem rastreabilidade até a venda que a originou
6. Todo cancelamento de item reverte a baixa de estoque
7. Toda ação de operador gera registro em `auditoria_log`
