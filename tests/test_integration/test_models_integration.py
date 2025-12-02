"""
Testes de integração para módulos
"""

import pytest
import tempfile
from pathlib import Path

from models import Transaction, TransactionSource, TransactionCategory, ProcessingStats


class TestModelsIntegration:
    """Testes de integração dos modelos."""
    
    def test_transaction_creation(self):
        """Testa criação de transação."""
        tx = Transaction(
            date="2025-10-15",
            description="Teste",
            amount=-100.0,
            source=TransactionSource.PIX,
            month_ref="Outubro 2025",
            category=TransactionCategory.MERCADO
        )
        
        assert tx.date == "2025-10-15"
        assert tx.description == "Teste"
        assert tx.amount == -100.0
    
    def test_transaction_to_dict(self):
        """Testa conversão de transação para dicionário."""
        tx = Transaction(
            description="Teste",
            date="2025-10-15",
            amount=-100.0,
            source=TransactionSource.PIX,
            month_ref="Outubro 2025",
            category=TransactionCategory.MERCADO
        )
        
        tx_dict = tx.to_dict()
        
        assert isinstance(tx_dict, dict)
    
    def test_processing_stats_add_error(self):
        """Testa adição de erro às estatísticas."""
        stats = ProcessingStats()
        
        stats.add_error("Erro de teste")
        
        assert len(stats.errors) == 1
        assert stats.errors[0] == "Erro de teste"
    
    def test_processing_stats_add_warning(self):
        """Testa adição de aviso às estatísticas."""
        stats = ProcessingStats()
        
        stats.add_warning("Aviso de teste")
        
        assert len(stats.warnings) == 1
        assert stats.warnings[0] == "Aviso de teste"
    
    def test_processing_stats_multiple_errors(self):
        """Testa múltiplos erros."""
        stats = ProcessingStats()
        
        stats.add_error("Erro 1")
        stats.add_error("Erro 2")
        stats.add_error("Erro 3")
        
        assert len(stats.errors) == 3
    
    def test_processing_stats_initial_values(self):
        """Testa valores iniciais das estatísticas."""
        stats = ProcessingStats()
        
        assert stats.files_processed == 0
        assert stats.transactions_extracted == 0
        assert stats.transactions_categorized == 0
        assert stats.new_categories_learned == 0
        assert stats.processing_time_seconds == 0.0
        assert len(stats.errors) == 0
        assert len(stats.warnings) == 0
    
    def test_transaction_source_enum(self):
        """Testa enum TransactionSource."""
        assert hasattr(TransactionSource, 'PIX')
        assert hasattr(TransactionSource, 'CARD')
    
    def test_transaction_category_enum(self):
        """Testa enum TransactionCategory."""
        assert hasattr(TransactionCategory, 'MERCADO')
        assert hasattr(TransactionCategory, 'TRANSPORTE')
        assert hasattr(TransactionCategory, 'CASA')
        assert hasattr(TransactionCategory, 'LAZER')
        assert hasattr(TransactionCategory, 'A_DEFINIR')
    
    def test_transaction_with_all_categories(self):
        """Testa transação com diferentes categorias."""
        categories = [
            TransactionCategory.MERCADO,
            TransactionCategory.TRANSPORTE,
            TransactionCategory.CASA,
            TransactionCategory.LAZER,
            TransactionCategory.RECEITA,
        ]
        
        for cat in categories:
            tx = Transaction(
                description=f"Test {cat.name}",
                date="2025-10-15",
                amount=-100.0,
                source=TransactionSource.PIX,
                month_ref="Outubro 2025",
                category=cat
            )
            assert tx.category == cat
    
    def test_transaction_with_different_sources(self):
        """Testa transação com diferentes fontes."""
        sources = [
            TransactionSource.PIX,
            TransactionSource.CARD,
        ]
        
        for source in sources:
            tx = Transaction(
                description=f"Test {source.name}",
                date="2025-10-15",
                amount=-100.0,
                source=source,
                month_ref="Outubro 2025",
                category=TransactionCategory.MERCADO
            )
            assert tx.source == source
    
    def test_processing_stats_tracks_progress(self):
        """Testa rastreamento de progresso."""
        stats = ProcessingStats()
        
        # Simula processamento
        stats.files_processed = 5
        stats.transactions_extracted = 100
        stats.transactions_categorized = 95
        stats.new_categories_learned = 10
        stats.processing_time_seconds = 2.5
        
        assert stats.files_processed == 5
        assert stats.transactions_extracted == 100
        assert stats.transactions_categorized == 95
        assert stats.new_categories_learned == 10
        assert stats.processing_time_seconds == 2.5
    
    def test_transaction_negative_amount_is_expense(self):
        """Testa que valor negativo é despesa."""
        tx = Transaction(
            description="Despesa",
            date="2025-10-15",
            amount=-150.0,
            source=TransactionSource.PIX,
            month_ref="Outubro 2025",
            category=TransactionCategory.MERCADO
        )
        
        assert tx.amount < 0
    
    def test_transaction_positive_amount_is_income(self):
        """Testa que valor positivo é receita."""
        tx = Transaction(
            description="Receita",
            date="2025-10-15",
            amount=5000.0,
            source=TransactionSource.PIX,
            month_ref="Outubro 2025",
            category=TransactionCategory.RECEITA
        )
        
        assert tx.amount > 0
    
    def test_stats_can_track_errors_and_warnings_together(self):
        """Testa rastreamento simultâneo de erros e avisos."""
        stats = ProcessingStats()
        
        stats.add_error("Erro crítico")
        stats.add_warning("Aviso importante")
        stats.add_error("Outro erro")
        stats.add_warning("Outro aviso")
        
        assert len(stats.errors) == 2
        assert len(stats.warnings) == 2
    
    def test_transaction_month_ref_format(self):
        """Testa formato de referência do mês."""
        tx = Transaction(
            description="Teste",
            date="2025-10-15",
            amount=-100.0,
            source=TransactionSource.PIX,
            month_ref="Outubro 2025",
            category=TransactionCategory.MERCADO
        )
        
        assert isinstance(tx.month_ref, str)
        assert "2025" in tx.month_ref
    
    def test_transaction_date_format(self):
        """Testa formato de data."""
        tx = Transaction(
            description="Teste",
            date="2025-10-15",
            amount=-100.0,
            source=TransactionSource.PIX,
            month_ref="Outubro 2025",
            category=TransactionCategory.MERCADO
        )
        
        assert tx.date is not None
        # Pode ser string ou Date object
        date_str = str(tx.date)
        assert "2025" in date_str
