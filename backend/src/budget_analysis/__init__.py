"""
Módulo de Análise de Orçamento Semanal
======================================

Este módulo analisa padrões de gastos históricos e gera metas semanais
por categoria, fonte e pessoa.

Componentes:
- models: Modelos de dados para análise
- recurring_analyzer: Identifica transações recorrentes
- weekly_budget_calculator: Calcula orçamento semanal
- person_mapper: Mapeia cartões para pessoas
"""

from .models import (
    RecurringTransaction,
    WeeklyBudget,
    WeekOfMonth,
    PersonCardMapping
)
from .recurring_analyzer import RecurringAnalyzer
from .weekly_budget_calculator import WeeklyBudgetCalculator
from .person_mapper import PersonMapper

__all__ = [
    'RecurringTransaction',
    'WeeklyBudget',
    'WeekOfMonth',
    'PersonCardMapping',
    'RecurringAnalyzer',
    'WeeklyBudgetCalculator',
    'PersonMapper'
]

__version__ = "1.0.0"
