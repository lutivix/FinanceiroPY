"""
Repositório para gerenciamento de orçamentos semanais
======================================================

Gerencia persistência e consultas de orçamentos semanais no banco de dados.
"""

import sqlite3
import logging
import json
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import date, datetime

from budget_analysis.models import WeeklyBudget, RecurringTransaction

logger = logging.getLogger(__name__)


class BudgetRepository:
    """Repositório para gerenciar orçamentos semanais no banco de dados."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Garante que a tabela de orçamentos existe."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela de orçamentos semanais
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS weekly_budgets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        generated_at TEXT NOT NULL,
                        month_ref TEXT NOT NULL,
                        week_number INTEGER NOT NULL,
                        category TEXT NOT NULL,
                        source TEXT NOT NULL,
                        person TEXT NOT NULL,
                        expected_amount REAL NOT NULL,
                        is_recurring BOOLEAN NOT NULL,
                        recurring_items TEXT,
                        confidence REAL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(generated_at, week_number, category, source, person)
                    )
                """)
                
                # Índices para performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_budgets_month 
                    ON weekly_budgets(month_ref)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_budgets_generated 
                    ON weekly_budgets(generated_at)
                """)
                
                conn.commit()
                logger.info("✅ Tabela weekly_budgets verificada/criada")
        
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabela weekly_budgets: {e}")
    
    def save_budgets(self, budgets: List[WeeklyBudget], generated_at: date) -> bool:
        """
        Salva lista de orçamentos semanais no banco.
        
        Args:
            budgets: Lista de orçamentos semanais
            generated_at: Data de geração do orçamento
            
        Returns:
            True se salvou com sucesso
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Limpa orçamentos da mesma data (atualização)
                cursor.execute("""
                    DELETE FROM weekly_budgets 
                    WHERE generated_at = ?
                """, (generated_at.isoformat(),))
                
                # Insere novos orçamentos
                for budget in budgets:
                    month_ref = f"{generated_at.year}-{generated_at.month:02d}"
                    
                    cursor.execute("""
                        INSERT INTO weekly_budgets 
                        (generated_at, month_ref, week_number, category, source, person,
                         expected_amount, is_recurring, recurring_items, confidence)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        generated_at.isoformat(),
                        month_ref,
                        budget.week_number,
                        budget.category.value,
                        budget.source.value,
                        budget.person,
                        budget.expected_amount,
                        len(budget.recurring_items) > 0,
                        json.dumps(budget.recurring_items) if budget.recurring_items else None,
                        None  # confidence virá dos RecurringTransactions
                    ))
                
                conn.commit()
                logger.info(f"✅ {len(budgets)} orçamentos salvos no banco")
                return True
        
        except Exception as e:
            logger.error(f"❌ Erro ao salvar orçamentos: {e}")
            return False
    
    def get_latest_budget(self) -> Tuple[Optional[date], List[Dict]]:
        """
        Retorna o orçamento mais recente.
        
        Returns:
            Tupla (data_geração, lista_orçamentos)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Busca data mais recente
                cursor.execute("""
                    SELECT MAX(generated_at) FROM weekly_budgets
                """)
                
                result = cursor.fetchone()
                if not result or not result[0]:
                    return None, []
                
                latest_date = date.fromisoformat(result[0])
                
                # Busca todos os orçamentos dessa data
                cursor.execute("""
                    SELECT week_number, category, source, person, 
                           expected_amount, is_recurring, recurring_items
                    FROM weekly_budgets
                    WHERE generated_at = ?
                    ORDER BY week_number, category
                """, (result[0],))
                
                budgets = []
                for row in cursor.fetchall():
                    budgets.append({
                        'week_number': row[0],
                        'category': row[1],
                        'source': row[2],
                        'person': row[3],
                        'expected_amount': row[4],
                        'is_recurring': bool(row[5]),
                        'recurring_items': json.loads(row[6]) if row[6] else []
                    })
                
                logger.info(f"📊 Orçamento mais recente: {latest_date} ({len(budgets)} itens)")
                return latest_date, budgets
        
        except Exception as e:
            logger.error(f"❌ Erro ao buscar orçamento mais recente: {e}")
            return None, []
    
    def get_budgets_by_month(self, year: int, month: int) -> List[Dict]:
        """
        Retorna orçamentos de um mês específico.
        
        Args:
            year: Ano
            month: Mês (1-12)
            
        Returns:
            Lista de orçamentos do mês
        """
        try:
            month_ref = f"{year}-{month:02d}"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT generated_at, week_number, category, source, person,
                           expected_amount, is_recurring, recurring_items
                    FROM weekly_budgets
                    WHERE month_ref = ?
                    ORDER BY generated_at DESC, week_number, category
                """, (month_ref,))
                
                budgets = []
                for row in cursor.fetchall():
                    budgets.append({
                        'generated_at': row[0],
                        'week_number': row[1],
                        'category': row[2],
                        'source': row[3],
                        'person': row[4],
                        'expected_amount': row[5],
                        'is_recurring': bool(row[6]),
                        'recurring_items': json.loads(row[7]) if row[7] else []
                    })
                
                logger.info(f"📊 {len(budgets)} orçamentos encontrados para {month_ref}")
                return budgets
        
        except Exception as e:
            logger.error(f"❌ Erro ao buscar orçamentos do mês: {e}")
            return []
    
    def get_budget_summary_by_week(self, generated_at: date = None) -> Dict:
        """
        Retorna resumo consolidado por semana.
        
        Args:
            generated_at: Data de geração (None = mais recente)
            
        Returns:
            Dicionário com totais por semana, pessoa e categoria
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Define qual data usar
                if generated_at is None:
                    cursor.execute("SELECT MAX(generated_at) FROM weekly_budgets")
                    result = cursor.fetchone()
                    if not result or not result[0]:
                        return {}
                    generated_at = date.fromisoformat(result[0])
                
                # Busca dados
                cursor.execute("""
                    SELECT week_number, person, category, SUM(expected_amount)
                    FROM weekly_budgets
                    WHERE generated_at = ?
                    GROUP BY week_number, person, category
                    ORDER BY week_number
                """, (generated_at.isoformat(),))
                
                summary = {}
                for row in cursor.fetchall():
                    week = row[0]
                    person = row[1]
                    category = row[2]
                    amount = row[3]
                    
                    if week not in summary:
                        summary[week] = {
                            'total': 0,
                            'by_person': {},
                            'by_category': {}
                        }
                    
                    summary[week]['total'] += amount
                    summary[week]['by_person'][person] = summary[week]['by_person'].get(person, 0) + amount
                    summary[week]['by_category'][category] = summary[week]['by_category'].get(category, 0) + amount
                
                return summary
        
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resumo semanal: {e}")
            return {}
