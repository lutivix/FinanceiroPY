"""
Testes para o repositório de categorias
========================================

Testa funcionalidades de persistência e recuperação de categorias.
"""

import pytest
import sqlite3
from pathlib import Path

try:
    from database.category_repository import CategoryRepository
    from models import TransactionCategory, LearnedCategory
except ImportError:
    pytest.skip("Módulos ainda não disponíveis", allow_module_level=True)


class TestCategoryRepository:
    """Testes do repositório de categorias."""
    
    @pytest.fixture
    def repository(self, test_db_path):
        """Cria repositório com banco de teste."""
        repo = CategoryRepository(test_db_path)
        yield repo
        # Cleanup - fecha conexões explicitamente
        if hasattr(repo, 'conn'):
            repo.conn.close()
        import gc
        gc.collect()
    
    def test_initialization_creates_table(self, test_db_path, repository):
        """Testa se a inicialização cria a tabela no banco."""
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        # Verifica se tabela existe
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='categorias_aprendidas'"
        )
        result = cursor.fetchone()
        
        conn.close()
        
        assert result is not None
    
    def test_save_category(self, repository):
        """Testa salvamento de categoria aprendida."""
        learned = LearnedCategory(
            description="Supermercado Zona Sul",
            category=TransactionCategory.MERCADO,
            confidence=0.95,
            usage_count=1
        )
        
        result = repository.save_category(learned)
        
        assert result is True
    
    def test_find_category_by_description(self, repository):
        """Testa busca de categoria por descrição."""
        learned = LearnedCategory(
            description="Uber Trip",
            category=TransactionCategory.TRANSPORTE,
            confidence=0.9,
            usage_count=1
        )
        
        # Salva categoria
        repository.save_category(learned)
        
        # Busca categoria
        found_category = repository.find_category("UBER TRIP")
        
        assert found_category is not None
        assert found_category == TransactionCategory.TRANSPORTE
    
    def test_find_category_nonexistent(self, repository):
        """Testa busca de categoria não existente."""
        result = repository.find_category("DESCRIÇÃO INEXISTENTE")
        
        assert result is None
    
    def test_get_category_mapping(self, repository):
        """Testa recuperação de todos os mapeamentos."""
        # Adiciona alguns mapeamentos
        repository.save_category(LearnedCategory("Desc 1", TransactionCategory.MERCADO, 0.9, usage_count=1))
        repository.save_category(LearnedCategory("Desc 2", TransactionCategory.TRANSPORTE, 0.9, usage_count=1))
        repository.save_category(LearnedCategory("Desc 3", TransactionCategory.CASA, 0.9, usage_count=1))
        
        mappings = repository.get_category_mapping()
        
        assert isinstance(mappings, dict)
        assert len(mappings) >= 3
        assert "DESC 1" in mappings
        assert mappings["DESC 1"] == TransactionCategory.MERCADO
    
    def test_update_existing_category(self, repository):
        """Testa atualização de categoria existente."""
        description = "Netflix"
        
        # Primeira categoria
        repository.save_category(LearnedCategory(description, TransactionCategory.LAZER, 0.9, usage_count=1))
        
        # Atualiza para outra categoria
        repository.save_category(LearnedCategory(description, TransactionCategory.STREAM, 0.95, usage_count=1))
        
        # Verifica se foi atualizado
        category = repository.find_category(description)
        assert category == TransactionCategory.STREAM
    
    def test_delete_category(self, repository):
        """Testa exclusão de categoria."""
        description = "Temp Description"
        repository.save_category(LearnedCategory(description, TransactionCategory.COMPRAS, 0.9, usage_count=1))
        
        # Deleta
        result = repository.delete_category(description.upper())
        
        assert result is True
        assert repository.find_category(description) is None
    
    def test_delete_nonexistent_category(self, repository):
        """Testa exclusão de categoria inexistente."""
        result = repository.delete_category("NUNCA EXISTIU")
        
        # Deve retornar False
        assert result is False
    
    def test_get_all_categories(self, repository):
        """Testa recuperação de todas as categorias."""
        # Adiciona categorias
        repository.save_category(LearnedCategory("Cat 1", TransactionCategory.MERCADO, 0.9, usage_count=1))
        repository.save_category(LearnedCategory("Cat 2", TransactionCategory.TRANSPORTE, 0.9, usage_count=1))
        
        all_cats = repository.get_all_categories()
        
        assert isinstance(all_cats, list)
        assert len(all_cats) >= 2
    
    def test_update_usage_count(self, repository):
        """Testa atualização de contador de uso."""
        description = "Uber"
        repository.save_category(LearnedCategory(description, TransactionCategory.TRANSPORTE, 0.9, usage_count=1))
        
        # Atualiza contador
        result = repository.update_usage_count(description.upper())
        
        assert result is True
    
    def test_get_stats(self, repository):
        """Testa estatísticas de categorias."""
        # Adiciona categorias de várias tipos
        repository.save_category(LearnedCategory("Super 1", TransactionCategory.MERCADO, 0.9, usage_count=1))
        repository.save_category(LearnedCategory("Super 2", TransactionCategory.MERCADO, 0.9, usage_count=1))
        repository.save_category(LearnedCategory("Uber 1", TransactionCategory.TRANSPORTE, 0.9, usage_count=1))
        
        stats = repository.get_stats()
        
        assert isinstance(stats, dict)
        assert 'total_categories' in stats or len(stats) > 0
    
    def test_find_similar_patterns(self, repository):
        """Testa busca de padrões similares."""
        repository.save_category(LearnedCategory("Supermercado Zona", TransactionCategory.MERCADO, 0.9, usage_count=1))
        repository.save_category(LearnedCategory("Supermercado Extra", TransactionCategory.MERCADO, 0.9, usage_count=1))
        repository.save_category(LearnedCategory("Uber Trip", TransactionCategory.TRANSPORTE, 0.9, usage_count=1))
        
        # find_category já faz busca com padrões
        result = repository.find_category("SUPERMERCADO")
        
        assert result is not None
        assert result == TransactionCategory.MERCADO
    
    def test_database_persistence(self, test_db_path):
        """Testa persistência entre instâncias do repositório."""
        # Primeira instância
        repo1 = CategoryRepository(test_db_path)
        repo1.save_category(LearnedCategory("Persistent", TransactionCategory.COMPRAS, 0.9, usage_count=1))
        if hasattr(repo1, 'conn'):
            repo1.conn.close()
        
        # Segunda instância
        repo2 = CategoryRepository(test_db_path)
        category = repo2.find_category("PERSISTENT")
        if hasattr(repo2, 'conn'):
            repo2.conn.close()
        
        assert category == TransactionCategory.COMPRAS
    
    def test_normalized_vs_original_description(self, repository):
        """Testa diferença entre descrição normalizada e original."""
        original = "Supermercado Zona Sul - Filial 123"
        
        repository.save_category(LearnedCategory(original, TransactionCategory.MERCADO, 0.9, usage_count=1))
        
        # Busca deve funcionar com variações
        assert repository.find_category("supermercado zona sul") is not None
        assert repository.find_category("SUPERMERCADO") is not None
    
    def test_handle_special_characters(self, repository):
        """Testa tratamento de caracteres especiais."""
        description = "Açougue São José"
        category = TransactionCategory.MERCADO
        
        repository.save_category(LearnedCategory(description, category, 0.9, usage_count=1))
        
        found = repository.find_category(description.upper())
        assert found == category
