"""
Script para complementar Outubro e Novembro 2025
Busca transações faltantes da tabela transacoes_openfinance
"""

import os
import sqlite3
import pandas as pd
import configparser
from datetime import datetime

def carregar_configuracao():
    config = configparser.ConfigParser()
    config_file = 'config.ini'
    
    if not os.path.exists(config_file):
        config_file = 'config.example.ini'
        print("⚠️  config.ini não encontrado. Usando config.example.ini")
    
    config.read(config_file, encoding='utf-8')
    return config

def main():
    print("🔄 Importando Transações do Open Finance para lancamentos")
    print("=" * 60)
    print("ℹ️  Importa apenas DÉBITOS, excluindo pagamentos de fatura")
    
    # Configuração
    config = carregar_configuracao()
    
    diretorio_base = config.get('PATHS', 'diretorio_arquivos', fallback='dados')
    if not os.path.isabs(diretorio_base):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        diretorio_arquivos = os.path.join(project_root, diretorio_base)
    else:
        diretorio_arquivos = diretorio_base
    
    arquivo_db = os.path.join(diretorio_arquivos, "db", "financeiro.db")
    
    # Conecta ao banco
    conn = sqlite3.connect(arquivo_db)
    cursor = conn.cursor()
    
    # Verifica tabela transacoes_openfinance
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transacoes_openfinance'")
    if not cursor.fetchone():
        print("❌ Tabela transacoes_openfinance não encontrada!")
        conn.close()
        return
    # Estatísticas atuais
    cursor.execute("SELECT COUNT(*) FROM lancamentos")
    total_atual = cursor.fetchone()[0]
    print(f"\n📊 Situação atual em lancamentos: {total_atual:,} registros")
    
    cursor.execute("""
        SELECT MesComp, COUNT(*) as qty 
        FROM lancamentos 
        GROUP BY MesComp 
        ORDER BY MesComp
    """)
    print("\nDistribuição por mês:")
    for row in cursor.fetchall():
        print(f"   {row[0]:20} {row[1]:>6,} registros")
        print(f"   {row[0]:20} {row[1]:>6,} registros")
    
    # Busca transações do Open Finance (só débitos)
    print("\n🔍 Buscando transações no Open Finance...")
    query_openfinance = """
    SELECT 
        data,
        descricao,
        valor,
        categoria,
        fonte,
        mes_comp
    FROM transacoes_openfinance
    WHERE tipo_transacao = 'DEBIT'
      AND descricao NOT IN (
        'Pagamento recebido',
        'Rendimentos',
        'ITAU VISA     4703-7093',
        'ITAU BLACK  3102-1222',
        'Dinheiro recebido Desconto por pagamento antecipado histórico'
      )
      AND descricao NOT LIKE '%ITAU VISA%'
      AND descricao NOT LIKE '%ITAU BLACK%'
      AND descricao NOT LIKE '%ITAU MASTER%'
      AND descricao NOT LIKE '%PGTO FATURA%'
      AND descricao NOT LIKE '%PAGAMENTO CARTAO%'
      AND descricao NOT LIKE '%PAGAMENTO EFETUADO%'
    ORDER BY data
    """
    
    df_openfinance = pd.read_sql_query(query_openfinance, conn)
    print(f"✅ {len(df_openfinance):,} transações encontradas no Open Finance")
    
    if len(df_openfinance) == 0:
        print("⚠️  Nenhuma transação para adicionar")
        conn.close()
        return
    
    # Remove duplicatas no próprio Open Finance
    # Prepara todas as transações para inserção
    print("\n🔄 Preparando transações para inserção...")
    novas_transacoes = []
    
    for _, row in df_openfinance.iterrows():
        novas_transacoes.append({
            'Data': row['data'],
            'Descricao': row['descricao'],
            'Valor': row['valor'],
            'Categoria': row['categoria'] if pd.notna(row['categoria']) and row['categoria'] != '' else 'A definir',
            'Fonte': row['fonte'],
            'MesComp': row['mes_comp'],
            'id': '',
            'raw_data': 'openfinance',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        })
    
    if not novas_transacoes:
        print("✅ Todas as transações do Open Finance já existem em lancamentos!")
        print("ℹ️  Nada a adicionar")
        conn.close()
        return
    
    if not novas_transacoes:
        print("⚠️  Nenhuma transação para adicionar")
        conn.close()
        return
    
    print(f"✅ {len(novas_transacoes):,} transações a adicionar")
    
    # Estatísticas por mês
    df_stats = pd.DataFrame(novas_transacoes)
    print("\nDistribuição por mês das novas transações:")
    for mes, count in df_stats.groupby('MesComp').size().items():
        print(f"   {mes:20} {count:>6,} registros")
    if len(novas_transacoes) > 5:
        print(f"   ... e mais {len(novas_transacoes) - 5} transações")
    
    # Confirma inserção
    print()
    resposta = input("Deseja adicionar essas transações? (S/N): ")
    if resposta.upper() != 'S':
        print("❌ Operação cancelada pelo usuário")
        conn.close()
        return
    
    # Insere
    print("\n⏳ Inserindo transações...")
    df_insert = pd.DataFrame(novas_transacoes)
    df_insert.to_sql('lancamentos', conn, if_exists='append', index=False)
    
    conn.commit()
    print(f"✅ {len(novas_transacoes):,} transações adicionadas com sucesso!")
    
    # Estatísticas finais
    # Estatísticas finais
    cursor.execute("SELECT COUNT(*) FROM lancamentos")
    total_final = cursor.fetchone()[0]
    
    print(f"\n📊 Total de registros adicionados: {len(novas_transacoes):,}")
    print(f"📊 Total geral em lancamentos: {total_final:,} registros (era {total_atual:,})")
    
    print("\n📅 Distribuição final por mês:")
    cursor.execute("""
        SELECT MesComp, COUNT(*) as qty 
        FROM lancamentos 
        GROUP BY MesComp 
        ORDER BY MesComp
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]:20} {row[1]:>6,} registros")
    conn.close()
    print("\n" + "=" * 60)
    print("🎉 Processo concluído com sucesso!")
    print("=" * 60)

if __name__ == "__main__":
    main()
