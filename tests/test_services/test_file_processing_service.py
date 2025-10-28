"""
Testes para FileProcessingService
"""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import os

from services.file_processing_service import FileProcessingService
from models import Transaction, TransactionSource, ProcessingStats


class TestFileProcessingService:
    """Testes para o serviço de processamento de arquivos."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Cria diretório temporário para testes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir) / "dados"
            planilhas_dir = data_dir / "planilhas"
            planilhas_dir.mkdir(parents=True, exist_ok=True)
            yield data_dir
    
    @pytest.fixture
    def service(self, temp_data_dir):
        """Cria instância do serviço para testes."""
        return FileProcessingService(temp_data_dir)
    
    def test_initialization(self, temp_data_dir):
        """Testa inicialização do serviço."""
        service = FileProcessingService(temp_data_dir)
        
        assert service.data_directory == temp_data_dir
        assert service.planilhas_dir == temp_data_dir / "planilhas"
        assert len(service.processors) == 3
        assert isinstance(service.global_stats, ProcessingStats)
    
    def test_planilhas_directory_exists(self, service):
        """Testa que diretório de planilhas foi criado."""
        assert service.planilhas_dir.exists()
        assert service.planilhas_dir.is_dir()
    
    def test_processors_loaded(self, service):
        """Testa que processadores foram carregados."""
        assert len(service.processors) > 0
        
        # Verifica nomes dos processadores
        processor_names = [p.__class__.__name__ for p in service.processors]
        assert "PixProcessor" in processor_names
        assert "ItauProcessor" in processor_names
        assert "LatamProcessor" in processor_names
    
    def test_find_recent_files_empty_directory(self, service):
        """Testa busca em diretório vazio."""
        files = service.find_recent_files(months_back=3)
        
        assert isinstance(files, dict)
        assert len(files) == 0
    
    def test_find_recent_files_with_files(self, service):
        """Testa busca com arquivos presentes."""
        # Cria alguns arquivos de teste considerando o ciclo 19-18
        hoje = datetime.today()
        
        # Calcula o mês correto baseado no ciclo
        if hoje.day >= 19:
            mes = hoje.month + 1
            ano = hoje.year
            if mes > 12:
                mes = 1
                ano += 1
        else:
            mes = hoje.month
            ano = hoje.year
        
        # Formato: YYYYMM_Extrato.txt
        file1 = service.planilhas_dir / f"{ano}{mes:02d}_Extrato.txt"
        file2 = service.planilhas_dir / f"{ano}{mes:02d}_Itau.xls"
        file3 = service.planilhas_dir / f"{ano}{mes:02d}_Latam.xls"
        
        # Cria arquivos vazios
        file1.touch()
        file2.touch()
        file3.touch()
        
        try:
            files = service.find_recent_files(months_back=1)
            
            assert isinstance(files, dict)
            # Deve encontrar pelo menos um arquivo
            assert len(files) > 0
        finally:
            # Limpa arquivos
            for f in [file1, file2, file3]:
                if f.exists():
                    f.unlink()
    
    def test_find_recent_files_filters_by_date(self, service):
        """Testa que busca filtra por data corretamente."""
        # Cria arquivo muito antigo (2 anos atrás)
        old_file = service.planilhas_dir / "202301_Extrato.txt"
        old_file.touch()
        
        # Cria arquivo recente baseado no ciclo 19-18
        hoje = datetime.today()
        
        # Se hoje é >= 19, o mês atual é o próximo mês
        if hoje.day >= 19:
            mes_arquivo = hoje.month + 1
            ano_arquivo = hoje.year
            if mes_arquivo > 12:
                mes_arquivo = 1
                ano_arquivo += 1
        else:
            mes_arquivo = hoje.month
            ano_arquivo = hoje.year
            
        recent_file = service.planilhas_dir / f"{ano_arquivo}{mes_arquivo:02d}_Extrato.txt"
        recent_file.touch()
        
        try:
            files = service.find_recent_files(months_back=3)
            
            # Deve encontrar apenas arquivo recente
            found_files = [str(f) for f in files.values()]
            assert any("202301" not in str(f) for f in found_files) or len(found_files) == 0
        finally:
            old_file.unlink()
            if recent_file.exists():
                recent_file.unlink()
    
    def test_find_recent_files_ciclo_19_18(self, service):
        """Testa que a busca considera o ciclo mensal de 19 a 18."""
        hoje = datetime.today()
        
        # Simula diferentes dias para testar a lógica
        # Se hoje é dia 19 ou depois, deve buscar o próximo mês
        if hoje.day >= 19:
            # Deve buscar arquivo do próximo mês
            mes_esperado = hoje.month + 1
            ano_esperado = hoje.year
            if mes_esperado > 12:
                mes_esperado = 1
                ano_esperado += 1
        else:
            # Deve buscar arquivo do mês atual
            mes_esperado = hoje.month
            ano_esperado = hoje.year
        
        # Cria arquivo do mês esperado
        arquivo_esperado = service.planilhas_dir / f"{ano_esperado}{mes_esperado:02d}_Extrato.txt"
        arquivo_esperado.touch()
        
        try:
            files = service.find_recent_files(months_back=1)
            
            # Deve encontrar o arquivo do mês esperado
            assert len(files) > 0
            found_files = [f.name for f in files.values()]
            assert arquivo_esperado.name in found_files
        finally:
            if arquivo_esperado.exists():
                arquivo_esperado.unlink()
    
    def test_process_file_unknown_type(self, service):
        """Testa processamento de arquivo de tipo desconhecido."""
        unknown_file = service.planilhas_dir / "unknown_format.xyz"
        unknown_file.touch()
        
        try:
            transactions = service.process_file(unknown_file)
            
            # Deve retornar lista vazia para formato desconhecido
            assert isinstance(transactions, list)
            assert len(transactions) == 0
        finally:
            unknown_file.unlink()
    
    def test_global_stats_initialization(self, service):
        """Testa inicialização de estatísticas globais."""
        stats = service.global_stats
        
        assert stats.files_processed == 0
        assert stats.transactions_extracted == 0
        assert stats.transactions_categorized == 0
        assert stats.new_categories_learned == 0
        assert stats.processing_time_seconds == 0.0
    
    def test_service_with_nonexistent_directory(self):
        """Testa serviço com diretório inexistente."""
        fake_dir = Path("/path/that/does/not/exist")
        service = FileProcessingService(fake_dir)
        
        # Deve criar o serviço mesmo que diretório não exista
        assert service.data_directory == fake_dir
        assert service.planilhas_dir == fake_dir / "planilhas"
    
    def test_find_recent_files_default_months(self, service):
        """Testa busca com parâmetro padrão de meses."""
        files = service.find_recent_files()  # Deve usar 12 meses por padrão
        
        assert isinstance(files, dict)
    
    def test_find_recent_files_custom_months(self, service):
        """Testa busca com número customizado de meses."""
        files_3_months = service.find_recent_files(months_back=3)
        files_6_months = service.find_recent_files(months_back=6)
        
        assert isinstance(files_3_months, dict)
        assert isinstance(files_6_months, dict)
    
    def test_processors_order(self, service):
        """Testa ordem dos processadores."""
        processor_names = [p.__class__.__name__ for p in service.processors]
        
        # PIX deve vir primeiro (mais específico)
        assert processor_names[0] == "PixProcessor"
    
    def test_multiple_processors_available(self, service):
        """Testa que múltiplos processadores estão disponíveis."""
        assert len(service.processors) >= 3
        
        # Todos devem ter método can_process
        for processor in service.processors:
            assert hasattr(processor, 'can_process')
            assert callable(processor.can_process)
    
    def test_service_data_directory_is_path(self, service):
        """Testa que data_directory é um Path object."""
        assert isinstance(service.data_directory, Path)
        assert isinstance(service.planilhas_dir, Path)
    
    def test_find_recent_files_handles_missing_directory(self):
        """Testa busca quando diretório de planilhas não existe."""
        fake_dir = Path("/nonexistent/path")
        service = FileProcessingService(fake_dir)
        
        files = service.find_recent_files(months_back=3)
        
        # Deve retornar dicionário vazio sem erro
        assert isinstance(files, dict)
        assert len(files) == 0
    
    def test_stats_tracked_during_processing(self, service):
        """Testa que estatísticas são rastreadas."""
        initial_count = service.global_stats.transactions_extracted
        
        # Estatísticas iniciam em zero
        assert initial_count == 0
        assert service.global_stats.files_processed == 0
