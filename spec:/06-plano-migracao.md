# 06 — Plano de Migração da Fantastsoft

## Princípio geral

**Nunca desligar o que funciona antes do substituto estar estável.**
Cada fase termina com uma validação formal antes de avançar.

---

## Fase 1 — Automação dos lançamentos (meses 0–3)

**Objetivo:** ERP recebe dados de vendas automaticamente via n8n, sem operação manual.

**O que construir:**
- [ ] Infraestrutura: Docker Compose com PostgreSQL, Redis, FastAPI, n8n
- [ ] Autenticação JWT (login, refresh, logout)
- [ ] CRUD de produtos (importar catálogo da Fantastsoft)
- [ ] Módulo de estoque básico (saldo + movimentações)
- [ ] Endpoint de webhook para n8n
- [ ] Fila de entrega de webhooks com retry
- [ ] Tela de consulta de vendas (somente leitura)

**O que NÃO fazer ainda:**
- PDV próprio
- Emissão NFC-e
- Substituição de qualquer tela da Fantastsoft

**Critério de conclusão:**
O n8n está capturando dados de cada venda da Fantastsoft (via exportação periódica ou leitura do banco local) e enviando ao ERP. Os dados batem com os da Fantastsoft em 100% das vendas do dia.

**Estratégia de extração da Fantastsoft:**
1. Investigar banco local (provável SQL Server LocalDB ou SQLite)
2. Se acessível: ler tabelas diretamente via ODBC ou arquivo
3. Se não acessível: usar exportação de relatório diário em CSV/Excel
4. n8n agendado (ex: a cada 5 minutos) para capturar novas vendas

---

## Fase 2 — Controle de estoque (meses 3–5)

**Objetivo:** Estoque controlado no ERP próprio com confiabilidade.

**O que construir:**
- [ ] Importar saldo inicial de estoque da Fantastsoft
- [ ] Baixa automática via eventos de venda
- [ ] Alertas de estoque mínimo (via n8n → WhatsApp)
- [ ] Tela de estoque com histórico de movimentações
- [ ] Ajuste manual de estoque (com motivo obrigatório)

**Critério de conclusão:**
Saldo do ERP próprio diverge menos de 1% do saldo da Fantastsoft ao final de cada dia, por 2 semanas consecutivas.

---

## Fase 3 — PDV próprio em paralelo (meses 5–8)

**Objetivo:** PDV próprio operando em ambiente real, Fantastsoft como backup.

**O que construir:**
- [ ] Interface PDV (React) — busca de produto, quantidade, subtotal
- [ ] Integração PIX (QR Code dinâmico)
- [ ] Integração TEF (cartão débito/crédito)
- [ ] Fluxo de pagamento completo
- [ ] Impressão em Epson (ESC/POS)
- [ ] Abertura e fechamento de caixa
- [ ] Cancelamento de item e de venda
- [ ] Desconto e acréscimo
- [ ] Treinamento dos operadores

**Validação:**
- 1 semana operando em paralelo (mesmas vendas lançadas nos dois sistemas)
- Conferência diária de totais
- Zero erros de cálculo

**Critério de conclusão:**
PDV próprio processa 100 vendas reais sem erro, em paralelo com a Fantastsoft.

---

## Fase 4 — Substituição completa (meses 8–10)

**Objetivo:** Fantastsoft desinstalada. ERP próprio como único sistema.

**O que construir:**
- [ ] Todos os módulos secundários (caderneta, voucher, comanda)
- [ ] Relatórios equivalentes aos da Fantastsoft
- [ ] Backup automático configurado
- [ ] Monitoramento de uptime (Uptime Kuma ou similar)
- [ ] Procedimento de recuperação de falha documentado

**Critério de conclusão:**
30 dias operando sem a Fantastsoft, sem incidentes críticos.

---

## Fase 5 — Emissão fiscal própria (meses 10–14)

**Objetivo:** ERP emitindo NFC-e diretamente, sem depender de biblioteca de terceiros da Fantastsoft.

**O que construir:**
- [ ] Integração com SEFAZ (biblioteca Python: `python-nfe` ou `nfelib`)
- [ ] Certificado digital A1/A3
- [ ] Ambiente de homologação → validação → produção
- [ ] Contingência offline (NFC-e em contingência EPEC)
- [ ] Cancelamento de NFC-e via SEFAZ
- [ ] Inutilização de numeração
- [ ] Consulta de status de nota

**Critério de conclusão:**
1.000 NFC-e emitidas em produção sem rejeição da SEFAZ.

---

## Riscos e mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Banco da Fantastsoft inacessível | Média | Alto | Usar exportação CSV como fallback |
| Rejeição NFC-e na SEFAZ | Baixa | Alto | Testar 100% em homologação antes |
| Resistência dos operadores | Média | Médio | Treinamento gradual + interface simples |
| Perda de dados na migração | Baixa | Alto | Backup completo antes de cada fase |
| PIX sem confirmação | Baixa | Médio | Timeout + processo de reconciliação |
| Queda do servidor ERP | Baixa | Alto | Fantastsoft como fallback até Fase 4 |
