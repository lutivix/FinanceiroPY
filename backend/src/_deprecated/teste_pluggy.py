#!/usr/bin/env python3
"""
Script de teste para integração com Pluggy
Execute este script para testar a conexão e buscar dados
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
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Testa a integração com Pluggy."""
    
    print("=" * 70)
    print("🔌 TESTE DE INTEGRAÇÃO PLUGGY - OPEN FINANCE")
    print("=" * 70)
    print()
    
    # Verifica se o SDK está instalado
    if not PLUGGY_AVAILABLE:
        print("❌ ERRO: Pluggy SDK não está instalado!")
        print()
        print("📦 Instale executando:")
        print("   pip install pluggy-sdk")
        print()
        return
    
    # Solicita credenciais
    print("🔑 CONFIGURAÇÃO DE CREDENCIAIS")
    print("-" * 70)
    print()
    print("📍 Obtenha suas credenciais em: https://dashboard.pluggy.ai/")
    print()
    
    client_id = input("CLIENT_ID: ").strip()
    client_secret = input("CLIENT_SECRET: ").strip()
    
    if not client_id or not client_secret:
        print("❌ Credenciais não fornecidas!")
        return
    
    print()
    print("=" * 70)
    print("🚀 INICIANDO TESTES...")
    print("=" * 70)
    print()
    
    try:
        # 1. Inicializa cliente
        logger.info("1️⃣ Inicializando cliente Pluggy...")
        client = PluggyClient(client_id, client_secret)
        
        # 2. Testa conexão
        logger.info("2️⃣ Testando conexão...")
        if not client.test_connection():
            logger.error("❌ Falha na conexão!")
            return
        
        # 3. Cria serviço de sincronização
        logger.info("3️⃣ Criando serviço de sincronização...")
        sync = PluggySyncService(client)
        
        # 4. Exibe resumo das contas
        sync.print_summary()
        
        # 5. Busca transações
        print()
        print("=" * 70)
        print("💰 BUSCANDO TRANSAÇÕES DOS ÚLTIMOS 30 DIAS")
        print("=" * 70)
        print()
        
        from_date = datetime.now() - timedelta(days=30)
        to_date = datetime.now()
        
        transactions = sync.sync_all_transactions(from_date, to_date)
        
        if transactions:
            logger.info(f"✅ {len(transactions)} transações encontradas!")
            print()
            print("📋 PRIMEIRAS 10 TRANSAÇÕES:")
            print("-" * 70)
            
            for i, tx in enumerate(transactions[:10], 1):
                signal = "+" if tx.amount > 0 else ""
                print(f"{i:2}. {tx.date} | {tx.description[:40]:40} | {signal}R$ {tx.amount:>10,.2f}")
                print(f"    Fonte: {tx.source.value} | Categoria: {tx.category.value}")
        else:
            logger.warning("⚠️  Nenhuma transação encontrada neste período")
        
        print()
        print("=" * 70)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 70)
        print()
        print("💡 PRÓXIMOS PASSOS:")
        print("   1. Adicione as credenciais no arquivo config.ini")
        print("   2. Execute o agente_financeiro.py para processar automaticamente")
        print("=" * 70)
        
    except Exception as e:
        logger.error(f"❌ Erro durante o teste: {e}")
        logger.exception("Detalhes do erro:")
        return


if __name__ == "__main__":
    main()
