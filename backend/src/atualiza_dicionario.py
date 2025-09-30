
import os
import pandas as pd
import sqlite3
import configparser

# Configuração do projeto
def carregar_configuracao():
    config = configparser.ConfigParser()
    config_file = 'config.ini'
    
    if not os.path.exists(config_file):
        config_file = 'config.example.ini'
        print("⚠️  config.ini não encontrado. Usando config.example.ini")
    
    config.read(config_file)
    return config

config = carregar_configuracao()

# Obtém diretório dos arquivos da configuração
diretorio_base = config.get('PATHS', 'diretorio_arquivos', fallback='dados')
if not os.path.isabs(diretorio_base):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    diretorio_arquivos = os.path.join(project_root, diretorio_base)
else:
    diretorio_arquivos = diretorio_base

arquivo_excel_nome = config.get('EXCEL', 'arquivo_saida', fallback='consolidado_temp.xlsx')
arquivo_consolidado = os.path.join(diretorio_arquivos, "planilhas", arquivo_excel_nome)
arquivo_db = os.path.join(diretorio_arquivos, "db", "financeiro.db")

# Conecta ao banco
conn = sqlite3.connect(arquivo_db)
cursor = conn.cursor()

# Cria a tabela de categorias se não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS categorias_aprendidas (
    descricao TEXT PRIMARY KEY,
    categoria TEXT NOT NULL
)
""")
conn.commit()

# Lê dicionário atual do banco
df_existente = pd.read_sql_query("SELECT * FROM categorias_aprendidas", conn)
mapa_db = dict(zip(df_existente["descricao"].str.upper().str.strip(), df_existente["categoria"].str.strip()))

# Lê o consolidado
df_consolidado = pd.read_excel(arquivo_consolidado)
df_consolidado = df_consolidado.dropna(subset=["Descricao", "Categoria"])

# Função para limpar datas das descrições
def limpar_data_descricao(desc):
    """Remove padrões de data (dd/mm) do final das descrições"""
    import re
    desc = desc.strip()
    # Remove padrões como " 01/02", " 03/12", etc. do final
    desc = re.sub(r'\s*\d{2}/\d{2}$', '', desc)
    return desc.strip()

# Constrói dicionário novo
df_consolidado["Descricao"] = df_consolidado["Descricao"].str.upper().str.strip()
df_consolidado["Categoria"] = df_consolidado["Categoria"].str.strip()

# Limpa datas das descrições antes de adicionar
df_consolidado["Descricao"] = df_consolidado["Descricao"].apply(limpar_data_descricao)

novos = []
for _, row in df_consolidado.iterrows():
    desc = row["Descricao"]
    cat = row["Categoria"]
    if desc not in mapa_db and cat != "A definir":
        novos.append((desc, cat))

# Insere no banco
if novos:
    cursor.executemany("INSERT OR IGNORE INTO categorias_aprendidas (descricao, categoria) VALUES (?, ?)", novos)
    conn.commit()
    print(f"✅ {len(novos)} novas categorias adicionadas ao dicionário.")
else:
    print("✅ Nenhuma nova categoria para adicionar.")

conn.close()
