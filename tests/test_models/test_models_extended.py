"""
Testes adicionais para aumentar cobertura de Models
"""

import pytest
from datetime import datetime

from models import Transaction, TransactionSource, TransactionCategory, LearnedCategory, ProcessingStats


class TestTransactionExtended:
    """Testes estendidos para Transaction."""
    
    def test_transaction_str_representation(self):
        """Testa representação em string."""
        tx = Transaction(
            description="Teste",
            amount=-100.0
        )
        
        tx_str = str(tx)
        assert isinstance(tx_str, str)
    
    def test_transaction_equality(self):
        """Testa igualdade de transações."""
        tx1 = Transaction(description="Test", amount=-100.0)
        tx2 = Transaction(description="Test", amount=-100.0)
        
        # IDs são diferentes por padrão
        assert tx1.id != tx2.id
    
    def test_transaction_with_raw_data(self):
        """Testa transação com dados brutos."""
        raw = {"original": "data", "value": 123}
        tx = Transaction(
            description="Test",
            amount=-100.0,
            raw_data=raw
        )
        
        assert tx.raw_data == raw
    
    def test_transaction_created_at_set(self):
        """Testa que created_at é definido."""
        tx = Transaction(description="Test", amount=-100.0)
        
        assert tx.created_at is not None
        assert isinstance(tx.created_at, datetime)
    
    def test_transaction_updated_at_optional(self):
        """Testa que updated_at é opcional."""
        tx = Transaction(description="Test", amount=-100.0)
        
        assert tx.updated_at is None
    
    def test_transaction_validates_empty_description(self):
        """Testa validação de descrição vazia."""
        with pytest.raises(ValueError):
            Transaction(description="", amount=-100.0)
    
    def test_transaction_strips_description(self):
        """Testa remoção de espaços da descrição."""
        tx = Transaction(description="  Test  ", amount=-100.0)
        
        assert tx.description == "Test"
    
    def test_transaction_with_whitespace_only_description_fails(self):
        """Testa que descrição só com espaços falha."""
        with pytest.raises(ValueError):
            Transaction(description="   ", amount=-100.0)


class TestLearnedCategoryExtended:
    """Testes estendidos para LearnedCategory."""
    
    def test_learned_category_validates_empty_description(self):
        """Testa validação de descrição vazia."""
        with pytest.raises(ValueError):
            LearnedCategory(description="", category=TransactionCategory.MERCADO)
    
    def test_learned_category_validates_confidence_range(self):
        """Testa validação de intervalo de confiança."""
        with pytest.raises(ValueError):
            LearnedCategory(
                description="Test",
                category=TransactionCategory.MERCADO,
                confidence=1.5  # > 1.0
            )
        
        with pytest.raises(ValueError):
            LearnedCategory(
                description="Test",
                category=TransactionCategory.MERCADO,
                confidence=-0.1  # < 0.0
            )
    
    def test_learned_category_normalizes_description(self):
        """Testa normalização de descrição."""
        learned = LearnedCategory(
            description="supermercado",
            category=TransactionCategory.MERCADO
        )
        
        assert learned.description == "SUPERMERCADO"
    
    def test_learned_category_to_dict(self):
        """Testa conversão para dicionário."""
        learned = LearnedCategory(
            description="Test",
            category=TransactionCategory.MERCADO,
            confidence=0.95
        )
        
        learned_dict = learned.to_dict()
        
        assert isinstance(learned_dict, dict)
        assert 'description' in learned_dict
        assert 'category' in learned_dict
        assert 'confidence' in learned_dict
    
    def test_learned_category_default_confidence(self):
        """Testa valor padrão de confiança."""
        learned = LearnedCategory(
            description="Test",
            category=TransactionCategory.MERCADO
        )
        
        assert learned.confidence == 1.0
    
    def test_learned_category_default_usage_count(self):
        """Testa valor padrão de contador de uso."""
        learned = LearnedCategory(
            description="Test",
            category=TransactionCategory.MERCADO
        )
        
        assert learned.usage_count == 1
    
    def test_learned_category_learned_at_set(self):
        """Testa que learned_at é definido."""
        learned = LearnedCategory(
            description="Test",
            category=TransactionCategory.MERCADO
        )
        
        assert learned.learned_at is not None
        assert isinstance(learned.learned_at, datetime)


class TestProcessingStatsExtended:
    """Testes estendidos para ProcessingStats."""
    
    def test_stats_default_values(self):
        """Testa valores padrão."""
        stats = ProcessingStats()
        
        assert stats.files_processed == 0
        assert stats.transactions_extracted == 0
        assert stats.transactions_categorized == 0
        assert stats.new_categories_learned == 0
        assert stats.processing_time_seconds == 0.0
        assert isinstance(stats.errors, list)
        assert isinstance(stats.warnings, list)
    
    def test_stats_add_multiple_errors(self):
        """Testa adição de múltiplos erros."""
        stats = ProcessingStats()
        
        for i in range(10):
            stats.add_error(f"Erro {i}")
        
        assert len(stats.errors) == 10
    
    def test_stats_add_multiple_warnings(self):
        """Testa adição de múltiplos avisos."""
        stats = ProcessingStats()
        
        for i in range(5):
            stats.add_warning(f"Aviso {i}")
        
        assert len(stats.warnings) == 5
    
    def test_stats_tracks_processing_time(self):
        """Testa rastreamento de tempo de processamento."""
        stats = ProcessingStats()
        
        stats.processing_time_seconds = 15.5
        
        assert stats.processing_time_seconds == 15.5
    
    def test_stats_increment_counters(self):
        """Testa incremento de contadores."""
        stats = ProcessingStats()
        
        stats.files_processed += 1
        stats.transactions_extracted += 50
        stats.transactions_categorized += 45
        stats.new_categories_learned += 5
        
        assert stats.files_processed == 1
        assert stats.transactions_extracted == 50
        assert stats.transactions_categorized == 45
        assert stats.new_categories_learned == 5


class TestTransactionSourceEnum:
    """Testes para enum TransactionSource."""
    
    def test_all_sources_exist(self):
        """Testa que todas as fontes existem."""
        assert hasattr(TransactionSource, 'PIX')
        assert hasattr(TransactionSource, 'CARD')
    
    def test_source_values(self):
        """Testa valores das fontes."""
        assert TransactionSource.PIX.value == "PIX"
        assert TransactionSource.CARD.value == "Cartão"


class TestTransactionCategoryEnum:
    """Testes para enum TransactionCategory."""
    
    def test_all_main_categories_exist(self):
        """Testa que categorias principais existem."""
        categories = [
            'A_DEFINIR', 'CASA', 'COMPRAS', 'EDUCACAO', 'INVESTIMENTO',
            'LAZER', 'MERCADO', 'RECEITA', 'ROUPA', 'SAUDE',
            'SEGURO', 'STREAM', 'TRANSPORTE', 'UTILIDADES', 'VIAGEM'
        ]
        
        for cat in categories:
            assert hasattr(TransactionCategory, cat)
    
    def test_category_values_are_strings(self):
        """Testa que valores são strings."""
        assert isinstance(TransactionCategory.MERCADO.value, str)
        assert isinstance(TransactionCategory.TRANSPORTE.value, str)
    
    def test_a_definir_is_default(self):
        """Testa que A_DEFINIR existe como padrão."""
        assert hasattr(TransactionCategory, 'A_DEFINIR')
