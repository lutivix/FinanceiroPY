"""
Script Unificado para Atualizar Dicionário de Categorias
Suporta 3 fontes: consolidado, controle_pessoal, db
"""

import os
import sys
import pandas as pd
import sqlite3
import configparser

def carregar_configuracao():
    config = configparser.ConfigParser()
    config_file = 'config.ini'
    
    if not os.path.exists(config_file):
        config_file = 'config.example.ini'
        print("⚠️  config.ini não encontrado. Usando config.example.ini")
    
    config.read(config_file, encoding='utf-8')
    return config

def limpar_data_descricao(desc):
    """Remove padrões de data (dd/mm) do final das descrições"""
    import re
    desc = desc.strip()
    # Remove padrões como " 01/02", " 03/12", etc. do final
    desc = re.sub(r'\s*\d{2}/\d{2}$', '', desc)
    
    # Remove datas específicas do PIX
    if "PIX" in desc and len(desc) >= 5:
        possivel_data = desc[-5:]
        if "/" in possivel_data and possivel_data.replace("/", "").isdigit():
            return desc[:-5].strip()
    
    return desc.strip()

def atualizar_de_consolidado(conn, diretorio_arquivos, config):
    """Atualiza dicionário a partir do Excel consolidado"""
    print("\n📁 MODO: Excel Consolidado")
    print("=" * 60)
    
    arquivo_excel_nome = config.get('EXCEL', 'arquivo_saida', fallback='consolidado_temp.xlsx')
    arquivo_consolidado = os.path.join(diretorio_arquivos, "planilhas", arquivo_excel_nome)
    
    if not os.path.exists(arquivo_consolidado):
        print(f"❌ Arquivo não encontrado: {arquivo_consolidado}")
        return 0
    
    print(f"📄 Lendo: {arquivo_consolidado}")
    df_consolidado = pd.read_excel(arquivo_consolidado)
    df_consolidado = df_consolidado.dropna(subset=["Descricao", "Categoria"])
    
    df_consolidado["Descricao"] = df_consolidado["Descricao"].str.upper().str.strip()
    df_consolidado["Categoria"] = df_consolidado["Categoria"].str.strip()
    df_consolidado["Descricao"] = df_consolidado["Descricao"].apply(limpar_data_descricao)
    
    return df_consolidado[df_consolidado["Categoria"] != "A definir"]

def atualizar_de_controle_pessoal(conn, diretorio_arquivos):
    """Atualiza dicionário a partir do Controle_pessoal.xlsm"""
    print("\n📁 MODO: Excel Controle Pessoal (aba Anual)")
    print("=" * 60)
    
    arquivo_excel = os.path.join(diretorio_arquivos, "planilhas", "Controle_pessoal.xlsm")
    
    if not os.path.exists(arquivo_excel):
        print(f"❌ Arquivo não encontrado: {arquivo_excel}")
        return 0
    
    print(f"📄 Lendo: {arquivo_excel}")
    xls = pd.ExcelFile(arquivo_excel)
    
    if "Anual" not in xls.sheet_names:
        print("❌ A aba 'Anual' não foi encontrada")
        return 0
    
    df_controle = pd.read_excel(xls, sheet_name="Anual")
    
    # Encontra colunas
    descricao_col = next((col for col in df_controle.columns if col.strip().lower() in ["descricao", "descrição"]), None)
    categoria_col = next((col for col in df_controle.columns if col.strip().lower() == "categoria"), None)
    
    if not descricao_col or not categoria_col:
        print("❌ Colunas 'Descrição' e/ou 'Categoria' não encontradas na aba 'Anual'")
        return 0
    
    df_controle = df_controle.dropna(subset=[descricao_col, categoria_col])
    df_controle["Descricao"] = df_controle[descricao_col].astype(str).str.upper().str.strip()
    df_controle["Categoria"] = df_controle[categoria_col].astype(str).str.strip()
    df_controle["Descricao"] = df_controle["Descricao"].apply(limpar_data_descricao)
    
    return df_controle[df_controle["Categoria"] != "A definir"]

