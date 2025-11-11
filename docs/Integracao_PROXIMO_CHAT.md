# 🚀 Integração Open Finance (Pluggy) - Contexto Rápido

> **📌 Documento para IA/Próximas Sessões**  
> **Última atualização:** 11/11/2025  
> **Status:** ✅ FASE 1 COMPLETA | **2.318 transações** importadas | **Banco de dados** sincronizado

---

## 🎉 CONQUISTAS v2.3.0 (11/11/2025)

### **✅ FASE 1 CONCLUÍDA: IMPORTAÇÃO ANUAL OPEN FINANCE**

- **2.318 transações** importadas para `transacoes_openfinance`
- **Período:** 19/12/2024 a 11/11/2025 (11 meses completos)
- **94,7% categorização automática** via CategorizationService (2.194 transações)
- **124 transações "A definir"** (5,3% - para categorização manual)
- **Ciclo de faturamento 19-18** implementado e validado
- **Script:** `backend/src/sync_openfinance_anual.py`
- **Database:** `dados/db/financeiro.db` → tabela `transacoes_openfinance`

### **📊 Distribuição por Mês (Ciclo 19-18):**

```
Janeiro 2025:   281 transações (19/12/24 a 18/01/25)
Fevereiro 2025: 266 transações (19/01/25 a 18/02/25)
Março 2025:     188 transações (19/02/25 a 18/03/25)
Abril 2025:     193 transações (19/03/25 a 18/04/25)
Maio 2025:      186 transações (19/04/25 a 18/05/25)
Junho 2025:     216 transações (19/05/25 a 18/06/25)
Julho 2025:     205 transações (19/06/25 a 18/07/25)
Agosto 2025:    198 transações (19/07/25 a 18/08/25)
Setembro 2025:  233 transações (19/08/25 a 18/09/25)
Outubro 2025:   211 transações (19/09/25 a 18/10/25)
Novembro 2025:  141 transações (19/10/25 a 10/11/25) ← Mês atual
```

### **💳 Distribuição por Fonte:**

```
Visa Virtual:       716 transações
PIX:                523 transações
Visa Bia:           510 transações
Visa Recorrente:    231 transações
Visa Físico:        190 transações
Visa Mae:           148 transações
```

### **🏷️ Top 10 Categorias:**

```
1. Mercado:   256 | 2. Compras: 175 | 3. Padaria: 158
4. Lazer:     149 | 5. Stream:  138 | 6. A definir: 124
7. Cartão:    120 | 8. Casa:    119 | 9. Esporte: 109
10. Feira:     97
```

### **🗄️ Estrutura da Tabela `transacoes_openfinance` (21 campos):**

```sql
- Identificação: id, provider_id (UNIQUE), account_id
- Dados: data, descricao, valor
- Categorização: categoria (usuário), categoria_banco, tag
- Origem: fonte, pagador, cartao_final
- Período: mes_comp (ciclo 19-18)
- Banco: tipo_transacao, tipo_conta, origem_banco
- Parcelas: parcela_numero, parcela_total, data_compra
- Moeda: moeda_original, valor_moeda_original
- Controle: origem_dado, sincronizado_em
- Auditoria: created_at, updated_at, metadata_json
```

---

## � CONQUISTAS v2.2.0 (10-11/11/2025)

### **✅ EXCEL CONSOLIDADO OPEN FINANCE FUNCIONANDO!**

- **141 transações processadas** (Novembro 2025 - Ciclo 19/10 a 18/11)
- **614 transações históricas** fetched (3 contas Itaú: 2 cartões + 1 corrente)
- **83% categorização automática** via CategorizationService
- **Conversão de moedas** (USD/EUR/GBP → BRL automático)
- **Identificação de parcelas** (1/3, 2/5, etc.) com metadata completa
- **Formato 100% compatível** com consolidado_temp.xlsx
- **Script:** `backend/src/gerar_excel_pluggy.py`
- **Output:** `dados/planilhas/consolidado_pluggy_nov2025.xlsx`

### **📊 Resultados Novembro 2025:**

```
Total: 141 transações
├─ Débitos (130): R$ -12.391,35
├─ Créditos (11): R$ -9.579,96
├─ Categorizado: 117/141 (83%)
├─ Parcelas: 33 identificadas
└─ Moedas: 13 USD convertidas

Fontes:
├─ Visa Bia: 28 | PIX: 28 | Master Físico: 22
├─ Visa Recorrente: 16 | Visa Mae: 12
└─ Master Virtual: 11 | Visa Físico: 11 | Visa Virtual: 7 | Master Recorrente: 6

Top Categorias:
├─ A definir: 23 (16.3%) | Mercado: 16 | Cartão: 10
└─ Compras: 8 | Esporte: 7 | Stream: 7 | Casa: 7
```

---

