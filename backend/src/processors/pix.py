"""
Processador para extratos PIX (arquivos TXT)
"""

from typing import List
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

from .base import BaseProcessor
from models import Transaction, TransactionSource, TransactionCategory

logger = logging.getLogger(__name__)


class PixProcessor(BaseProcessor):
    """Processador específico para extratos PIX em formato TXT."""
    
    def __init__(self):
        super().__init__("PIX")
    
    def can_process(self, file_path: Path) -> bool:
        """
        Verifica se pode processar arquivo PIX.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            True se é arquivo PIX (.txt com _Extrato)
        """
        return (
            file_path.suffix.lower() == '.txt' and
            '_Extrato' in file_path.name
        )
    
    def process_file(self, file_path: Path) -> List[Transaction]:
        """
        Processa arquivo de extrato PIX.
        
        Args:
            file_path: Caminho do arquivo TXT
            
        Returns:
            Lista de transações PIX
        """
        if not self.validate_file(file_path):
            return []
        
        self.log_processing_start(file_path)
        transactions = []
        month_ref = self.extract_month_reference(file_path)
        
        try:
            # Lê arquivo CSV com separador ponto e vírgula
            df = pd.read_csv(
                file_path, 
                sep=";", 
                header=None, 
                names=["Data", "Descricao", "Valor"], 
                encoding="utf-8"
            )
            
            # Converte tipos
            df["Data"] = pd.to_datetime(df["Data"], errors="coerce", dayfirst=True)
            df["Valor"] = (df["Valor"]
                          .astype(str)
                          .str.replace(",", ".")
                          .astype(float) * -1)  # PIX são negativos no extrato
            
            # Remove linhas inválidas
            df = df.dropna(subset=["Data", "Valor"])
            
            # Filtra transações internas do banco
            df = df[~df["Descricao"].str.upper().str.contains(
                "ITAU BLACK|ITAU VISA", na=False
            )]
            
            for _, row in df.iterrows():
                if self.should_skip_transaction(row["Descricao"], row["Valor"]):
                    continue
                
                transaction = Transaction(
                    date=row["Data"].date(),
                    description=self.normalize_description(row["Descricao"]),
                    amount=row["Valor"],
                    source=TransactionSource.PIX,
                    category=TransactionCategory.A_DEFINIR,
                    month_ref=month_ref,
                    raw_data={
                        "original_description": row["Descricao"],
                        "file_source": str(file_path)
                    }
                )
                
                transactions.append(transaction)
            
            self.stats.files_processed += 1
            self.stats.transactions_extracted += len(transactions)
            self.log_processing_end(len(transactions))
            
        except Exception as e:
            error_msg = f"Erro ao processar {file_path}: {e}"
            self.stats.add_error(error_msg)
            logger.error(f"❌ [{self.source_name}] {error_msg}")
        
        return transactions
    
    def _detect_transaction_type(self, description: str) -> TransactionCategory:
        """
        Detecta tipo de transação PIX baseado na descrição.
        
        Args:
            description: Descrição da transação
            
        Returns:
            Categoria detectada
        """
        desc_upper = description.upper()
        
        # Padrões específicos para PIX
        if "SISPAG PIX" in desc_upper:
            return TransactionCategory.SALARIO
        
        if "REND PAGO APLIC" in desc_upper:
            return TransactionCategory.INVESTIMENTOS
        
        if any(word in desc_upper for word in ["PAGTO REMUNERACAO", "PAGTO SALARIO"]):
            return TransactionCategory.SALARIO
        
        # Padrões comuns
        if any(word in desc_upper for word in ["UBER", "99POP", "TAXI"]):
            return TransactionCategory.TRANSPORTE
        
        if any(word in desc_upper for word in ["IFOOD", "RAPPI", "DELIVERY"]):
            return TransactionCategory.ALIMENTACAO
        
        if any(word in desc_upper for word in ["MERCADO", "SUPERMERCADO", "PADARIA"]):
            return TransactionCategory.ALIMENTACAO
        
        return TransactionCategory.A_DEFINIR