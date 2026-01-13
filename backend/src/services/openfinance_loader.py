"""
Serviço para carregar dados validados do Open Finance
====================================================

Carrega transações da tabela transacoes_openfinance (dados validados
do Pluggy API) e converte para o formato Transaction do sistema.

Estes dados têm prioridade sobre dados do Excel, pois foram validados
e categorizados corretamente durante o trial do Open Finance.

Autor: Sistema
Data: 2026-01-13
Versão: 1.0
"""

import sqlite3
import logging
from typing import List, Optional
from pathlib import Path
from datetime import datetime

from models import Transaction, TransactionSource, TransactionCategory

logger = logging.getLogger(__name__)


class OpenFinanceLoader:
    """
    Carrega transações validadas do Open Finance.
    
    A tabela transacoes_openfinance contém dados históricos do período
    em que o sistema usava a API do Pluggy (trial period).
    Estes dados são 100% validados e devem ser carregados ANTES
    de processar arquivos Excel para evitar duplicatas.
    """
    
    def __init__(self, db_path: Path):
        """
        Inicializa o loader.
        
        Args:
            db_path: Caminho para o banco de dados SQLite
        """
        self.db_path = db_path
        self.stats = {
            'available': 0,
            'loaded': 0,
            'errors': 0
        }
    
    def check_table_exists(self) -> bool:
        """
        Verifica se a tabela transacoes_openfinance existe.
        
        Returns:
            True se existe, False caso contrário
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='transacoes_openfinance'
                """)
                exists = cursor.fetchone() is not None
                
                if exists:
                    # Conta registros disponíveis
                    cursor.execute("SELECT COUNT(*) FROM transacoes_openfinance")
                    self.stats['available'] = cursor.fetchone()[0]
                    logger.info(
                        f"📊 Tabela transacoes_openfinance encontrada: "
                        f"{self.stats['available']} registros disponíveis"
                    )
                else:
                    logger.info("ℹ️  Tabela transacoes_openfinance não encontrada")
                
                return exists
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar tabela: {e}")
            return False
    
    def load_transactions(self, 
                         only_validated: bool = True,
                         mes_comp_filter: Optional[str] = None) -> List[Transaction]:
        """
        Carrega transações do Open Finance convertidas para Transaction.
        
        Args:
            only_validated: Se True, carrega apenas registros validados (padrão)
            mes_comp_filter: Filtro opcional por mês competência (ex: '202511')
            
        Returns:
            Lista de objetos Transaction
        """
        transactions = []
        
        # Verifica se tabela existe
        if not self.check_table_exists():
            logger.warning("⚠️  Nenhum dado do Open Finance disponível")
            return transactions
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Monta query
                query = """
                    SELECT 
                        provider_id,
                        data,
                        descricao,
                        valor,
                        categoria,
                        fonte,
                        mes_comp,
                        metadata_json
                    FROM transacoes_openfinance
                    WHERE 1=1
                """
                
                params = []
                
                # Filtro por mês competência se especificado
                if mes_comp_filter:
                    query += " AND mes_comp = ?"
                    params.append(mes_comp_filter)
                
                # Ordena por data
                query += " ORDER BY data"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                logger.info(
                    f"📥 Carregando {len(rows)} transações do Open Finance"
                    + (f" (mês: {mes_comp_filter})" if mes_comp_filter else "")
                )
                
                # Converte cada row para Transaction
                for row in rows:
                    try:
                        transaction = self._row_to_transaction(row)
                        if transaction:
                            transactions.append(transaction)
                            self.stats['loaded'] += 1
                    except Exception as e:
                        self.stats['errors'] += 1
                        logger.warning(f"⚠️  Erro ao converter transação: {e}")
                        continue
                
                logger.info(
                    f"✅ {self.stats['loaded']} transações carregadas do Open Finance "
                    f"({self.stats['errors']} erros)"
                )
                
        except Exception as e:
            logger.error(f"❌ Erro ao carregar transações do Open Finance: {e}")
        
        return transactions
    
    def _row_to_transaction(self, row: tuple) -> Optional[Transaction]:
        """
        Converte uma row do banco para objeto Transaction.
        
        Args:
            row: Tupla com dados da transação
            
        Returns:
            Objeto Transaction ou None se houver erro
        """
        try:
            (
                provider_id,
                data_str,
                descricao,
                valor,
                categoria,
                fonte,
                mes_comp,
                metadata_json
            ) = row
            
            # Converte data
            if isinstance(data_str, str):
                date_obj = datetime.strptime(data_str, '%Y-%m-%d').date()
            else:
                date_obj = data_str
            
            # Mapeia fonte para TransactionSource
            try:
                # Fonte já vem no formato correto do banco (ex: "Master Físico")
                source = TransactionSource(fonte)
            except ValueError:
                # Se fonte não é reconhecida, usa PIX como fallback
                logger.warning(f"⚠️  Fonte desconhecida: {fonte}, usando PIX")
                source = TransactionSource.PIX
            
            # Mapeia categoria para TransactionCategory
            try:
                category = TransactionCategory(categoria)
            except ValueError:
                # Se categoria não é reconhecida, usa A_DEFINIR
                logger.warning(f"⚠️  Categoria desconhecida: {categoria}, usando A definir")
                category = TransactionCategory.A_DEFINIR
            
            # CORREÇÃO: Inverte sinal do PIX no OpenFinance
            # No OpenFinance, PIX vem com sinal invertido em relação aos Excel
            amount_value = float(valor)
            if source == TransactionSource.PIX:
                amount_value = -amount_value
            
            # Cria Transaction
            transaction = Transaction(
                date=date_obj,
                description=descricao,
                amount=amount_value,
                source=source,
                category=category,
                month_ref=mes_comp,
                id=f"openfinance-{provider_id}",
                raw_data={'origin': 'openfinance', 'provider_id': provider_id}
            )
            
            return transaction
            
        except Exception as e:
            logger.error(f"❌ Erro ao converter row: {e}")
            return None
    
    def get_available_months(self) -> List[str]:
        """
        Retorna lista de meses com dados disponíveis no Open Finance.
        
        Returns:
            Lista de strings no formato 'YYYYMM' (ex: ['202510', '202511'])
        """
        months = []
        
        if not self.check_table_exists():
            return months
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT mes_comp 
                    FROM transacoes_openfinance 
                    ORDER BY mes_comp
                """)
                
                months = [row[0] for row in cursor.fetchall() if row[0]]
                logger.info(f"📅 Meses disponíveis no Open Finance: {', '.join(months)}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar meses disponíveis: {e}")
        
        return months
    
    def get_date_range(self) -> tuple:
        """
        Retorna o range de datas disponível no Open Finance.
        
        Returns:
            Tupla (data_inicial, data_final) como strings YYYY-MM-DD
        """
        if not self.check_table_exists():
            return None, None
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT MIN(data), MAX(data) 
                    FROM transacoes_openfinance
                """)
                
                min_date, max_date = cursor.fetchone()
                
                if min_date and max_date:
                    logger.info(f"📅 Range Open Finance: {min_date} até {max_date}")
                
                return min_date, max_date
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar range de datas: {e}")
            return None, None
    
    def get_stats(self) -> dict:
        """Retorna estatísticas de carregamento."""
        return self.stats.copy()


