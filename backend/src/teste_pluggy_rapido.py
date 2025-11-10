#!/usr/bin/env python3
"""
Script de teste rápido para Pluggy - COM CREDENCIAIS HARD-CODED
Apenas para teste! NÃO COMMITE ESTE ARQUIVO!
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Adiciona o diretório pai ao path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from integrations.pluggy_client import PluggyClient, PLUGGY_AVAILABLE
from integrations.pluggy_sync import PluggySyncService

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ⚠️ CREDENCIAIS - APENAS PARA TESTE!
CLIENT_ID = "0774411c-feca-44dc-83df-b5ab7a1735a6"
CLIENT_SECRET = "3bd7389d-72d6-419a-804a-146e3e0eaacf"

def main():
    """Testa a integração com Pluggy."""
    
    print("=" * 70)
    print("🔌 TESTE RÁPIDO - PLUGGY")
    print("=" * 70)
    print()
    
    if not PLUGGY_AVAILABLE:
        print("❌ Pluggy SDK não instalado!")
        print("Execute: pip install pluggy-sdk")
        return
    
    try:
        # 1. Inicializa cliente
        print("1️⃣  Inicializando cliente...")
        client = PluggyClient(CLIENT_ID, CLIENT_SECRET)
        
        # 2. Testa conexão
        print("2️⃣  Testando conexão...")
        if not client.test_connection():
            print("❌ Falha na conexão!")
            return
        
        # 3. Busca items
        print("3️⃣  Buscando items (contas conectadas)...")
        items = client.get_items()
        print(f"   Encontrados: {len(items)} items")
        
        # 4. Para cada item, busca contas
        print("4️⃣  Buscando contas...")
        for item in items:
            item_id = item.get('id')
            print(f"   Item ID: {item_id}")
            
            accounts = client.get_accounts(item_id)
            print(f"   Contas: {len(accounts)}")
            
            for acc in accounts:
                print(f"      - {acc.get('name')} ({acc.get('type')})")
                print(f"        Saldo: R$ {acc.get('balance', 0):,.2f}")
        
        # 5. Busca transações
        print("5️⃣  Buscando transações dos últimos 30 dias...")
        from_date = datetime.now() - timedelta(days=30)
        
        sync = PluggySyncService(client)
        transactions = sync.sync_all_transactions(from_date=from_date)
        
        print(f"   Total: {len(transactions)} transações")
        
        if transactions:
            print("\n📋 PRIMEIRAS 5 TRANSAÇÕES:")
            for i, tx in enumerate(transactions[:5], 1):
                print(f"   {i}. {tx.date} | {tx.description[:40]} | R$ {tx.amount:,.2f}")
        
        print()
        print("=" * 70)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 70)
        
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        logger.exception("Detalhes:")


if __name__ == "__main__":
    main()
