"""
Lista todas as transações dos últimos 3 meses do Mercado Pago
"""
import requests
from datetime import datetime, timedelta
import json

CLIENT_ID = '0774411c-feca-44dc-83df-b5ab7a1735a6'
CLIENT_SECRET = '3bd7389d-72d6-419a-804a-146e3e0eaacf'
ITEM_ID = '879f822e-ad2b-48bb-8137-cf761ab1a1a3'  # Mercado Pago REAL

BASE_URL = 'https://api.pluggy.ai'

print("=" * 100)
print("💰 TRANSAÇÕES DOS ÚLTIMOS 3 MESES - MERCADO PAGO")
print("=" * 100)

# Autenticar
print("\n🔐 Autenticando...")
auth_response = requests.post(f'{BASE_URL}/auth', json={
    'clientId': CLIENT_ID,
    'clientSecret': CLIENT_SECRET
})
api_key = auth_response.json()['apiKey']
headers = {'X-API-KEY': api_key}
print("✅ Autenticado com sucesso")

# Buscar contas
print("\n🏦 Buscando contas...")
accounts_response = requests.get(f'{BASE_URL}/accounts?itemId={ITEM_ID}', headers=headers)
accounts = accounts_response.json().get('results', [])
print(f"✅ {len(accounts)} conta(s) encontrada(s)")

# Período: últimos 3 meses
date_to = datetime.now()
date_from = date_to - timedelta(days=90)
print(f"\n📅 Período: {date_from.strftime('%d/%m/%Y')} a {date_to.strftime('%d/%m/%Y')}")

# Para cada conta, buscar transações
todas_transacoes = []

for acc in accounts:
    account_id = acc['id']
    account_name = acc['name']
    
    print(f"\n{'=' * 100}")
    print(f"🏦 Conta: {account_name}")
    print(f"   ID: {account_id}")
    print(f"   Saldo: R$ {acc['balance']:.2f}")
    print(f"{'=' * 100}")
    
    # Buscar transações com paginação
    page = 1
    total_transacoes = 0
    
    while True:
        trans_url = f'{BASE_URL}/transactions'
        params = {
            'accountId': account_id,
            'from': date_from.strftime('%Y-%m-%d'),
            'to': date_to.strftime('%Y-%m-%d'),
            'page': page,
            'pageSize': 500  # Máximo por página
        }
        
        trans_response = requests.get(trans_url, headers=headers, params=params)
        trans_data = trans_response.json()
        
        transactions = trans_data.get('results', [])
        if not transactions:
            break
            
        todas_transacoes.extend(transactions)
        total_transacoes += len(transactions)
        
        print(f"\n📄 Página {page}: {len(transactions)} transações")
        
        # Verificar se tem mais páginas
        if page >= trans_data.get('totalPages', 1):
            break
        
        page += 1
    
    print(f"\n✅ Total de transações na conta: {total_transacoes}")

# Ordenar por data (mais recente primeiro)
todas_transacoes.sort(key=lambda x: x['date'], reverse=True)

print(f"\n{'=' * 100}")
print(f"📊 RESUMO GERAL")
print(f"{'=' * 100}")
print(f"Total de transações: {len(todas_transacoes)}")

# Estatísticas
creditos = [t for t in todas_transacoes if t['type'] == 'CREDIT']
debitos = [t for t in todas_transacoes if t['type'] == 'DEBIT']

total_credito = sum(t['amount'] for t in creditos)
total_debito = sum(abs(t['amount']) for t in debitos)

print(f"\n💵 Créditos: {len(creditos)} transações = R$ {total_credito:.2f}")
print(f"💸 Débitos: {len(debitos)} transações = R$ {total_debito:.2f}")
print(f"💰 Saldo do período: R$ {(total_credito - total_debito):.2f}")

# Listar todas as transações
print(f"\n{'=' * 100}")
print(f"📋 LISTA COMPLETA DE TRANSAÇÕES")
print(f"{'=' * 100}")

for idx, trans in enumerate(todas_transacoes, 1):
    # Data formatada
    data_obj = datetime.fromisoformat(trans['date'].replace('Z', '+00:00'))
    data_br = data_obj.strftime('%d/%m/%Y %H:%M')
    
    # Tipo e símbolo
    tipo = trans['type']
    simbolo = '📈' if tipo == 'CREDIT' else '📉'
    sinal = '+' if tipo == 'CREDIT' else '-'
    
    # Valor
    valor = trans['amount']
    
    # Descrição
    descricao = trans['description']
    
    # Categoria
    categoria = trans.get('category', 'Sem categoria')
    
    print(f"\n{idx:3d}. {simbolo} {data_br}")
    print(f"     {sinal}R$ {abs(valor):>10.2f} | {descricao}")
    print(f"     Categoria: {categoria}")
    
    # Dados de pagamento (se disponível)
    if trans.get('paymentData'):
        payment = trans['paymentData']
        if payment.get('paymentMethod'):
            print(f"     Método: {payment['paymentMethod']}")
        if payment.get('receiver', {}).get('documentNumber', {}).get('value'):
            print(f"     CPF: {payment['receiver']['documentNumber']['value']}")

print(f"\n{'=' * 100}")
print(f"✅ Listagem completa!")
print(f"{'=' * 100}")

# Salvar em JSON para análise
output_file = 'transacoes_3meses.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'periodo': {
            'inicio': date_from.strftime('%Y-%m-%d'),
            'fim': date_to.strftime('%Y-%m-%d')
        },
        'resumo': {
            'total_transacoes': len(todas_transacoes),
            'creditos': {
                'quantidade': len(creditos),
                'total': total_credito
            },
            'debitos': {
                'quantidade': len(debitos),
                'total': total_debito
            },
            'saldo_periodo': total_credito - total_debito
        },
        'transacoes': todas_transacoes
    }, f, indent=2, ensure_ascii=False)

print(f"\n💾 Dados salvos em: {output_file}")