# Função de conveniência para uso direto
def load_openfinance_transactions(db_path: Path, 
                                 mes_comp_filter: Optional[str] = None) -> List[Transaction]:
    """
    Função de conveniência para carregar transações do Open Finance.
    
    Args:
        db_path: Caminho do banco de dados
        mes_comp_filter: Filtro opcional por mês
        
    Returns:
        Lista de transações
    """
    loader = OpenFinanceLoader(db_path)
    return loader.load_transactions(mes_comp_filter=mes_comp_filter)


# Teste rápido do módulo
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Configura logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Path do banco
    db_path = Path("../../dados/db/financeiro.db")
    
    if not db_path.exists():
        print(f"❌ Banco não encontrado: {db_path}")
        print("💡 Execute a partir do diretório correto")
        sys.exit(1)
    
    print("=" * 60)
    print("TESTE DO OPENFINANCE LOADER")
    print("=" * 60)
    
    # Cria loader
    loader = OpenFinanceLoader(db_path)
    
    # Verifica disponibilidade
    if loader.check_table_exists():
        # Mostra meses disponíveis
        months = loader.get_available_months()
        print(f"\n📅 Meses com dados: {', '.join(months)}")
        
        # Mostra range de datas
        min_date, max_date = loader.get_date_range()
        print(f"📅 Range: {min_date} até {max_date}")
        
        # Carrega transações
        print("\n📥 Carregando transações...")
        transactions = loader.load_transactions()
        
        print(f"\n✅ {len(transactions)} transações carregadas")
        
        # Mostra primeiras 5
        if transactions:
            print("\n📋 Primeiras 5 transações:")
            for i, t in enumerate(transactions[:5], 1):
                print(f"  {i}. {t.date} | {t.description[:40]:40s} | R$ {t.amount:8.2f} | {t.source.value}")
        
        # Estatísticas
        stats = loader.get_stats()
        print(f"\n📊 Estatísticas:")
        print(f"  Disponíveis: {stats['available']}")
        print(f"  Carregadas: {stats['loaded']}")
        print(f"  Erros: {stats['errors']}")
    else:
        print("\n⚠️  Nenhum dado do Open Finance encontrado")
    
    print("\n" + "=" * 60)
