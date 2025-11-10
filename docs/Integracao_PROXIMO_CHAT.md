# 🚀 Integração Open Finance (Pluggy) - Contexto Rápido

> **📌 Documento para IA/Próximas Sessões**  
> **Última atualização:** 10/11/2025  
> **Status:** ✅ REST API funcionando | Sandbox + Mercado Pago Real conectados

---

## 🎯 O QUE JÁ FUNCIONA

### ✅ **Integração Estabelecida**

- **Serviço:** Pluggy (agregador Open Finance Brasil)
- **Conta criada:** Meu Pluggy Dashboard
- **Contas conectadas:**
  - 🏦 **Mercado Pago** (real) - Item ID: `879f822e-ad2b-48bb-8137-cf761ab1a1a3`
  - 🧪 **Sandbox** (teste) - Item ID: `06f300c4-75e0-4a2f-bbea-e0fb1a1a13cf`

### ✅ **Dados Recuperados com Sucesso**

- ✅ **Saldo da conta** (R$ 6,68 no Mercado Pago)
- ✅ **Transações** com categoria automática
- ✅ **Dados de identidade** (nome, CPF, endereço, telefone)
- ✅ **Investimentos** (consulta funciona, mas vazia no MP)

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

### **Scripts Funcionais:**

- ✅ `backend/src/teste_pluggy_rest.py` - **Exemplo working de REST API**
- ✅ `backend/src/verificar_dados_completos.py` - **Recupera todos os dados (conta, transações, identidade, investimentos)**

### **Scripts Obsoletos (não usar):**

- ❌ `teste_pluggy.py` - Usa SDK (não funciona)
- ❌ `teste_pluggy_rapido.py` - Usa SDK (não funciona)
- ❌ `testar_item_pluggy.py` - Usa SDK (retorna 403)
- ❌ `criar_item_pluggy.py` - Usa SDK (não funciona)
- ❌ `pluggy_connect.html` - Widget (CDN com problemas)

### **Código de Integração:**

- ⚠️ `backend/src/integrations/pluggy_client.py` - **PRECISA REFATORAR** (ainda usa SDK)
- ⚠️ `backend/src/integrations/pluggy_sync.py` - Serviço de sincronização (não testado)

### **Documentação:**

- 📖 `docs/INTEGRACAO_PLUGGY.md` - Documentação inicial (desatualizada)
- 📋 `docs/CHECKLIST_PLUGGY.md` - Checklist de implementação

---

## 🎯 PRÓXIMOS PASSOS (ROADMAP)

### **Fase 1: Segurança** 🔐

- [ ] Criar `.env` na raiz do projeto
- [ ] Instalar `python-decouple`
- [ ] Migrar credenciais de `config.ini` para `.env`
- [ ] Atualizar `.gitignore` para incluir `.env`
- [ ] Atualizar scripts para usar `decouple.config()`

### **Fase 2: Refatoração** 🔧

- [ ] Refatorar `pluggy_client.py` para usar REST API (não SDK)
- [ ] Implementar refresh automático de API key (expira em 2h)
- [ ] Adicionar error handling e retry logic
- [ ] Implementar logging adequado
- [ ] Remover dependência do `pluggy-sdk`

### **Fase 3: Sincronização** 🔄

- [ ] Atualizar `pluggy_sync.py` para trabalhar com REST API
- [ ] Mapear campos de transação Pluggy → Transaction model
- [ ] Implementar detecção de duplicatas
- [ ] Criar lógica de sincronização incremental
- [ ] Testar com dados reais do Mercado Pago

### **Fase 4: Expansão** 🏦

- [ ] Conectar conta Itaú via Dashboard
- [ ] Testar com múltiplas contas
- [ ] Validar categorização automática
- [ ] Comparar com dados manuais existentes

### **Fase 5: Automação** 🤖

- [ ] Integrar com `agente_financeiro.py`
- [ ] Criar script de sincronização automática
- [ ] Adicionar ao fluxo de processamento mensal
- [ ] Criar relatórios consolidados (manual + Open Finance)

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
