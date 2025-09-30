
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

arquivo_excel = os.path.join(diretorio_arquivos, "planilhas", "Controle_pessoal.xlsm")
arquivo_db = os.path.join(diretorio_arquivos, "db", "financeiro.db")

conn = sqlite3.connect(arquivo_db)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS categorias_aprendidas (
    descricao TEXT PRIMARY KEY,
    categoria TEXT NOT NULL
)
""")
conn.commit()

df_existente = pd.read_sql_query("SELECT * FROM categorias_aprendidas", conn)
mapa_db = dict(zip(df_existente["descricao"].str.upper().str.strip(),
                   df_existente["categoria"].str.strip()))

# Verifica se a aba "Anual" existe
xls = pd.ExcelFile(arquivo_excel)
if "Anual" not in xls.sheet_names:
    raise ValueError("❌ A aba 'Anual' não foi encontrada no Controle_pessoal.xlsm")

df_controle = pd.read_excel(xls, sheet_name="Anual")

colunas = [col.strip().lower() for col in df_controle.columns]

descricao_col = next((col for col in df_controle.columns if col.strip().lower() in ["descricao", "descrição"]), None)
categoria_col = next((col for col in df_controle.columns if col.strip().lower() == "categoria"), None)

if not descricao_col or not categoria_col:
    raise ValueError("Colunas 'Descrição' e/ou 'Categoria' não encontradas na aba 'Anual'.")

df_controle = df_controle.dropna(subset=[descricao_col, categoria_col])
df_controle["Descricao"] = df_controle[descricao_col].astype(str).str.upper().str.strip()
df_controle["Categoria"] = df_controle[categoria_col].astype(str).str.strip()

def normalizar_descricao(desc):
    desc = desc.upper().strip()
    if "PIX" in desc and len(desc) >= 5:
        possivel_data = desc[-5:]
        if "/" in possivel_data and possivel_data.replace("/", "").isdigit():
            return desc[:-5].strip()
    return desc

df_controle["DescricaoNormalizada"] = df_controle["Descricao"].apply(normalizar_descricao)

novas_linhas = []
for _, row in df_controle.iterrows():
    desc = row["DescricaoNormalizada"]
    cat = row["Categoria"]
    if desc not in mapa_db and cat != "A definir":
        novas_linhas.append((desc, cat))

if novas_linhas:
    cursor.executemany("INSERT OR IGNORE INTO categorias_aprendidas (descricao, categoria) VALUES (?, ?)", novas_linhas)
    conn.commit()
    print(f"✅ {len(novas_linhas)} novas categorias adicionadas ao dicionário a partir da aba 'Anual'.")
else:
    print("✅ Nenhuma nova categoria a partir da aba 'Anual'.")

conn.close()
