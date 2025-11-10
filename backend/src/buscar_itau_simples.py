"""
Buscar transações do Itaú e salvar em JSON (sem output de console)
"""
import requests
from datetime import datetime, timedelta
import json

CLIENT_ID = '0774411c-feca-44dc-83df-b5ab7a1735a6'
CLIENT_SECRET = '3bd7389d-72d6-419a-804a-146e3e0eaacf'
ITEM_ID = '60cbf151-aaed-45c7-afac-f2aab15e6299'  # Itaú REAL
BASE_URL = 'https://api.pluggy.ai'

# Autenticar
auth_response = requests.post(f'{BASE_URL}/auth', json={
    'clientId': CLIENT_ID,
    'clientSecret': CLIENT_SECRET
})
api_key = auth_response.json()['apiKey']
headers = {'X-API-KEY': api_key}

# Buscar contas
accounts_response = requests.get(f'{BASE_URL}/accounts?itemId={ITEM_ID}', headers=headers)
accounts = accounts_response.json().get('results', [])

# Período: últimos 3 meses
date_to = datetime.now()
date_from = date_to - timedelta(days=90)

todas_transacoes = []
todas_contas = []

for acc in accounts:
    account_id = acc['id']
    account_name = acc['name']
    
    # Salvar info da conta
    todas_contas.append({
        'id': account_id,
        'name': account_name,
        'type': acc['type'],
        'subtype': acc.get('subtype'),
        'balance': acc['balance'],
        'number': acc.get('number'),
        'owner': acc.get('owner')
    })
    
    # Buscar transações
    page = 1
    while True:
        params = {
            'accountId': account_id,
            'from': date_from.strftime('%Y-%m-%d'),
            'to': date_to.strftime('%Y-%m-%d'),
            'page': page,
            'pageSize': 500
        }
        
        trans_response = requests.get(f'{BASE_URL}/transactions', headers=headers, params=params)
        trans_data = trans_response.json()
        transactions = trans_data.get('results', [])
        
        if not transactions:
            break
        
        # Adicionar nome da conta
        for t in transactions:
            t['_account_name'] = account_name
            t['_account_type'] = acc['type']
            
        todas_transacoes.extend(transactions)
        
        if page >= trans_data.get('totalPages', 1):
            break
        page += 1

# Ordenar por data
todas_transacoes.sort(key=lambda x: x['date'], reverse=True)

# Estatísticas
creditos = [t for t in todas_transacoes if t['type'] == 'CREDIT']
debitos = [t for t in todas_transacoes if t['type'] == 'DEBIT']
total_credito = sum(t['amount'] for t in creditos)
total_debito = sum(abs(t['amount']) for t in debitos)

# Categorias
categorias = {}
for t in todas_transacoes:
    cat = t.get('category', 'Sem categoria')
    categorias[cat] = categorias.get(cat, 0) + 1

# Salvar em JSON
output = {
    'banco': 'Itaú',
    'item_id': ITEM_ID,
    'periodo': {
        'inicio': date_from.strftime('%Y-%m-%d'),
        'fim': date_to.strftime('%Y-%m-%d')
    },
    'contas': todas_contas,
    'resumo': {
        'total_contas': len(todas_contas),
        'total_transacoes': len(todas_transacoes),
        'creditos': {
            'quantidade': len(creditos),
            'total': round(total_credito, 2)
        },
        'debitos': {
            'quantidade': len(debitos),
            'total': round(total_debito, 2)
        },
        'movimentacao_total': round(total_credito + total_debito, 2),
        'categorias': categorias
    },
    'transacoes': todas_transacoes
}

with open('transacoes_itau_3meses.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Total de contas: {len(todas_contas)}")
print(f"Total de transacoes: {len(todas_transacoes)}")
print(f"Creditos: {len(creditos)} = R$ {total_credito:.2f}")
print(f"Debitos: {len(debitos)} = R$ {total_debito:.2f}")
print(f"\nDados salvos em: transacoes_itau_3meses.json")
