"""
Testes para o repositório de transações
========================================

Testa funcionalidades de persistência e recuperação de transações.
"""

import pytest
import sqlite3
from datetime import date

try:
    from database.transaction_repository import TransactionRepository
    from models import Transaction, TransactionSource, TransactionCategory
except ImportError:
    pytest.skip("Módulos ainda não disponíveis", allow_module_level=True)


def create_test_transaction(data=date(2025, 10, 15), descricao="TESTE", valor=-100.0):
    """Helper para criar transação de teste."""
    return Transaction(
        date=data,
        description=descricao,
        amount=valor,
        source=TransactionSource.PIX,
        category=TransactionCategory.A_DEFINIR,
        month_ref="202510"
    )


class TestTransactionRepository:
    """Testes do repositório de transações."""
    
    @pytest.fixture
    def repository(self, test_db_path):
        """Cria repositório com banco de teste."""
        repo = TransactionRepository(test_db_path)
        yield repo
        # Cleanup - fecha conexões explicitamente
        if hasattr(repo, 'conn'):
            repo.conn.close()
        import gc
        gc.collect()
    
    def test_initialization_creates_table(self, repository, test_db_path):
        """Testa se inicialização cria tabela."""
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        # Verifica se tabela existe
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='lancamentos'"
        )
        result = cursor.fetchone()
        
        conn.close()
        
        assert result is not None
        assert result[0] == 'lancamentos'
    
    def test_save_transaction(self, repository):
        """Testa salvamento de transação."""
        tx = create_test_transaction()
        
        result = repository.save_transaction(tx)
        
        assert result is True
    
    def test_save_multiple_transactions(self, repository, test_db_path):
        """Testa salvamento de múltiplas transações."""
        transactions = [
            create_test_transaction(descricao="TX1"),
            create_test_transaction(descricao="TX2"),
            create_test_transaction(descricao="TX3"),
        ]
        
        # Salvar transações
        count = repository.save_transactions(transactions)
        
        assert count == 3
        
        # Verificar se foram salvas
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM lancamentos")
        db_count = cursor.fetchone()[0]
        conn.close()
        
        assert db_count == 3

