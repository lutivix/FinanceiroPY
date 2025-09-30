"""
Serviço principal que orquestra todo o processamento
"""

import logging
from typing import List, Dict, Optional, Any
from pathlib import Path
import time
from datetime import datetime

from models import Transaction, ProcessingStats
from database import TransactionRepository, CategoryRepository
from services.file_processing_service import FileProcessingService
from services.categorization_service import CategorizationService
from services.report_service import ReportService

logger = logging.getLogger(__name__)


class FinancialAgentService:
    """
    Serviço principal que orquestra todo o processamento financeiro.
    Este é o ponto de entrada principal da aplicação modular.
    """
    
    def __init__(self, data_directory: Path, config: Dict[str, Any] = None):
        self.data_directory = Path(data_directory)
        self.config = config or {}
        
        # Inicializa repositórios
        db_path = self.data_directory / "db" / "financeiro.db"
        self.transaction_repo = TransactionRepository(db_path)
        self.category_repo = CategoryRepository(db_path)
        
        # Inicializa serviços
        self.file_service = FileProcessingService(self.data_directory)
        self.categorization_service = CategorizationService(self.category_repo)
        self.report_service = ReportService(self.data_directory)
        
        # Estatísticas da sessão
        self.session_stats = ProcessingStats()
    
    def run_complete_processing(self, months_back: int = 12, 
                              save_to_database: bool = True,
                              generate_excel: bool = True) -> Dict[str, Any]:
        """
        Executa o processamento completo (equivale ao agente_financeiro.py original).
        
        Args:
            months_back: Quantos meses para trás buscar arquivos
            save_to_database: Se deve salvar no banco de dados
            generate_excel: Se deve gerar planilha Excel
            
        Returns:
            Dicionário com resultados do processamento
        """
        start_time = time.time()
        logger.info("🚀 Iniciando processamento completo do Agente Financeiro IA")
        
        # Reseta estatísticas
        self.session_stats = ProcessingStats()
        
        try:
            # 1. Valida ambiente
            if not self._validate_environment():
                return {"success": False, "error": "Ambiente inválido"}
            
            # 2. Processa arquivos
            logger.info("📂 Etapa 1: Processamento de arquivos")
            transactions = self.file_service.process_all_files(months_back)
            
            if not transactions:
                logger.warning("⚠️ Nenhuma transação encontrada")
                return {"success": False, "error": "Nenhuma transação encontrada"}
            
            self.session_stats.transactions_extracted = len(transactions)
            logger.info(f"✅ {len(transactions)} transações extraídas")
            
            # 3. Categoriza transações
            logger.info("🏷️ Etapa 2: Categorização de transações")
            categorized_transactions = self.categorization_service.categorize_transactions(transactions)
            
            categorized_count = sum(1 for t in categorized_transactions 
                                  if t.category.value != "A definir")
            self.session_stats.transactions_categorized = categorized_count
            logger.info(f"✅ {categorized_count}/{len(transactions)} transações categorizadas")
            
            # 4. Salva no banco (opcional)
            saved_count = 0
            if save_to_database:
                logger.info("💾 Etapa 3: Salvando no banco de dados")
                saved_count = self.transaction_repo.save_transactions(categorized_transactions)
                logger.info(f"✅ {saved_count} transações salvas no banco")
            
            # 5. Gera Excel (opcional)
            excel_path = None
            if generate_excel:
                logger.info("📊 Etapa 4: Gerando planilha Excel")
                excel_filename = self.config.get("excel_filename", "consolidado_temp.xlsx")
                excel_path = self.report_service.generate_consolidated_excel(
                    categorized_transactions, excel_filename
                )
                if excel_path:
                    logger.info(f"✅ Excel gerado: {excel_path}")
            
            # 6. Finaliza estatísticas
            self.session_stats.processing_time_seconds = time.time() - start_time
            
            # 7. Gera resumo
            summary = self._generate_session_summary(
                categorized_transactions, excel_path, saved_count
            )
            
            logger.info("🎉 Processamento completo finalizado com sucesso!")
            logger.info(self.session_stats.summary())
            
            return {
                "success": True,
                "summary": summary,
                "stats": self.session_stats,
                "excel_path": str(excel_path) if excel_path else None,
                "transactions_count": len(categorized_transactions)
            }
            
        except Exception as e:
            error_msg = f"Erro durante processamento completo: {e}"
            logger.error(f"❌ {error_msg}")
            self.session_stats.add_error(error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "stats": self.session_stats
            }
    
    def process_single_file(self, file_path: Path, 
                          categorize: bool = True) -> Dict[str, Any]:
        """
        Processa um arquivo específico.
        
        Args:
            file_path: Caminho do arquivo
            categorize: Se deve categorizar as transações
            
        Returns:
            Resultado do processamento
        """
        logger.info(f"📄 Processando arquivo individual: {file_path.name}")
        
        try:
            # Processa arquivo
            transactions = self.file_service.process_file(file_path)
            
            if not transactions:
                return {"success": False, "error": "Nenhuma transação extraída"}
            
            # Categoriza se solicitado
            if categorize:
                transactions = self.categorization_service.categorize_transactions(transactions)
            
            return {
                "success": True,
                "transactions": transactions,
                "count": len(transactions)
            }
            
        except Exception as e:
            error_msg = f"Erro ao processar arquivo {file_path.name}: {e}"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def learn_categories_from_excel(self, excel_path: Path) -> Dict[str, Any]:
        """
        Aprende categorias a partir de um Excel já categorizado.
        
        Args:
            excel_path: Caminho do arquivo Excel
            
        Returns:
            Resultado do aprendizado
        """
        logger.info(f"🧠 Aprendendo categorias de: {excel_path.name}")
        
        try:
            # Lê Excel
            import pandas as pd
            df = pd.read_excel(excel_path)
            
            # Valida colunas necessárias
            required_cols = ["Descricao", "Categoria"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                return {
                    "success": False,
                    "error": f"Colunas não encontradas: {missing_cols}"
                }
            
            # Filtra apenas transações categorizadas
            df_categorized = df[
                (df["Categoria"].notna()) & 
                (df["Categoria"] != "A definir")
            ]
            
            if len(df_categorized) == 0:
                return {
                    "success": False,
                    "error": "Nenhuma transação categorizada encontrada"
                }
            
            # Aprende categorias
            learned_count = 0
            for _, row in df_categorized.iterrows():
                description = str(row["Descricao"]).strip()
                category_str = str(row["Categoria"]).strip()
                
                # Tenta encontrar a categoria
                try:
                    from models import TransactionCategory
                    category = TransactionCategory(category_str)
                    
                    if self.categorization_service.learn_category(description, category):
                        learned_count += 1
                        
                except ValueError:
                    logger.warning(f"⚠️ Categoria inválida: {category_str}")
            
            # Atualiza cache
            self.categorization_service.refresh_cache()
            
            logger.info(f"✅ {learned_count} categorias aprendidas")
            
            return {
                "success": True,
                "learned_count": learned_count,
                "total_processed": len(df_categorized)
            }
            
        except Exception as e:
            error_msg = f"Erro ao aprender categorias: {e}"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def generate_reports(self, transactions: List[Transaction] = None) -> Dict[str, Any]:
        """
        Gera relatórios completos.
        
        Args:
            transactions: Lista de transações (se None, busca do banco)
            
        Returns:
            Relatórios gerados
        """
        logger.info("📊 Gerando relatórios completos")
        
        try:
            # Se não forneceu transações, busca do banco
            if transactions is None:
                # Busca transações dos últimos 12 meses
                from datetime import date, timedelta
                end_date = date.today()
                start_date = end_date - timedelta(days=365)
                transactions = self.transaction_repo.get_transactions_by_period(start_date, end_date)
            
            if not transactions:
                return {"success": False, "error": "Nenhuma transação para gerar relatórios"}
            
            # Gera diferentes tipos de relatório
            reports = {
                "categorized": self.report_service.generate_categorized_report(transactions),
                "monthly": self.report_service.generate_monthly_report(transactions),
                "by_source": self.report_service.generate_source_report(transactions),
                "dashboard": self.report_service.generate_dashboard_data(transactions)
            }
            
            logger.info("✅ Relatórios gerados com sucesso")
            
            return {
                "success": True,
                "reports": reports,
                "transactions_analyzed": len(transactions)
            }
            
        except Exception as e:
            error_msg = f"Erro ao gerar relatórios: {e}"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def _validate_environment(self) -> bool:
        """Valida se o ambiente está configurado corretamente."""
        return self.file_service.validate_data_directory()
    
    def _generate_session_summary(self, transactions: List[Transaction], 
                                 excel_path: Optional[Path], 
                                 saved_count: int) -> Dict[str, Any]:
        """Gera resumo da sessão de processamento."""
        if not transactions:
            return {}
        
        # Estatísticas básicas
        total_income = sum(t.amount for t in transactions if t.amount > 0)
        total_expenses = sum(t.amount for t in transactions if t.amount < 0)
        categorized_count = sum(1 for t in transactions if t.category.value != "A definir")
        
        # Por fonte
        by_source = {}
        for t in transactions:
            source = t.source.value
            by_source[source] = by_source.get(source, 0) + 1
        
        # Por categoria
        by_category = {}
        for t in transactions:
            category = t.category.value
            by_category[category] = by_category.get(category, 0) + 1
        
        return {
            "processing_date": datetime.now().isoformat(),
            "transactions": {
                "total": len(transactions),
                "categorized": categorized_count,
                "saved_to_db": saved_count
            },
            "financial": {
                "total_income": total_income,
                "total_expenses": total_expenses,
                "net_balance": total_income + total_expenses
            },
            "by_source": by_source,
            "by_category": by_category,
            "files": {
                "excel_generated": excel_path is not None,
                "excel_path": str(excel_path) if excel_path else None
            },
            "period": {
                "start": min(t.date for t in transactions).isoformat(),
                "end": max(t.date for t in transactions).isoformat()
            }
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Retorna status geral do sistema.
        
        Returns:
            Status do sistema
        """
        try:
            # Status dos repositórios
            transaction_stats = self.transaction_repo.get_stats()
            category_stats = self.category_repo.get_stats()
            
            # Status dos arquivos
            file_summary = self.file_service.get_file_summary()
            
            # Status dos serviços
            categorization_stats = self.categorization_service.get_stats()
            
            return {
                "system": {
                    "data_directory": str(self.data_directory),
                    "environment_valid": self._validate_environment()
                },
                "database": {
                    "transactions": transaction_stats,
                    "categories": category_stats
                },
                "files": file_summary,
                "services": {
                    "categorization": categorization_stats
                },
                "last_session": self.session_stats.summary() if self.session_stats.files_processed > 0 else None
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter status: {e}")
            return {"error": str(e)}