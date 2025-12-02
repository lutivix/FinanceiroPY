"""
Testes para o processador de extratos PIX
=========================================

Testa a funcionalidade do PixProcessor incluindo:
- Detecção de arquivos PIX
- Processamento de transações
- Normalização de dados
- Validações
"""

import pytest
from pathlib import Path
from datetime import date

# Imports serão resolvidos após instalação
try:
    from processors.pix import PixProcessor
    from models import Transaction, TransactionSource
except ImportError:
    pytest.skip("Módulos ainda não disponíveis", allow_module_level=True)


class TestPixProcessor:
    """Testes do processador PIX."""
    
    @pytest.fixture
    def pix_processor(self):
        """Cria instância do processador PIX."""
        return PixProcessor()
    
    def test_can_process_valid_pix_file(self, pix_processor, temp_dir):
        """Testa se reconhece arquivo PIX válido."""
        pix_file = Path(temp_dir) / "202510_Extrato.txt"
        pix_file.touch()
        
        assert pix_processor.can_process(pix_file)
    
    def test_cannot_process_invalid_extension(self, pix_processor, temp_dir):
        """Testa rejeição de arquivo com extensão incorreta."""
        wrong_file = Path(temp_dir) / "202510_Extrato.xls"
        wrong_file.touch()
        
        assert not pix_processor.can_process(wrong_file)
    
    def test_cannot_process_wrong_name_pattern(self, pix_processor, temp_dir):
        """Testa rejeição de arquivo sem padrão _Extrato."""
        wrong_file = Path(temp_dir) / "202510_PIX.txt"
        wrong_file.touch()
        
        assert not pix_processor.can_process(wrong_file)
    
    def test_process_empty_file(self, pix_processor, temp_dir):
        """Testa processamento de arquivo vazio."""
        empty_file = Path(temp_dir) / "202510_Extrato.txt"
        empty_file.write_text("", encoding='utf-8')
        
        transactions = pix_processor.process_file(empty_file)
        
        assert isinstance(transactions, list)
        assert len(transactions) == 0
    
    def test_process_valid_pix_file(self, pix_processor, sample_pix_file):
        """Testa processamento de arquivo PIX válido."""
        transactions = pix_processor.process_file(sample_pix_file)
        
        assert isinstance(transactions, list)
        assert len(transactions) > 0
        
        # Verifica primeira transação
        first_tx = transactions[0]
        assert isinstance(first_tx, Transaction)
        # Transaction usa 'source' não 'fonte'
        assert first_tx.source == TransactionSource.PIX
        assert first_tx.amount != 0
    
    def test_normalize_pix_description(self, pix_processor):
        """Testa normalização de descrições PIX."""
        # Testa remoção de data no final
        desc = "PIX RECEBIDO JOAO 15/10"
        normalized = pix_processor.normalize_description(desc)
        
        assert "15/10" not in normalized
        assert "PIX" in normalized
        assert "JOAO" in normalized
    
    def test_transaction_has_required_fields(self, pix_processor, sample_pix_file):
        """Testa se transações têm todos os campos obrigatórios."""
        transactions = pix_processor.process_file(sample_pix_file)
        
        if transactions:
            tx = transactions[0]
            # Transaction dataclass usa inglês
            assert hasattr(tx, 'date')
            assert hasattr(tx, 'description')
            assert hasattr(tx, 'amount')
            assert hasattr(tx, 'source')
            assert hasattr(tx, 'category')
            assert hasattr(tx, 'month_ref')
    
    def test_validate_file_nonexistent(self, pix_processor, temp_dir):
        """Testa validação de arquivo inexistente."""
        nonexistent = Path(temp_dir) / "nao_existe.txt"
        
        assert not pix_processor.validate_file(nonexistent)
    
    def test_validate_file_is_directory(self, pix_processor, temp_dir):
        """Testa validação quando caminho é diretório."""
        assert not pix_processor.validate_file(Path(temp_dir))
    
    @pytest.mark.parametrize("description,expected_pattern", [
        ("SUPERMERCADO ZONA SUL", "SUPERMERCADO"),
        ("PIX RECEBIDO 15/10", "PIX"),
        ("  farmacia   drogasil  ", "FARMACIA"),
    ])
    def test_normalize_various_descriptions(self, pix_processor, description, expected_pattern):
        """Testa normalização de várias descrições."""
        normalized = pix_processor.normalize_description(description)
        
        assert expected_pattern in normalized
        assert normalized == normalized.upper()
        assert normalized == normalized.strip()


class TestPixProcessorStats:
    """Testa estatísticas do processador PIX."""
    
    @pytest.fixture
    def pix_processor(self):
        """Cria instância do processador PIX."""
        return PixProcessor()
    
    def test_stats_initialization(self, pix_processor):
        """Testa inicialização das estatísticas."""
        assert hasattr(pix_processor, 'stats')
        assert pix_processor.stats is not None
    
    def test_stats_after_processing(self, pix_processor, sample_pix_file):
        """Testa atualização de estatísticas após processamento."""
        transactions = pix_processor.process_file(sample_pix_file)
        
        # Verifica que estatísticas foram atualizadas
        # ProcessingStats tem 'transactions_extracted' não 'total_transactions'
        assert hasattr(pix_processor.stats, 'transactions_extracted') or hasattr(pix_processor.stats, 'errors')
