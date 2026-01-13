"""
Weekly Budget Calculator - Calculador de Orçamento Semanal
==========================================================

Calcula orçamento semanal combinando:
- Transações recorrentes identificadas
- Médias semanais para categorias variáveis
- Orçamento ideal definido
"""

from typing import List, Dict
from collections import defaultdict
from datetime import date, timedelta
import logging
from models import Transaction, TransactionCategory
from .models import (
    RecurringTransaction, 
    WeeklyBudget, 
    WeeklyBudgetSummary,
    WeekOfMonth
)
from .person_mapper import PersonMapper

logger = logging.getLogger(__name__)


# Categorias consideradas variáveis (não têm contas fixas)
VARIABLE_CATEGORIES = [
    TransactionCategory.MERCADO,
    TransactionCategory.COMBUSTIVEL,
    TransactionCategory.PADARIA,
    TransactionCategory.LANCHE,
    TransactionCategory.LAZER,
    TransactionCategory.COMPRAS
]


class WeeklyBudgetCalculator:
    """
    Calcula orçamento semanal por categoria, pessoa e fonte.
    
    Combina transações recorrentes com análise de médias semanais
    para categorias variáveis.
    """
    
    def __init__(self, person_mapper: PersonMapper = None):
        """
        Inicializa o calculador.
        
        Args:
            person_mapper: Mapeador de pessoas (opcional)
        """
        self.person_mapper = person_mapper or PersonMapper()
        logger.info("WeeklyBudgetCalculator inicializado")
    
    def calculate(self,
                 recurring_transactions: List[RecurringTransaction],
                 historical_transactions: List[Transaction],
                 months_for_average: int = 12) -> List[WeeklyBudget]:
        """
        Calcula orçamento semanal.
        
        Args:
            recurring_transactions: Transações recorrentes identificadas
            historical_transactions: Histórico completo para cálculo de médias
            months_for_average: Meses para calcular média (padrão: 12)
            
        Returns:
            Lista de orçamentos semanais
        """
        logger.info("Calculando orçamento semanal...")
        
        budgets = []
        
        # 1. Cria budgets das transações recorrentes
        for recurring in recurring_transactions:
            budget = WeeklyBudget(
                week_of_month=recurring.week_of_month,
                category=recurring.category,
                source=recurring.source,
                person=recurring.person,
                expected_amount=recurring.avg_amount,
                recurring_items=[recurring.description],
                is_variable=False,
                calculation_method="recurring"
            )
            budgets.append(budget)
        
        logger.info(f"✅ {len(budgets)} budgets de recorrentes criados")
        
        # 2. Calcula médias semanais para categorias variáveis
        variable_budgets = self._calculate_variable_budgets(
            historical_transactions,
            months_for_average
        )
        budgets.extend(variable_budgets)
        logger.info(f"✅ {len(variable_budgets)} budgets variáveis calculados")
        
        # 3. Consolida budgets duplicados (mesma semana/categoria/fonte)
        consolidated = self._consolidate_budgets(budgets)
        logger.info(f"✅ {len(consolidated)} budgets consolidados")
        
        return consolidated
    
    def _calculate_variable_budgets(self,
                                   transactions: List[Transaction],
                                   months: int) -> List[WeeklyBudget]:
        """
        Calcula orçamento para categorias variáveis baseado em média semanal.
        
        Args:
            transactions: Transações históricas
            months: Meses para análise
            
        Returns:
            Lista de budgets variáveis
        """
        budgets = []
        
        # Filtra transações variáveis
        variable_txns = [
            t for t in transactions 
            if t.category in VARIABLE_CATEGORIES and t.amount < 0
        ]
        
        if not variable_txns:
            return budgets
        
        # Agrupa por semana, categoria, fonte
        grouped = defaultdict(list)
        for txn in variable_txns:
            week = WeekOfMonth.from_day(txn.date.day)
            key = (week, txn.category, txn.source)
            grouped[key].append(abs(txn.amount))
        
        # Calcula média semanal para cada grupo
        for (week, category, source), amounts in grouped.items():
            if not amounts:
                continue
            
            # Média arredondada para menos
            avg_weekly = sum(amounts) / len(amounts)
            avg_weekly = int(avg_weekly)  # Arredonda para menos
            
            person = self.person_mapper.get_person(source)
            
            budget = WeeklyBudget(
                week_of_month=week,
                category=category,
                source=source,
                person=person,
                expected_amount=avg_weekly,
                recurring_items=[],
                is_variable=True,
                calculation_method="average"
            )
            budgets.append(budget)
        
        return budgets
    
    def _consolidate_budgets(self, budgets: List[WeeklyBudget]) -> List[WeeklyBudget]:
        """
        Consolida budgets com mesma semana/categoria/fonte.
        
        Soma valores e junta itens recorrentes.
        """
        grouped = defaultdict(list)
        
        for budget in budgets:
            key = (
                budget.week_of_month,
                budget.category,
                budget.source,
                budget.person
            )
            grouped[key].append(budget)
        
        consolidated = []
        for key, budget_list in grouped.items():
            week, category, source, person = key
            
            # Soma valores
            total_amount = sum(b.expected_amount for b in budget_list)
            
            # Junta itens recorrentes
            all_items = []
            for b in budget_list:
                all_items.extend(b.recurring_items)
            
            # Determina se é variável
            is_variable = any(b.is_variable for b in budget_list)
            
            # Método de cálculo
            methods = set(b.calculation_method for b in budget_list)
            if "recurring" in methods and "average" in methods:
                method = "mixed"
            elif "recurring" in methods:
                method = "recurring"
            else:
                method = "average"
            
            consolidated_budget = WeeklyBudget(
                week_of_month=week,
                category=category,
                source=source,
                person=person,
                expected_amount=total_amount,
                recurring_items=all_items,
                is_variable=is_variable,
                calculation_method=method
            )
            consolidated.append(consolidated_budget)
        
        return consolidated
    
    def generate_summary(self, budgets: List[WeeklyBudget]) -> List[WeeklyBudgetSummary]:
        """
        Gera resumo consolidado por semana.
        
        Args:
            budgets: Lista de orçamentos semanais
            
        Returns:
            Lista de resumos por semana
        """
        # Agrupa por semana
        by_week = defaultdict(list)
        for budget in budgets:
            by_week[budget.week_of_month].append(budget)
        
        summaries = []
        for week in sorted(by_week.keys(), key=lambda w: w.number):
            week_budgets = by_week[week]
            
            # Total da semana
            total = sum(b.expected_amount for b in week_budgets)
            
            # Por pessoa
            by_person = defaultdict(float)
            for b in week_budgets:
                by_person[b.person] += b.expected_amount
            
            # Por categoria
            by_category = defaultdict(float)
            for b in week_budgets:
                by_category[b.category.value] += b.expected_amount
            
            summary = WeeklyBudgetSummary(
                week_of_month=week,
                total_expected=total,
                by_person=dict(by_person),
                by_category=dict(by_category),
                budgets=week_budgets
            )
            summaries.append(summary)
        
        return summaries
    
    def export_to_dict(self, budgets: List[WeeklyBudget]) -> Dict:
        """
        Exporta budgets para dicionário.
        
        Returns:
            Dicionário com estrutura completa
        """
        summaries = self.generate_summary(budgets)
        
        return {
            "total_budgets": len(budgets),
            "monthly_total": sum(b.expected_amount for b in budgets),
            "by_week": [s.to_dict() for s in summaries],
            "detailed_budgets": [b.to_dict() for b in budgets]
        }
