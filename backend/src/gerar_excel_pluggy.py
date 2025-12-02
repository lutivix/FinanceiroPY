"""
Gera Excel consolidado a partir das transações do Pluggy
Formato compatível com consolidado_temp.xlsx
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import requests
from datetime import datetime, timedelta
import pandas as pd
from models import TransactionSource, TransactionCategory, Transaction, get_card_source
from database import CategoryRepository
from services.categorization_service import CategorizationService

# Configurações
CLIENT_ID = '0774411c-feca-44dc-83df-b5ab7a1735a6'
CLIENT_SECRET = '3bd7389d-72d6-419a-804a-146e3e0eaacf'
ITEM_ID = '60cbf151-aaed-45c7-afac-f2aab15e6299'  # Itaú
BASE_URL = 'https://api.pluggy.ai'

# Período do ciclo 19-18 para Novembro
# 19/10/2025 a 18/11/2025
date_from = datetime(2025, 10, 19)
date_to = datetime(2025, 11, 18)

print("=" * 100)
print("📊 GERANDO EXCEL CONSOLIDADO PLUGGY - NOVEMBRO 2025")
print("=" * 100)
print(f"Período: {date_from.strftime('%d/%m/%Y')} a {date_to.strftime('%d/%m/%Y')}")
print(f"Ciclo: 19-18 (Novembro 2025)")

# 1. Autenticar
print("\n🔐 Autenticando...")
auth_response = requests.post(f'{BASE_URL}/auth', json={
    'clientId': CLIENT_ID,
    'clientSecret': CLIENT_SECRET
})
api_key = auth_response.json()['apiKey']
headers = {'X-API-KEY': api_key}
print("✅ Autenticado")

# 2. Buscar contas
print("\n🏦 Buscando contas...")
accounts_response = requests.get(f'{BASE_URL}/accounts?itemId={ITEM_ID}', headers=headers)
accounts = accounts_response.json().get('results', [])
print(f"✅ {len(accounts)} conta(s) encontrada(s)")

# 3. Buscar transações de todas as contas
print("\n💰 Buscando transações...")
todas_transacoes_pluggy = []

for acc in accounts:
    account_id = acc['id']
    account_name = acc['name']
    account_type = acc['type']
    account_number = acc.get('number', '')
    
    print(f"   • {account_name} ({account_type})...", end=' ')
    
    page = 1
    count = 0
    
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
        
        # Adiciona metadados da conta
        for t in transactions:
            t['_account_name'] = account_name
            t['_account_type'] = account_type
            t['_account_number'] = account_number
            
        todas_transacoes_pluggy.extend(transactions)
        count += len(transactions)
        
        if page >= trans_data.get('totalPages', 1):
            break
        page += 1
    
    print(f"{count} transações")

print(f"\n✅ Total: {len(todas_transacoes_pluggy)} transações")

# 4. Transformar para modelo Transaction e categorizar
print("\n🏷️  Categorizando transações...")

# Inicializa serviço de categorização
db_path = Path(__file__).parent.parent.parent / 'dados' / 'db' / 'financeiro.db'
category_repo = CategoryRepository(str(db_path))
categorization_service = CategorizationService(category_repo)

# Mapeamento de mês
meses_pt = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

df_data = []

for trans_pluggy in todas_transacoes_pluggy:
    # Data
    data_obj = datetime.fromisoformat(trans_pluggy['date'].replace('Z', '+00:00'))
    data = data_obj.date()
    
    # Descrição
    descricao = trans_pluggy['description']
    
    # Valor - usar amountInAccountCurrency se disponível (conversão de moeda)
    valor_original = trans_pluggy['amount']
    valor = trans_pluggy.get('amountInAccountCurrency') or valor_original
    
    # Se moeda estrangeira, adicionar info na descrição
    if trans_pluggy.get('currencyCode') != 'BRL' and trans_pluggy.get('amountInAccountCurrency'):
        moeda = trans_pluggy['currencyCode']
        descricao = f"{descricao} ({moeda} {abs(valor_original):.2f})"
    
    # Determinar Fonte baseado no tipo de conta e número do cartão
    account_type = trans_pluggy['_account_type']
    account_name = trans_pluggy['_account_name']
    account_number = trans_pluggy['_account_number']
    
    if account_type == 'BANK':
        # Conta corrente = PIX
        fonte = TransactionSource.PIX
    else:
        # Cartão de crédito - pega final do cartão
        credit_meta = trans_pluggy.get('creditCardMetadata', {})
        card_number = credit_meta.get('cardNumber', '')
        
        if not card_number and account_number:
            # Tenta extrair final do número da conta
            card_number = account_number[-4:] if len(account_number) >= 4 else ''
        
        # Determina banco pelo nome da conta
        if 'LATAM' in account_name.upper() or 'VISA' in account_name.upper():
            bank = 'latam'
        else:
            bank = 'itau'
        
        # Mapeia usando função existente
        fonte = get_card_source(card_number, bank)
    
    # Mês de Competência (ciclo 19-18)
    # Como já filtramos pelo período correto, sabemos que é Novembro 2025
    mes_comp = "Novembro 2025"
    
    # Criar Transaction para categorizar
    transaction = Transaction(
        date=data,
        description=descricao,
        amount=valor,
        source=fonte,
        category=TransactionCategory.A_DEFINIR,
        month_ref=mes_comp
    )
    
    # Aplicar categorização inteligente
    categoria = categorization_service.categorize_transaction(transaction)
    
    # Informações extras
    categoria_banco = trans_pluggy.get('category', 'Sem categoria')
    tipo_transacao = trans_pluggy['type']
    provider_id = trans_pluggy.get('providerId', '')
    
    # Informação de parcelas
    credit_meta = trans_pluggy.get('creditCardMetadata', {})
    parcela_info = ""
    if credit_meta and credit_meta.get('totalInstallments'):
        parcela_num = credit_meta.get('installmentNumber', 1)
        parcela_total = credit_meta.get('totalInstallments', 1)
        parcela_info = f"{parcela_num}/{parcela_total}"
    
    # Monta linha do DataFrame
    df_data.append({
        'Data': data,
        'Descricao': descricao,
        'Fonte': fonte.value,
        'Valor': valor,
        'Categoria': categoria.value,
        'MesComp': mes_comp,
        # Colunas extras
        'Origem_Banco': account_name,
        'Tipo_Conta': account_type,
        'Categoria_Banco': categoria_banco,
        'Tipo_Transacao': tipo_transacao,
        'Parcela': parcela_info,
        'Provider_ID': provider_id
    })

print(f"✅ {len(df_data)} transações categorizadas")

# 5. Criar DataFrame e ordenar
print("\n📊 Gerando Excel...")
df = pd.DataFrame(df_data)

# Ordena por MesComp, Fonte (desc) e Data (igual ao consolidado_temp.xlsx)
df = df.sort_values(['MesComp', 'Fonte', 'Data'], ascending=[True, False, True])

# 6. Salvar Excel
output_dir = Path(__file__).parent.parent.parent / 'dados' / 'planilhas'
output_file = output_dir / 'consolidado_pluggy_nov2025.xlsx'

df.to_excel(output_file, index=False)

print(f"✅ Excel gerado: {output_file}")

# 7. Estatísticas
print(f"\n{'=' * 100}")
print("📈 ESTATÍSTICAS")
print(f"{'=' * 100}")

total_transacoes = len(df)
creditos = df[df['Tipo_Transacao'] == 'CREDIT']
debitos = df[df['Tipo_Transacao'] == 'DEBIT']

print(f"Total de transações: {total_transacoes}")
print(f"Créditos: {len(creditos)} = R$ {creditos['Valor'].sum():.2f}")
print(f"Débitos: {len(debitos)} = R$ {debitos['Valor'].sum():.2f}")

print(f"\nTransações por fonte:")
for fonte, count in df['Fonte'].value_counts().items():
    print(f"  • {fonte}: {count} transações")

print(f"\nTop 10 categorias:")
for cat, count in df['Categoria'].value_counts().head(10).items():
    print(f"  • {cat}: {count} transações")

# Parceladas
parceladas = df[df['Parcela'] != '']
print(f"\nTransações parceladas: {len(parceladas)}")

# A definir
a_definir = df[df['Categoria'] == 'A definir']
print(f"Sem categoria: {len(a_definir)} ({len(a_definir)/total_transacoes*100:.1f}%)")

print(f"\n{'=' * 100}")
print("✅ CONCLUÍDO!")
print(f"{'=' * 100}")
