"""
Testes para o módulo Budget Analysis
====================================

Testa RecurringAnalyzer, WeeklyBudgetCalculator e PersonMapper.
"""

import pytest
import sys
from pathlib import Path
from datetime import date, timedelta
from decimal import Decimal

# Adiciona backend/src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend" / "src"))

from models import Transaction, TransactionSource, TransactionCategory
from budget_analysis import (
    RecurringAnalyzer,
    WeeklyBudgetCalculator,
    PersonMapper,
    WeekOfMonth
)


class TestPersonMapper:
    """Testes para PersonMapper."""
    
    def test_get_person_master_fisico(self):
        """Testa mapeamento de Master Físico para Usuário."""
        mapper = PersonMapper()
        person = mapper.get_person(TransactionSource.ITAU_MASTER_FISICO)
        assert person == "Usuário"
    
    def test_get_person_visa_bia(self):
        """Testa mapeamento de Visa Bia para Bia."""
        mapper = PersonMapper()
        person = mapper.get_person(TransactionSource.LATAM_VISA_BIA)
        assert person == "Bia"
    
    def test_get_person_visa_mae(self):
        """Testa mapeamento de Visa Mãe para Mãe."""
        mapper = PersonMapper()
        person = mapper.get_person(TransactionSource.LATAM_VISA_MAE)
        assert person == "Mãe"
    
    def test_get_person_pix(self):
        """Testa mapeamento de PIX para Usuário."""
        mapper = PersonMapper()
        person = mapper.get_person(TransactionSource.PIX)
        assert person == "Usuário"
    
    def test_get_all_people(self):
        """Testa listagem de todas as pessoas."""
        mapper = PersonMapper()
        people = mapper.get_all_people()
        assert "Usuário" in people
        assert "Bia" in people
        assert "Mãe" in people
        assert len(people) == 3


class TestWeekOfMonth:
    """Testes para WeekOfMonth."""
    
    def test_from_day_week_1(self):
        """Testa dia 5 deve ser semana 1."""
        week = WeekOfMonth.from_day(5)
        assert week == WeekOfMonth.WEEK_1
        assert week.number == 1
    
    def test_from_day_week_2(self):
        """Testa dia 10 deve ser semana 2."""
        week = WeekOfMonth.from_day(10)
        assert week == WeekOfMonth.WEEK_2
        assert week.number == 2
    
    def test_from_day_week_3(self):
        """Testa dia 18 deve ser semana 3."""
        week = WeekOfMonth.from_day(18)
        assert week == WeekOfMonth.WEEK_3
        assert week.number == 3
    
    def test_from_day_week_4(self):
        """Testa dia 25 deve ser semana 4."""
        week = WeekOfMonth.from_day(25)
        assert week == WeekOfMonth.WEEK_4
        assert week.number == 4
    
    def test_from_day_week_5(self):
        """Testa dia 30 deve ser semana 5."""
        week = WeekOfMonth.from_day(30)
        assert week == WeekOfMonth.WEEK_5
        assert week.number == 5
    
    def test_day_range(self):
        """Testa intervalo de dias da semana 1."""
        week = WeekOfMonth.WEEK_1
        assert week.day_range == (1, 7)


