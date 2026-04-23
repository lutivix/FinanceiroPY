# 🧪 Guia Completo - Plaid Sandbox

**Data:** 21/04/2026  
**Status:** ✅ Ativo  
**Contexto:** Desenvolvimento e testes com Plaid antes de produção

---

## 🎯 O Que é o Sandbox?

O **Plaid Sandbox** é um ambiente de desenvolvimento **100% gratuito** e **totalmente funcional** para testar toda a API Plaid sem custos.

**Características principais:**
- ✅ **Grátis permanentemente** (sem expiração)
- ✅ **Todas as funcionalidades** disponíveis
- ✅ **Items ilimitados** (conexões bancárias de teste)
- ✅ **Dados de teste realistas** (transações, contas, investimentos)
- ✅ **Webhooks funcionais** para testes
- ✅ **Sem necessidade de aprovação** (disponível imediatamente)

---

## 🔑 Credenciais de Teste

### Padrão Universal

**Para todos os bancos de teste:**
```
Username: user_good
Password: pass_good
```

**Outras credenciais disponíveis:**

| Username | Password | Comportamento |
|----------|----------|---------------|
| `user_good` | `pass_good` | ✅ Login bem-sucedido com dados completos |
| `user_bad` | `pass_good` | ❌ Falha de autenticação (teste erro) |
| `user_custom_*` | `pass_good` | 🎯 Cenários específicos (MFA, múltiplas contas) |

---

## 🏦 Instituições de Teste

### Banco Global Principal

**First Platypus Bank** (Banco fictício global)
- **Institution ID:** `ins_109508`
- **Uso:** Testes gerais de funcionalidades
- **Produtos:** Todos disponíveis
- **Dados:** Transações, contas corrente/poupança, investimentos

### Bancos Brasileiros (Sandbox)

Todos os principais bancos brasileiros têm versões sandbox:
- ✅ Itaú (versão sandbox)
- ✅ Bradesco (versão sandbox)
- ✅ Banco do Brasil (versão sandbox)
- ✅ Santander (versão sandbox)
- ✅ Nubank (versão sandbox)
- ✅ Inter (versão sandbox)
- ✅ C6 Bank (versão sandbox)

**⚠️ Nota:** Comportamentos específicos de cada instituição podem não ser 100% idênticos à produção.

---

## 🚀 Como Usar o Sandbox

### 1. **Configuração Inicial**

```python
from plaid.api import plaid_api
from plaid import Configuration, ApiClient, Environment

# Credenciais do dashboard (Team Settings → Keys → Sandbox)
CLIENT_ID = 'seu_client_id'
SANDBOX_SECRET = 'seu_sandbox_secret'

# Configurar para Sandbox
configuration = Configuration(
    host=Environment.Sandbox,  # ← IMPORTANTE: Sandbox
    api_key={
        'clientId': CLIENT_ID,
        'secret': SANDBOX_SECRET,
    }
)

client = plaid_api.PlaidApi(ApiClient(configuration))
```

### 2. **Criar Item de Teste (Bypassando Link UI)**

**Método recomendado para testes automatizados:**

```python
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.products import Products

# Criar item direto via API (sem interface gráfica)
request = SandboxPublicTokenCreateRequest(
    institution_id='ins_109508',  # First Platypus Bank
    initial_products=[Products('transactions'), Products('investments')]
)

response = client.sandbox_public_token_create(request)
public_token = response['public_token']

print(f"✅ Public token criado: {public_token}")
```

**Por que usar este método?**
- ⚡ Mais rápido (sem UI)
- 🤖 Ideal para testes automatizados
- 🔄 Repetível e confiável

### 3. **Trocar por Access Token**

```python
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest

# Trocar public_token por access_token (permanente)
exchange_request = ItemPublicTokenExchangeRequest(
    public_token=public_token
)

exchange_response = client.item_public_token_exchange(exchange_request)
access_token = exchange_response['access_token']
item_id = exchange_response['item_id']

print(f"✅ Access token: {access_token}")
print(f"✅ Item ID: {item_id}")

# Guarde access_token - você usará para todas as chamadas futuras!
```

### 4. **Buscar Dados de Teste**

**Contas:**
```python
from plaid.model.accounts_get_request import AccountsGetRequest

request = AccountsGetRequest(access_token=access_token)
response = client.accounts_get(request)

for account in response['accounts']:
    print(f"{account['name']}: {account['balances']['current']}")
```

