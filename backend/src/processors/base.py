"""
Classe base para processadores de extratos financeiros
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import pandas as pd
from pathlib import Path
import logging

from models import Transaction, ProcessingStats

logger = logging.getLogger(__name__)


class BaseProcessor(ABC):
    """Classe base para todos os processadores de extratos."""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.stats = ProcessingStats()
    
    @abstractmethod
    def can_process(self, file_path: Path) -> bool:
        """
        Verifica se este processador pode processar o arquivo.
        
        Args:
            file_path: Caminho para o arquivo
            
        Returns:
            True se pode processar, False caso contrário
        """
        pass
    
    @abstractmethod
    def process_file(self, file_path: Path) -> List[Transaction]:
        """
        Processa um arquivo e retorna lista de transações.
        
        Args:
            file_path: Caminho para o arquivo
            
        Returns:
            Lista de transações extraídas
        """
        pass
    
    def validate_file(self, file_path: Path) -> bool:
        """
        Valida se o arquivo existe e pode ser lido.
        
        Args:
            file_path: Caminho para o arquivo
            
        Returns:
            True se válido, False caso contrário
        """
        if not file_path.exists():
            self.stats.add_error(f"Arquivo não encontrado: {file_path}")
            return False
        
        if not file_path.is_file():
            self.stats.add_error(f"Caminho não é um arquivo: {file_path}")
            return False
        
        try:
            # Tenta abrir o arquivo para verificar permissões
            with open(file_path, 'rb') as f:
                f.read(1)
            return True
        except Exception as e:
            self.stats.add_error(f"Erro ao acessar arquivo {file_path}: {e}")
            return False
    
    def normalize_description(self, description: str) -> str:
        """
        Normaliza descrição da transação.
        
        Args:
            description: Descrição original
            
        Returns:
            Descrição normalizada
        """
        if not description:
            return ""
        
        desc = str(description).strip().upper()
        
        # Remove datas do final de PIX (formato DD/MM)
        if "PIX" in desc and len(desc) >= 5:
            possivel_data = desc[-5:]
            if "/" in possivel_data and possivel_data.replace("/", "").isdigit():
                desc = desc[:-5].strip()
        
        return desc
    
    def should_skip_transaction(self, description: str, amount: float) -> bool:
        """
        Verifica se uma transação deve ser ignorada.
        
        Args:
            description: Descrição da transação
            amount: Valor da transação
            
        Returns:
            True se deve ser ignorada, False caso contrário
        """
        if not description or pd.isna(amount) or amount == 0:
            return True
        
        desc_upper = description.upper()
        
        # Lista de padrões para ignorar
        skip_patterns = [
            "PAGAMENTO EFETUADO",
            "ITAU BLACK",
            "ITAU VISA",
        ]
        
        for pattern in skip_patterns:
            if pattern in desc_upper:
                return True
        
        # Ignora transações em moedas estrangeiras
        foreign_currencies = ["USD", "$", "€", "EURO", "CHF", "GBP", "SWITZERLAND"]
        for currency in foreign_currencies:
            if currency in desc_upper:
                self.stats.add_warning(f"Transação em moeda estrangeira ignorada: {description}")
                return True
        
        return False
    
    def extract_month_reference(self, file_path: Path) -> str:
        """
        Extrai referência do mês a partir do nome do arquivo.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Mês de referência (ex: "Janeiro 2025")
        """
        filename = file_path.stem
        apenas_numeros = ''.join(filter(str.isdigit, filename))
        
        if len(apenas_numeros) >= 6:
            ano = apenas_numeros[:4]
            mes = int(apenas_numeros[4:6])
            
            meses_pt = {
                1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
                5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
                9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
            }
            
            return f"{meses_pt.get(mes, 'Mês')} {ano}"
        
        return "Data não identificada"
    
    def log_processing_start(self, file_path: Path):
        """Log de início do processamento."""
        logger.info(f"🔄 [{self.source_name}] Processando: {file_path.name}")
    
    def log_processing_end(self, transactions_count: int):
        """Log de fim do processamento."""
        logger.info(f"✅ [{self.source_name}] {transactions_count} transações extraídas")
    
    def get_stats(self) -> ProcessingStats:
        """Retorna estatísticas do processamento."""
        return self.stats