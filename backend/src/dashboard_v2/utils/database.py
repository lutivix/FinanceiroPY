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
    # Forçar nova conexão a cada chamada (sem cache)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, isolation_level=None)
    conn.execute("PRAGMA read_uncommitted = true")
    
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
        
        # Converter valor para float (caso venha como string)
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
        
        # Remover linhas onde valor não pôde ser convertido
        df = df.dropna(subset=['valor'])
        
        df['valor_normalizado'] = df['valor'].abs()
        
        # Renomear rowid para id
        df = df.rename(columns={'rowid': 'id'})
    
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

def obter_orcamento_mais_recente():
    """
    Retorna o orçamento semanal mais recente do banco.
    
    Returns:
        Dict com data de geração e dados do orçamento
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Busca data mais recente
        query_date = "SELECT MAX(generated_at) FROM weekly_budgets"
        latest_date = pd.read_sql_query(query_date, conn).iloc[0, 0]
        
        if not latest_date:
            conn.close()
            return None
        
        # Busca dados do orçamento
        query_budgets = f"""
        SELECT 
            week_number,
            category,
            source,
            person,
            expected_amount,
            is_recurring,
            recurring_items
        FROM weekly_budgets
        WHERE generated_at = '{latest_date}'
        ORDER BY week_number, category
        """
        
        df = pd.read_sql_query(query_budgets, conn)
        conn.close()
        
        return {
            'generated_at': latest_date,
            'budgets': df.to_dict('records')
        }
    
    except Exception as e:
        print(f"❌ Erro ao buscar orçamento: {e}")
        return None


def obter_resumo_orcamento_semanal():
    """
    Retorna resumo consolidado do orçamento por semana.
    
    Returns:
        Dict com totais por semana, pessoa e categoria
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Busca data mais recente
        query_date = "SELECT MAX(generated_at) FROM weekly_budgets"
        latest_date = pd.read_sql_query(query_date, conn).iloc[0, 0]
        
        if not latest_date:
            conn.close()
            return {}
        
        # Resumo por semana
        query = f"""
        SELECT 
            week_number,
            person,
            category,
            SUM(expected_amount) as total
        FROM weekly_budgets
        WHERE generated_at = '{latest_date}'
        GROUP BY week_number, person, category
        ORDER BY week_number
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Organiza por semana
        summary = {}
        for week in df['week_number'].unique():
            week_data = df[df['week_number'] == week]
            summary[int(week)] = {
                'total': week_data['total'].sum(),
                'by_person': week_data.groupby('person')['total'].sum().to_dict(),
                'by_category': week_data.groupby('category')['total'].sum().to_dict()
            }
        
        return {
            'generated_at': latest_date,
            'summary': summary
        }
    
    except Exception as e:
        print(f"❌ Erro ao gerar resumo de orçamento: {e}")
        return {}


def obter_meses_orcamento_disponiveis():
    """
    Retorna lista de meses com orçamento disponível.
    
    Returns:
        List de dicts com label e value para dropdown
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        
        query = """
        SELECT DISTINCT generated_at
        FROM weekly_budgets
        ORDER BY generated_at DESC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return [{'label': 'Nenhum orçamento disponível', 'value': 'none'}]
        
        meses = []
        for date_str in df['generated_at']:
            # Converte YYYY-MM-DD para formato legível
            try:
                date_obj = pd.to_datetime(date_str)
                # Formato: 13 de Janeiro de 2026
                label = date_obj.strftime('%d de %B de %Y')
                # Traduz mês para português
                meses_pt = {
                    'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março',
                    'April': 'Abril', 'May': 'Maio', 'June': 'Junho',
                    'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro',
                    'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
                }
                for eng, pt in meses_pt.items():
                    label = label.replace(eng, pt)
                value = date_str
                meses.append({'label': label, 'value': value})
            except:
                continue
        
        return meses if meses else [{'label': 'Atual', 'value': 'current'}]
    
    except Exception as e:
        print(f"❌ Erro ao buscar meses de orçamento: {e}")
        return [{'label': 'Atual', 'value': 'current'}]


def obter_resumo_orcamento_por_data(data_geracao: str):
    """
    Retorna resumo de orçamento para uma data específica.
    
    Args:
        data_geracao: Data no formato YYYY-MM-DD
        
    Returns:
        Dict com totais por semana, pessoa e categoria
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Resumo por semana
        query = f"""
        SELECT 
            week_number,
            person,
            category,
            SUM(expected_amount) as total
        FROM weekly_budgets
        WHERE generated_at = '{data_geracao}'
        GROUP BY week_number, person, category
        ORDER BY week_number
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return {}
        
        # Organiza por semana
        summary = {}
        for week in df['week_number'].unique():
            week_data = df[df['week_number'] == week]
            summary[int(week)] = {
                'total': week_data['total'].sum(),
                'by_person': week_data.groupby('person')['total'].sum().to_dict(),
                'by_category': week_data.groupby('category')['total'].sum().to_dict()
            }
        
        return {
            'generated_at': data_geracao,
            'summary': summary
        }
    
    except Exception as e:
        print(f"❌ Erro ao buscar orçamento por data: {e}")
        return {}


def obter_meses_disponiveis_para_comparacao():
    """
    Retorna lista de meses disponíveis para comparação (baseado nas transações reais)
    
    Returns:
        Lista de dicts com 'label' e 'value' (YYYY-MM)
    """
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        
        query = """
        SELECT DISTINCT
            strftime('%Y-%m', Data) as year_month,
            strftime('%m', Data) as month_num,
            strftime('%Y', Data) as year
        FROM lancamentos
        WHERE Categoria NOT IN ('INVESTIMENTOS', 'SALÁRIO', 'Salário', 'Investimentos')
        ORDER BY year_month DESC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Mapeamento de meses
        meses_pt = {
            '01': 'Janeiro', '02': 'Fevereiro', '03': 'Março', '04': 'Abril',
            '05': 'Maio', '06': 'Junho', '07': 'Julho', '08': 'Agosto',
            '09': 'Setembro', '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'
        }
        
        opcoes = []
        for _, row in df.iterrows():
            mes_nome = meses_pt.get(row['month_num'], row['month_num'])
            opcoes.append({
                'label': f"{mes_nome} {row['year']}",
                'value': row['year_month']
            })
        
        return opcoes
    
    except Exception as e:
        print(f"❌ Erro ao buscar meses disponíveis: {e}")
        return []