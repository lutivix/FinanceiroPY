"""
Script para atualizar um mês específico na tabela lancamentos
A partir do Excel consolidado
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
    print("🔄 Atualização Mensal de lancamentos via Consolidado")
    print("=" * 60)
    
    # Verifica argumento
    if len(sys.argv) < 2:
        print("❌ Modo de uso: python agente_financeiro_mensal.py <mes>")
        print("\nExemplo:")
        print("  python agente_financeiro_mensal.py \"Dezembro 2025\"")
        print("  python agente_financeiro_mensal.py \"Janeiro 2025\"")
        sys.exit(1)
    
    mes_filtro = sys.argv[1]
    print(f"📅 Mês selecionado: {mes_filtro}")
    
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
    
    # Verifica quantos registros existem no mês
    cursor.execute("SELECT COUNT(*) FROM lancamentos WHERE MesComp = ?", (mes_filtro,))
    total_antes = cursor.fetchone()[0]
    print(f"\n📊 Registros atuais em '{mes_filtro}': {total_antes:,}")
    
    # Lê consolidado
    print(f"\n📄 Lendo arquivo consolidado: {arquivo_excel_nome}")
    df = pd.read_excel(arquivo_consolidado)
    print(f"✅ {len(df):,} registros no Excel")
    
    # Filtra apenas o mês desejado
    if 'MesComp' not in df.columns:
        print("❌ Coluna 'MesComp' não encontrada no Excel!")
        conn.close()
        return
    
    df_mes = df[df['MesComp'] == mes_filtro].copy()
    
    if len(df_mes) == 0:
        print(f"⚠️  Nenhum registro encontrado para '{mes_filtro}' no consolidado")
        conn.close()
        return
    
    print(f"✅ {len(df_mes):,} registros encontrados para '{mes_filtro}'")
    
    # Valida colunas necessárias
    colunas_necessarias = ['Data', 'Descricao', 'Fonte', 'Valor', 'Categoria', 'MesComp']
    colunas_faltantes = [col for col in colunas_necessarias if col not in df_mes.columns]
    
    if colunas_faltantes:
        print(f"❌ Colunas faltantes no Excel: {colunas_faltantes}")
        conn.close()
        return
    
    # Prepara dados
    print("\n⏳ Preparando dados para atualização...")
    df_mes['created_at'] = datetime.now().isoformat()
    df_mes['updated_at'] = datetime.now().isoformat()
    
    if 'id' not in df_mes.columns:
        df_mes['id'] = ''
    
    if 'raw_data' not in df_mes.columns:
        df_mes['raw_data'] = ''
    
    # Mostra amostra
    print("\n📝 Primeiras 5 transações a serem atualizadas:")
    for i, row in df_mes.head(5).iterrows():
        print(f"   {row['Data']} | {row['Descricao'][:40]:40} | R$ {abs(row['Valor']):>10.2f} | {row['Categoria']}")
    
    if len(df_mes) > 5:
        print(f"   ... e mais {len(df_mes) - 5} transações")
    
    # Confirma
    print()
    print(f"⚠️  ATENÇÃO: Isso irá:")
    print(f"   1. DELETAR todos os {total_antes:,} registros atuais de '{mes_filtro}'")
    print(f"   2. INSERIR {len(df_mes):,} registros do consolidado")
    print()
    
    resposta = input("Deseja continuar? (S/N): ")
    if resposta.upper() != 'S':
        print("❌ Operação cancelada pelo usuário")
        conn.close()
        return
    
    # Delete registros antigos do mês
    print(f"\n🗑️  Deletando registros antigos de '{mes_filtro}'...")
    cursor.execute("DELETE FROM lancamentos WHERE MesComp = ?", (mes_filtro,))
    conn.commit()
    print(f"✅ {total_antes:,} registros deletados")
    
    # Insere novos dados
    print(f"\n⏳ Inserindo {len(df_mes):,} novos registros...")
    df_mes.to_sql('lancamentos', conn, if_exists='append', index=False)
    conn.commit()
    
    # Verifica inserção
    cursor.execute("SELECT COUNT(*) FROM lancamentos WHERE MesComp = ?", (mes_filtro,))
    total_depois = cursor.fetchone()[0]
    
    print(f"✅ {total_depois:,} registros inseridos com sucesso!")
    
    # Estatísticas finais
    cursor.execute("SELECT COUNT(*) FROM lancamentos")
    total_geral = cursor.fetchone()[0]
    
    print(f"\n📊 Total geral em lancamentos: {total_geral:,} registros")
    
    print("\n📅 Distribuição por mês:")
    cursor.execute("""
        SELECT MesComp, COUNT(*) as qty 
        FROM lancamentos 
        GROUP BY MesComp 
        ORDER BY MesComp
    """)
    for row in cursor.fetchall():
        destaque = " ⬅️" if row[0] == mes_filtro else ""
        print(f"   {row[0]:20} {row[1]:>6,} registros{destaque}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("🎉 Processo concluído com sucesso!")
    print("=" * 60)

if __name__ == "__main__":
    main()
