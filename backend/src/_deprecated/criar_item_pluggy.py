"""
Script para criar Item (conectar conta) no Pluggy via API
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pluggy_sdk import Configuration, ApiClient, AuthApi, ConnectorApi, ItemsApi
from pluggy_sdk.models import AuthRequest, CreateItem, CreateItemParameters
import time

# Credenciais
CLIENT_ID = '0774411c-feca-44dc-83df-b5ab7a1735a6'
CLIENT_SECRET = '3bd7389d-72d6-419a-804a-146e3e0eaacf'

print("=" * 70)
print("🔌 CRIAR ITEM PLUGGY - Conectar Conta Bancária")
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

# 2. Configurar cliente autenticado
print("\n2️⃣  Configurando cliente...")
cfg_auth = Configuration(access_token=access_token)
with ApiClient(cfg_auth) as api_client:
    connector_api = ConnectorApi(api_client)
    item_api = ItemsApi(api_client)
    
    # 3. Listar conectores disponíveis
    print("\n3️⃣  Buscando conectores disponíveis...")
    connectors_response = connector_api.connectors_list()
    connectors = connectors_response.results if hasattr(connectors_response, 'results') else []
    
    print(f"\n   📋 {len(connectors)} conectores disponíveis:")
    print("\n   BANCOS DE TESTE (Sandbox):")
    for conn in connectors[:5]:
        conn_dict = conn.to_dict() if hasattr(conn, 'to_dict') else conn
        if isinstance(conn_dict, dict):
            print(f"   • ID {conn_dict.get('id')}: {conn_dict.get('name')}")
    
    # 4. Criar Item com Pluggy Bank (banco de teste)
    print("\n4️⃣  Criando Item com Pluggy Bank (banco de teste)...")
    print("   Usando credenciais de teste: user-ok / password-ok")
    
    # Preparar parâmetros
    parameters = CreateItemParameters(
        user='user-ok',
        password='password-ok'
    )
    
    # Criar Item
    item_request = CreateItem(
        connector_id=201,  # ID do Pluggy Bank
        parameters=parameters
    )
    
    try:
        item_response = item_api.items_create(item_request)
        item_dict = item_response.to_dict() if hasattr(item_response, 'to_dict') else item_response
        
        item_id = item_dict.get('id')
        status = item_dict.get('status')
        
        print(f"\n   ✅ Item criado com sucesso!")
        print(f"   📌 Item ID: {item_id}")
        print(f"   📊 Status: {status}")
        
        # 5. Aguardar sincronização
        print("\n5️⃣  Aguardando sincronização com o banco...")
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            time.sleep(2)
            attempt += 1
            
            # Buscar status atualizado
            updated_item = item_api.items_retrieve(item_id)
            updated_dict = updated_item.to_dict() if hasattr(updated_item, 'to_dict') else updated_item
            current_status = updated_dict.get('status')
            
            print(f"   ⏳ Tentativa {attempt}/{max_attempts} - Status: {current_status}")
            
            if current_status in ['UPDATED', 'PARTIAL_SUCCESS']:
                print(f"\n   ✅ Sincronização concluída! Status: {current_status}")
                break
            elif current_status in ['LOGIN_ERROR', 'OUTDATED', 'ERROR']:
                print(f"\n   ❌ Erro na sincronização: {current_status}")
                break
        
        print("\n" + "=" * 70)
        print("✅ ITEM CRIADO COM SUCESSO!")
        print("=" * 70)
        print(f"\n🔑 COPIE ESTE ITEM ID: {item_id}")
        print("\nAgora você pode usar este ID para buscar contas e transações!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n   ❌ Erro ao criar item: {e}")
        import traceback
        traceback.print_exc()
