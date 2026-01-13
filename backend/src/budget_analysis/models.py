"""
Modelos de Dados - Análise de Orçamento Semanal
===============================================

Define as estruturas de dados usadas na análise de padrões de gastos
e geração de orçamento semanal.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Dict, Optional
from enum import Enum
from models import TransactionCategory, TransactionSource


class WeekOfMonth(Enum):
    """Semanas do mês baseadas em dias fixos."""
    WEEK_1 = (1, 7)    # Dias 1-7
    WEEK_2 = (8, 14)   # Dias 8-14
    WEEK_3 = (15, 21)  # Dias 15-21
    WEEK_4 = (22, 28)  # Dias 22-28
    WEEK_5 = (29, 31)  # Dias 29-31 (dias extras)
    
    @classmethod
    def from_day(cls, day: int) -> 'WeekOfMonth':
        """Retorna a semana do mês baseado no dia."""
        if 1 <= day <= 7:
            return cls.WEEK_1
        elif 8 <= day <= 14:
            return cls.WEEK_2
        elif 15 <= day <= 21:
            return cls.WEEK_3
        elif 22 <= day <= 28:
            return cls.WEEK_4
        else:
            return cls.WEEK_5
    
    @property
    def number(self) -> int:
        """Retorna o número da semana (1-5)."""
        return list(WeekOfMonth).index(self) + 1
    
    @property
    def day_range(self) -> tuple:
        """Retorna o intervalo de dias (início, fim)."""
        return self.value


@dataclass
class PersonCardMapping:
    """Mapeamento entre pessoa e cartões."""
    person: str  # "Usuário", "Bia", "Mãe"
    sources: List[TransactionSource]
    description: str = ""
    
    def __post_init__(self):
        """Validação."""
        if not self.person:
            raise ValueError("Pessoa não pode estar vazia")
        if not self.sources:
            raise ValueError("Deve ter pelo menos uma fonte")


# Mapeamentos padrão pessoa-cartão
DEFAULT_PERSON_MAPPINGS = [
    PersonCardMapping(
        person="Usuário",
        sources=[
            TransactionSource.ITAU_MASTER_FISICO,
            TransactionSource.ITAU_MASTER_VIRTUAL,
            TransactionSource.ITAU_MASTER_RECORRENTE
        ],
        description="Cartões Master Itaú"
    ),
    PersonCardMapping(
        person="Bia",
        sources=[
            TransactionSource.LATAM_VISA_FISICO,
            TransactionSource.LATAM_VISA_VIRTUAL,
            TransactionSource.LATAM_VISA_BIA
        ],
        description="Cartões Visa - Bia e adicional"
    ),
    PersonCardMapping(
        person="Mãe",
        sources=[
            TransactionSource.LATAM_VISA_MAE
        ],
        description="Cartão Visa - Mãe (adicional)"
    )
]


@dataclass
class RecurringTransaction:
    """
    Transação recorrente identificada através de análise histórica.
    
    Attributes:
        description: Descrição normalizada da transação
        category: Categoria da transação
        avg_amount: Valor médio nos últimos meses
        typical_day: Dia típico do mês (1-31)
        week_of_month: Semana do mês onde ocorre
        source: Fonte da transação (cartão)
        person: Pessoa associada ao cartão
        occurrences: Número de vezes que apareceu
        months_analyzed: Quantos meses foram analisados
        confidence: Confiança na recorrência (0-1)
        last_seen: Data da última ocorrência
        monthly_pattern: Padrão de valores por mês
    """
    description: str
    category: TransactionCategory
    avg_amount: float
    typical_day: int
    week_of_month: WeekOfMonth
    source: TransactionSource
    person: str
    occurrences: int
    months_analyzed: int
    confidence: float
    last_seen: date
    monthly_pattern: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validações."""
        if not 1 <= self.typical_day <= 31:
            raise ValueError("Dia típico deve estar entre 1 e 31")
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confiança deve estar entre 0 e 1")
        if self.occurrences > self.months_analyzed:
            raise ValueError("Ocorrências não pode ser maior que meses analisados")
    
    @property
    def is_highly_confident(self) -> bool:
        """Retorna True se a confiança é alta (>= 0.8)."""
        return self.confidence >= 0.8
    
    @property
    def recurrence_rate(self) -> float:
        """Taxa de recorrência (% de meses que apareceu)."""
        return self.occurrences / self.months_analyzed if self.months_analyzed > 0 else 0


@dataclass
class WeeklyBudget:
    """
    Orçamento semanal por categoria, pessoa e fonte.
    
    Attributes:
        week_of_month: Semana do mês (1-5)
        category: Categoria de gasto
        source: Fonte da transação (cartão)
        person: Pessoa associada
        expected_amount: Valor esperado para a semana
        recurring_items: Lista de transações recorrentes esperadas
        is_variable: Se é categoria variável (ex: Mercado, Combustível)
        calculation_method: Método usado para calcular (recorrente, média, ideal)
    """
    week_of_month: WeekOfMonth
    category: TransactionCategory
    source: TransactionSource
    person: str
    expected_amount: float
    recurring_items: List[str] = field(default_factory=list)
    is_variable: bool = False
    calculation_method: str = "recurring"  # recurring, average, ideal
    
    def __post_init__(self):
        """Validações."""
        if self.expected_amount < 0:
            raise ValueError("Valor esperado não pode ser negativo")
    
    @property
    def week_number(self) -> int:
        """Retorna o número da semana."""
        return self.week_of_month.number
    
    @property
    def has_recurring_items(self) -> bool:
        """Retorna True se tem itens recorrentes."""
        return len(self.recurring_items) > 0
    
    def to_dict(self) -> Dict:
        """Converte para dicionário."""
        return {
            "week": self.week_number,
            "week_days": f"{self.week_of_month.day_range[0]}-{self.week_of_month.day_range[1]}",
            "category": self.category.value,
            "source": self.source.value,
            "person": self.person,
            "expected_amount": round(self.expected_amount, 2),
            "recurring_items": self.recurring_items,
            "is_variable": self.is_variable,
            "calculation_method": self.calculation_method
        }


@dataclass
class WeeklyBudgetSummary:
    """Resumo de orçamento semanal consolidado."""
    week_of_month: WeekOfMonth
    total_expected: float
    by_person: Dict[str, float] = field(default_factory=dict)
    by_category: Dict[str, float] = field(default_factory=dict)
    budgets: List[WeeklyBudget] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Converte para dicionário."""
        return {
            "week": self.week_of_month.number,
            "week_days": f"{self.week_of_month.day_range[0]}-{self.week_of_month.day_range[1]}",
            "total_expected": round(self.total_expected, 2),
            "by_person": {k: round(v, 2) for k, v in self.by_person.items()},
            "by_category": {k: round(v, 2) for k, v in self.by_category.items()},
            "budgets": [b.to_dict() for b in self.budgets]
        }
