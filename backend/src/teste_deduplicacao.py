"""
Script de teste para lógica de deduplicação de transações
===========================================================

Testa a lógica de deduplicação usando banco SQLite in-memory,
sem afetar as bases de dados reais (lancamentos ou transacoes_openfinance).

Funcionalidades testadas:
1. Normalização de descrições (remove datas dd/mm e parcelas x/y)
2. Deduplicação baseada em chave composta (Data, Desc_normalizada, Valor, Fonte)
3. Priorização de dados do transacoes_openfinance sobre Excel
4. Inserção sem duplicatas

Autor: Sistema
Data: 2026-01-13
"""

import sqlite3
import re
import logging
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeduplicationHelper:
    """Helper para normalização e deduplicação de transações"""
    
    @staticmethod
    def normalize_description_for_dedup(description: str) -> str:
        """
        Normaliza descrição removendo partes variáveis para deduplicação.
        
        Remove:
        - Datas no formato dd/mm (ex: "PIX RECEBIDO 25/12" -> "PIX RECEBIDO")
        - Parcelas no formato x/y (ex: "COMPRA 2/5" -> "COMPRA")
        - Espaços múltiplos e pontuação extra
        
        Args:
            description: Descrição original
            
        Returns:
            Descrição normalizada para chave de deduplicação
        """
        if not description:
            return ""
        
        # Converte para uppercase e remove espaços extras
        desc = description.strip().upper()
        
        # Remove datas no final (formato dd/mm)
        # Exemplo: "PIX ENVIADO 15/11" -> "PIX ENVIADO"
        desc = re.sub(r'\s+\d{2}/\d{2}$', '', desc)
        
        # Remove parcelas (formato x/y ou x/yy)
        # Exemplo: "MERCADO LIVRE 2/12" -> "MERCADO LIVRE"
        desc = re.sub(r'\s+\d{1,2}/\d{1,2}$', '', desc)
        
        # Remove múltiplos espaços
        desc = re.sub(r'\s+', ' ', desc).strip()
        
        return desc
    
    @staticmethod
    def generate_dedup_key(data: str, descricao: str, valor: float, fonte: str) -> str:
        """
        Gera chave composta para deduplicação.
        
        Args:
            data: Data no formato YYYY-MM-DD ou dd/mm/yyyy
            descricao: Descrição da transação
            valor: Valor da transação
            fonte: Fonte da transação
            
        Returns:
            Chave composta no formato "YYYY-MM-DD|DESC_NORM|VALOR|FONTE"
        """
        # Normaliza data para YYYY-MM-DD
        if '/' in data:
            # Converte dd/mm/yyyy para YYYY-MM-DD
            parts = data.split('/')
            if len(parts) == 3:
                data_norm = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
            else:
                data_norm = data
        else:
            data_norm = data
        
        # Normaliza descrição
        desc_norm = DeduplicationHelper.normalize_description_for_dedup(descricao)
        
        # Normaliza valor (2 casas decimais)
        valor_norm = f"{float(valor):.2f}"
        
        # Fonte em uppercase
        fonte_norm = fonte.upper().strip()
        
        return f"{data_norm}|{desc_norm}|{valor_norm}|{fonte_norm}"