## 🎯 O QUE JÁ FUNCIONA

### ✅ **Integração Estabelecida**

- **Serviço:** Pluggy (agregador Open Finance Brasil)
- **Conta criada:** Meu Pluggy Dashboard
- **Contas conectadas:**
  - 🏦 **Itaú (REAL)** - Item ID: `60cbf151-aaed-45c7-afac-f2aab15e6299`
    - LATAM PASS VISA PLATINUM (6259) - R$ 15.159,75
    - PERSON MULTIPLO BLACK (4059) - R$ 18.272,58
    - Conta Corrente (00002663-4) - R$ 129,06
  - 🏦 **Mercado Pago** (real) - Item ID: `879f822e-ad2b-48bb-8137-cf761ab1a1a3`
  - 🧪 **Sandbox** (teste) - Item ID: `06f300c4-75e0-4a2f-bbea-e0fb1a1a13cf`

### ✅ **Dados Recuperados com Sucesso**

- ✅ **Saldo das contas** (3 contas Itaú + Mercado Pago)
- ✅ **614 transações históricas** (últimos 3 meses)
- ✅ **Transações com categoria bancária** automática
- ✅ **Metadata de parcelas** (installments, purchaseDate, billId)
- ✅ **Conversão de moedas** (amountInAccountCurrency)
- ✅ **Card numbers** para mapeamento de fontes
- ✅ **Dados de identidade** (nome, CPF, endereço, telefone)
- ✅ **Excel consolidado** compatível com sistema existente

---

## 🔑 CREDENCIAIS

**⚠️ Armazenadas em:** `backend/src/config.ini` (NÃO versionado)

```ini
[PLUGGY]
CLIENT_ID = 0774411c-feca-44dc-83df-b5ab7a1735a6
CLIENT_SECRET = 3bd7389d-72d6-419a-804a-146e3e0eaacf
```

**🔐 Segurança:**

- ✅ `.gitignore` protege `config.ini`
- ✅ `config.example.ini` versionado sem credenciais
- ⚠️ **PRÓXIMO PASSO:** Migrar para `.env` + python-decouple

---

## 🛠️ SOLUÇÃO TÉCNICA (IMPORTANTE!)

### ❌ **pluggy-sdk NÃO FUNCIONA**

- **Problema:** Bug no SDK - envia header `Authorization: Bearer {key}` (errado)
- **Erro retornado:** `403 Forbidden`
- **Status:** SDK instalado mas **não usar**

### ✅ **REST API FUNCIONA PERFEITAMENTE**

- **Solução:** Usar biblioteca `requests` diretamente
- **Header correto:** `X-API-KEY: {apiKey}`
- **Base URL:** `https://api.pluggy.ai`

### **Código Working (Template):**

```python
import requests

# 1. Autenticar
auth_response = requests.post('https://api.pluggy.ai/auth', json={
    'clientId': CLIENT_ID,
    'clientSecret': CLIENT_SECRET
})
api_key = auth_response.json()['apiKey']
headers = {'X-API-KEY': api_key}

# 2. Listar contas
accounts = requests.get(
    f'https://api.pluggy.ai/accounts?itemId={ITEM_ID}',
    headers=headers
).json()

# 3. Buscar transações
transactions = requests.get(
    f'https://api.pluggy.ai/transactions?accountId={account_id}&from={date_from}&to={date_to}',
    headers=headers
).json()
```

---

## 📂 ARQUIVOS RELEVANTES

### **✅ Scripts de Produção (backend/src/):**

- ✅ **`sync_openfinance_anual.py`** - **NOVO!** Sincronização anual (12 meses) para banco de dados
- ✅ **`gerar_excel_pluggy.py`** - Geração de Excel consolidado Open Finance
- ✅ `atualizar_categoria_vestuario.py` - Manutenção de categorias
- ✅ `limpar_categorias.py` - Limpeza de duplicatas no banco

### **✅ Scripts de Teste de API (scripts/testes/):**

- ✅ `teste_pluggy_rest.py` - Teste REST API Pluggy
- ✅ `verificar_dados_completos.py` - Validação completa (contas, transações, identidade)
- ✅ `buscar_itau_simples.py` - Fetch 614 transações Itaú sem emojis
- ✅ `listar_transacoes_3meses.py` - Demo Mercado Pago (15 transações)
- ✅ `verificar_parcelas.py` - Análise de metadata de parcelas (121 encontradas)

### **❌ Scripts Obsoletos (backend/src/\_deprecated/):**