**Transações:**
```python
from plaid.model.transactions_get_request import TransactionsGetRequest
from datetime import date, timedelta

request = TransactionsGetRequest(
    access_token=access_token,
    start_date=date.today() - timedelta(days=90),
    end_date=date.today()
)

response = client.transactions_get(request)
transactions = response['transactions']

print(f"📋 {len(transactions)} transações encontradas")
```

**Investimentos:**
```python
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest

request = InvestmentsHoldingsGetRequest(access_token=access_token)
response = client.investments_holdings_get(request)

holdings = response['holdings']
securities = response['securities']

print(f"💰 {len(holdings)} posições de investimento")
```

---

## 🔬 Testando Cenários Específicos

### Simular Erro `ITEM_LOGIN_REQUIRED`

**Use case:** Testar fluxo de atualização quando usuário muda senha no banco

```python
from plaid.model.sandbox_item_reset_login_request import SandboxItemResetLoginRequest

# Forçar item a entrar em estado de erro
request = SandboxItemResetLoginRequest(access_token=access_token)
response = client.sandbox_item_reset_login(request)

print("✅ Item em estado ITEM_LOGIN_REQUIRED")
print("Agora você pode testar seu fluxo de update mode!")
```

**⏰ Comportamento automático:** Items no sandbox entram automaticamente em `ITEM_LOGIN_REQUIRED` após **30 dias**.

### Testar Webhooks

**Disparar webhook manualmente:**

```python
from plaid.model.sandbox_item_fire_webhook_request import SandboxItemFireWebhookRequest

# Disparar webhook de teste
request = SandboxItemFireWebhookRequest(
    access_token=access_token,
    webhook_code='DEFAULT_UPDATE'  # Tipo de webhook
)

response = client.sandbox_item_fire_webhook(request)
print("✅ Webhook enviado para sua URL configurada!")
```

**Webhooks disponíveis para teste:**
- `DEFAULT_UPDATE` - Novas transações disponíveis
- `INITIAL_UPDATE` - Primeira sincronização completa
- `HISTORICAL_UPDATE` - Dados históricos
- `TRANSACTIONS_REMOVED` - Transações removidas

### Simular Atualização de Transações

**Testar transações pendentes → posted:**

```python
from plaid.model.sandbox_item_fire_webhook_request import SandboxItemFireWebhookRequest

# Simular mudança de status de transações
request = SandboxItemFireWebhookRequest(
    access_token=access_token,
    webhook_code='DEFAULT_UPDATE'
)

response = client.sandbox_item_fire_webhook(request)

# Agora busque transações novamente - verá mudanças!
```

---

## 📊 Dados de Teste Gerados

### O Que Esperar

**Contas típicas geradas:**
- 💳 Checking (Conta Corrente) - Saldo: ~$1,000 - $5,000
- 💰 Savings (Poupança) - Saldo: ~$5,000 - $20,000
- 💼 Investment (Investimentos) - Saldo: ~$10,000 - $50,000
- 📈 Credit Card (Cartão de Crédito) - Limite: ~$2,000 - $10,000

**Transações típicas:**
- 📋 50-200 transações (últimos 90 dias)
- 🏪 Categorias variadas (supermercado, restaurantes, utilidades, etc)
- 💵 Valores realistas ($5 - $500)
- ⏰ Datas distribuídas naturalmente
- ⚡ Mix de pendentes e posted

**⚠️ Importante:** Dados sandbox são **consistentes internamente**, mas podem não refletir relacionamentos complexos (ex: saldo inconsistente com transações).

---

## ⚡ Endpoints Exclusivos do Sandbox

**Estes endpoints SÓ funcionam no Sandbox:**

| Endpoint | Propósito |
|----------|-----------|
| `/sandbox/public_token/create` | Criar item sem UI |
| `/sandbox/item/reset_login` | Simular expiração de login |
| `/sandbox/item/fire_webhook` | Disparar webhooks de teste |
| `/sandbox/item/set_verification_status` | Testar fluxos de verificação |
| `/sandbox/transfer/fire_webhook` | Webhooks de transferências |
| `/sandbox/income/fire_webhook` | Webhooks de income |

---

## 🔄 Migração Sandbox → Production

### Quando Sua Produção For Aprovada

**O que mudar:**

