"""
Serviço de processamento de arquivos de extratos
"""

import logging
from typing import List, Dict, Optional
from pathlib import Path
import time
from datetime import datetime, timedelta

from models import Transaction, ProcessingStats
from processors import BaseProcessor, PixProcessor, ItauProcessor, LatamProcessor, CardStatementV2Processor

logger = logging.getLogger(__name__)


class FileProcessingService:
    """Serviço responsável pelo processamento de arquivos de extratos."""
    
    def __init__(self, data_directory: Path):
        self.data_directory = Path(data_directory)
        self.planilhas_dir = self.data_directory / "planilhas"
        
        # Inicializa processadores
        # IMPORTANTE: os processadores do formato NOVO (CardStatementV2Processor)
        # vêm ANTES dos antigos (ItauProcessor/LatamProcessor) propositalmente.
        # A seleção é feita por detecção de cabeçalho na planilha, não só pelo
        # nome do arquivo — então um arquivo no formato novo precisa ser
        # interceptado aqui antes de cair no parser antigo (que não reconhece
        # a diferença de layout e produziria resultado errado silenciosamente).
        self.processors: List[BaseProcessor] = [
            PixProcessor(),
            CardStatementV2Processor('itau'),
            CardStatementV2Processor('latam'),
            ItauProcessor(), 
            LatamProcessor()
        ]
        
        # Estatísticas globais
        self.global_stats = ProcessingStats()
    
    def find_recent_files(self, months_back: int = 12) -> Dict[str, Path]:
        """
        Busca arquivos de extratos dos últimos meses.
        Considera que o ciclo mensal vai do dia 19 de um mês ao dia 18 do próximo.
        IMPORTANTE: Apenas arquivos >= 202512 (dezembro 2025) - Open Finance cobre até novembro 2025.
        
        Args:
            months_back: Quantos meses para trás buscar
            
        Returns:
            Dicionário com chave identificadora -> caminho do arquivo
        """
        logger.info(f"🔍 Buscando arquivos dos últimos {months_back} meses em {self.planilhas_dir}")
        
        if not self.planilhas_dir.exists():
            logger.error(f"❌ Diretório não encontrado: {self.planilhas_dir}")
            return {}
        
        arquivos_encontrados = {}
        hoje = datetime.today()
        
        # Determina o "mês atual" baseado no ciclo 19-18
        # Se estamos no dia 19 ou depois, o ciclo atual é do PRÓXIMO mês
        # Exemplo: 19/10 a 18/11 é o ciclo de NOVEMBRO (arquivo 202511)
        if hoje.day >= 19:
            # Avança para o próximo mês
            mes_atual = hoje.month + 1
            ano_atual = hoje.year
            # Ajusta se passou de dezembro
            if mes_atual > 12:
                mes_atual = 1
                ano_atual += 1
        else:
            # Se estamos antes do dia 19, o ciclo atual é do mês corrente
            # Exemplo: 07/10 está no ciclo que vai de 19/09 a 18/10, então mês atual é 10
            mes_atual = hoje.month
            ano_atual = hoje.year
        
        for i in range(months_back):
            # Calcula o ano e mês da iteração atual
            mes = mes_atual - i
            ano = ano_atual
            
            # Ajusta ano se o mês ficar negativo
            while mes <= 0:
                mes += 12
                ano -= 1
            
            ano_mes = f"{ano:04d}{mes:02d}"
            
            # FILTRO: Ignora arquivos anteriores a dezembro 2025 (202512)
            if int(ano_mes) < 202512:
                logger.debug(f"⏭️ Ignorando {ano_mes} (anterior a dezembro 2025)")
                continue
            
            # Padrões de arquivo esperados
            patterns = [
                f"{ano_mes}_Extrato.txt",    # PIX
                f"{ano_mes}_Itau.xls",       # Itaú
                f"{ano_mes}_Itau.xlsx",      # Itaú (novo formato)
                f"{ano_mes}_Latam.xls",      # Latam
                f"{ano_mes}_Latam.xlsx"      # Latam (novo formato)
            ]
            
            for pattern in patterns:
                arquivo_path = self.planilhas_dir / pattern
                if arquivo_path.exists():
                    # Determina tipo baseado no nome
                    if "_Extrato" in pattern:
                        tipo = "Pix"
                    elif "_Itau" in pattern:
                        tipo = "Itau"
                    elif "_Latam" in pattern:
                        tipo = "Latam"
                    else:
                        tipo = "Unknown"
                    
                    chave = f"{tipo}_{ano_mes}"
                    arquivos_encontrados[chave] = arquivo_path
                    logger.debug(f"✅ Encontrado: {pattern}")
        
        logger.info(f"📊 Total de arquivos encontrados: {len(arquivos_encontrados)}")
        return arquivos_encontrados
    
    def process_file(self, file_path: Path) -> List[Transaction]:
        """
        Processa um arquivo específico.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Lista de transações extraídas
        """
        logger.info(f"🔄 Processando arquivo: {file_path.name}")
        
        # Encontra processador adequado
        processor = self._find_processor(file_path)
        if not processor:
            error_msg = f"Nenhum processador encontrado para: {file_path.name}"
            logger.error(f"❌ {error_msg}")
            self.global_stats.add_error(error_msg)
            return []
        
        # Processa arquivo
        try:
            transactions = processor.process_file(file_path)
            
            # Atualiza estatísticas globais
            processor_stats = processor.get_stats()
            self.global_stats.files_processed += processor_stats.files_processed
            self.global_stats.transactions_extracted += processor_stats.transactions_extracted
            self.global_stats.errors.extend(processor_stats.errors)
            self.global_stats.warnings.extend(processor_stats.warnings)
            
            return transactions
            
        except Exception as e:
            error_msg = f"Erro inesperado ao processar {file_path.name}: {e}"
            logger.error(f"❌ {error_msg}")
            self.global_stats.add_error(error_msg)
            return []
    
    def process_all_files(self, months_back: int = 12) -> List[Transaction]:
        """
        Processa todos os arquivos encontrados.
        
        Args:
            months_back: Quantos meses para trás buscar
            
        Returns:
            Lista consolidada de todas as transações
        """
        start_time = time.time()
        logger.info("🚀 Iniciando processamento de todos os arquivos")
        
        # Reseta estatísticas
        self.global_stats = ProcessingStats()
        
        # Busca arquivos
        arquivos = self.find_recent_files(months_back)
        if not arquivos:
            logger.warning("⚠️ Nenhum arquivo encontrado para processar")
            return []
        
        # Processa cada arquivo
        todas_transacoes = []
        
        for chave, arquivo_path in arquivos.items():
            logger.info(f"🔄 Processando {chave}: {arquivo_path.name}")
            
            transacoes = self.process_file(arquivo_path)
            if transacoes:
                todas_transacoes.extend(transacoes)
                logger.info(f"✅ {len(transacoes)} transações extraídas de {arquivo_path.name}")
            else:
                logger.warning(f"⚠️ Nenhuma transação extraída de {arquivo_path.name}")
        
        # Finaliza estatísticas
        self.global_stats.processing_time_seconds = time.time() - start_time
        
        logger.info(f"🎉 Processamento concluído!")
        logger.info(self.global_stats.summary())
        
        return todas_transacoes
    
    def _find_processor(self, file_path: Path) -> Optional[BaseProcessor]:
        """
        Encontra o processador adequado para um arquivo.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Processador adequado ou None
        """
        for processor in self.processors:
            if processor.can_process(file_path):
                return processor
        return None
    
    def validate_data_directory(self) -> bool:
        """
        Valida se o diretório de dados está configurado corretamente.
        
        Returns:
            True se válido, False caso contrário
        """
        logger.info(f"🔍 Validando diretório de dados: {self.data_directory}")
        
        # Verifica se diretório principal existe
        if not self.data_directory.exists():
            logger.error(f"❌ Diretório principal não existe: {self.data_directory}")
            return False
        
        # Verifica subdiretórios necessários
        subdirs = ["planilhas", "db"]
        missing_dirs = []
        
        for subdir in subdirs:
            subdir_path = self.data_directory / subdir
            if not subdir_path.exists():
                missing_dirs.append(subdir)
        
        if missing_dirs:
            logger.error(f"❌ Subdiretórios não encontrados: {missing_dirs}")
            logger.info("💡 Execute o script setup.bat para criar a estrutura necessária")
            return False
        
        logger.info("✅ Estrutura de diretórios válida")
        return True
    
    def get_file_summary(self) -> Dict:
        """
        Retorna resumo dos arquivos disponíveis.
        
        Returns:
            Dicionário com resumo dos arquivos
        """
        arquivos = self.find_recent_files()
        
        summary = {
            "total_files": len(arquivos),
            "files_by_type": {"Pix": 0, "Itau": 0, "Latam": 0},
            "files_by_month": {},
            "oldest_file": None,
            "newest_file": None
        }
        
        if not arquivos:
            return summary
        
        # Analisa arquivos
        for chave, arquivo_path in arquivos.items():
            tipo, ano_mes = chave.split("_", 1)
            
            # Conta por tipo
            if tipo in summary["files_by_type"]:
                summary["files_by_type"][tipo] += 1
            
            # Conta por mês
            if ano_mes not in summary["files_by_month"]:
                summary["files_by_month"][ano_mes] = 0
            summary["files_by_month"][ano_mes] += 1
            
            # Determina mais antigo e mais novo
            if not summary["oldest_file"] or ano_mes < summary["oldest_file"]:
                summary["oldest_file"] = ano_mes
            
            if not summary["newest_file"] or ano_mes > summary["newest_file"]:
                summary["newest_file"] = ano_mes
        
        return summary
    
    def get_processing_stats(self) -> ProcessingStats:
        """
        Retorna estatísticas do último processamento.
        
        Returns:
            Estatísticas de processamento
        """
        return self.global_stats