"""
Serviço de geração de relatórios e exportação
"""

import logging
from typing import List, Dict, Optional, Any
from pathlib import Path
import pandas as pd
from datetime import datetime, date

from models import Transaction, TransactionCategory, TransactionSource

logger = logging.getLogger(__name__)


class ReportService:
    """Serviço responsável pela geração de relatórios e exportações."""
    
    def __init__(self, data_directory: Path):
        self.data_directory = Path(data_directory)
        self.planilhas_dir = self.data_directory / "planilhas"
    
    def generate_consolidated_excel(self, transactions: List[Transaction], 
                                  filename: str = "consolidado_temp.xlsx") -> Optional[Path]:
        """
        Gera planilha Excel consolidada (mantém compatibilidade com versão original).
        
        Args:
            transactions: Lista de transações para consolidar
            filename: Nome do arquivo Excel a ser gerado
            
        Returns:
            Caminho do arquivo gerado ou None se erro
        """
        if not transactions:
            logger.warning("⚠️ Nenhuma transação para gerar Excel")
            return None
        
        logger.info(f"📊 Gerando Excel consolidado com {len(transactions)} transações")
        
        try:
            # Converte transações para DataFrame
            df_data = []
            for transaction in transactions:
                df_data.append({
                    "Data": transaction.date,
                    "Descricao": transaction.description,
                    "Fonte": transaction.source.value,
                    "Valor": transaction.amount,
                    "Categoria": transaction.category.value,
                    "MesComp": transaction.month_ref
                })
            
            df = pd.DataFrame(df_data)
            
            # Ordena por MesComp, Fonte (desc) e Data conforme solicitado
            df = df.sort_values(["MesComp", "Fonte", "Data"], ascending=[True, False, True])
            
            # Salva Excel
            output_path = self.planilhas_dir / filename
            df.to_excel(output_path, index=False)
            
            logger.info(f"✅ Excel gerado: {output_path}")
            logger.info(f"📈 Resumo: {len(df)} transações, período: {df['Data'].min()} a {df['Data'].max()}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar Excel: {e}")
            return None
    
    def generate_categorized_report(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """
        Gera relatório detalhado por categorias.
        
        Args:
            transactions: Lista de transações
            
        Returns:
            Dicionário com análise por categorias
        """
        logger.info(f"📊 Gerando relatório categorizado para {len(transactions)} transações")
        
        if not transactions:
            return {"error": "Nenhuma transação fornecida"}
        
        # Agrupa por categoria
        category_data = {}
        total_income = 0
        total_expenses = 0
        
        for transaction in transactions:
            category = transaction.category.value
            
            if category not in category_data:
                category_data[category] = {
                    "transactions": [],
                    "total_amount": 0,
                    "count": 0,
                    "avg_amount": 0
                }
            
            category_data[category]["transactions"].append(transaction)
            category_data[category]["total_amount"] += transaction.amount
            category_data[category]["count"] += 1
            
            # Soma totais
            if transaction.amount > 0:
                total_income += transaction.amount
            else:
                total_expenses += transaction.amount
        
        # Calcula médias
        for category_info in category_data.values():
            if category_info["count"] > 0:
                category_info["avg_amount"] = category_info["total_amount"] / category_info["count"]
        
        # Ordena categorias por valor total (em módulo)
        sorted_categories = sorted(
            category_data.items(),
            key=lambda x: abs(x[1]["total_amount"]),
            reverse=True
        )
        
        return {
            "summary": {
                "total_transactions": len(transactions),
                "total_income": total_income,
                "total_expenses": total_expenses,
                "net_balance": total_income + total_expenses,
                "categories_count": len(category_data)
            },
            "by_category": dict(sorted_categories),
            "period": {
                "start_date": min(t.date for t in transactions).isoformat(),
                "end_date": max(t.date for t in transactions).isoformat()
            }
        }
    
    def generate_monthly_report(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """
        Gera relatório mensal.
        
        Args:
            transactions: Lista de transações
            
        Returns:
            Dicionário com análise mensal
        """
        logger.info(f"📅 Gerando relatório mensal para {len(transactions)} transações")
        
        if not transactions:
            return {"error": "Nenhuma transação fornecida"}
        
        # Agrupa por mês
        monthly_data = {}
        
        for transaction in transactions:
            month_key = transaction.month_ref
            
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    "income": 0,
                    "expenses": 0,
                    "transactions_count": 0,
                    "transactions": [],
                    "categories": {}
                }
            
            month_info = monthly_data[month_key]
            month_info["transactions"].append(transaction)
            month_info["transactions_count"] += 1
            
            # Soma receitas/despesas
            if transaction.amount > 0:
                month_info["income"] += transaction.amount
            else:
                month_info["expenses"] += transaction.amount
            
            # Conta por categoria
            category = transaction.category.value
            if category not in month_info["categories"]:
                month_info["categories"][category] = 0
            month_info["categories"][category] += transaction.amount
        
        # Calcula saldos e ordena
        for month_key, month_info in monthly_data.items():
            month_info["balance"] = month_info["income"] + month_info["expenses"]
            
            # Ordena categorias por valor
            month_info["categories"] = dict(
                sorted(month_info["categories"].items(),
                      key=lambda x: abs(x[1]), reverse=True)
            )
        
        # Ordena meses (mais recente primeiro)
        sorted_months = dict(
            sorted(monthly_data.items(), key=lambda x: x[0], reverse=True)
        )
        
        return {
            "by_month": sorted_months,
            "summary": {
                "months_count": len(monthly_data),
                "total_income": sum(m["income"] for m in monthly_data.values()),
                "total_expenses": sum(m["expenses"] for m in monthly_data.values()),
                "average_monthly_income": sum(m["income"] for m in monthly_data.values()) / len(monthly_data) if monthly_data else 0,
                "average_monthly_expenses": sum(m["expenses"] for m in monthly_data.values()) / len(monthly_data) if monthly_data else 0
            }
        }
    
    def generate_source_report(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """
        Gera relatório por fonte (PIX, cartões, etc.).
        
        Args:
            transactions: Lista de transações
            
        Returns:
            Dicionário com análise por fonte
        """
        logger.info(f"💳 Gerando relatório por fonte para {len(transactions)} transações")
        
        if not transactions:
            return {"error": "Nenhuma transação fornecida"}
        
        # Agrupa por fonte
        source_data = {}
        
        for transaction in transactions:
            source = transaction.source.value
            
            if source not in source_data:
                source_data[source] = {
                    "transactions": [],
                    "total_amount": 0,
                    "count": 0,
                    "income": 0,
                    "expenses": 0
                }
            
            source_info = source_data[source]
            source_info["transactions"].append(transaction)
            source_info["total_amount"] += transaction.amount
            source_info["count"] += 1
            
            if transaction.amount > 0:
                source_info["income"] += transaction.amount
            else:
                source_info["expenses"] += transaction.amount
        
        # Ordena por número de transações
        sorted_sources = dict(
            sorted(source_data.items(),
                  key=lambda x: x[1]["count"], reverse=True)
        )
        
        return {
            "by_source": sorted_sources,
            "summary": {
                "sources_count": len(source_data),
                "most_used_source": max(source_data.items(), key=lambda x: x[1]["count"])[0] if source_data else None,
                "total_transactions": sum(s["count"] for s in source_data.values())
            }
        }
    
    def export_to_csv(self, transactions: List[Transaction], 
                     filename: str = "export.csv") -> Optional[Path]:
        """
        Exporta transações para CSV.
        
        Args:
            transactions: Lista de transações
            filename: Nome do arquivo CSV
            
        Returns:
            Caminho do arquivo gerado ou None se erro
        """
        if not transactions:
            logger.warning("⚠️ Nenhuma transação para exportar")
            return None
        
        logger.info(f"📄 Exportando {len(transactions)} transações para CSV")
        
        try:
            # Converte para DataFrame
            df_data = []
            for transaction in transactions:
                df_data.append({
                    "ID": transaction.id,
                    "Data": transaction.date.isoformat(),
                    "Descricao": transaction.description,
                    "Valor": transaction.amount,
                    "Fonte": transaction.source.value,
                    "Categoria": transaction.category.value,
                    "MesReferencia": transaction.month_ref,
                    "CriadoEm": transaction.created_at.isoformat()
                })
            
            df = pd.DataFrame(df_data)
            
            # Salva CSV
            output_path = self.planilhas_dir / filename
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            logger.info(f"✅ CSV exportado: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Erro ao exportar CSV: {e}")
            return None
    
    def generate_dashboard_data(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """
        Gera dados prontos para dashboard/visualização.
        
        Args:
            transactions: Lista de transações
            
        Returns:
            Dicionário com dados para dashboard
        """
        if not transactions:
            return {"error": "Nenhuma transação fornecida"}
        
        logger.info(f"📊 Gerando dados de dashboard para {len(transactions)} transações")
        
        # Dados básicos
        total_income = sum(t.amount for t in transactions if t.amount > 0)
        total_expenses = sum(t.amount for t in transactions if t.amount < 0)
        
        # Top categorias (despesas)
        expense_categories = {}
        for t in transactions:
            if t.amount < 0:
                cat = t.category.value
                expense_categories[cat] = expense_categories.get(cat, 0) + abs(t.amount)
        
        top_expense_categories = sorted(
            expense_categories.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Evolução mensal
        monthly_evolution = {}
        for t in transactions:
            month = t.month_ref
            if month not in monthly_evolution:
                monthly_evolution[month] = {"income": 0, "expenses": 0}
            
            if t.amount > 0:
                monthly_evolution[month]["income"] += t.amount
            else:
                monthly_evolution[month]["expenses"] += abs(t.amount)
        
        return {
            "summary": {
                "total_transactions": len(transactions),
                "total_income": total_income,
                "total_expenses": abs(total_expenses),
                "net_balance": total_income + total_expenses,
                "avg_transaction": sum(t.amount for t in transactions) / len(transactions)
            },
            "top_expense_categories": top_expense_categories,
            "monthly_evolution": monthly_evolution,
            "transactions_by_source": {
                source.value: len([t for t in transactions if t.source == source])
                for source in TransactionSource
            },
            "recent_transactions": [
                {
                    "date": t.date.isoformat(),
                    "description": t.description,
                    "amount": t.amount,
                    "category": t.category.value,
                    "source": t.source.value
                }
                for t in sorted(transactions, key=lambda x: x.date, reverse=True)[:10]
            ]
        }