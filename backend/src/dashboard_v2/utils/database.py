"""
Utilitários de banco de dados
Funções para carregar e processar dados do SQLite
"""

import sqlite3
from pathlib import Path
import pandas as pd

# Caminho do banco
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
DB_PATH = BASE_DIR / 'dados' / 'db' / 'financeiro.db'

def carregar_transacoes(mes_filtro='TODOS'):
    """
    Carrega transações do banco (exceto INVESTIMENTOS, SALÁRIO, pagamentos de fatura)
    
    Args:
        mes_filtro: Mês para filtrar (ex: 'Dezembro 2025') ou 'TODOS'
    
    Returns:
        DataFrame com as transações
    """
    conn = sqlite3.connect(DB_PATH)
    
    # Query base
    query = """
    SELECT 
        rowid,
        Data as data,
        Descricao as descricao,
        Valor as valor,
        Categoria as categoria,
        Fonte as fonte,
        MesComp as mes_comp
    FROM lancamentos
    WHERE Categoria NOT IN ('INVESTIMENTOS', 'SALÁRIO', 'Salário', 'Investimentos')
      AND (
        Descricao NOT LIKE '%ITAU VISA%'
        AND Descricao NOT LIKE '%ITAU BLACK%'
        AND Descricao NOT LIKE '%ITAU MASTER%'
        AND Descricao NOT LIKE '%PGTO FATURA%'
        AND Descricao NOT LIKE '%PAGAMENTO CARTAO%'
        AND Descricao NOT LIKE '%PAGAMENTO EFETUADO%'
      )
    """
    
    # Adiciona filtro de mês se especificado
    if mes_filtro != 'TODOS':
        query += f" AND MesComp = '{mes_filtro}'"
    
    query += " ORDER BY data DESC"
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Processar dados
    if len(df) > 0:
        df['data'] = pd.to_datetime(df['data'], errors='coerce')
        df['valor_normalizado'] = df['valor'].abs()
        
        # Remove duplicatas
        df = df.drop_duplicates(subset=['data', 'descricao', 'valor', 'fonte'], keep='first')
        df = df.drop_duplicates(subset=['rowid'], keep='first')
    
    return df

def obter_meses_disponiveis():
    """
    Retorna lista de meses disponíveis no banco
    
    Returns:
        Lista de strings com os meses (ex: ['Dezembro 2025', 'Novembro 2025'])
    """
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT DISTINCT MesComp 
    FROM lancamentos 
    WHERE Categoria NOT IN ('INVESTIMENTOS', 'SALÁRIO', 'Salário', 'Investimentos')
    ORDER BY MesComp DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df['MesComp'].tolist()

def obter_categorias():
    """
    Retorna lista de categorias únicas (exceto as especiais)
    
    Returns:
        Lista de strings com categorias
    """
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT DISTINCT Categoria 
    FROM lancamentos 
    WHERE Categoria NOT IN ('INVESTIMENTOS', 'SALÁRIO', 'A definir', 'Salário', 'Investimentos')
    ORDER BY Categoria
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df['Categoria'].tolist()

def obter_fontes():
    """
    Retorna lista de fontes únicas
    
    Returns:
        Lista de strings com fontes
    """
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT DISTINCT Fonte 
    FROM lancamentos 
    WHERE Categoria NOT IN ('INVESTIMENTOS', 'SALÁRIO', 'Salário', 'Investimentos')
    ORDER BY Fonte
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df['Fonte'].tolist()

def calcular_estatisticas(df):
    """
    Calcula estatísticas básicas do DataFrame
    
    Args:
        df: DataFrame com as transações
    
    Returns:
        Dict com estatísticas
    """
    if len(df) == 0:
        return {
            'total': 0,
            'media_mensal': 0,
            'total_categorizado': 0,
            'total_pendente': 0,
            'perc_categorizado': 0,
            'num_transacoes': 0,
            'num_meses': 0
        }
    
    # Filtrar apenas débitos (valor POSITIVO = gastos)
    df_debitos = df[df['valor'] > 0].copy()
    
    total = df_debitos['valor_normalizado'].sum()
    num_meses = df_debitos['mes_comp'].nunique()
    media_mensal = total / num_meses if num_meses > 0 else 0
    
    total_categorizado = len(df_debitos[df_debitos['categoria'] != 'A definir'])
    total_pendente = len(df_debitos[df_debitos['categoria'] == 'A definir'])
    perc_categorizado = (total_categorizado / len(df_debitos) * 100) if len(df_debitos) > 0 else 0
    
    return {
        'total': total,
        'media_mensal': media_mensal,
        'total_categorizado': total_categorizado,
        'total_pendente': total_pendente,
        'perc_categorizado': perc_categorizado,
        'num_transacoes': len(df_debitos),
        'num_meses': num_meses
    }

def atualizar_categoria(rowid, nova_categoria):
    """
    Atualiza categoria de uma transação
    
    Args:
        rowid: ID da linha no banco
        nova_categoria: Nova categoria
    
    Returns:
        bool: True se sucesso, False se erro
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE lancamentos SET Categoria = ? WHERE rowid = ?",
            (nova_categoria, rowid)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Erro ao atualizar categoria: {e}")
        return False
