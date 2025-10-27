"""
Testes para o serviço de categorização
======================================

Testa o sistema de categorização automática de transações.
"""

import pytest
from datetime import date

try:
    from services.categorization_service import CategorizationService
    from database.category_repository import CategoryRepository
    from models import Transaction, TransactionSource, TransactionCategory
except ImportError:
    pytest.skip("Módulos ainda não disponíveis", allow_module_level=True)


def create_test_transaction_with_description(descricao):
    """Helper para criar transação de teste."""
    return Transaction(
        date=date(2025, 10, 15),
        description=descricao,
        amount=-100.0,
        source=TransactionSource.PIX,
        category=TransactionCategory.A_DEFINIR,
        month_ref="202510"
    )


class TestCategorizationService:
    """Testes do serviço de categorização."""
    
    @pytest.fixture
    def categorization_service(self, initialized_db):
        """Cria serviço com banco inicializado."""
        category_repo = CategoryRepository(initialized_db)
        service = CategorizationService(category_repo)
        yield service
        # Cleanup - fecha conexões
        if hasattr(category_repo, 'conn'):
            category_repo.conn.close()
        import gc
        gc.collect()
    
    def test_initialization(self, categorization_service):
        """Testa inicialização do serviço."""
        assert categorization_service is not None
        assert hasattr(categorization_service, 'category_repo')
    
    def test_categorize_transaction(self, categorization_service):
        """Testa categorização de transação."""
        tx = create_test_transaction_with_description("SUPERMERCADO ZONA SUL")
        category = categorization_service.categorize_transaction(tx)
        
        assert category is not None
        # categorize_transaction retorna TransactionCategory (Enum)
        assert isinstance(category, TransactionCategory)
    
    def test_categorize_multiple_transactions(self, categorization_service):
        """Testa categorização de múltiplas transações."""
        transactions = [
            create_test_transaction_with_description("SUPERMERCADO"),
            create_test_transaction_with_description("RESTAURANTE"),
            create_test_transaction_with_description("FARMACIA"),
        ]
        
        categorized = categorization_service.categorize_transactions(transactions)
        
        assert len(categorized) == 3
        # categorize_transactions retorna lista de Transaction com categoria atualizada
        for tx in categorized:
            assert isinstance(tx.category, TransactionCategory)
    
    def test_categorize_consistent(self, categorization_service):
        """Testa se categorização é consistente."""
        tx = create_test_transaction_with_description("SUPERMERCADO ZONA SUL")
        
        # Deve retornar a mesma categoria múltiplas vezes
        results = [categorization_service.categorize_transaction(tx).value for _ in range(5)]
        
        assert len(set(results)) == 1  # Todos os resultados devem ser iguais
