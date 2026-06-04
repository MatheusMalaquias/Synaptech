# 01 — Análise do Sistema Atual (Fantastsoft)

## Contexto

A empresa é um FLV (Frutas, Legumes e Verduras) que utiliza o **Fantastsoft FantastPDV versão 10.2.416.11029**.
O sistema opera em um computador Windows com:
- Impressora térmica: **Epson (ppEscPosEpson)**
- Tipo de nota fiscal: **NFC-e (Série 01)**
- Nome do computador: DESKTOP-0AAH9PE
- Módulo de acesso remoto: Fantastsoft Remote (via ID/senha de uso único)

---

## Telas mapeadas

### Tela 1 — Pesquisa de Produtos

Função: catálogo de produtos, acessível durante o fluxo de venda (F7).

Campos visíveis:
- `Descrição Reduzida` — nome curto do produto
- `Descrição Adicional` — sempre vazio nas amostras (campo legado ou subutilizado)
- `Código de Barras` — identificador único numérico
- `ID` — chave interna sequencial
- `Un` — unidade: KG ou UN
- `Preço` — preço de venda (R$)
- `TT` — flag tributação: T (tributado) ou F (não tributado/isento)
- `% Trib` — alíquota ICMS: 18 quando TT=T, 0 quando TT=F
- `% Red` — redução de base de cálculo (0 em todos os visíveis)
- `Estoque` — saldo atual (pode ser negativo; ex: AGRIÃO = -1)

Produtos mapeados das imagens:

| ID  | Produto            | Un | Preço  | TT | %Trib | Estoque   |
|-----|--------------------|----|--------|----|-------|-----------|
| 45  | ABACATE            | KG | 9,99   | T  | 18    | 121.982   |
| 121 | ABACAXI            | UN | 4,99   | T  | 18    | 91        |
| 12  | ABOBORA ITALIANA   | KG | 6,99   | T  | 18    | 427.959   |
| 11  | ABOBORA MENINA     | KG | 9,99   | T  | 18    | 92.151    |
| 10  | ABOBORA MORANGA    | KG | 5,99   | T  | 18    | 194.857   |
| 9   | ABOBORA SERGIPANA  | UN | 7,00   | T  | 18    | 133       |
| 102 | ABOBRINHA RALADA   | UN | 6,00   | F  | 0     | 160       |
| 66  | AÇUCAR MASCAVO     | UN | 3,00   | T  | 18    | 136       |
| 91  | AGRIÃO             | UN | 675,00 | F  | 0     | -1        |
| 141 | ALDODÃO DOCE       | UN | 3,50   | T  | 18    | 120       |
| 122 | ALFACE AMERICANA   | UN | 2,50   | T  | 18    | 298       |
| 88  | ALFACE COMUM       | UN | 2,50   | T  | 18    | 279.728   |
| 77  | ALHO               | KG | 29,99  | T  | 18    | 405       |
| 105 | ALHO DESCASCADO    | UN | 18,00  | T  | 18    | 98        |
| 99  | ALHO PORÓ          | UN | 2,50   | T  | 18    | 143       |
| 89  | ALMEIRÃO           | UN | 14,99  | T  | 18    | 144.550   |
| 120 | AMEIXA             | UN | 6,50   | T  | 18    | 182       |
| 107 | BALA               | UN | 3,75   | T  | 18    | 196       |
| 106 | BALAS              | KG | 4,99   | T  | 18    | 416.039   |
| 500 | BANANA NANICA      | KG | 5,99   | T  | 18    | 115.050   |
| 123 | BANANA OURO        | KG | 6,99   | T  | 18    | 147.291   |
| 124 | BANANA PÃO         | KG | 7,99   | T  | 18    | 371.730   |

**Observação sobre estoque:** valores muito altos em KG (ex: 427.959) podem indicar estoque em gramas ou falta de baixa histórica. Precisa ser investigado antes da migração.

---

### Tela 2 — Modal de Quantidade

Função: capturar a quantidade após seleção do produto.