class TransactionDeduplicator:
    """Classe principal para teste de deduplicação"""
    
    def __init__(self, use_memory: bool = True):
        """
        Inicializa o testador.
        
        Args:
            use_memory: Se True, usa banco in-memory (padrão). 
                       Se False, cria arquivo temporário.
        """
        self.use_memory = use_memory
        self.conn = None
        self.helper = DeduplicationHelper()
        self.stats = {
            'total_processed': 0,
            'inserted': 0,
            'duplicates_skipped': 0,
            'from_openfinance': 0,
            'from_excel': 0
        }
    
    def connect(self):
        """Conecta ao banco de dados (in-memory ou temporário)"""
        if self.use_memory:
            self.conn = sqlite3.connect(':memory:')
            logger.info("✅ Conectado ao banco SQLite in-memory")
        else:
            db_path = Path(__file__).parent / 'test_dedup_temp.db'
            self.conn = sqlite3.connect(db_path)
            logger.info(f"✅ Conectado ao banco temporário: {db_path}")
        
        self._create_tables()
    
    def _create_tables(self):
        """Cria tabelas de teste"""
        cursor = self.conn.cursor()
        
        # Tabela lancamentos (similar à real)
        cursor.execute("""
            CREATE TABLE lancamentos (
                Data TEXT NOT NULL,
                Descricao TEXT NOT NULL,
                Valor REAL NOT NULL,
                Fonte TEXT NOT NULL,
                Categoria TEXT NOT NULL,
                MesComp TEXT NOT NULL,
                id TEXT,
                raw_data TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT
            )
        """)
        
        # Tabela transacoes_openfinance (simulada)
        cursor.execute("""
            CREATE TABLE transacoes_openfinance (
                id TEXT PRIMARY KEY,
                data_transacao TEXT NOT NULL,
                descricao TEXT NOT NULL,
                valor REAL NOT NULL,
                fonte TEXT NOT NULL,
                categoria TEXT,
                mes_ref TEXT,
                parcela_numero INTEGER,
                parcela_total INTEGER,
                validated BOOLEAN DEFAULT 1
            )
        """)
        
        # Índice para acelerar busca de duplicatas
        cursor.execute("""
            CREATE INDEX idx_lancamentos_dedup 
            ON lancamentos(Data, Descricao, Valor, Fonte)
        """)
        
        self.conn.commit()
        logger.info("✅ Tabelas criadas com sucesso")
    
    def insert_test_openfinance_data(self):
        """Insere dados de teste simulando transacoes_openfinance"""
        cursor = self.conn.cursor()
        
        test_data = [
            ('of-001', '2025-11-15', 'PIX ENVIADO MERCADO', -50.00, 'ITAU', 'Alimentação', '202511', None, None, 1),
            ('of-002', '2025-11-16', 'COMPRA AMAZON 1/3', -299.90, 'LATAM', 'Compras Online', '202511', 1, 3, 1),
            ('of-003', '2025-11-17', 'SPOTIFY PREMIUM', -19.90, 'ITAU', 'Assinaturas', '202511', None, None, 1),
            ('of-004', '2025-11-18', 'PIX RECEBIDO SALARIO', 5000.00, 'ITAU', 'Salário', '202511', None, None, 1),
        ]
        
        cursor.executemany("""
            INSERT INTO transacoes_openfinance 
            (id, data_transacao, descricao, valor, fonte, categoria, mes_ref, parcela_numero, parcela_total, validated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, test_data)
        
        self.conn.commit()
        logger.info(f"✅ {len(test_data)} registros inseridos em transacoes_openfinance")
        
        return len(test_data)
    
    def simulate_excel_data(self) -> List[Dict]:
        """Simula dados vindos do Excel (alguns duplicados, alguns novos)"""
        return [
            # Duplicata exata (já existe no OpenFinance)
            {'Data': '2025-11-15', 'Descricao': 'PIX ENVIADO MERCADO', 'Valor': -50.00, 
             'Fonte': 'ITAU', 'Categoria': 'Alimentação', 'MesComp': '202511'},
            
            # Duplicata com data no final (dd/mm)
            {'Data': '2025-11-16', 'Descricao': 'COMPRA AMAZON 1/3 16/11', 'Valor': -299.90, 
             'Fonte': 'LATAM', 'Categoria': 'Compras Online', 'MesComp': '202511'},
            
            # Duplicata com parcela diferente (mesma compra, outra parcela)
            {'Data': '2025-12-16', 'Descricao': 'COMPRA AMAZON 2/3', 'Valor': -299.90, 
             'Fonte': 'LATAM', 'Categoria': 'Compras Online', 'MesComp': '202512'},
            
            # Nova transação (não existe no OpenFinance)
            {'Data': '2025-12-20', 'Descricao': 'PADARIA DO ZE', 'Valor': -25.50, 
             'Fonte': 'ITAU', 'Categoria': 'Alimentação', 'MesComp': '202512'},
            
            # Nova transação (mês posterior ao OpenFinance)
            {'Data': '2026-01-05', 'Descricao': 'NETFLIX ASSINATURA', 'Valor': -49.90, 
             'Fonte': 'ITAU', 'Categoria': 'Assinaturas', 'MesComp': '202601'},
        ]
    
    def check_duplicate(self, data: str, descricao: str, valor: float, fonte: str) -> bool:
        """
        Verifica se transação já existe no banco.
        
        Args:
            data: Data da transação
            descricao: Descrição da transação
            valor: Valor da transação
            fonte: Fonte da transação
            
        Returns:
            True se já existe (duplicata), False se é nova
        """
        cursor = self.conn.cursor()
        
        # Normaliza descrição para comparação
        desc_norm = self.helper.normalize_description_for_dedup(descricao)
        
        # Normaliza data para ISO
        data_iso = data if '-' in data else self._convert_date_to_iso(data)
        
        # Normaliza valor (2 casas decimais)
        valor_norm = float(valor)
        
        # Busca transações com mesma data, valor e fonte
        cursor.execute("""
            SELECT Descricao FROM lancamentos 
            WHERE Data = ? 
            AND ABS(Valor - ?) < 0.01
            AND UPPER(Fonte) = UPPER(?)
        """, (data_iso, valor_norm, fonte))
        
        existing_descs = cursor.fetchall()
        
        # Compara descrições normalizadas
        for (existing_desc,) in existing_descs:
            existing_norm = self.helper.normalize_description_for_dedup(existing_desc)
            if existing_norm == desc_norm:
                logger.debug(f"🔍 Duplicata detectada: '{descricao}' vs '{existing_desc}'")
                return True  # Duplicata encontrada
        
        return False  # Não é duplicata
    
    def _convert_date_to_iso(self, date_str: str) -> str:
        """Converte data dd/mm/yyyy para YYYY-MM-DD"""
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) == 3:
                return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
        return date_str
    
    def insert_transaction_safe(self, transaction: Dict, source: str = 'excel') -> bool:
        """
        Insere transação com verificação de duplicata.
        
        Args:
            transaction: Dicionário com dados da transação
            source: Origem dos dados ('openfinance' ou 'excel')
            
        Returns:
            True se inseriu, False se era duplicata
        """
        self.stats['total_processed'] += 1
        
        # Verifica duplicata
        if self.check_duplicate(
            transaction['Data'],
            transaction['Descricao'],
            transaction['Valor'],
            transaction['Fonte']
        ):
            self.stats['duplicates_skipped'] += 1
            logger.debug(f"⏭️  Duplicata ignorada: {transaction['Descricao']} - R$ {transaction['Valor']}")
            return False
        
        # Insere transação
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO lancamentos 
            (Data, Descricao, Valor, Fonte, Categoria, MesComp, id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            transaction['Data'],
            transaction['Descricao'],
            transaction['Valor'],
            transaction['Fonte'],
            transaction['Categoria'],
            transaction['MesComp'],
            f"{source}-{self.stats['inserted']+1}",
            datetime.now().isoformat()
        ))
        
        self.conn.commit()
        self.stats['inserted'] += 1
        
        if source == 'openfinance':
            self.stats['from_openfinance'] += 1
        else:
            self.stats['from_excel'] += 1
        
        logger.debug(f"✅ Inserida: {transaction['Descricao']} - R$ {transaction['Valor']}")
        return True
    
    def load_from_openfinance(self) -> int:
        """
        Carrega dados validados do transacoes_openfinance para lancamentos.
        
        Returns:
            Número de registros carregados
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT data_transacao, descricao, valor, fonte, categoria, mes_ref
            FROM transacoes_openfinance
            WHERE validated = 1
            ORDER BY data_transacao
        """)
        
        rows = cursor.fetchall()
        loaded = 0
        
        logger.info(f"📥 Carregando {len(rows)} registros do OpenFinance...")
        
        for row in rows:
            transaction = {
                'Data': row[0],
                'Descricao': row[1],
                'Valor': row[2],
                'Fonte': row[3],
                'Categoria': row[4] or 'A definir',
                'MesComp': row[5] or ''
            }
            
            if self.insert_transaction_safe(transaction, source='openfinance'):
                loaded += 1
        
        logger.info(f"✅ {loaded} registros do OpenFinance inseridos")
        return loaded
    
    def load_from_excel(self, excel_data: List[Dict]) -> int:
        """
        Carrega dados do Excel com verificação de duplicatas.
        
        Args:
            excel_data: Lista de dicionários com dados do Excel
            
        Returns:
            Número de registros inseridos (sem duplicatas)
        """
        logger.info(f"📥 Processando {len(excel_data)} registros do Excel...")
        
        loaded = 0
        for transaction in excel_data:
            if self.insert_transaction_safe(transaction, source='excel'):
                loaded += 1
        
        logger.info(f"✅ {loaded} registros novos do Excel inseridos")
        return loaded
    
    def print_statistics(self):
        """Imprime estatísticas do processamento"""
        logger.info("\n" + "="*60)
        logger.info("📊 ESTATÍSTICAS DE DEDUPLICAÇÃO")
        logger.info("="*60)
        logger.info(f"Total processado:        {self.stats['total_processed']}")
        logger.info(f"✅ Inseridas:            {self.stats['inserted']}")
        logger.info(f"⏭️  Duplicatas ignoradas: {self.stats['duplicates_skipped']}")
        logger.info(f"🏦 Do OpenFinance:       {self.stats['from_openfinance']}")
        logger.info(f"📊 Do Excel:             {self.stats['from_excel']}")
        logger.info("="*60)
        
        # Taxa de deduplicação
        if self.stats['total_processed'] > 0:
            dedup_rate = (self.stats['duplicates_skipped'] / self.stats['total_processed']) * 100
            logger.info(f"Taxa de deduplicação: {dedup_rate:.1f}%")
    
    def show_final_data(self):
        """Mostra dados finais na tabela lancamentos"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT Data, Descricao, Valor, Fonte, Categoria
            FROM lancamentos
            ORDER BY Data
        """)
        
        rows = cursor.fetchall()
        
        logger.info("\n" + "="*60)
        logger.info("📋 DADOS FINAIS NA TABELA LANCAMENTOS")
        logger.info("="*60)
        
        for i, row in enumerate(rows, 1):
            data, desc, valor, fonte, cat = row
            logger.info(f"{i}. {data} | {desc[:40]:40s} | R$ {valor:8.2f} | {fonte:10s} | {cat}")
        
        logger.info(f"\nTotal de registros: {len(rows)}")
    
    def test_deduplication_scenarios(self):
        """Testa cenários específicos de deduplicação"""
        logger.info("\n" + "="*60)
        logger.info("🧪 TESTANDO CENÁRIOS DE DEDUPLICAÇÃO")
        logger.info("="*60)
        
        # Teste 1: Descrição com data no final
        desc1 = "PIX ENVIADO MERCADO 15/11"
        desc2 = "PIX ENVIADO MERCADO"
        norm1 = self.helper.normalize_description_for_dedup(desc1)
        norm2 = self.helper.normalize_description_for_dedup(desc2)
        
        logger.info(f"\n1️⃣  Teste: Descrição com data")
        logger.info(f"   Original: '{desc1}'")
        logger.info(f"   Normalizada: '{norm1}'")
        logger.info(f"   Comparação: '{desc2}'")
        logger.info(f"   Normalizada: '{norm2}'")
        logger.info(f"   ✅ Iguais: {norm1 == norm2}")
        
        # Teste 2: Descrição com parcelas
        desc3 = "COMPRA AMAZON 1/3"
        desc4 = "COMPRA AMAZON 2/3"
        norm3 = self.helper.normalize_description_for_dedup(desc3)
        norm4 = self.helper.normalize_description_for_dedup(desc4)
        
        logger.info(f"\n2️⃣  Teste: Descrição com parcelas")
        logger.info(f"   Original: '{desc3}'")
        logger.info(f"   Normalizada: '{norm3}'")
        logger.info(f"   Comparação: '{desc4}'")
        logger.info(f"   Normalizada: '{norm4}'")
        logger.info(f"   ✅ Iguais: {norm3 == norm4}")
        
        # Teste 3: Chave composta
        key1 = self.helper.generate_dedup_key('2025-11-15', 'PIX ENVIADO MERCADO 15/11', -50.00, 'ITAU')
        key2 = self.helper.generate_dedup_key('2025-11-15', 'PIX ENVIADO MERCADO', -50.00, 'ITAU')
        
        logger.info(f"\n3️⃣  Teste: Chave composta")
        logger.info(f"   Chave 1: '{key1}'")
        logger.info(f"   Chave 2: '{key2}'")
        logger.info(f"   ✅ Iguais: {key1 == key2}")
    
    def close(self):
        """Fecha conexão com banco"""
        if self.conn:
            self.conn.close()
            logger.info("✅ Conexão fechada")


def main():
    """Função principal de teste"""
    logger.info("="*60)
    logger.info("🧪 TESTE DE DEDUPLICAÇÃO DE TRANSAÇÕES")
    logger.info("="*60)
    logger.info("Ambiente: SQLite in-memory (não afeta bases reais)")
    logger.info("="*60)
    
    # Inicializa testador
    dedup = TransactionDeduplicator(use_memory=True)
    
    try:
        # 1. Conecta e cria tabelas
        dedup.connect()
        
        # 2. Insere dados de teste do OpenFinance
        logger.info("\n📝 ETAPA 1: Populando transacoes_openfinance")
        dedup.insert_test_openfinance_data()
        
        # 3. Testa cenários de normalização
        dedup.test_deduplication_scenarios()
        
        # 4. Carrega do OpenFinance primeiro (prioridade)
        logger.info("\n📝 ETAPA 2: Carregando do OpenFinance")
        dedup.load_from_openfinance()
        
        # 5. Simula dados do Excel
        excel_data = dedup.simulate_excel_data()
        
        # 6. Carrega do Excel com deduplicação
        logger.info("\n📝 ETAPA 3: Carregando do Excel (com deduplicação)")
        dedup.load_from_excel(excel_data)
        
        # 7. Mostra estatísticas
        dedup.print_statistics()
        
        # 8. Mostra dados finais
        dedup.show_final_data()
        
        logger.info("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"❌ Erro durante teste: {e}")
        raise
    finally:
        dedup.close()


if __name__ == "__main__":
    main()