class TestRecurringAnalyzer:
    """Testes para RecurringAnalyzer."""
    
    @pytest.fixture
    def sample_transactions(self):
        """Cria transações de exemplo para testes."""
        transactions = []
        base_date = date(2025, 1, 5)
        
        # Netflix - recorrente por 6 meses
        for month in range(6):
            txn_date = base_date.replace(month=base_date.month + month)
            transactions.append(Transaction(
                id=f"netflix_{month}",
                date=txn_date,
                description="NETFLIX BRASIL",
                amount=55.90,  # Positivo = despesa
                source=TransactionSource.ITAU_MASTER_VIRTUAL,
                category=TransactionCategory.STREAM,
                month_ref=f"{txn_date.year}-{txn_date.month:02d}"
            ))
        
        # Spotify - recorrente por 6 meses
        for month in range(6):
            txn_date = base_date.replace(month=base_date.month + month, day=15)
            transactions.append(Transaction(
                id=f"spotify_{month}",
                date=txn_date,
                description="SPOTIFY BRASIL",
                amount=21.90,  # Positivo = despesa
                source=TransactionSource.ITAU_MASTER_VIRTUAL,
                category=TransactionCategory.STREAM,
                month_ref=f"{txn_date.year}-{txn_date.month:02d}"
            ))
        
        # Mercado - não recorrente (apenas 2 meses)
        for month in [0, 1]:
            txn_date = base_date.replace(month=base_date.month + month, day=10)
            transactions.append(Transaction(
                id=f"mercado_{month}",
                date=txn_date,
                description="SUPERMERCADO BH",
                amount=450.00,  # Positivo = despesa
                source=TransactionSource.ITAU_MASTER_FISICO,
                category=TransactionCategory.MERCADO,
                month_ref=f"{txn_date.year}-{txn_date.month:02d}"
            ))
        
        return transactions
    
    def test_analyze_finds_recurring(self, sample_transactions):
        """Testa identificação de transações recorrentes."""
        analyzer = RecurringAnalyzer(min_months=3)
        recurring = analyzer.analyze(sample_transactions, months_to_analyze=12)
        
        # Deve encontrar Netflix e Spotify (6 meses cada)
        assert len(recurring) >= 2
        
        # Verifica se Netflix está presente
        netflix = [r for r in recurring if "NETFLIX" in r.description.upper()]
        assert len(netflix) > 0
        
        # Verifica se Spotify está presente
        spotify = [r for r in recurring if "SPOTIFY" in r.description.upper()]
        assert len(spotify) > 0
    
    def test_analyze_filters_non_recurring(self, sample_transactions):
        """Testa que transações não recorrentes são filtradas."""
        analyzer = RecurringAnalyzer(min_months=3)
        recurring = analyzer.analyze(sample_transactions, months_to_analyze=12)
        
        # Mercado tem apenas 2 meses, não deve aparecer
        mercado = [r for r in recurring if "MERCADO" in r.description.upper()]
        assert len(mercado) == 0
    
    def test_analyze_empty_transactions(self):
        """Testa análise com lista vazia."""
        analyzer = RecurringAnalyzer(min_months=3)
        recurring = analyzer.analyze([], months_to_analyze=12)
        assert len(recurring) == 0
    
    def test_get_summary_report(self, sample_transactions):
        """Testa geração de relatório resumido."""
        analyzer = RecurringAnalyzer(min_months=3)
        recurring = analyzer.analyze(sample_transactions, months_to_analyze=12)
        
        summary = analyzer.get_summary_report(recurring)
        
        assert "total" in summary
        assert summary["total"] >= 2


class TestWeeklyBudgetCalculator:
    """Testes para WeeklyBudgetCalculator."""
    
    @pytest.fixture
    def recurring_transactions(self):
        """Cria RecurringTransaction de exemplo."""
        from budget_analysis.models import RecurringTransaction
        
        return [
            RecurringTransaction(
                description="NETFLIX BRASIL",
                category=TransactionCategory.STREAM,
                avg_amount=55.90,
                typical_day=5,
                week_of_month=WeekOfMonth.WEEK_1,
                source=TransactionSource.ITAU_MASTER_VIRTUAL,
                person="Usuário",
                occurrences=6,
                months_analyzed=12,
                confidence=0.5,
                last_seen=date.today()
            )
        ]
    
    def test_calculate_creates_budgets(self, recurring_transactions):
        """Testa criação de budgets."""
        calculator = WeeklyBudgetCalculator()
        budgets = calculator.calculate(recurring_transactions, [])
        
        assert len(budgets) > 0
    
    def test_export_to_dict(self, recurring_transactions):
        """Testa exportação para dicionário."""
        calculator = WeeklyBudgetCalculator()
        budgets = calculator.calculate(recurring_transactions, [])
        
        export = calculator.export_to_dict(budgets)
        
        assert "total_budgets" in export
        assert "monthly_total" in export
        assert "by_week" in export


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
