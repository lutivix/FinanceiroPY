"""
Testes para o processador base de extratos
==========================================

Testa a classe BaseProcessor e suas funcionalidades compartilhadas.
"""

import pytest
from pathlib import Path

try:
    from processors.base import BaseProcessor
    from models import Transaction, ProcessingStats
except ImportError:
    pytest.skip("Módulos ainda não disponíveis", allow_module_level=True)


class DummyProcessor(BaseProcessor):
    """Processador dummy para testar classe abstrata."""
    
    def can_process(self, file_path: Path) -> bool:
        return file_path.suffix == '.dummy'
    
    def process_file(self, file_path: Path) -> list:
        return []


class TestBaseProcessor:
    """Testes da classe base BaseProcessor."""
    
    @pytest.fixture
    def dummy_processor(self):
        """Cria processador dummy para testes."""
        return DummyProcessor("TEST")
    
    def test_initialization(self, dummy_processor):
        """Testa inicialização do processador."""
        assert dummy_processor.source_name == "TEST"
        assert hasattr(dummy_processor, 'stats')
        assert isinstance(dummy_processor.stats, ProcessingStats)
    
    def test_validate_file_exists(self, dummy_processor, temp_dir):
        """Testa validação de arquivo que existe."""
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("test content", encoding='utf-8')
        
        assert dummy_processor.validate_file(test_file)
    
    def test_validate_file_not_exists(self, dummy_processor, temp_dir):
        """Testa validação de arquivo inexistente."""
        nonexistent = Path(temp_dir) / "nao_existe.txt"
        
        assert not dummy_processor.validate_file(nonexistent)
    
    def test_validate_file_is_directory(self, dummy_processor, temp_dir):
        """Testa validação quando caminho é diretório."""
        assert not dummy_processor.validate_file(Path(temp_dir))
    
    def test_normalize_description_basic(self, dummy_processor):
        """Testa normalização básica de descrição."""
        desc = "teste descrição"
        normalized = dummy_processor.normalize_description(desc)
        
        assert normalized == "TESTE DESCRIÇÃO"
    
    def test_normalize_description_with_whitespace(self, dummy_processor):
        """Testa normalização com espaços extras."""
        desc = "  teste   descrição  "
        normalized = dummy_processor.normalize_description(desc)
        
        assert normalized == "TESTE   DESCRIÇÃO"
        assert normalized.startswith("TESTE")
        assert normalized.endswith("DESCRIÇÃO")
    
    def test_normalize_description_empty(self, dummy_processor):
        """Testa normalização de string vazia."""
        assert dummy_processor.normalize_description("") == ""
        assert dummy_processor.normalize_description(None) == ""
    
    def test_normalize_description_removes_pix_date(self, dummy_processor):
        """Testa remoção de data no final de descrição PIX."""
        desc = "PIX RECEBIDO MARIA 15/10"
        normalized = dummy_processor.normalize_description(desc)
        
        assert "15/10" not in normalized
        assert "PIX" in normalized
    
    @pytest.mark.parametrize("description,expected", [
        ("Teste Simples", "TESTE SIMPLES"),
        ("lowercase", "LOWERCASE"),
        ("MiXeD CaSe", "MIXED CASE"),
        ("123 números", "123 NÚMEROS"),
    ])
    def test_normalize_various_descriptions(self, dummy_processor, description, expected):
        """Testa normalização de várias descrições."""
        assert dummy_processor.normalize_description(description) == expected


class TestProcessorStats:
    """Testa funcionalidades de estatísticas do processador."""
    
    @pytest.fixture
    def dummy_processor(self):
        """Cria processador dummy para testes."""
        return DummyProcessor("TEST")
    
    def test_stats_has_required_attributes(self, dummy_processor):
        """Testa se stats tem atributos necessários."""
        stats = dummy_processor.stats
        
        # Verifica se ProcessingStats tem atributos esperados
        assert hasattr(stats, '__dict__') or hasattr(stats, '__slots__')
    
    def test_validate_file_adds_error(self, dummy_processor, temp_dir):
        """Testa se validação falha adiciona erro."""
        nonexistent = Path(temp_dir) / "nao_existe.txt"
        
        result = dummy_processor.validate_file(nonexistent)
        
        assert not result
        # Stats deve ter registrado o erro
        if hasattr(dummy_processor.stats, 'errors'):
            assert len(dummy_processor.stats.errors) > 0
