"""
Script de Análise de Padrões Semanais
=====================================

Analisa transações históricas e gera orçamento semanal por categoria,
fonte e pessoa.

Uso:
    python analisar_padroes_semanais.py [--months-history 12] [--min-recurrence 3]

Output:
    - Relatório de transações recorrentes
    - Orçamento semanal consolidado
    - Arquivo JSON com resultados
"""

import sys
import os
import json
import logging
from pathlib import Path
from datetime import date, timedelta
from typing import List

# Adiciona backend/src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.transaction_repository import TransactionRepository
from budget_analysis import (
    RecurringAnalyzer,
    WeeklyBudgetCalculator,
    PersonMapper
)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('budget_analysis.log')
    ]
)
logger = logging.getLogger(__name__)


def load_historical_transactions(months: int = 12) -> List:
    """
    Carrega transações históricas do banco de dados.
    
    Args:
        months: Quantos meses carregar
        
    Returns:
        Lista de transações
    """
    logger.info(f"📥 Carregando transações dos últimos {months} meses...")
    
    # Caminho do banco
    db_path = Path(__file__).parent.parent.parent / "dados" / "db" / "financeiro.db"
    
    if not db_path.exists():
        logger.error(f"❌ Banco de dados não encontrado: {db_path}")
        return []
    
    # Repositório
    repo = TransactionRepository(str(db_path))
    
    # Período
    end_date = date.today()
    start_date = end_date - timedelta(days=months * 30)
    
    # Busca transações
    transactions = repo.get_transactions_by_period(start_date, end_date)
    
    logger.info(f"✅ {len(transactions)} transações carregadas")
    return transactions


def analyze_recurring_patterns(transactions: List, 
                               min_months: int = 3) -> List:
    """
    Analisa e identifica transações recorrentes.
    
    Args:
        transactions: Lista de transações
        min_months: Mínimo de meses para considerar recorrente
        
    Returns:
        Lista de transações recorrentes
    """
    logger.info("🔍 Analisando padrões recorrentes...")
    
    analyzer = RecurringAnalyzer(min_months=min_months)
    recurring = analyzer.analyze(transactions, months_to_analyze=12)
    
    # Resumo
    summary = analyzer.get_summary_report(recurring)
    logger.info("📊 Resumo de Recorrências:")
    logger.info(f"   Total: {summary['total']}")
    logger.info(f"   Alta confiança: {summary['high_confidence']}")
    logger.info(f"   Valor mensal total: R$ {summary['total_monthly_value']:,.2f}")
    
    return recurring


def calculate_weekly_budgets(recurring: List, 
                            historical: List) -> List:
    """
    Calcula orçamento semanal.
    
    Args:
        recurring: Transações recorrentes
        historical: Transações históricas
        
    Returns:
        Lista de orçamentos semanais
    """
    logger.info("💰 Calculando orçamento semanal...")
    
    calculator = WeeklyBudgetCalculator()
    budgets = calculator.calculate(recurring, historical)
    
    logger.info(f"✅ {len(budgets)} orçamentos semanais calculados")
    
    return budgets


def export_results(recurring: List, budgets: List, output_file: str = "weekly_budget.json"):
    """
    Exporta resultados para arquivo JSON.
    
    Args:
        recurring: Transações recorrentes
        budgets: Orçamentos semanais
        output_file: Nome do arquivo de saída
    """
    logger.info(f"💾 Exportando resultados para {output_file}...")
    
    # Calculadora para gerar sumário
    calculator = WeeklyBudgetCalculator()
    
    # Estrutura de saída
    output = {
        "generated_at": date.today().isoformat(),
        "recurring_transactions": {
            "total": len(recurring),
            "items": [
                {
                    "description": r.description,
                    "category": r.category.value,
                    "person": r.person,
                    "source": r.source.value,
                    "avg_amount": round(r.avg_amount, 2),
                    "typical_day": r.typical_day,
                    "week": r.week_of_month.number,
                    "occurrences": r.occurrences,
                    "confidence": round(r.confidence, 2)
                }
                for r in sorted(recurring, key=lambda x: (x.week_of_month.number, x.category.value))
            ]
        },
        "weekly_budgets": calculator.export_to_dict(budgets)
    }
    
    # Salva arquivo
    output_path = Path(__file__).parent / output_file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    logger.info(f"✅ Resultados exportados: {output_path}")


def print_weekly_summary(budgets: List):
    """
    Imprime resumo semanal no console.
    
    Args:
        budgets: Orçamentos semanais
    """
    calculator = WeeklyBudgetCalculator()
    summaries = calculator.generate_summary(budgets)
    
    print("\n" + "="*80)
    print("📅 ORÇAMENTO SEMANAL - RESUMO")
    print("="*80)
    
    for summary in summaries:
        week_days = f"{summary.week_of_month.day_range[0]}-{summary.week_of_month.day_range[1]}"
        print(f"\n🗓️  SEMANA {summary.week_of_month.number} (Dias {week_days})")
        print(f"   Total Esperado: R$ {summary.total_expected:,.2f}")
        
        print("\n   Por Pessoa:")
        for person, amount in sorted(summary.by_person.items()):
            print(f"      {person}: R$ {amount:,.2f}")
        
        print("\n   Por Categoria (Top 5):")
        top_categories = sorted(summary.by_category.items(), key=lambda x: x[1], reverse=True)[:5]
        for category, amount in top_categories:
            print(f"      {category}: R$ {amount:,.2f}")
        
        # Itens recorrentes
        recurring_budgets = [b for b in summary.budgets if b.has_recurring_items]
        if recurring_budgets:
            print("\n   Contas Fixas:")
            for budget in sorted(recurring_budgets, key=lambda b: b.expected_amount, reverse=True)[:5]:
                items = ", ".join(budget.recurring_items[:2])
                print(f"      {items}: R$ {budget.expected_amount:,.2f} ({budget.person})")
    
    print("\n" + "="*80)
    print(f"💵 TOTAL MENSAL ESTIMADO: R$ {sum(b.expected_amount for b in budgets):,.2f}")
    print("="*80 + "\n")


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Análise de Padrões Semanais')
    parser.add_argument('--months-history', type=int, default=12,
                       help='Meses de histórico para analisar (padrão: 12)')
    parser.add_argument('--min-recurrence', type=int, default=3,
                       help='Mínimo de meses para considerar recorrente (padrão: 3)')
    parser.add_argument('--output', type=str, default='weekly_budget.json',
                       help='Arquivo de saída (padrão: weekly_budget.json)')
    
    args = parser.parse_args()
    
    try:
        logger.info("🚀 Iniciando análise de padrões semanais...")
        
        # 1. Carrega transações
        transactions = load_historical_transactions(args.months_history)
        if not transactions:
            logger.error("❌ Nenhuma transação encontrada")
            return 1
        
        # 2. Analisa recorrências
        recurring = analyze_recurring_patterns(transactions, args.min_recurrence)
        
        # 3. Calcula orçamento semanal
        budgets = calculate_weekly_budgets(recurring, transactions)
        
        # 4. Exporta resultados
        export_results(recurring, budgets, args.output)
        
        # 5. Mostra resumo
        print_weekly_summary(budgets)
        
        logger.info("🎉 Análise concluída com sucesso!")
        return 0
    
    except Exception as e:
        logger.error(f"❌ Erro durante análise: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
