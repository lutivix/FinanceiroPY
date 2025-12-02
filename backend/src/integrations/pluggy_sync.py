#!/usr/bin/env python3
"""
Serviço de sincronização automática com Pluggy
Converte dados do Pluggy para o formato do sistema
"""

import logging
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
import sys

# Adiciona o diretório pai ao path para imports
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from models import Transaction, TransactionSource, TransactionCategory
from integrations.pluggy_client import PluggyClient

logger = logging.getLogger(__name__)


class PluggySyncService:
    """Serviço para sincronizar dados do Pluggy com o sistema."""
    
    def __init__(self, pluggy_client: PluggyClient):
        """
        Inicializa o serviço de sincronização.
        
        Args:
            pluggy_client: Cliente Pluggy configurado
        """
        self.pluggy = pluggy_client
    
    def convert_transaction(
        self,
        pluggy_transaction: Dict[str, Any],
        account_info: Dict[str, Any]
    ) -> Transaction:
        """
        Converte uma transação do Pluggy para o modelo do sistema.
        
        Args:
            pluggy_transaction: Transação retornada pela API Pluggy
            account_info: Informações da conta
            
        Returns:
            Transaction do sistema
        """
        # Extrai informações básicas
        date_str = pluggy_transaction.get('date', '')
        date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
        
        description = pluggy_transaction.get('description', 'Sem descrição')
        amount = pluggy_transaction.get('amount', 0.0)
        
        # Determina a fonte baseado no tipo de conta
        source = self._determine_source(account_info, pluggy_transaction)
        
        # Categoria (se disponível no Pluggy Pro)
        category_name = pluggy_transaction.get('category')
        category = self._map_category(category_name) if category_name else TransactionCategory.A_DEFINIR
        
        return Transaction(
            date=date,
            description=description,
            amount=float(amount),
            source=source,
            category=category,
            id=pluggy_transaction.get('id')
        )
    
    def _determine_source(
        self,
        account_info: Dict[str, Any],
        transaction: Dict[str, Any]
    ) -> TransactionSource:
        """
        Determina a fonte da transação baseado no tipo de conta.
        
        Args:
            account_info: Informações da conta
            transaction: Dados da transação
            
        Returns:
            TransactionSource apropriado
        """
        account_type = account_info.get('type', '').upper()
        account_subtype = account_info.get('subtype', '').upper()
        account_name = account_info.get('name', '').lower()
        
        # PIX ou conta corrente
        if account_type == 'BANK':
            return TransactionSource.PIX
        
        # Cartão de crédito
        if account_type == 'CREDIT' and account_subtype == 'CREDIT_CARD':
            # Tenta identificar a bandeira
            brand = account_info.get('creditData', {}).get('brand', '').lower()
            card_number = account_info.get('number', '')
            
            # Mastercard (Itaú)
            if 'master' in brand or 'itau' in account_name or 'itaú' in account_name:
                # Verifica se é cartão específico pelo final
                if card_number == '4059':
                    return TransactionSource.ITAU_MASTER_FISICO
                elif card_number in ['5678', '9012']:  # Ajuste conforme seus cartões
                    return TransactionSource.ITAU_MASTER_VIRTUAL
                else:
                    return TransactionSource.ITAU_MASTER_RECORRENTE
            
            # Visa (Latam)
            elif 'visa' in brand or 'latam' in account_name:
                if card_number == '1152':
                    return TransactionSource.LATAM_VISA_FISICO
                elif card_number in ['3456', '7890']:  # Ajuste conforme seus cartões
                    return TransactionSource.LATAM_VISA_VIRTUAL
                else:
                    return TransactionSource.LATAM_VISA_RECORRENTE
        
        # Padrão: PIX
        return TransactionSource.PIX
    
    def _map_category(self, pluggy_category: str) -> TransactionCategory:
        """
        Mapeia categoria do Pluggy para categoria do sistema.
        
        Args:
            pluggy_category: Nome da categoria do Pluggy
            
        Returns:
            TransactionCategory do sistema
        """
        # Mapeamento de categorias Pluggy -> Sistema
        category_map = {
            'Transfer': TransactionCategory.A_DEFINIR,
            'Food and Drink': TransactionCategory.MERCADO,
            'Groceries': TransactionCategory.MERCADO,
            'Restaurants': TransactionCategory.LANCHE,
            'Transportation': TransactionCategory.CARRO,
            'Gas': TransactionCategory.COMBUSTIVEL,
            'Health': TransactionCategory.FARMACIA,
            'Shopping': TransactionCategory.COMPRAS,
            'Entertainment': TransactionCategory.LAZER,
            'Travel': TransactionCategory.VIAGEM,
            'Bills': TransactionCategory.CASA,
            'Education': TransactionCategory.FACULDADE,
            'Income': TransactionCategory.SALARIO,
            'Investments': TransactionCategory.INVESTIMENTOS,
        }
        
        return category_map.get(pluggy_category, TransactionCategory.A_DEFINIR)
    
    def sync_all_transactions(
        self,
        from_date: datetime = None,
        to_date: datetime = None
    ) -> List[Transaction]:
        """
        Sincroniza todas as transações do Pluggy.
        
        Args:
            from_date: Data inicial
            to_date: Data final
            
        Returns:
            Lista de Transaction do sistema
        """
        logger.info("🔄 Iniciando sincronização com Pluggy...")
        
        all_data = self.pluggy.get_all_transactions(from_date, to_date)
        
        system_transactions = []
        
        for account_key, data in all_data.items():
            account_info = data['account']
            transactions = data['transactions']
            
            logger.info(f"📥 Convertendo {len(transactions)} transações de {account_key}")
            
            for pluggy_tx in transactions:
                try:
                    system_tx = self.convert_transaction(pluggy_tx, account_info)
                    system_transactions.append(system_tx)
                except Exception as e:
                    logger.error(f"❌ Erro ao converter transação: {e}")
                    continue
        
        logger.info(f"✅ {len(system_transactions)} transações sincronizadas!")
        return system_transactions
    
    def print_summary(self):
        """Exibe resumo das contas conectadas."""
        logger.info("=" * 60)
        logger.info("📊 RESUMO DAS CONTAS CONECTADAS")
        logger.info("=" * 60)
        
        items = self.pluggy.get_items()
        
        if not items:
            logger.warning("⚠️  Nenhuma conta conectada no Pluggy")
            return
        
        for item in items:
            connector_name = item.get('connector', {}).get('name', 'Desconhecido')
            status = item.get('status', 'UNKNOWN')
            
            logger.info(f"\n🏦 {connector_name}")
            logger.info(f"   Status: {status}")
            
            accounts = self.pluggy.get_accounts(item['id'])
            
            for account in accounts:
                name = account.get('name', 'Sem nome')
                acc_type = account.get('type', 'UNKNOWN')
                balance = account.get('balance', 0)
                
                logger.info(f"   💳 {name} ({acc_type})")
                logger.info(f"      Saldo: R$ {balance:,.2f}")
                
                if acc_type == 'CREDIT':
                    credit_data = account.get('creditData', {})
                    limit = credit_data.get('creditLimit', 0)
                    available = credit_data.get('availableCreditLimit', 0)
                    logger.info(f"      Limite: R$ {limit:,.2f}")
                    logger.info(f"      Disponível: R$ {available:,.2f}")
        
        logger.info("=" * 60)
