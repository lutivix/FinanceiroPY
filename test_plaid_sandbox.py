#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Conexão Plaid Sandbox
Valida integração básica com API Plaid usando credenciais sandbox
"""

from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid import Configuration, ApiClient, Environment
from datetime import date, timedelta

# Configuração Sandbox
CLIENT_ID = '69e7b1383357a7000e4e1ebb'
SECRET = '9229419b2929fdb0b28082ed5a4592'

print("="*60)
print("🧪 TESTE PLAID SANDBOX - FINANCEIRO PERSONAL")
print("="*60)

# Inicializar cliente
configuration = Configuration(
    host=Environment.Sandbox,
    api_key={
        'clientId': CLIENT_ID,
        'secret': SECRET,
    }
)

client = plaid_api.PlaidApi(ApiClient(configuration))

# ============================================================
# TESTE 1: Criar Link Token
# ============================================================
print("\n[1/5] 🔗 Criando Link Token...")
try:
    request = LinkTokenCreateRequest(
        products=[Products("transactions"), Products("investments")],
        client_name="Financeiro Personal",
        country_codes=[CountryCode('US')],  # Temporário - US sempre funciona
        language='en',  # Inglês para US
        user=LinkTokenCreateRequestUser(
            client_user_id='test_user_financeiro'
        )
    )
    
    response = client.link_token_create(request)
    link_token = response['link_token']
    print(f"   ✅ Link token criado: {link_token[:30]}...")
except Exception as e:
    print(f"   ❌ Erro: {e}")
    exit(1)

# ============================================================
# TESTE 2: Criar Item de Teste (Simula conexão bancária)
# ============================================================
print("\n[2/5] 🏦 Criando item de teste no sandbox...")
try:
    # Usar First Platypus Bank (banco de teste global)
    sandbox_request = SandboxPublicTokenCreateRequest(
        institution_id='ins_109508',  # First Platypus Bank
        initial_products=[Products('transactions'), Products('investments')]
    )
    sandbox_response = client.sandbox_public_token_create(sandbox_request)
    public_token = sandbox_response['public_token']
    print(f"   ✅ Public token: {public_token[:30]}...")
except Exception as e:
    print(f"   ❌ Erro: {e}")
    exit(1)

# ============================================================
# TESTE 3: Trocar por Access Token (permanente)
# ============================================================
print("\n[3/5] 🔑 Trocando por access token...")
try:
    exchange_request = ItemPublicTokenExchangeRequest(
        public_token=public_token
    )
    exchange_response = client.item_public_token_exchange(exchange_request)
    access_token = exchange_response['access_token']
    item_id = exchange_response['item_id']
    print(f"   ✅ Access token: {access_token[:30]}...")
    print(f"   ✅ Item ID: {item_id}")
except Exception as e:
    print(f"   ❌ Erro: {e}")
    exit(1)

# ============================================================
# TESTE 4: Buscar Contas
# ============================================================
print("\n[4/5] 💳 Buscando contas conectadas...")
try:
    accounts_request = AccountsGetRequest(
        access_token=access_token
    )
    accounts_response = client.accounts_get(accounts_request)
    accounts = accounts_response['accounts']
    
    print(f"   ✅ {len(accounts)} contas encontradas:\n")
    for acc in accounts:
        balance = acc['balances']['current'] or 0
        print(f"      📊 {acc['name']}")
        print(f"         Tipo: {acc['type']} / {acc['subtype']}")
        print(f"         Saldo: {acc['balances']['iso_currency_code']} {balance:,.2f}")
        print(f"         ID: {acc['account_id']}")
        print()
except Exception as e:
    print(f"   ❌ Erro: {e}")
    exit(1)

# ============================================================
# TESTE 5: Buscar Transações
# ============================================================
print("[5/5] 📋 Buscando transações (últimos 90 dias)...")
try:
    start_date = date.today() - timedelta(days=90)
    end_date = date.today()
    
    transactions_request = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date
    )
    transactions_response = client.transactions_get(transactions_request)
    transactions = transactions_response['transactions']
    total_transactions = transactions_response['total_transactions']
    
    print(f"   ✅ {total_transactions} transações encontradas!\n")
    
    # Mostrar primeiras 10 transações
    print("   📝 Primeiras 10 transações:")
    print("   " + "-"*70)
    for txn in transactions[:10]:
        # Plaid usa positivo = débito, negativo = crédito
        tipo = "💸 Débito " if txn['amount'] > 0 else "💰 Crédito"
        valor = abs(txn['amount'])
        categoria = txn['category'][0] if txn.get('category') else 'Sem categoria'
        
        print(f"   {txn['date']} | {tipo} | {txn['iso_currency_code']} {valor:8.2f}")
        print(f"      {txn['name'][:50]}")
        print(f"      Categoria: {categoria}")
        print()
    
    if total_transactions > 10:
        print(f"   ... e mais {total_transactions - 10} transações")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")
    exit(1)

# ============================================================
# RESUMO FINAL
# ============================================================
print("\n" + "="*60)
print("✅ TODOS OS TESTES PASSARAM!")
print("="*60)
print(f"""
📊 RESUMO:
   • Link Token:      Criado com sucesso
   • Item/Conexão:    Criado (banco de teste)
   • Access Token:    {access_token[:20]}...
   • Contas:          {len(accounts)} encontradas
   • Transações:      {total_transactions} encontradas (90 dias)

🎯 PRÓXIMOS PASSOS:
   1. ✅ Integração com Plaid funcionando!
   2. ⏳ Aguardar aprovação de produção (status: Requested)
   3. 🔧 Adaptar sync_openfinance.py para usar Plaid
   4. 📊 Mapear estrutura Plaid → Banco de dados
   5. 🚀 Quando aprovado: trocar sandbox → production

💰 CUSTO ESTIMADO (quando aprovar produção):
   • 4 contas × ($0.30 + $0.18) = $1.08/mês ≈ R$ 5,40/mês
   • Economia de R$ 490/mês vs Belvo
   • Economia de R$ 2.495/mês vs Pluggy

🔗 Links úteis:
   • Dashboard: https://dashboard.plaid.com
   • Docs: https://plaid.com/docs/
   • API Reference: https://plaid.com/docs/api/

⚠️  LEMBRETE: Essas são credenciais SANDBOX (desenvolvimento)
   Quando produção aprovar, você receberá credenciais diferentes!
""")
print("="*60)
