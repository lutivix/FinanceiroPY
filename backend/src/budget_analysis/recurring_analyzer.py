"""
Recurring Analyzer - Analisador de Transações Recorrentes
=========================================================

Identifica transações recorrentes baseado em padrões históricos.
Critérios: mesma categoria + descrição similar por 3+ meses.
"""

from typing import List, Dict
from datetime import date, timedelta
from collections import defaultdict
import math
import logging
from models import Transaction, TransactionCategory
from .models import RecurringTransaction, WeekOfMonth
from .person_mapper import PersonMapper

logger = logging.getLogger(__name__)


class RecurringAnalyzer:
    """
    Analisa transações históricas para identificar padrões recorrentes.
    
    Usa critérios conservadores:
    - Mínimo 3 meses de ocorrência
    - Matching por categoria + descrição normalizada
    - Valor arredondado para menos
    """
    
    def __init__(self, 
                 min_months: int = 3,
                 day_tolerance: int = 2,
                 person_mapper: PersonMapper = None):
        """
        Inicializa o analisador.
        
        Args:
            min_months: Mínimo de meses para considerar recorrente (padrão: 3)
            day_tolerance: Tolerância de dias para agrupar (padrão: ±2)
            person_mapper: Mapeador de pessoas (opcional)
        """
        self.min_months = min_months
        self.day_tolerance = day_tolerance
        self.person_mapper = person_mapper or PersonMapper()
        logger.info(
            f"RecurringAnalyzer inicializado: min_months={min_months}, "
            f"day_tolerance={day_tolerance}"
        )
    
    def analyze(self, transactions: List[Transaction], 
                months_to_analyze: int = 12) -> List[RecurringTransaction]:
        """
        Analisa transações e identifica padrões recorrentes.
        
        Args:
            transactions: Lista de transações históricas
            months_to_analyze: Quantos meses analisar (padrão: 12)
            
        Returns:
            Lista de transações recorrentes identificadas
        """
        logger.info(f"Analisando {len(transactions)} transações...")
        
        # Filtra apenas despesas (valores negativos)
        expenses = [t for t in transactions if t.amount < 0]
        logger.info(f"Despesas para análise: {len(expenses)}")
        
        # Agrupa por chave de matching (categoria + descrição normalizada)
        grouped = self._group_by_pattern(expenses)
        logger.info(f"Padrões identificados: {len(grouped)}")
        
        # Identifica recorrências
        recurring = []
        for pattern_key, txns in grouped.items():
            # Verifica se tem ocorrências suficientes
            unique_months = self._count_unique_months(txns)
            
            if unique_months >= self.min_months:
                recurring_txn = self._create_recurring_transaction(
                    pattern_key, txns, months_to_analyze
                )
                if recurring_txn:
                    recurring.append(recurring_txn)
        
        logger.info(f"✅ {len(recurring)} transações recorrentes identificadas")
        return recurring
    
    def _normalize_description(self, description: str) -> str:
        """
        Normaliza descrição para matching.
        
        Remove números, caracteres especiais, mantém palavras principais.
        """
        import re
        # Remove números
        text = re.sub(r'\d+', '', description)
        # Remove caracteres especiais exceto espaços
        text = re.sub(r'[^\w\s]', '', text)
        # Uppercase e trim
        text = text.upper().strip()
        # Remove espaços múltiplos
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def _group_by_pattern(self, transactions: List[Transaction]) -> Dict[str, List[Transaction]]:
        """
        Agrupa transações por padrão (categoria + descrição normalizada).
        
        Returns:
            Dicionário: chave_padrão -> lista de transações
        """
        grouped = defaultdict(list)
        
        for txn in transactions:
            # Ignora categoria "A definir"
            if txn.category == TransactionCategory.A_DEFINIR:
                continue
            
            # Cria chave de padrão
            normalized = self._normalize_description(txn.description)
            pattern_key = f"{txn.category.value}|{normalized}|{txn.source.value}"
            
            grouped[pattern_key].append(txn)
        
        return grouped
    
    def _count_unique_months(self, transactions: List[Transaction]) -> int:
        """Conta quantos meses únicos têm transações."""
        unique_months = set()
        for txn in transactions:
            month_key = f"{txn.date.year}-{txn.date.month:02d}"
            unique_months.add(month_key)
        return len(unique_months)
    
    def _calculate_typical_day(self, transactions: List[Transaction]) -> int:
        """
        Calcula o dia típico do mês baseado na mediana.
        
        Usa mediana para evitar outliers.
        """
        days = sorted([t.date.day for t in transactions])
        if len(days) == 0:
            return 1
        
        # Mediana
        mid = len(days) // 2
        if len(days) % 2 == 0:
            typical = (days[mid - 1] + days[mid]) // 2
        else:
            typical = days[mid]
        
        return typical
    
    def _calculate_avg_amount(self, transactions: List[Transaction]) -> float:
        """
        Calcula valor médio arredondando para menos.
        
        Args:
            transactions: Lista de transações
            
        Returns:
            Valor médio arredondado para menos
        """
        if not transactions:
            return 0.0
        
        # Usa valores absolutos
        amounts = [abs(t.amount) for t in transactions]
        avg = sum(amounts) / len(amounts)
        
        # Arredonda para menos (floor)
        return math.floor(avg * 100) / 100  # 2 decimais
    
    def _calculate_confidence(self, unique_months: int, months_analyzed: int) -> float:
        """
        Calcula confiança da recorrência.
        
        Confiança = (meses com ocorrência) / (meses analisados)
        """
        return min(unique_months / months_analyzed, 1.0)
    
    def _create_recurring_transaction(self, 
                                     pattern_key: str,
                                     transactions: List[Transaction],
                                     months_analyzed: int) -> RecurringTransaction:
        """
        Cria objeto RecurringTransaction a partir do grupo.
        
        Args:
            pattern_key: Chave do padrão
            transactions: Transações do grupo
            months_analyzed: Meses analisados
            
        Returns:
            RecurringTransaction ou None se inválido
        """
        try:
            # Extrai informações
            parts = pattern_key.split('|')
            category_name = parts[0]
            source_name = parts[2]
            
            # Pega categoria e source da primeira transação
            first = transactions[0]
            category = first.category
            source = first.source
            
            # Calcula métricas
            typical_day = self._calculate_typical_day(transactions)
            week = WeekOfMonth.from_day(typical_day)
            avg_amount = self._calculate_avg_amount(transactions)
            unique_months = self._count_unique_months(transactions)
            confidence = self._calculate_confidence(unique_months, months_analyzed)
            person = self.person_mapper.get_person(source)
            
            # Padrão mensal
            monthly_pattern = {}
            for txn in transactions:
                month_key = f"{txn.date.year}-{txn.date.month:02d}"
                monthly_pattern[month_key] = abs(txn.amount)
            
            return RecurringTransaction(
                description=first.description,
                category=category,
                avg_amount=avg_amount,
                typical_day=typical_day,
                week_of_month=week,
                source=source,
                person=person,
                occurrences=len(transactions),
                months_analyzed=months_analyzed,
                confidence=confidence,
                last_seen=max(t.date for t in transactions),
                monthly_pattern=monthly_pattern
            )
        
        except Exception as e:
            logger.error(f"Erro ao criar RecurringTransaction: {e}")
            return None
    
    def get_summary_report(self, recurring: List[RecurringTransaction]) -> Dict:
        """
        Gera relatório resumido das recorrências.
        
        Returns:
            Dicionário com estatísticas
        """
        if not recurring:
            return {"total": 0}
        
        # Por categoria
        by_category = defaultdict(list)
        for r in recurring:
            by_category[r.category.value].append(r)
        
        # Por pessoa
        by_person = defaultdict(list)
        for r in recurring:
            by_person[r.person].append(r)
        
        # Por semana
        by_week = defaultdict(list)
        for r in recurring:
            by_week[r.week_of_month.number].append(r)
        
        return {
            "total": len(recurring),
            "high_confidence": len([r for r in recurring if r.is_highly_confident]),
            "by_category": {k: len(v) for k, v in by_category.items()},
            "by_person": {k: len(v) for k, v in by_person.items()},
            "by_week": {k: len(v) for k, v in by_week.items()},
            "total_monthly_value": sum(r.avg_amount for r in recurring)
        }