```python
# ANTES - Sandbox
configuration = Configuration(
    host=Environment.Sandbox,  # ← Mude isto
    api_key={
        'clientId': CLIENT_ID,
        'secret': SANDBOX_SECRET,  # ← E isto
    }
)

# DEPOIS - Production
configuration = Configuration(
    host=Environment.Production,  # ← Production
    api_key={
        'clientId': CLIENT_ID,  # ← Mesmo client_id
        'secret': PRODUCTION_SECRET,  # ← Secret diferente!
    }
)
```

**⚠️ ATENÇÃO:**
- ❌ **NÃO use sandbox secret em produção!**
- ❌ **Access tokens do sandbox NÃO funcionam em produção!**
- ✅ Cada ambiente tem seus próprios secrets e tokens
- ✅ Client ID é o mesmo em ambos

### Checklist de Migração

**Antes de ir para produção:**
- [ ] Todos os fluxos testados no sandbox
- [ ] Tratamento de erros implementado
- [ ] Webhooks configurados e testados
- [ ] Update mode (ITEM_LOGIN_REQUIRED) implementado
- [ ] Logs e monitoramento prontos
- [ ] Código revisado e testado

**Ao migrar:**
- [ ] Trocar `Environment.Sandbox` → `Environment.Production`
- [ ] Trocar `sandbox_secret` → `production_secret`
- [ ] Remover chamadas a endpoints `/sandbox/*`
- [ ] Atualizar URLs de webhook (se aplicável)
- [ ] Testar com 1-2 contas reais primeiro
- [ ] Monitorar logs por 24-48h

---

## ⚠️ Diferenças Sandbox vs Production

### O Que o Sandbox NÃO Simula

**Comportamentos específicos de instituições:**
- ❌ Limites de histórico por banco (sandbox sempre retorna 90 dias)
- ❌ OAuth real de cada banco (usa fluxo genérico)
- ❌ Quirks específicos de cada instituição
- ❌ Velocidade real de sincronização

**Comunicações:**
- ❌ E-mails de confirmação não são enviados
- ❌ SMS de verificação não são enviados
- ❌ Notificações push não funcionam

**Requisitos:**
- ✅ Sandbox aceita `http://` em redirect URIs
- ❌ Production requer `https://` obrigatório
- ✅ Sandbox não exige use case configurado
- ❌ Production exige use case no Link (desde Out/2024)

**Consistência de dados:**
- ⚠️ Saldos podem não bater com transações
- ⚠️ Transferências não aparecem em transactions
- ⚠️ Alguns produtos (Signal) retornam dados aleatórios

### O Que Funciona Igual

**Funcionalidades idênticas:**
- ✅ Estrutura de API (endpoints, parâmetros)
- ✅ Formatos de resposta
- ✅ Códigos de erro
- ✅ Rate limits (mesmos limites)
- ✅ Webhooks (mesmos tipos)
- ✅ SDKs (mesmo código)

---

## 🎯 Casos de Uso Recomendados

### 1. **Desenvolvimento Inicial** ✅
**Use:** Sandbox exclusivamente  
**Por quê:** Grátis, rápido, sem risco

### 2. **Testes Automatizados** ✅
**Use:** Sandbox + `/sandbox/public_token/create`  
**Por quê:** Bypass Link UI, testes repetíveis

### 3. **Testes Manuais/QA** ✅
**Use:** Sandbox com Link UI  
**Por quê:** Simula experiência do usuário

### 4. **Validação Final** ⚠️
**Use:** Production (Trial/Limited Production)  
**Por quê:** Teste com dados reais antes de lançar

### 5. **Produção** ❌
**Use:** Production aprovado  
**Por quê:** Dados reais, billing ativo

---

## 📝 Exemplo Completo - Fluxo de Teste

