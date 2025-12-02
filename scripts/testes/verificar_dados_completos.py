"""
Verificar TODOS os campos disponíveis na API Pluggy
"""
import requests
from datetime import datetime, timedelta
import json

CLIENT_ID = '0774411c-feca-44dc-83df-b5ab7a1735a6'
CLIENT_SECRET = '3bd7389d-72d6-419a-804a-146e3e0eaacf'
# ITEM_ID = '06f300c4-75e0-4a2f-bbea-e0fb1a1a13cf'  # Sandbox
ITEM_ID = '879f822e-ad2b-48bb-8137-cf761ab1a1a3'  # Mercado Pago REAL

BASE_URL = 'https://api.pluggy.ai'

# Autenticar
auth_response = requests.post(f'{BASE_URL}/auth', json={
    'clientId': CLIENT_ID,
    'clientSecret': CLIENT_SECRET
})
api_key = auth_response.json()['apiKey']
headers = {'X-API-KEY': api_key}

# Buscar contas
print("=" * 80)
print("📊 DADOS COMPLETOS DISPONÍVEIS NA API PLUGGY")
print("=" * 80)

accounts_response = requests.get(f'{BASE_URL}/accounts?itemId={ITEM_ID}', headers=headers)
accounts = accounts_response.json().get('results', [])

for acc in accounts:
    print(f"\n{'=' * 80}")
    print(f"🏦 CONTA: {acc['name']} (Tipo: {acc['type']})")
    print(f"{'=' * 80}")
    print(json.dumps(acc, indent=2, ensure_ascii=False))
    
    # Buscar transações
    account_id = acc['id']
    date_to = datetime.now().strftime('%Y-%m-%d')
    date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    trans_url = f'{BASE_URL}/transactions?accountId={account_id}&from={date_from}&to={date_to}'
    trans_response = requests.get(trans_url, headers=headers)
    trans_data = trans_response.json()
    
    if 'results' in trans_data and trans_data['results']:
        print(f"\n{'=' * 80}")
        print(f"💰 PRIMEIRA TRANSAÇÃO COMPLETA")
        print(f"{'=' * 80}")
        print(json.dumps(trans_data['results'][0], indent=2, ensure_ascii=False))
    else:
        print(f"\n   ℹ️  Sem transações nos últimos 30 dias")

# Buscar outros endpoints disponíveis
print(f"\n{'=' * 80}")
print("🔍 TESTANDO OUTROS ENDPOINTS")
print(f"{'=' * 80}")

# Identity
print("\n📇 Identity:")
identity_response = requests.get(f'{BASE_URL}/identity?itemId={ITEM_ID}', headers=headers)
if identity_response.status_code == 200:
    print(json.dumps(identity_response.json(), indent=2, ensure_ascii=False))
else:
    print(f"   Status {identity_response.status_code}: {identity_response.text}")

# Investments
print("\n💎 Investments:")
invest_response = requests.get(f'{BASE_URL}/investments?itemId={ITEM_ID}', headers=headers)
if invest_response.status_code == 200:
    print(json.dumps(invest_response.json(), indent=2, ensure_ascii=False))
else:
    print(f"   Status {invest_response.status_code}: {invest_response.text}")

print(f"\n{'=' * 80}")
print("✅ ANÁLISE COMPLETA")
print(f"{'=' * 80}")
