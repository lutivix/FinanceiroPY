#!/usr/bin/env python3
"""
Cliente para integração com Pluggy API
Fornece acesso aos dados do Open Finance via Pluggy
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import pluggy_sdk
    from pluggy_sdk import Configuration, ApiClient, AuthApi, ItemsApi, AccountApi, TransactionApi
    PLUGGY_AVAILABLE = True
except ImportError:
    PLUGGY_AVAILABLE = False
    logger.warning("⚠️  Pluggy SDK não instalado. Execute: pip install pluggy-sdk")


class PluggyClient:
    """Cliente para integração com a API Pluggy."""
    
    def __init__(self, client_id: str, client_secret: str):
        """
        Inicializa o cliente Pluggy.
        
        Args:
            client_id: Client ID fornecido pelo Pluggy
            client_secret: Client Secret fornecido pelo Pluggy
        """
        if not PLUGGY_AVAILABLE:
            raise ImportError(
                "Pluggy SDK não está instalado. "
                "Execute: pip install pluggy-sdk"
            )
        
        self.client_id = client_id
        self.client_secret = client_secret
        
        try:
            # Configura API client
            configuration = Configuration()
            self.api_client = ApiClient(configuration)
            
            # Autentica e obtém access token
            auth_api = AuthApi(self.api_client)
            auth_request = pluggy_sdk.AuthRequest(
                client_id=client_id,
                client_secret=client_secret
            )
            auth_response = auth_api.auth_create(auth_request)
            self.access_token = auth_response.api_key
            
            # Atualiza configuração com o token
            configuration.api_key['X-API-KEY'] = self.access_token
            
            # Inicializa APIs
            self.items_api = ItemsApi(self.api_client)
            self.account_api = AccountApi(self.api_client)
            self.transaction_api = TransactionApi(self.api_client)
            
            logger.info("✅ Cliente Pluggy inicializado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar cliente Pluggy: {e}")
            raise
    
    def get_items(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de items (conexões bancárias) conectadas.
        
        Note: A API Pluggy não tem endpoint direto para listar items.
        Precisamos buscar através das contas.
        
        Returns:
            Lista de items com informações das conexões
        """
        try:
            # A API não lista items diretamente, então vamos buscar contas
            # e extrair os item_ids únicos
            response = self.account_api.accounts_list()
            accounts = response.results if hasattr(response, 'results') else []
            
            # Extrai item_ids únicos
            item_ids_set = set()
            for acc in accounts:
                acc_dict = acc.to_dict() if hasattr(acc, 'to_dict') else acc
                item_id = acc_dict.get('item_id')
                if item_id:
                    item_ids_set.add(item_id)
            
            items = [{'id': item_id} for item_id in item_ids_set]
            logger.info(f"📋 {len(items)} item(s) encontrado(s)")
            return items
        except Exception as e:
            logger.error(f"❌ Erro ao buscar items: {e}")
            return []
    
    def get_accounts(self, item_id: str) -> List[Dict[str, Any]]:
        """
        Retorna contas vinculadas a um item.
        
        Args:
            item_id: ID do item (conexão bancária)
            
        Returns:
            Lista de contas (checking, savings, credit card)
        """
        try:
            response = self.account_api.accounts_list(item_id=item_id)
            accounts = response.results if hasattr(response, 'results') else []
            logger.info(f"💳 {len(accounts)} conta(s) encontrada(s)")
            return [acc.to_dict() if hasattr(acc, 'to_dict') else acc for acc in accounts]
        except Exception as e:
            logger.error(f"❌ Erro ao buscar contas: {e}")
            return []
    
    def get_transactions(
        self, 
        account_id: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        page_size: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Retorna transações de uma conta.
        
        Args:
            account_id: ID da conta
            from_date: Data inicial (padrão: 12 meses atrás)
            to_date: Data final (padrão: hoje)
            page_size: Tamanho da página (padrão: 500)
            
        Returns:
            Lista de transações
        """
        if from_date is None:
            from_date = datetime.now() - timedelta(days=365)
        
        if to_date is None:
            to_date = datetime.now()
        
        try:
            response = self.transaction_api.transactions_list(
                account_id=account_id,
                _from=from_date.strftime('%Y-%m-%d'),
                to=to_date.strftime('%Y-%m-%d'),
                page_size=page_size
            )
            
            results = response.results if hasattr(response, 'results') else []
            transactions = [tx.to_dict() if hasattr(tx, 'to_dict') else tx for tx in results]
            logger.info(f"💰 {len(transactions)} transação(ões) encontrada(s)")
            
            return transactions
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar transações: {e}")
            return []
    
    def get_all_transactions(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retorna todas as transações de todos os items/contas.
        
        Args:
            from_date: Data inicial
            to_date: Data final
            
        Returns:
            Dicionário com transações organizadas por conta
        """
        all_transactions = {}
        
        try:
            # Busca todos os items
            items = self.get_items()
            
            for item in items:
                item_id = item.get('id')
                connector_name = item.get('connector', {}).get('name', 'Desconhecido')
                
                logger.info(f"🏦 Processando {connector_name}...")
                
                # Busca contas do item
                accounts = self.get_accounts(item_id)
                
                for account in accounts:
                    account_id = account.get('id')
                    account_name = account.get('name', 'Sem nome')
                    account_type = account.get('type', 'UNKNOWN')
                    
                    logger.info(f"  💳 {account_name} ({account_type})")
                    
                    # Busca transações
                    transactions = self.get_transactions(
                        account_id,
                        from_date,
                        to_date
                    )
                    
                    if transactions:
                        key = f"{connector_name}_{account_name}"
                        all_transactions[key] = {
                            'account': account,
                            'transactions': transactions
                        }
            
            logger.info(f"✅ Total: {len(all_transactions)} conta(s) com transações")
            return all_transactions
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar todas as transações: {e}")
            return {}
    
    def test_connection(self) -> bool:
        """
        Testa a conexão com a API Pluggy.
        
        Returns:
            True se conectado com sucesso
        """
        try:
            items = self.get_items()
            logger.info("✅ Conexão com Pluggy OK!")
            return True
        except Exception as e:
            logger.error(f"❌ Falha na conexão: {e}")
            return False
