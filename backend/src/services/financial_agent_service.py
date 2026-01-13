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
from services.openfinance_loader import OpenFinanceLoader

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
        
        # Habilita deduplicação por padrão (pode ser desabilitado via config)
        enable_dedup = self.config.get('enable_deduplication', True)
        self.transaction_repo = TransactionRepository(db_path, enable_deduplication=enable_dedup)
        self.category_repo = CategoryRepository(db_path)
        
        # Inicializa serviços
        self.file_service = FileProcessingService(self.data_directory)
        self.categorization_service = CategorizationService(self.category_repo)
        self.report_service = ReportService(self.data_directory)
        self.openfinance_loader = OpenFinanceLoader(db_path)
        
        # Estatísticas da sessão
        self.session_stats = ProcessingStats()
    
    def run_complete_processing(self, months_back: int = 12, 
                              save_to_database: bool = True,
                              generate_excel: bool = True,
                              load_openfinance: bool = True) -> Dict[str, Any]:
        """
        Executa o processamento completo (equivale ao agente_financeiro.py original).
        
        FLUXO ATUALIZADO COM DEDUPLICAÇÃO:
        1. Carrega transações validadas do Open Finance (se disponível)
        2. Processa arquivos Excel
        3. Categoriza todas as transações
        4. Salva no banco COM DEDUPLICAÇÃO (evita duplicatas)
        5. Gera Excel consolidado
        
        Args:
            months_back: Quantos meses para trás buscar arquivos
            save_to_database: Se deve salvar no banco de dados
            generate_excel: Se deve gerar planilha Excel
            load_openfinance: Se deve carregar dados do Open Finance primeiro
            
        Returns:
            Dicionário com resultados do processamento
        """
        start_time = time.time()
        logger.info("🚀 Iniciando processamento completo do Agente Financeiro IA")
        logger.info("🔒 Deduplicação ATIVADA - transacoes duplicadas serão ignoradas")
        
        # Reseta estatísticas
        self.session_stats = ProcessingStats()
        all_transactions = []
        openfinance_count = 0
        
        try:
            # 1. Valida ambiente
            if not self._validate_environment():
                return {"success": False, "error": "Ambiente inválido"}
            
            # 2. NOVO: Carrega do Open Finance primeiro (dados validados)
            openfinance_max_date = None
            if load_openfinance:
                logger.info("🏬 Etapa 1: Carregando transações do Open Finance")
                openfinance_transactions = self.openfinance_loader.load_transactions()
                
                if openfinance_transactions:
                    openfinance_count = len(openfinance_transactions)
                    
                    # FILTRAR Open Finance: EXCLUIR mes_comp = dezembro 2025
                    from datetime import datetime, date
                    limite_data = date(2025, 11, 18)
                    openfinance_filtered = []
                    removed_by_date = 0
                    removed_by_mescomp = 0
                    
                    for t in openfinance_transactions:
                        # Excluir se data > 18/11/2025
                        if t.date > limite_data:
                            removed_by_date += 1
                            continue
                        # Excluir se mes_comp = dezembro 2025
                        if hasattr(t, 'mes_comp') and t.mes_comp and '2025-12' in str(t.mes_comp):
                            removed_by_mescomp += 1
                            continue
                        openfinance_filtered.append(t)
                    
                    if removed_by_date > 0:
                        logger.info(f"🚫 {removed_by_date} transações do Open Finance removidas (após 18/11/2025)")
                    if removed_by_mescomp > 0:
                        logger.info(f"🚫 {removed_by_mescomp} transações do Open Finance removidas (mes_comp dezembro 2025)")
                    
                    all_transactions.extend(openfinance_filtered)
                    openfinance_count = len(openfinance_filtered)
                    logger.info(f"✅ {openfinance_count} transações carregadas do Open Finance")
                    
                    # Mostra range de datas do Open Finance
                    min_date, max_date = self.openfinance_loader.get_date_range()
                    if min_date and max_date:
                        # LIMITE FIXO: Usar apenas até 18/11/2025 para evitar ambiguidade com cartões
                        openfinance_max_date = "2025-11-18"
                        logger.info(f"📅 Período Open Finance: {min_date} a {max_date}")
                        logger.info(f"🔒 Data limite ajustada para: {openfinance_max_date}")
                else:
                    logger.info("ℹ️ Nenhum dado do Open Finance disponível")
            
            # 3. Processa arquivos Excel
            logger.info("📂 Etapa 2: Processamento de arquivos Excel")
            excel_transactions = self.file_service.process_all_files(months_back)
            
            if excel_transactions:
                # Filtra Excel: só aceita transações APÓS última data do Open Finance
                # IMPORTANTE: Para CARTÕES, sempre incluir (devido ao mes_comp)
                if openfinance_max_date:
                    from datetime import datetime
                    max_date_obj = datetime.fromisoformat(openfinance_max_date).date()
                    
                    filtered_excel = []
                    for t in excel_transactions:
                        # Cartões: SEMPRE incluir (dedup usa mes_comp)
                        if 'Master' in t.source.value or 'Visa' in t.source.value:
                            filtered_excel.append(t)
                        # PIX/Extrato: Filtrar por data
                        elif t.date > max_date_obj:
                            filtered_excel.append(t)
                    
                    excel_filtered_count = len(excel_transactions) - len(filtered_excel)
                    if excel_filtered_count > 0:
                        logger.info(
                            f"🚫 {excel_filtered_count} transações do Excel filtradas "
                            f"(período coberto pelo Open Finance)"
                        )
                    excel_transactions = filtered_excel
                
                all_transactions.extend(excel_transactions)
                logger.info(f"✅ {len(excel_transactions)} transações extraídas do Excel")
            
            if not all_transactions:
                logger.warning("⚠️ Nenhuma transação encontrada")
                return {"success": False, "error": "Nenhuma transação encontrada"}
            
            self.session_stats.transactions_extracted = len(all_transactions)
            logger.info(
                f"📊 Total: {len(all_transactions)} transações "
                f"(Open Finance: {openfinance_count}, Excel: {len(excel_transactions)})"
            )
            
            # 3.5. Remove duplicatas in-memory ANTES de categorizar
            logger.info("🔍 Etapa 2.5: Removendo duplicatas in-memory")
            original_count = len(all_transactions)
            
            # DEBUG: Contar Dezembro 2025 Master ANTES da deduplicação in-memory
            debug_dez_master_before = [t for t in all_transactions if t.month_ref == 'Dezembro 2025' and 'Master' in t.source.value]
            if debug_dez_master_before:
                total_before = sum(abs(t.amount) for t in debug_dez_master_before)
                logger.info(f"🔍 DEBUG: Dezembro 2025 Master ANTES dedup in-memory: {len(debug_dez_master_before)} transacoes = R$ {total_before:,.2f}")
            
            all_transactions = self._deduplicate_in_memory(all_transactions)
            duplicates_removed = original_count - len(all_transactions)
            
            # DEBUG: Contar Dezembro 2025 Master DEPOIS da deduplicação in-memory
            debug_dez_master_after = [t for t in all_transactions if t.month_ref == 'Dezembro 2025' and 'Master' in t.source.value]
            if debug_dez_master_after:
                total_after = sum(abs(t.amount) for t in debug_dez_master_after)
                logger.info(f"🔍 DEBUG: Dezembro 2025 Master DEPOIS dedup in-memory: {len(debug_dez_master_after)} transacoes = R$ {total_after:,.2f}")
            
            if duplicates_removed > 0:
                logger.info(
                    f"✅ {duplicates_removed} duplicatas removidas in-memory "
                    f"({len(all_transactions)} únicas)"
                )
            
            # 4. Categoriza transações
            logger.info("🏷️ Etapa 3: Categorização de transações")
            categorized_transactions = self.categorization_service.categorize_transactions(
                all_transactions
            )
            
            categorized_count = sum(1 for t in categorized_transactions 
                                  if t.category.value != "A definir")
            self.session_stats.transactions_categorized = categorized_count
            logger.info(f"✅ {categorized_count}/{len(all_transactions)} transações categorizadas")
            
            # 5. Salva no banco COM DEDUPLICAÇÃO (opcional)
            saved_count = 0
            if save_to_database:
                logger.info("💾 Etapa 4: Salvando no banco de dados (com deduplicação)")
                saved_count = self.transaction_repo.save_transactions(
                    categorized_transactions,
                    skip_duplicates=True  # Força verificação de duplicatas
                )
                logger.info(f"✅ {saved_count} transações salvas no banco")
                
                # Mostra estatísticas de deduplicação
                dedup_stats = self.transaction_repo.get_deduplication_stats()
                if dedup_stats['duplicates_skipped'] > 0:
                    logger.info(
                        f"🔍 Deduplicação: {dedup_stats['duplicates_skipped']} duplicatas ignoradas "
                        f"de {dedup_stats['checked']} verificadas"
                    )
            
            # 6. Gera Excel (opcional)
            excel_path = None
            if generate_excel:
                logger.info("📊 Etapa 5: Gerando planilha Excel")
                excel_filename = self.config.get("excel_filename", "consolidado_temp.xlsx")
                excel_path = self.report_service.generate_consolidated_excel(
                    categorized_transactions, excel_filename
                )
                if excel_path:
                    logger.info(f"✅ Excel gerado: {excel_path}")
            
            # 7. Finaliza estatísticas
            self.session_stats.processing_time_seconds = time.time() - start_time
            
            # 8. Gera resumo
            summary = self._generate_session_summary(
                categorized_transactions, excel_path, saved_count
            )
            
            # Adiciona estatísticas de deduplicação ao resumo
            summary['openfinance_loaded'] = openfinance_count
            summary['deduplication_stats'] = self.transaction_repo.get_deduplication_stats()
            
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
    
    def _deduplicate_in_memory(self, transactions: List[Transaction]) -> List[Transaction]:
        """
        Remove duplicatas in-memory usando mesma lógica do DeduplicationHelper.
        Prioriza transações do Open Finance sobre Excel quando há duplicatas.
        
        Args:
            transactions: Lista de transações com possíveis duplicatas
            
        Returns:
            Lista deduplicated com transações únicas
        """
        from utils import DeduplicationHelper
        
        seen_keys = {}
        unique_transactions = []
        duplicates_found = 0
        
        for transaction in transactions:
            # Gera chave de deduplicação incluindo mes_comp (crítico para cartões)
            # Cartões com mesma data/valor mas mes_comp diferente NÃO são duplicatas
            mes_comp_str = transaction.mes_comp if hasattr(transaction, 'mes_comp') and transaction.mes_comp else ""
            dedup_key = DeduplicationHelper.generate_dedup_key(
                data=transaction.date.isoformat(),
                descricao=transaction.description,
                valor=transaction.amount,
                fonte=transaction.source.value
            ) + f"_mescomp_{mes_comp_str}"
            
            # # DEBUG: Mostrar mes_comp para transações Master de dezembro
            # if 'Master' in transaction.source.value and transaction.date.month == 12 and transaction.date.year == 2025:
            #     origem = "OF" if (transaction.id and transaction.id.startswith("openfinance-")) else "Excel"
            #     logger.info(f"🔍 DEBUG dedup [{origem}] {transaction.date} {transaction.description[:30]} = R$ {transaction.amount:.2f} | mes_comp={mes_comp_str}")
            
            if dedup_key in seen_keys:
                duplicates_found += 1
                existing = seen_keys[dedup_key]
                
                # Prioriza Open Finance sobre Excel
                # (transações do Open Finance têm id começando com "openfinance-")
                if transaction.id and transaction.id.startswith("openfinance-"):
                    # Substitui Excel por Open Finance
                    if not (existing.id and existing.id.startswith("openfinance-")):
                        logger.debug(f"🔄 Substituindo Excel por Open Finance: {dedup_key}")
                        # Remove a transação Excel da lista
                        unique_transactions.remove(existing)
                        # Adiciona a do Open Finance
                        unique_transactions.append(transaction)
                        seen_keys[dedup_key] = transaction
                    else:
                        # Ambas são do Open Finance, ignora a duplicata
                        logger.debug(f"⏭️ Duplicata Open Finance ignorada: {dedup_key}")
                else:
                    # Transação atual é do Excel, mantém a existente (pode ser Open Finance)
                    logger.debug(f"⏭️ Duplicata Excel ignorada: {dedup_key}")
            else:
                # Primeira vez vendo essa transação
                seen_keys[dedup_key] = transaction
                unique_transactions.append(transaction)
        
        if duplicates_found > 0:
            logger.info(f"🧹 {duplicates_found} duplicatas removidas in-memory")
        
        return unique_transactions