**NÃO USAR! Movidos para \_deprecated/**

- ❌ `teste_pluggy.py` - Usa SDK (403 Forbidden)
- ❌ `teste_pluggy_rapido.py` - Usa SDK (403 Forbidden)
- ❌ `testar_item_pluggy.py` - Usa SDK (403 Forbidden)
- ❌ `criar_item_pluggy.py` - Usa SDK (403 Forbidden)
- ❌ `teste_pluggy.bat` - Chama SDK obsoleto
- ❌ `pluggy_connect.html` - Widget não funciona
- ❌ `pluggy_dashboard_help.html` - Desatualizado
- ❌ `listar_transacoes_itau.py` - Problemas de encoding

**Ver:** `backend/src/_deprecated/README.md` para detalhes

### **⚠️ Módulos Legados (backend/src/integrations/):**

- ⚠️ `pluggy_client.py` - **Ainda usa SDK** - Precisa refatorar para REST
- ⚠️ `pluggy_sync.py` - Precisa atualizar para REST API

### **Documentação:**

- 📖 `docs/INTEGRACAO_PLUGGY.md` - Documentação inicial (desatualizada)
- 📋 `docs/CHECKLIST_PLUGGY.md` - Checklist de implementação

---

## 🎯 PRÓXIMOS PASSOS (ROADMAP)

### ✅ **Fase 1: Fundação** (CONCLUÍDA - v2.1.0)

- [x] Integração REST API Pluggy
- [x] Autenticação OAuth2
- [x] Conexão Mercado Pago
- [x] Conexão Itaú (3 contas)
- [x] Fetch de transações
- [x] Documentação técnica

### ✅ **Fase 2: Geração de Excel** (CONCLUÍDA - v2.2.0)

- [x] Script `gerar_excel_pluggy.py`
- [x] Mapeamento de fontes (9 sources)
- [x] Categorização inteligente (83%)
- [x] Conversão de moedas (USD/EUR/GBP → BRL)
- [x] Identificação de parcelas
- [x] Formato compatível com `consolidado_temp.xlsx`
- [x] 614 transações processadas
- [x] Organização de scripts (`/scripts/`, `/_deprecated/`)

### ✅ **Fase 3: Banco de Dados Anual** (CONCLUÍDA - v2.3.0)

- [x] Criação da tabela `transacoes_openfinance` (21 campos)
- [x] Script `sync_openfinance_anual.py`
- [x] Importação de 12 meses (2.318 transações)
- [x] Ciclo de faturamento 19-18 implementado
- [x] Categorização automática (94,7%)
- [x] Mapeamento de fontes (6 tipos)
- [x] Metadata JSON completo
- [x] Prevenção de duplicatas (provider_id UNIQUE)
- [x] Validação de período (Jan-Nov 2025)

### 🔄 **Fase 4: Dashboard Automático** (PRÓXIMA)

- [ ] Gerar dashboard HTML/Excel com dados de `transacoes_openfinance`
- [ ] Comparação Real vs Ideal (budget tracking)
- [ ] Gráficos: mensal, por categoria, por fonte
- [ ] Evolução anual (Janeiro a Novembro)
- [ ] Alertas de gastos acima do orçamento
- [ ] Export para Excel compatível com `Controle_pessoal.xlsm`

### 📋 **Fase 5: Automação** (FUTURO)

- [ ] Sincronização semanal automática
- [ ] Dashboard atualizado automaticamente
- [ ] Notificações de novos gastos
- [ ] Relatório semanal por email
- [ ] Integração com planilha Excel existente

### 🔄 **Fase 3: Integração com Fluxo Principal** (PRÓXIMO)

- [ ] Integrar `gerar_excel_pluggy.py` com `agente_financeiro.py`
- [ ] Opção no menu: "Gerar consolidado Open Finance"
- [ ] Detecção de duplicatas (provider_id vs manual)
- [ ] Merge inteligente (Open Finance + arquivos manuais)
- [ ] Validação cruzada de valores

### 📋 **Fase 4: Automação** (FUTURO)

- [ ] Sincronização automática mensal
- [ ] Script scheduled (cron/task scheduler)
- [ ] Notificações de novas transações
- [ ] Categorização pendente (relatório "A definir")
- [ ] Comparativo automático (esperado vs real)

### 🏦 **Fase 5: Expansão** (FUTURO)

- [ ] Conectar outras contas bancárias se necessário
- [ ] Cartões de outros bancos
- [ ] Contas de investimento
- [ ] Relatórios consolidados multi-conta
- [ ] Dashboard web (futuro distante)

### 🔐 **Fase 6: Segurança e Compliance** (CONTÍNUO)

- [ ] Migrar credenciais para `.env`
- [ ] Implementar rotação de API keys
- [ ] Documentar compliance LGPD
- [ ] Audit log de acessos
- [ ] Criptografia de dados sensíveis

### 🔧 **Fase 7: Refatoração Técnica** (OPCIONAL)

- [ ] Refatorar `pluggy_client.py` para REST API
- [ ] Atualizar `pluggy_sync.py` para REST
- [ ] Remover dependência do `pluggy-sdk`
- [ ] Implementar error handling robusto
- [ ] Logging estruturado
- [ ] Testes automatizados

---

## 🐛 PROBLEMAS CONHECIDOS

### **1. SDK com Bug de Autenticação**

- **Sintoma:** `403 Forbidden` em todas as chamadas
- **Causa:** SDK envia `Authorization: Bearer` em vez de `X-API-KEY`
- **Solução:** Usar REST API com `requests`

### **2. Trial Expirado**

- **Status:** Trial de 7 dias expirou
- **Impacto:** ❌ Não pode conectar novas contas via código
- **Workaround:** ✅ Conectar via Dashboard (funciona)
- **Sandbox:** ✅ Continua funcionando normalmente

### **3. Widget PluggyConnect**

- **Problema:** CDN não carrega corretamente
- **Erro:** `PluggyConnect is not defined`
- **Status:** Abandonado - usar Dashboard

---

## 📊 DADOS REAIS OBTIDOS

### **Conta Mercado Pago (Real):**

```json
{
  "id": "7e372697-f64e-4a05-ab9f-75e39c2fe8ec",
  "type": "BANK",
  "subtype": "CHECKING_ACCOUNT",
  "name": "Mercado Pago",
  "balance": 6.68,
  "currencyCode": "BRL",
  "owner": "Luciano Costa Fernandes",
  "taxNumber": "991.808.986-53",
  "number": "0000000006959355-6"
}
```

### **Transação Exemplo:**

```json
{
  "id": "f8f14ad3-9891-436f-9e66-ccdc42374d29",
  "description": "Rendimentos",
  "amount": 0.01,
  "date": "2025-10-16T00:00:00.000Z",
  "category": "Proceeds interests and dividends",
  "status": "POSTED"
}
```

### **Identity Data:**

```json
{
  "fullName": "Luciano Costa Fernandes",
  "document": {
    "type": "CPF",
    "value": "99180898653"
  },
  "birthDate": "1973-06-22",
  "phoneNumbers": [{ "value": "27999926994" }],
  "emails": [{ "value": "luti_vix@hotmail.com" }]
}
```

---

## 🔗 LINKS ÚTEIS

- 🌐 **Dashboard Pluggy:** https://dashboard.pluggy.ai/
- 📖 **API Docs:** https://docs.pluggy.ai/
- 🔑 **Auth Endpoint:** `POST https://api.pluggy.ai/auth`
- 💳 **Accounts:** `GET https://api.pluggy.ai/accounts?itemId={id}`
- 💸 **Transactions:** `GET https://api.pluggy.ai/transactions?accountId={id}&from={date}&to={date}`
- 👤 **Identity:** `GET https://api.pluggy.ai/identity?itemId={id}`
- 📊 **Investments:** `GET https://api.pluggy.ai/investments?itemId={id}`

---

## 💡 DECISÕES TÉCNICAS

### **Por que REST API em vez do SDK?**

- ✅ SDK tem bug crítico de autenticação (não corrigido)
- ✅ REST API é mais confiável e direta
- ✅ Mais controle sobre headers e requisições
- ✅ Mais fácil de debugar e manter
- ✅ Performance similar

### **Por que não usar Web Scraping?**

- ❌ Ilegal e viola ToS dos bancos
- ❌ Quebraria com qualquer mudança no site
- ❌ Requer credenciais do banco (risco de segurança)
- ✅ Open Finance é regulado pelo Banco Central
- ✅ OAuth2 - sem compartilhar senha
- ✅ Read-only - não pode transferir dinheiro

### **Segurança do Open Finance:**

- ✅ Regulado pelo Banco Central do Brasil
- ✅ OAuth2 authentication (não compartilha senha)
- ✅ Read-only access (não pode transferir)
- ✅ ISO 27001, PCI DSS, LGPD compliant
- ✅ Consentimento explícito do usuário
- ✅ Auditoria e logs de acesso

---

## 📞 CONTATO/REFERÊNCIAS

**Desenvolvedor:** Luciano Costa Fernandes  
**Email:** luti_vix@hotmail.com  
**CPF:** 991.808.986-53  
**Projeto:** Agente Financeiro IA v2.0  
**Repositório:** FinanceiroPY (GitHub @lutivix)

---

**🎯 RESUMO PARA IA:**

- ✅ **Use REST API** (`requests`), não `pluggy-sdk`
- ✅ **Header:** `X-API-KEY`, não `Authorization`
- ✅ **Scripts working:** `teste_pluggy_rest.py`, `verificar_dados_completos.py`
- ✅ **Próximo:** Migrar para `.env`, refatorar `pluggy_client.py`, integrar com sistema principal
- ⚠️ **Pendente:** Conectar Itaú, implementar sync incremental, automatizar