def atualizar_de_db(conn):
    """Atualiza dicionário a partir da tabela lancamentos"""
    print("\n📁 MODO: Banco de Dados (tabela lancamentos)")
    print("=" * 60)
    
    query = """
    SELECT DISTINCT Descricao, Categoria 
    FROM lancamentos 
    WHERE Categoria IS NOT NULL 
      AND Categoria != ''
      AND Categoria != 'A definir'
      AND Categoria NOT IN ('INVESTIMENTOS', 'SALÁRIO', 'Salário', 'Investimentos')
    ORDER BY Descricao
    """
    
    print("📊 Lendo transações categorizadas do banco...")
    df_lancamentos = pd.read_sql_query(query, conn)
    print(f"✅ {len(df_lancamentos)} transações categorizadas encontradas")
    
    df_lancamentos["Descricao"] = df_lancamentos["Descricao"].str.upper().str.strip()
    df_lancamentos["Categoria"] = df_lancamentos["Categoria"].str.strip()
    df_lancamentos["Descricao"] = df_lancamentos["Descricao"].apply(limpar_data_descricao)
    
    return df_lancamentos

def main():
    print("🔄 Atualizador de Dicionário de Categorias")
    print("=" * 60)
    
    # Verifica argumento
    if len(sys.argv) < 2:
        print("❌ Modo de uso: python atualiza_dicionario_unificado.py <fonte>")
        print("\nFontes disponíveis:")
        print("  consolidado       - Lê do Excel consolidado_temp.xlsx")
        print("  controle_pessoal  - Lê da aba 'Anual' do Controle_pessoal.xlsm")
        print("  db                - Lê da tabela lancamentos do banco")
        sys.exit(1)
    
    fonte = sys.argv[1].lower()
    
    if fonte not in ['consolidado', 'controle_pessoal', 'db']:
        print(f"❌ Fonte inválida: {fonte}")
        print("Fontes válidas: consolidado, controle_pessoal, db")
        sys.exit(1)
    
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
    
    # Cria tabela se não existir
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categorias_aprendidas (
        descricao TEXT PRIMARY KEY,
        categoria TEXT NOT NULL
    )
    """)
    conn.commit()
    
    # Lê dicionário atual
    df_existente = pd.read_sql_query("SELECT * FROM categorias_aprendidas", conn)
    mapa_db = dict(zip(df_existente["descricao"].str.upper().str.strip(), 
                       df_existente["categoria"].str.strip()))
    
    print(f"📚 Dicionário atual: {len(mapa_db)} entradas")
    
    # Carrega dados conforme fonte
    if fonte == 'consolidado':
        df_dados = atualizar_de_consolidado(conn, diretorio_arquivos, config)
    elif fonte == 'controle_pessoal':
        df_dados = atualizar_de_controle_pessoal(conn, diretorio_arquivos)
    elif fonte == 'db':
        df_dados = atualizar_de_db(conn)
    
    if df_dados is None or len(df_dados) == 0:
        print("⚠️ Nenhum dado encontrado na fonte")
        conn.close()
        return
    
    # Processa novas entradas
    novos = []
    for _, row in df_dados.iterrows():
        desc = row["Descricao"]
        cat = row["Categoria"]
        if desc not in mapa_db:
            novos.append((desc, cat))
    
    # Insere no banco
    if novos:
        cursor.executemany("INSERT OR IGNORE INTO categorias_aprendidas (descricao, categoria) VALUES (?, ?)", novos)
        conn.commit()
        print(f"\n✅ {len(novos)} novas categorias adicionadas ao dicionário!")
        
        # Mostra algumas amostras
        if len(novos) <= 10:
            print("\n📝 Categorias adicionadas:")
            for desc, cat in novos:
                print(f"  • {desc[:50]:50} → {cat}")
        else:
            print(f"\n📝 Primeiras 10 categorias adicionadas:")
            for desc, cat in novos[:10]:
                print(f"  • {desc[:50]:50} → {cat}")
            print(f"  ... e mais {len(novos) - 10} categorias")
    else:
        print("\n✅ Nenhuma nova categoria para adicionar (dicionário já está atualizado)")
    
    conn.close()
    print("\n🎉 Processo concluído!")

if __name__ == "__main__":
    main()
