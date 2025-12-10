"""
Script para limpar e reconstruir a tabela lancamentos
Faz backup da tabela atual para lancamentos_archive
"""

import os
import sys
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
    print("🔄 Limpeza e Reconstrução da Tabela lancamentos")
    print("=" * 60)
    print()
    print("⚠️  ATENÇÃO: Este script irá:")
    print("   1. Renomear 'lancamentos' para 'lancamentos_archive'")
    print("   2. Criar nova tabela 'lancamentos' vazia")
    print("   3. Importar dados do Excel consolidado")
    print()
    
    resposta = input("Deseja continuar? (S/N): ")
    if resposta.upper() != 'S':
        print("❌ Operação cancelada pelo usuário")
        return
    
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
    arquivo_excel_nome = config.get('EXCEL', 'arquivo_saida', fallback='consolidado_temp.xlsx')
    arquivo_consolidado = os.path.join(diretorio_arquivos, "planilhas", arquivo_excel_nome)
    
    # Verifica se consolidado existe
    if not os.path.exists(arquivo_consolidado):
        print(f"❌ Arquivo consolidado não encontrado: {arquivo_consolidado}")
        print("💡 Execute primeiro o agente_financeiro.py para gerar o consolidado")
        return
    
    # Conecta ao banco
    conn = sqlite3.connect(arquivo_db)
    cursor = conn.cursor()
    
    # 1. Verifica quantos registros existem
    cursor.execute("SELECT COUNT(*) FROM lancamentos")
    total_antigo = cursor.fetchone()[0]
    print(f"\n📊 Registros atuais na tabela lancamentos: {total_antigo:,}")
    
    # 2. Remove tabela archive antiga se existir
    print("\n🗑️  Removendo backup antigo (se existir)...")
    cursor.execute("DROP TABLE IF EXISTS lancamentos_archive")
    
    # 3. Renomeia lancamentos atual para archive
    print("💾 Criando backup: lancamentos → lancamentos_archive")
    cursor.execute("ALTER TABLE lancamentos RENAME TO lancamentos_archive")
    conn.commit()
    print("✅ Backup criado com sucesso!")
    
    # 4. Cria nova tabela lancamentos com a mesma estrutura
    print("\n🔨 Criando nova tabela lancamentos...")
    cursor.execute("""
    CREATE TABLE lancamentos (
        id TEXT,
        Data DATE,
        Descricao TEXT,
        Fonte TEXT,
        Valor REAL,
        Categoria TEXT,
        MesComp TEXT,
        raw_data TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    print("✅ Nova tabela criada!")
    
    # 5. Lê consolidado
    print(f"\n📄 Lendo arquivo consolidado: {arquivo_excel_nome}")
    df = pd.read_excel(arquivo_consolidado)
    print(f"✅ {len(df):,} registros encontrados no Excel")
    
    # 6. Valida colunas necessárias
    colunas_necessarias = ['Data', 'Descricao', 'Fonte', 'Valor', 'Categoria', 'MesComp']
    colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]
    
    if colunas_faltantes:
        print(f"❌ Colunas faltantes no Excel: {colunas_faltantes}")
        print("🔄 Revertendo alterações...")
        cursor.execute("DROP TABLE lancamentos")
        cursor.execute("ALTER TABLE lancamentos_archive RENAME TO lancamentos")
        conn.commit()
        conn.close()
        return
    
    # 7. Prepara dados para inserção
    print("\n⏳ Preparando dados para inserção...")
    df['created_at'] = datetime.now().isoformat()
    df['updated_at'] = datetime.now().isoformat()
    
    # Garante que id existe
    if 'id' not in df.columns:
        df['id'] = ''
    
    # Garante que raw_data existe
    if 'raw_data' not in df.columns:
        df['raw_data'] = ''
    
    # 8. Insere dados
    print("⏳ Inserindo dados na nova tabela...")
    df.to_sql('lancamentos', conn, if_exists='append', index=False)
    
    # 9. Verifica inserção
    cursor.execute("SELECT COUNT(*) FROM lancamentos")
    total_novo = cursor.fetchone()[0]
    
    print(f"\n✅ Inserção concluída!")
    print(f"   📊 Registros antigos (archive): {total_antigo:,}")
    print(f"   📊 Registros novos (lancamentos): {total_novo:,}")
    print(f"   📉 Redução: {total_antigo - total_novo:,} registros ({(total_antigo - total_novo) / total_antigo * 100:.1f}%)")
    
    # 10. Completar Outubro e Novembro com Open Finance
    print("\n🔄 Completando Outubro e Novembro com dados do Open Finance...")
    
    # Verifica se tabela transacoes_openfinance existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transacoes_openfinance'")
    if cursor.fetchone():
        # Lê débitos de Out/Nov do Open Finance
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
          AND mes_comp IN ('Outubro 2025', 'Novembro 2025')
          AND descricao NOT LIKE '%ITAU VISA%'
          AND descricao NOT LIKE '%ITAU BLACK%'
          AND descricao NOT LIKE '%ITAU MASTER%'
          AND descricao NOT LIKE '%PGTO FATURA%'
          AND descricao NOT LIKE '%PAGAMENTO CARTAO%'
          AND descricao NOT LIKE '%PAGAMENTO EFETUADO%'
        """
        
        df_openfinance = pd.read_sql_query(query_openfinance, conn)
        
        if len(df_openfinance) > 0:
            print(f"✅ {len(df_openfinance):,} transações encontradas no Open Finance")
            
            # Prepara dados para inserção
            df_openfinance['Data'] = df_openfinance['data']
            df_openfinance['Descricao'] = df_openfinance['descricao']
            df_openfinance['Valor'] = df_openfinance['valor']
            df_openfinance['Categoria'] = df_openfinance['categoria']
            df_openfinance['Fonte'] = df_openfinance['fonte']
            df_openfinance['MesComp'] = df_openfinance['mes_comp']
            df_openfinance['id'] = ''
            df_openfinance['raw_data'] = 'openfinance'
            df_openfinance['created_at'] = datetime.now().isoformat()
            df_openfinance['updated_at'] = datetime.now().isoformat()
            
            # Remove duplicatas baseado em Data+Descricao+Valor
            df_openfinance = df_openfinance.drop_duplicates(subset=['Data', 'Descricao', 'Valor'], keep='first')
            print(f"✅ {len(df_openfinance):,} transações únicas (após remover duplicatas)")
            
            # Verifica se já existem no lancamentos (evita duplicatas)
            existing_check = []
            for _, row in df_openfinance.iterrows():
                cursor.execute("""
                    SELECT COUNT(*) FROM lancamentos 
                    WHERE Data = ? AND Descricao = ? AND Valor = ?
                """, (row['Data'], row['Descricao'], row['Valor']))
                if cursor.fetchone()[0] == 0:
                    existing_check.append(row)
            
            if existing_check:
                df_insert = pd.DataFrame(existing_check)
                df_insert[['Data', 'Descricao', 'Fonte', 'Valor', 'Categoria', 'MesComp', 
                          'id', 'raw_data', 'created_at', 'updated_at']].to_sql(
                    'lancamentos', conn, if_exists='append', index=False
                )
                print(f"✅ {len(df_insert):,} transações adicionadas (Out/Nov do Open Finance)")
            else:
                print("ℹ️  Nenhuma transação nova a adicionar (já existem no consolidado)")
        else:
            print("⚠️  Nenhuma transação encontrada no Open Finance para Out/Nov")
    else:
        print("⚠️  Tabela transacoes_openfinance não encontrada, pulando...")
    
    # 11. Estatísticas finais por mês
    cursor.execute("SELECT COUNT(*) FROM lancamentos")
    total_final = cursor.fetchone()[0]
    
    print("\n📅 Distribuição final por mês:")
    cursor.execute("""
        SELECT MesComp, COUNT(*) as qty 
        FROM lancamentos 
        GROUP BY MesComp 
        ORDER BY MesComp
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]:20} {row[1]:>6,} registros")
    
    print(f"\n📊 Total final: {total_final:,} registros")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("🎉 Processo concluído com sucesso!")
    print("💡 A tabela antiga está em 'lancamentos_archive' (pode ser removida depois)")
    print("=" * 60)

if __name__ == "__main__":
    main()
