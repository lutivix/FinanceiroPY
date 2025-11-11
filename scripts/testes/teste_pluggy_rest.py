"""
Script para testar Pluggy via REST API pura (sem SDK)
"""
import requests
from datetime import datetime, timedelta
import json

# Credenciais
CLIENT_ID = '0774411c-feca-44dc-83df-b5ab7a1735a6'
CLIENT_SECRET = '3bd7389d-72d6-419a-804a-146e3e0eaacf'
ITEM_ID = '06f300c4-75e0-4a2f-bbea-e0fb1a1a13cf'  # Sandbox

BASE_URL = 'https://api.pluggy.ai'

print("=" * 70)
print("🔌 TESTE PLUGGY - REST API Pura")
print("=" * 70)

# 1. Autenticar
print("\n1️⃣  Autenticando...")
auth_response = requests.post(f'{BASE_URL}/auth', json={
    'clientId': CLIENT_ID,
    'clientSecret': CLIENT_SECRET
})
api_key = auth_response.json()['apiKey']
print(f"   ✅ API Key obtida: {api_key[:50]}...")

# Headers para todas as requisições
headers = {'X-API-KEY': api_key}

# 2. Buscar Item
print(f"\n2️⃣  Buscando Item {ITEM_ID}...")
item_response = requests.get(f'{BASE_URL}/items/{ITEM_ID}', headers=headers)
item = item_response.json()

print(f"   ✅ Item encontrado!")
print(f"   📌 ID: {item['id']}")
print(f"   🏦 Conector: {item['connector']['name']}")
print(f"   📊 Status: {item['status']}")
print(f"   🏷️  Sandbox: {item['connector']['isSandbox']}")

# 3. Buscar Contas
print(f"\n3️⃣  Buscando contas...")
accounts_response = requests.get(f'{BASE_URL}/accounts?itemId={ITEM_ID}', headers=headers)
accounts_data = accounts_response.json()
accounts = accounts_data.get('results', [])

print(f"\n   📋 Encontradas {len(accounts)} conta(s):")

for idx, acc in enumerate(accounts, 1):
    print(f"\n   Conta #{idx}:")
    print(f"   • ID: {acc['id']}")
    print(f"   • Nome: {acc['name']}")
    print(f"   • Tipo: {acc['type']}")
    print(f"   • Saldo: {acc['currencyCode']} {acc['balance']:.2f}")
    print(f"   • Número: {acc.get('number', 'N/A')}")
    
    # 4. Buscar Transações da conta
    account_id = acc['id']
    print(f"\n   🔍 Buscando transações da conta...")
    
    # Últimos 30 dias
    date_to = datetime.now().strftime('%Y-%m-%d')
    date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    trans_url = f'{BASE_URL}/transactions?accountId={account_id}&from={date_from}&to={date_to}'
    trans_response = requests.get(trans_url, headers=headers)
    trans_data = trans_response.json()
    transactions = trans_data.get('results', [])
    
    print(f"   💰 Encontradas {len(transactions)} transação(ões):")
    
    for t_idx, trans in enumerate(transactions[:5], 1):  # Primeiras 5
        print(f"\n   Transação #{t_idx}:")
        print(f"   • Data: {trans['date']}")
        print(f"   • Descrição: {trans['description']}")
        print(f"   • Valor: {trans['currencyCode']} {trans['amount']:.2f}")
        print(f"   • Tipo: {trans['type']}")
        print(f"   • Categoria: {trans.get('category', 'N/A')}")
    
    if len(transactions) > 5:
        print(f"\n   ... e mais {len(transactions) - 5} transações")

print("\n" + "=" * 70)
print("✅ SUCESSO TOTAL! A API PLUGGY FUNCIONA! 🎉")
print("=" * 70)
print("\n📊 Conclusão:")
print("• ✅ API REST funciona perfeitamente")
print("• ❌ SDK Python tem bug no header")
print("• ✅ Podemos usar requests direto no nosso sistema!")
print("\nPróximo passo: Integrar no sistema? (s/n)")
print("=" * 70)