- Campo único: input numérico centralizado
- Aceita decimais (ex: 2,750 para KG)
- Sem validação de mínimo/máximo visível
- Unidade já herdada da seleção anterior

---

### Tela 3 — PDV com Item Lançado

Função: tela principal de venda com itens no carrinho.

Campos visíveis:
- `Série` — número da série NFC-e (01)
- `Quantidade Total` — número de itens na venda
- `Item` — sequência (001, 002...)
- `Descrição` — nome do produto
- `ID Produto` — código interno (ex: 77)
- `Quant.` — quantidade + unidade (ex: 2,750 KG)
- `Preço` — preço unitário
- `Total` — quantidade × preço (ex: 2,750 × 29,99 = 82,47)
- `Total Geral` — soma de todos os itens

Regra de cálculo confirmada: `ROUND(quantidade * preco_unitario, 2)`

---

### Tela 4 — Fantastsoft Remote

Função: acesso remoto ao computador do caixa (suporte técnico).
- ID de acesso: 213 372 402
- Senha de uso único (muda a cada sessão)
- Aviso sobre UAC do Windows
- **Implicação:** não há API REST exposta; o acesso remoto é sobre a interface gráfica

---

### Tela 5 — Caixa Livre (tela inicial do PDV)

Função: estado de espera entre vendas. Exibe "CAIXA LIVRE" em destaque.

Atalhos de teclado mapeados:

| Atalho       | Função                  |
|--------------|-------------------------|
| B            | Travar Caixa            |
| F1           | Ajuda                   |
| A            | Abrir Gaveta            |
| F4           | Pesquisa Cliente        |
| F7           | Pesquisa Produto        |
| N            | Receber Caderneta       |
| F10          | Cancelar Nota           |
| F9           | Cancelar Item           |
| C            | Desconto Nota           |
| Num -        | Desconto Item           |
| Ctrl+R       | Reimprimir Nota         |
| Ctrl+Alt+C   | NFC-e on-line (SEFAZ)   |
| F5           | Pagamento Dinheiro      |
| F6           | Pagamento Cheque        |
| D            | Cartão de Crédito       |
| E            | Cartão de Débito        |
| X            | PIX Dinâmico            |
| V            | Voucher                 |

---

## Avaliação técnica da Fantastsoft

| Aspecto              | Avaliação              | Confiança |
|----------------------|------------------------|-----------|
| Tem API REST         | Improvável             | Baixa     |
| Banco local          | Provável (SQL Server ou SQLite) | Média |
| Permite exportação   | Provável (relatórios)  | Média     |
| Permite importação   | Desconhecido           | Baixa     |
| NFC-e integrada      | Confirmado             | Alta      |
| TEF integrado        | Provável (cartões)     | Alta      |
| PIX integrado        | Confirmado (PIX Dinâmico) | Alta  |

**Estratégia de migração de dados:** investigar banco local da Fantastsoft (provavelmente acessível via ODBC ou arquivos) para extração do cadastro de produtos e histórico.

---

## Perguntas em aberto (respostas necessárias antes de implementar)

1. O estoque de KG é em quilos ou gramas? Como é feita entrada de estoque?
2. Existe balança integrada? O peso é capturado automaticamente?
3. O cliente é identificado na maioria das vendas ou são "consumidor final"?
4. O "Receber Comanda" é para delivery, mesa ou outro?
5. O PIX é integrado a qual banco/intermediador?
6. O TEF é integrado a qual adquirente (Cielo, Stone, Rede)?
7. Como funciona a caderneta (fiado)? Por CPF ou nome?
8. A empresa emite NF-e além de NFC-e?
9. Qual o regime tributário (Simples Nacional, Lucro Presumido)?
10. Quantos caixas operam simultaneamente?
11. Existe abertura/fechamento formal de caixa hoje?
12. Qual o volume médio de vendas por dia?
13. O que o n8n já faz hoje? Qual o gatilho atual?
14. Existe filial ou é loja única?
