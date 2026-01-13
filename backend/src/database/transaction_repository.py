"""
Repositório para gerenciamento de transações
"""

import sqlite3
import logging
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import date, datetime
import json

from models import Transaction, TransactionSource, TransactionCategory
from utils import DeduplicationHelper

logger = logging.getLogger(__name__)


class TransactionRepository:
    """Repositório para gerenciar transações no banco de dados."""
    
    def __init__(self, db_path: Path, enable_deduplication: bool = True):
        self.db_path = db_path
        self.enable_deduplication = enable_deduplication
        self.dedup_helper = DeduplicationHelper()
        self.dedup_stats = {'checked': 0, 'duplicates_skipped': 0}
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Garante que a tabela de transações existe com esquema compatível."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verifica se a tabela existe e seu esquema
                cursor.execute("PRAGMA table_info(lancamentos)")
                existing_columns = {row[1] for row in cursor.fetchall()}
                
                if not existing_columns:
                    # Tabela não existe, cria nova
                    logger.info("🆕 Criando nova tabela lancamentos...")
                    cursor.execute("""
                        CREATE TABLE lancamentos (
                            Data TEXT NOT NULL,
                            Descricao TEXT NOT NULL,
                            Valor REAL NOT NULL,
                            Fonte TEXT NOT NULL,
                            Categoria TEXT NOT NULL,
                            MesComp TEXT NOT NULL,
                            id TEXT,
                            raw_data TEXT,
                            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                            updated_at TEXT
                        )
                    """)
                elif 'id' not in existing_columns:
                    # Tabela existe mas sem coluna id - adiciona colunas extras
                    logger.info("🔄 Atualizando esquema da tabela lancamentos...")
                    try:
                        cursor.execute("ALTER TABLE lancamentos ADD COLUMN id TEXT")
                    except sqlite3.OperationalError:
                        pass  # Coluna já existe
                    try:
                        cursor.execute("ALTER TABLE lancamentos ADD COLUMN raw_data TEXT")
                    except sqlite3.OperationalError:
                        pass  # Coluna já existe
                    try:
                        cursor.execute("ALTER TABLE lancamentos ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP")
                    except sqlite3.OperationalError:
                        pass  # Coluna já existe
                    try:
                        cursor.execute("ALTER TABLE lancamentos ADD COLUMN updated_at TEXT")
                    except sqlite3.OperationalError:
                        pass  # Coluna já existe
                
                # Cria índices para performance (usando nomes em português)
                try:
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_data ON lancamentos(Data)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_categoria ON lancamentos(Categoria)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fonte ON lancamentos(Fonte)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mescomp ON lancamentos(MesComp)")
                except sqlite3.OperationalError:
                    pass  # Índices podem já existir
                
                conn.commit()
                logger.debug("✅ Tabela lancamentos verificada/atualizada")
        except Exception as e:
            logger.error(f"❌ Erro ao criar/atualizar tabela lancamentos: {e}")
            raise
    
    def save_transaction(self, transaction: Transaction) -> bool:
        """
        Salva uma transação no banco.
        
        Args:
            transaction: Transação a ser salva
            
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO lancamentos 
                    (Data, Descricao, Valor, Fonte, Categoria, MesComp, id, raw_data, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    transaction.date.isoformat(),
                    transaction.description,
                    transaction.amount,
                    transaction.source.value,
                    transaction.category.value,
                    transaction.month_ref,
                    transaction.id,
                    json.dumps(transaction.raw_data),
                    transaction.created_at.isoformat(),
                    None  # updated_at vazia por padrão
                ))
                conn.commit()
                logger.debug(f"✅ Transação salva: {transaction.description} - R$ {transaction.amount}")
                return True
        except Exception as e:
            logger.error(f"❌ Erro ao salvar transação: {e}")
            return False
    
    def check_duplicate(self, transaction: Transaction) -> bool:
        """
        Verifica se uma transação já existe no banco (duplicata).
        
        Usa normalização de descrição para detectar duplicatas mesmo quando:
        - Descrição tem datas (dd/mm) ou parcelas (x/y) variáveis
        - Há pequenas diferenças de formatação
        
        Args:
            transaction: Transação a verificar
            
        Returns:
            True se já existe (duplicata), False se é nova
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Normaliza descrição para comparação
                desc_norm = self.dedup_helper.normalize_description_for_dedup(
                    transaction.description
                )
                
                # Busca transações com mesma data, valor aproximado e fonte
                cursor.execute("""
                    SELECT Descricao FROM lancamentos 
                    WHERE Data = ? 
                    AND ABS(Valor - ?) < 0.01
                    AND UPPER(Fonte) = UPPER(?)
                """, (
                    transaction.date.isoformat(),
                    float(transaction.amount),
                    transaction.source.value
                ))
                
                existing_descs = cursor.fetchall()
                
                # Compara descrições normalizadas
                for (existing_desc,) in existing_descs:
                    existing_norm = self.dedup_helper.normalize_description_for_dedup(
                        existing_desc
                    )
                    if existing_norm == desc_norm:
                        logger.debug(
                            f"🔍 Duplicata detectada: '{transaction.description}' "
                            f"vs '{existing_desc}'",
                        )
                        return True  # Duplicata encontrada
                
                return False  # Não é duplicata
                
        except Exception as e:
            logger.warning(f"⚠️ Erro ao verificar duplicata: {e}")
            return False  # Em caso de erro, assume que não é duplicata
    
    def save_transactions(self, transactions: List[Transaction], skip_duplicates: bool = None) -> int:
        """
        Salva múltiplas transações no banco.
        
        Args:
            transactions: Lista de transações
            skip_duplicates: Se True, verifica duplicatas antes de inserir.
                           Se None, usa a configuração do repositório (self.enable_deduplication)
            
        Returns:
            Número de transações salvas com sucesso
        """
        # Determina se deve verificar duplicatas
        should_check_dupes = skip_duplicates if skip_duplicates is not None else self.enable_deduplication
        
        # DEBUG: Mostrar totais de Dezembro 2025 Master ANTES da deduplicação
        debug_dez_master = [t for t in transactions if t.month_ref == 'Dezembro 2025' and 'Master' in t.source.value]
        if debug_dez_master:
            total_dez_master = sum(abs(t.amount) for t in debug_dez_master)
            logger.info(f"🔍 DEBUG: Dezembro 2025 Master ANTES deduplicacao: {len(debug_dez_master)} transacoes = R$ {total_dez_master:,.2f}")
        
        saved_count = 0
        duplicates_count = 0
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for transaction in transactions:
                    # Verifica duplicata se habilitado
                    if should_check_dupes:
                        self.dedup_stats['checked'] += 1
                        if self.check_duplicate(transaction):
                            duplicates_count += 1
                            self.dedup_stats['duplicates_skipped'] += 1
                            logger.debug(f"⏭️  Duplicata ignorada: {transaction.description}")
                            continue  # Pula esta transação
                    
                    try:
                        cursor.execute("""
                            INSERT OR REPLACE INTO lancamentos 
                            (Data, Descricao, Valor, Fonte, Categoria, MesComp, id, raw_data, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            transaction.date.isoformat(),
                            transaction.description,
                            transaction.amount,
                            transaction.source.value,
                            transaction.category.value,
                            transaction.month_ref,
                            transaction.id,
                            json.dumps(transaction.raw_data),
                            transaction.created_at.isoformat(),
                            transaction.updated_at.isoformat() if transaction.updated_at else None
                        ))
                        saved_count += 1
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao salvar transação individual: {e}")
                
                conn.commit()
                
                # DEBUG: Mostrar totais de Dezembro 2025 Master DEPOIS da deduplicação
                if debug_dez_master:
                    saved_dez_master = [t for t in transactions if t.month_ref == 'Dezembro 2025' and 'Master' in t.source.value]
                    # Contar quantos foram realmente salvos (não eram duplicatas)
                    saved_count_dez = saved_count  # Aproximação
                    logger.info(f"🔍 DEBUG: Dezembro 2025 Master DEPOIS deduplicacao: {saved_count}/{len(transactions)} salvas, {duplicates_count} duplicatas removidas")
                
                # Log com estatísticas
                if duplicates_count > 0:
                    logger.info(
                        f"✅ {saved_count}/{len(transactions)} transações salvas "
                        f"({duplicates_count} duplicatas ignoradas)"
                    )
                else:
                    logger.info(f"✅ {saved_count}/{len(transactions)} transações salvas")
                    
        except Exception as e:
            logger.error(f"❌ Erro ao salvar transações em lote: {e}")
        
        return saved_count
    
    def get_transaction_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """
        Busca transação por ID.
        
        Args:
            transaction_id: ID da transação
            
        Returns:
            Transação encontrada ou None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, date, description, amount, source, category, month_ref, raw_data, created_at, updated_at
                    FROM lancamentos WHERE id = ?
                """, (transaction_id,))
                
                row = cursor.fetchone()
                if row:
                    return self._row_to_transaction(row)
        except Exception as e:
            logger.error(f"❌ Erro ao buscar transação por ID: {e}")
        
        return None
    
    def get_transactions_by_period(self, start_date: date, end_date: date) -> List[Transaction]:
        """
        Busca transações por período.
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Lista de transações no período
        """
        transactions = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, date, description, amount, source, category, month_ref, raw_data, created_at, updated_at
                    FROM lancamentos 
                    WHERE date BETWEEN ? AND ?
                    ORDER BY date DESC, created_at DESC
                """, (start_date.isoformat(), end_date.isoformat()))
                
                for row in cursor.fetchall():
                    transaction = self._row_to_transaction(row)
                    if transaction:
                        transactions.append(transaction)
        except Exception as e:
            logger.error(f"❌ Erro ao buscar transações por período: {e}")
        
        return transactions
    
    def get_transactions_by_category(self, category: TransactionCategory) -> List[Transaction]:
        """
        Busca transações por categoria.
        
        Args:
            category: Categoria das transações
            
        Returns:
            Lista de transações da categoria
        """
        transactions = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, date, description, amount, source, category, month_ref, raw_data, created_at, updated_at
                    FROM lancamentos 
                    WHERE category = ?
                    ORDER BY date DESC
                """, (category.value,))
                
                for row in cursor.fetchall():
                    transaction = self._row_to_transaction(row)
                    if transaction:
                        transactions.append(transaction)
        except Exception as e:
            logger.error(f"❌ Erro ao buscar transações por categoria: {e}")
        
        return transactions
    
    def update_transaction_category(self, transaction_id: str, new_category: TransactionCategory) -> bool:
        """
        Atualiza categoria de uma transação.
        
        Args:
            transaction_id: ID da transação
            new_category: Nova categoria
            
        Returns:
            True se atualizou com sucesso
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE lancamentos 
                    SET Categoria = ?, updated_at = ?
                    WHERE id = ?
                """, (new_category.value, datetime.now().isoformat(), transaction_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar categoria: {e}")
            return False
    
    def delete_transaction(self, transaction_id: str) -> bool:
        """
        Remove uma transação.
        
        Args:
            transaction_id: ID da transação
            
        Returns:
            True se removeu com sucesso
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM lancamentos WHERE id = ?", (transaction_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"❌ Erro ao remover transação: {e}")
            return False
    
    def get_summary_by_month(self) -> Dict[str, Dict[str, float]]:
        """
        Retorna resumo de transações por mês.
        
        Returns:
            Dicionário com resumo mensal
        """
        summary = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT month_ref, 
                           SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as receitas,
                           SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) as despesas,
                           COUNT(*) as total_transactions
                    FROM lancamentos 
                    GROUP BY month_ref
                    ORDER BY month_ref
                """)
                
                for row in cursor.fetchall():
                    month_ref, receitas, despesas, total = row
                    summary[month_ref] = {
                        "receitas": receitas or 0,
                        "despesas": despesas or 0,
                        "saldo": (receitas or 0) + (despesas or 0),
                        "total_transactions": total
                    }
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resumo mensal: {e}")
        
        return summary
    
    def get_deduplication_stats(self) -> Dict[str, int]:
        """
        Retorna estatísticas de deduplicação da sessão atual.
        
        Returns:
            Dicionário com 'checked' e 'duplicates_skipped'
        """
        return self.dedup_stats.copy()
    
    def reset_deduplication_stats(self):
        """Reseta as estatísticas de deduplicação."""
        self.dedup_stats = {'checked': 0, 'duplicates_skipped': 0}
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas gerais das transações.
        
        Returns:
            Dicionário com estatísticas
        """
        stats = {
            "total_transactions": 0,
            "total_income": 0,
            "total_expenses": 0,
            "transactions_by_source": {},
            "transactions_by_category": {}
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total de transações
                cursor.execute("SELECT COUNT(*) FROM lancamentos")
                stats["total_transactions"] = cursor.fetchone()[0]
                
                # Receitas e despesas
                cursor.execute("""
                    SELECT 
                        SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as receitas,
                        SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) as despesas
                    FROM lancamentos
                """)
                row = cursor.fetchone()
                stats["total_income"] = row[0] or 0
                stats["total_expenses"] = row[1] or 0
                
                # Por fonte
                cursor.execute("""
                    SELECT source, COUNT(*) 
                    FROM lancamentos 
                    GROUP BY source
                """)
                stats["transactions_by_source"] = dict(cursor.fetchall())
                
                # Por categoria
                cursor.execute("""
                    SELECT category, COUNT(*) 
                    FROM lancamentos 
                    GROUP BY category
                """)
                stats["transactions_by_category"] = dict(cursor.fetchall())
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar estatísticas: {e}")
        
        return stats
    
    def _row_to_transaction(self, row) -> Optional[Transaction]:
        """
        Converte linha do banco para objeto Transaction.
        
        Args:
            row: Linha do resultado da query
            
        Returns:
            Objeto Transaction ou None se erro
        """
        try:
            id_val, date_str, description, amount, source_str, category_str, month_ref, raw_data_str, created_at_str, updated_at_str = row
            
            return Transaction(
                id=id_val,
                date=datetime.fromisoformat(date_str).date(),
                description=description,
                amount=amount,
                source=TransactionSource(source_str),
                category=TransactionCategory(category_str),
                month_ref=month_ref,
                raw_data=json.loads(raw_data_str) if raw_data_str else {},
                created_at=datetime.fromisoformat(created_at_str),
                updated_at=datetime.fromisoformat(updated_at_str) if updated_at_str else None
            )
        except Exception as e:
            logger.warning(f"⚠️ Erro ao converter linha do banco: {e}")
            return None