```python
#!/usr/bin/env python3
"""
Exemplo completo de teste no Plaid Sandbox
"""
from plaid.api import plaid_api
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.products import Products
from plaid import Configuration, ApiClient, Environment
from datetime import date, timedelta

# Configuração
CLIENT_ID = 'seu_client_id'
SANDBOX_SECRET = 'seu_sandbox_secret'

configuration = Configuration(
    host=Environment.Sandbox,
    api_key={'clientId': CLIENT_ID, 'secret': SANDBOX_SECRET}
)
client = plaid_api.PlaidApi(ApiClient(configuration))

# 1. Criar item de teste
print("1️⃣ Criando item de teste...")
sandbox_request = SandboxPublicTokenCreateRequest(
    institution_id='ins_109508',
    initial_products=[Products('transactions')]
)
sandbox_response = client.sandbox_public_token_create(sandbox_request)
public_token = sandbox_response['public_token']
print(f"   ✅ Public token: {public_token[:20]}...")

# 2. Trocar por access token
print("\n2️⃣ Trocando por access token...")
exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
exchange_response = client.item_public_token_exchange(exchange_request)
access_token = exchange_response['access_token']
print(f"   ✅ Access token: {access_token[:20]}...")

# IMPORTANTE: Salve este access_token!
# Em produção, você guardaria no banco de dados

# 3. Buscar transações
print("\n3️⃣ Buscando transações...")
transactions_request = TransactionsGetRequest(
    access_token=access_token,
    start_date=date.today() - timedelta(days=30),
    end_date=date.today()
)
transactions_response = client.transactions_get(transactions_request)
transactions = transactions_response['transactions']

print(f"   ✅ {len(transactions)} transações encontradas!")

# 4. Processar transações
print("\n4️⃣ Primeiras 5 transações:")
for txn in transactions[:5]:
    tipo = "Débito" if txn['amount'] > 0 else "Crédito"
    print(f"   {txn['date']} | {tipo} | {txn['amount']:8.2f} | {txn['name']}")

print("\n✅ Teste concluído com sucesso!")
print("\n📝 Próximo passo: Salvar access_token e integrar com seu sistema")
```

---

## 🔗 Recursos Úteis

### Documentação Oficial
- [Sandbox Overview](https://plaid.com/docs/sandbox/)
- [Test Credentials](https://plaid.com/docs/sandbox/test-credentials/)
- [Sandbox Institutions](https://plaid.com/docs/sandbox/institutions/)
- [API Reference - Sandbox Endpoints](https://plaid.com/docs/api/sandbox/)

### Dashboard Plaid
- [Obter Credenciais Sandbox](https://dashboard.plaid.com/team/keys)
- [Configurar Webhooks](https://dashboard.plaid.com/developers/webhooks)
- [Ver Activity Logs](https://dashboard.plaid.com/activity)

### Código Exemplo
- [Plaid Quickstart (Python)](https://github.com/plaid/quickstart/tree/master/python)
- [Plaid Pattern (App Completo)](https://github.com/plaid/pattern)

---

## ❓ FAQ - Perguntas Frequentes

### O sandbox expira?
❌ **Não!** Sandbox é **grátis permanentemente** e nunca expira.

### Quantos items posso criar?
✅ **Ilimitados!** Crie quantos quiser para testes.

### Os dados mudam?
⚠️ **Sim, parcialmente.** Dados base são estáticos, mas você pode simular mudanças com endpoints sandbox.

### Posso testar com meu banco real?
❌ **Não no sandbox.** Use Production (Trial/Limited) para dados reais.

### Sandbox conta para billing?
✅ **Não!** Sandbox é **100% gratuito** e não conta para faturamento.

### Quando devo ir para produção?
✅ Quando:
- Todos os fluxos estiverem testados
- Tratamento de erros estiver completo
- Estiver pronto para testar com dados reais
- Tiver aprovação de produção do Plaid

---

## 🎓 Próximos Passos

**Você já tem:**
- ✅ Script de teste funcionando ([test_plaid_sandbox.py](../test_plaid_sandbox.py))
- ✅ Credenciais sandbox configuradas
- ✅ Entendimento do fluxo básico

**Próximas ações:**

1. **Hoje (1-2h):**
   - Execute `python test_plaid_sandbox.py`
   - Explore os dados retornados
   - Teste diferentes cenários

2. **Esta semana (4-6h):**
   - Adapte `sync_openfinance.py` para Plaid
   - Mapeie campos Pluggy → Plaid
   - Teste inserção no banco de dados

3. **Quando produção aprovar:**
   - Troque credenciais sandbox → production
   - Conecte contas reais
   - Monitore por 24-48h
   - Migre do Pluggy definitivamente

---

**Criado em:** 21/04/2026  
**Autor:** Sistema Financeiro  
**Status:** ✅ Guia completo de sandbox

**💡 Lembre-se:** Sandbox é seu ambiente seguro para testar tudo antes de ir para produção!
