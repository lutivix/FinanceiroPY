"""
Script para testar acesso aos dados do Item Pluggy
"""
import sys
import os
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pluggy_sdk import Configuration, ApiClient, AuthApi, AccountApi, TransactionApi, ItemsApi
from pluggy_sdk.models import AuthRequest

# Credenciais
CLIENT_ID = '0774411c-feca-44dc-83df-b5ab7a1735a6'
CLIENT_SECRET = '3bd7389d-72d6-419a-804a-146e3e0eaacf'

# Item ID obtido do Dashboard
# ITEM_ID = '879f822e-ad2b-48bb-8137-cf761ab1a1a3'  # Mercado Pago (OAuth - não funciona)
ITEM_ID = '06f300c4-75e0-4a2f-bbea-e0fb1a1a13cf'  # Pluggy Bank Sandbox

print("=" * 70)
print("🔌 TESTE PLUGGY - Buscar Dados do Item")
print("=" * 70)

# 1. Autenticar
print("\n1️⃣  Autenticando...")
cfg = Configuration()
with ApiClient(cfg) as api_client:
    auth_api = AuthApi(api_client)
    auth_request = AuthRequest(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    auth_response = auth_api.auth_create(auth_request)
    access_token = auth_response.api_key
    print(f"   ✅ Token obtido: {access_token[:30]}...")

# 2. Buscar informações do Item
print(f"\n2️⃣  Buscando informações do Item {ITEM_ID}...")
cfg_auth = Configuration(access_token=access_token)
with ApiClient(cfg_auth) as api_client:
    items_api = ItemsApi(api_client)
    account_api = AccountApi(api_client)
    transaction_api = TransactionApi(api_client)
    
    try:
        # Buscar Item
        item = items_api.items_retrieve(ITEM_ID)
        item_dict = item.to_dict() if hasattr(item, 'to_dict') else item
        
        print(f"\n   ✅ Item encontrado!")
        print(f"   📌 ID: {item_dict.get('id')}")
        print(f"   🏦 Conector: {item_dict.get('connector', {}).get('name')}")
        print(f"   📊 Status: {item_dict.get('status')}")
        print(f"   📅 Criado em: {item_dict.get('created_at')}")
        print(f"   🔄 Última atualização: {item_dict.get('last_updated_at')}")
        
        # 3. Buscar contas
        print(f"\n3️⃣  Buscando contas do Item...")
        accounts_response = account_api.accounts_list(item_id=ITEM_ID)
        accounts = accounts_response.results if hasattr(accounts_response, 'results') else []
        
        print(f"\n   📋 Encontradas {len(accounts)} conta(s):")
        
        for idx, acc in enumerate(accounts, 1):
            acc_dict = acc.to_dict() if hasattr(acc, 'to_dict') else acc
            print(f"\n   Conta #{idx}:")
            print(f"   • ID: {acc_dict.get('id')}")
            print(f"   • Nome: {acc_dict.get('name')}")
            print(f"   • Tipo: {acc_dict.get('type')}")
            print(f"   • Saldo: R$ {acc_dict.get('balance', 0):.2f}")
            print(f"   • Moeda: {acc_dict.get('currency_code')}")
            
            # 4. Buscar transações da conta
            account_id = acc_dict.get('id')
            print(f"\n   🔍 Buscando transações da conta {account_id}...")
            
            # Últimos 30 dias
            date_to = datetime.now()
            date_from = date_to - timedelta(days=30)
            
            try:
                transactions_response = transaction_api.transactions_list(
                    account_id=account_id,
                    var_from=date_from.strftime('%Y-%m-%d'),
                    to=date_to.strftime('%Y-%m-%d')
                )
                transactions = transactions_response.results if hasattr(transactions_response, 'results') else []
                
                print(f"   💰 Encontradas {len(transactions)} transação(ões) nos últimos 30 dias:")
                
                for t_idx, trans in enumerate(transactions[:10], 1):  # Mostrar apenas 10 primeiras
                    trans_dict = trans.to_dict() if hasattr(trans, 'to_dict') else trans
                    print(f"\n   Transação #{t_idx}:")
                    print(f"   • Data: {trans_dict.get('date')}")
                    print(f"   • Descrição: {trans_dict.get('description')}")
                    print(f"   • Valor: R$ {trans_dict.get('amount', 0):.2f}")
                    print(f"   • Tipo: {trans_dict.get('type')}")
                    print(f"   • Categoria: {trans_dict.get('category')}")
                
                if len(transactions) > 10:
                    print(f"\n   ... e mais {len(transactions) - 10} transações")
                    
            except Exception as e:
                print(f"   ⚠️  Erro ao buscar transações: {e}")
        
        print("\n" + "=" * 70)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 70)
        print("\n🎉 A integração Pluggy está FUNCIONANDO!")
        print("📊 Você conseguiu acessar contas e transações via API!")
        print("\nPróximo passo: Integrar no sistema principal? (s/n)")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n   ❌ Erro ao buscar dados do Item: {e}")
        import traceback
        traceback.print_exc()
