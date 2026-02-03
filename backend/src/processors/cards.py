"""
Processador para extratos de cartões (arquivos Excel)
"""

from typing import List, Optional
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

from .base import BaseProcessor
from models import Transaction, TransactionSource, TransactionCategory, get_card_source

logger = logging.getLogger(__name__)


class CardProcessor(BaseProcessor):
    """Processador base para cartões de crédito (Itaú e Latam)."""
    
    def __init__(self, bank_name: str):
        super().__init__(f"Cartão {bank_name}")
        self.bank_name = bank_name.lower()
    
    def can_process(self, file_path: Path) -> bool:
        """
        Verifica se pode processar arquivo de cartão.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            True se é arquivo Excel do banco específico
        """
        return (
            file_path.suffix.lower() in ['.xls', '.xlsx'] and
            self.bank_name.title() in file_path.name
        )
    
    def process_file(self, file_path: Path) -> List[Transaction]:
        """
        Processa arquivo de extrato de cartão.
        
        Args:
            file_path: Caminho do arquivo Excel
            
        Returns:
            Lista de transações do cartão
        """
        if not self.validate_file(file_path):
            return []
        
        self.log_processing_start(file_path)
        transactions = []
        month_ref = self.extract_month_reference(file_path)
        
        # Extrai mes_comp do nome do arquivo (formato: 202512_Itau.xls -> 2025-12)
        mes_comp = ""
        filename = file_path.stem
        apenas_numeros = ''.join(filter(str.isdigit, filename))
        if len(apenas_numeros) >= 6:
            ano = apenas_numeros[:4]
            mes = apenas_numeros[4:6]
            mes_comp = f"{ano}-{mes}"
        
        try:
            # Lê arquivo Excel
            df = pd.read_excel(file_path)
            
            # DEBUG: Mostrar totais do arquivo
            logger.info(f"🔍 DEBUG {file_path.name}: {len(df)} linhas lidas do Excel")
            
            # Processa transações por seção de cartão
            transactions = self._extract_transactions_by_card(df, month_ref, file_path, mes_comp)
            
            # DEBUG: Mostrar quantas transações foram extraídas
            if month_ref == 'Dezembro 2025':
                total_value = sum(abs(t.amount) for t in transactions)
                
                # Contar por source
                from collections import Counter
                source_counts = Counter([t.source.value for t in transactions])
                source_values = {}
                for source_name in source_counts.keys():
                    source_txs = [t for t in transactions if t.source.value == source_name]
                    source_values[source_name] = sum(abs(t.amount) for t in source_txs)
                
                logger.info(f"🔍 DEBUG {file_path.name} - Dezembro 2025 TOTAL: {len(transactions)} transacoes = R$ {total_value:,.2f}")
                logger.info(f"🔍 DEBUG {file_path.name} - Distribuição por source:")
                for source_name, count in source_counts.items():
                    logger.info(f"   {source_name}: {count} transacoes = R$ {source_values[source_name]:,.2f}")
            
            self.stats.files_processed += 1
            self.stats.transactions_extracted += len(transactions)
            self.log_processing_end(len(transactions))
            
        except Exception as e:
            error_msg = f"Erro ao processar {file_path}: {e}"
            self.stats.add_error(error_msg)
            logger.error(f"❌ [{self.source_name}] {error_msg}")
        
        return transactions
    
    def _extract_card_final(self, df: pd.DataFrame) -> Optional[str]:
        """
        Extrai final do cartão do DataFrame.
        
        Args:
            df: DataFrame do Excel
            
        Returns:
            Final do cartão (4 dígitos) ou None
        """
        for _, row in df.iterrows():
            col_a = str(row.iloc[0]).strip()
            if "FINAL" in col_a.upper():
                final = ''.join(filter(str.isdigit, col_a))
                if len(final) >= 4:
                    return final[-4:]
        return None
    
    def _extract_transactions_by_card(self, df: pd.DataFrame, month_ref: str, file_path: Path, mes_comp: str = "") -> List[Transaction]:
        """
        Extrai transações agrupadas por cartão.
        Cada seção do arquivo corresponde a um cartão específico.
        
        Args:
            df: DataFrame do Excel
            month_ref: Referência do mês
            file_path: Caminho do arquivo original
            mes_comp: Mês de compensação (formato YYYY-MM)
            
        Returns:
            Lista de transações
        """
        transactions = []
        current_card_final = None
        current_source = None
        ultima_data = None
        aguardando_valor_real = False
        
        for i, row in df.iterrows():
            col_a = str(row.iloc[0]).strip()
            col_b = str(row.iloc[1]).strip()
            col_d = row.iloc[3] if len(row) > 3 else None
            valor = pd.to_numeric(col_d, errors="coerce") if col_d is not None else None
            
            # Verifica se é linha de final do cartão
            if "FINAL" in col_a.upper():
                final = ''.join(filter(str.isdigit, col_a))
                if len(final) >= 4:
                    current_card_final = final[-4:]
                    current_source = get_card_source(current_card_final, self.bank_name)
                continue
            
            # Ignora linhas vazias ou inválidas
            if not col_b or col_b.strip().upper() in ["NAN", ""]:
                continue
            
            # Se não temos um cartão atual, usa virtual como padrão
            if current_source is None:
                current_source = (TransactionSource.ITAU_MASTER_VIRTUAL 
                                if self.bank_name.lower() == "itau" 
                                else TransactionSource.LATAM_VISA_VIRTUAL)
                # DEBUG: Avisar quando usa source default
                if month_ref == 'Dezembro 2025':
                    logger.debug(f"🔍 Usando source default para {self.bank_name}: {current_source.value}")
            
            # Verifica se deve pular esta transação
            if self.should_skip_transaction(col_b, valor if valor is not None else 0):
                continue
            
            # Processa data
            try:
                data = pd.to_datetime(col_a, dayfirst=True, errors="coerce")
                if pd.notnull(data):
                    data = data.date()
                else:
                    data = None
                
                # Tratamento especial para conversões de moeda
                if "dólar de conversão" in col_b.lower():
                    ultima_data = data
                    aguardando_valor_real = True
                    continue
                    
            except:
                data = None
            
            # Usa última data se necessário
            if pd.isnull(data) and pd.notnull(valor):
                if aguardando_valor_real:
                    data = ultima_data
                    aguardando_valor_real = False
                else:
                    continue
            elif pd.isnull(data):
                continue
            
            # Cria transação se tem valor válido e data válida
            if pd.notnull(valor) and valor != 0 and data is not None:
                transaction = Transaction(
                    date=data,
                    description=col_b.strip(),
                    amount=float(valor),
                    source=current_source,
                    category=TransactionCategory.A_DEFINIR,
                    month_ref=month_ref,
                    mes_comp=mes_comp,
                    raw_data={
                        "original_description": col_b,
                        "file_source": str(file_path),
                        "bank": self.bank_name,
                        "card_final": current_card_final
                    }
                )
                
                transactions.append(transaction)
        
        return transactions
    
    def _extract_transactions(self, df: pd.DataFrame, source: TransactionSource, 
                            month_ref: str, file_path: Path) -> List[Transaction]:
        """
        Extrai transações do DataFrame.
        
        Args:
            df: DataFrame do Excel
            source: Fonte da transação (tipo de cartão)
            month_ref: Referência do mês
            file_path: Caminho do arquivo original
            
        Returns:
            Lista de transações
        """
        transactions = []
        ultima_data = None
        aguardando_valor_real = False
        
        for _, row in df.iterrows():
            col_a = str(row.iloc[0]).strip()
            col_b = str(row.iloc[1]).strip()
            col_d = row.iloc[3] if len(row) > 3 else None
            valor = pd.to_numeric(col_d, errors="coerce") if col_d is not None else None
            
            # Ignora linha do final do cartão
            if "FINAL" in col_a.upper():
                continue
            
            # Ignora linhas vazias ou inválidas
            if not col_b or col_b.strip().upper() in ["NAN", ""]:
                continue
            
            # Verifica se deve pular esta transação
            if self.should_skip_transaction(col_b, valor if valor is not None else 0):
                continue
            
            # Processa data
            try:
                data = pd.to_datetime(col_a, dayfirst=True, errors="coerce")
                if pd.notnull(data):
                    data = data.date()
                else:
                    data = None
                
                # Tratamento especial para conversões de moeda
                if "dólar de conversão" in col_b.lower():
                    ultima_data = data
                    aguardando_valor_real = True
                    continue
                    
            except:
                data = None
            
            # Usa última data se necessário
            if pd.isnull(data) and pd.notnull(valor):
                if aguardando_valor_real:
                    data = ultima_data
                    aguardando_valor_real = False
                else:
                    continue
            elif pd.isnull(data):
                continue
            
            # Cria transação se tem valor válido
            if pd.notnull(valor) and valor != 0:
                transaction = Transaction(
                    date=data,
                    description=col_b.strip(),
                    amount=float(valor),
                    source=source,
                    category=TransactionCategory.A_DEFINIR,
                    month_ref=month_ref,
                    raw_data={
                        "original_description": col_b,
                        "file_source": str(file_path),
                        "bank": self.bank_name,
                        "card_final": self._extract_card_final(
                            pd.DataFrame([row])
                        ) if "FINAL" in col_a.upper() else None
                    }
                )
                
                transactions.append(transaction)
        
        return transactions


class ItauProcessor(CardProcessor):
    """Processador específico para cartões Itaú."""
    
    def __init__(self):
        super().__init__("Itau")


class LatamProcessor(CardProcessor):
    """Processador específico para cartões Latam."""
    
    def __init__(self):
        super().__init__("Latam")