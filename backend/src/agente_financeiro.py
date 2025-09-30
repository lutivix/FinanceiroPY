
import os
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
from calendar import month_name
import configparser

# Configuração do projeto
def carregar_configuracao():
    config = configparser.ConfigParser()
    config_file = 'config.ini'
    
    # Se não existe config.ini, usa o exemplo
    if not os.path.exists(config_file):
        config_file = 'config.example.ini'
        print("⚠️  config.ini não encontrado. Usando config.example.ini")
        print("💡 Copie config.example.ini para config.ini e ajuste seus caminhos")
    
    config.read(config_file)
    return config

config = carregar_configuracao()

# Obtém diretório dos arquivos da configuração
diretorio_base = config.get('PATHS', 'diretorio_arquivos', fallback='dados')
# Se é caminho relativo, usa relativo ao script atual
if not os.path.isabs(diretorio_base):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))  # Volta 2 níveis
    diretorio_arquivos = os.path.join(project_root, diretorio_base)
else:
    diretorio_arquivos = diretorio_base

def arquivos_recentes(diretorio, bases):
    arquivos_validos = {}
    hoje = datetime.today()
    base_data = hoje.replace(day=1)
    if hoje.day >= 19:
        base_data = (base_data + timedelta(days=32)).replace(day=1)  # próximo mês

    meses_retroativos = config.getint('PROCESSAMENTO', 'meses_retroativos', fallback=12)
    
    for i in range(meses_retroativos):
        data_ref = base_data - pd.DateOffset(months=i)
        ano_mes = data_ref.strftime("%Y%m")
        for base in bases:
            nome = f"{ano_mes}_Extrato.txt" if base == "Pix" else f"{ano_mes}_{base}.xls"
            caminho = os.path.join(diretorio, "planilhas", nome)  # Adiciona subpasta planilhas
            if os.path.exists(caminho):
                arquivos_validos[f"{base}_{ano_mes}"] = os.path.join("planilhas", nome)
    return arquivos_validos


def extrair_mes_comp(nome_arquivo):
    apenas_numeros = ''.join(filter(str.isdigit, nome_arquivo))
    ano, mes = apenas_numeros[:4], int(apenas_numeros[4:6])
    meses_pt = { "January": "Janeiro", "February": "Fevereiro", "March": "Março",
        "April": "Abril", "May": "Maio", "June": "Junho", "July": "Julho",
        "August": "Agosto", "September": "Setembro", "October": "Outubro",
        "November": "Novembro", "December": "Dezembro" }
    return f"{meses_pt.get(month_name[mes], month_name[mes])} {ano}"

conn = sqlite3.connect(os.path.join(diretorio_arquivos, "db", "financeiro.db"))
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS categorias_aprendidas (
    descricao TEXT PRIMARY KEY, categoria TEXT NOT NULL)""")
conn.commit()
df_existente = pd.read_sql_query("SELECT * FROM categorias_aprendidas", conn)
mapa_aprendizado = dict(zip(df_existente["descricao"].str.upper().str.strip(),
                            df_existente["categoria"].str.strip()))
conn.close()

def tratar_extrato_excel(df, origem):
    finais_latam = {"1152": "Visa Recorrente", "6259": "Visa Físico", "3666": "Visa Bia", "8106": "Visa Mae"}
    finais_itau = {"4059": "Master Físico", "2800": "Master Recorrente", "2001": "Master Recorrente"}
    df_lancamentos, final_cartao = [], None
    ultima_data, aguardando_valor_real = None, False

    for _, row in df.iterrows():
        col_a = str(row.iloc[0]).strip()
        col_b = str(row.iloc[1]).strip()
        col_d = row.iloc[3] if len(row) > 3 else None
        valor = pd.to_numeric(col_d, errors="coerce") if col_d is not None else None

        if "FINAL" in col_a.upper():
            final_cartao = ''.join(filter(str.isdigit, col_a))[-4:]
            continue

        if not col_b or col_b.strip().upper() in ["NAN", ""]:
            continue
        if "PAGAMENTO EFETUADO" in col_b.upper():
            continue
        if any(palavra in col_b.upper() for palavra in ["ITAU BLACK", "ITAU VISA"]):
            continue
        if any(moeda in col_b.upper() for moeda in ["USD", "$", "€", "EURO", "CHF", "GBP", "SWITZERLAND"]):
            continue

        try:
            data = pd.to_datetime(col_a, dayfirst=True, errors="coerce").date()
            if "dólar de conversão" in col_b.lower():
                ultima_data = data
                aguardando_valor_real = True
                continue
        except:
            data = None

        if pd.isnull(data) and pd.notnull(valor):
            if aguardando_valor_real:
                data = ultima_data
                aguardando_valor_real = False
            else:
                continue
        elif pd.isnull(data):
            continue

        if pd.notnull(valor):
            if origem == "Latam":
                fonte = finais_latam.get(final_cartao, "Visa Virtual")
            elif origem == "Itau":
                fonte = finais_itau.get(final_cartao, "Master Virtual")
            else:
                fonte = origem

            df_lancamentos.append({
                "Data": data,
                "Descricao": col_b,
                "Valor": valor,
                "Fonte": fonte
            })

    return pd.DataFrame(df_lancamentos)

def tratar_extrato_txt(caminho, origem):
    df_txt = pd.read_csv(caminho, sep=";", header=None, names=["Data", "Descricao", "Valor"], encoding="utf-8")
    df_txt["Data"] = pd.to_datetime(df_txt["Data"], errors="coerce", dayfirst=True).dt.date
    df_txt["Valor"] = df_txt["Valor"].astype(str).str.replace(",", ".").astype(float) * -1
    df_txt["Fonte"] = origem
    df_txt = df_txt[~df_txt["Descricao"].str.upper().str.contains("ITAU BLACK|ITAU VISA", na=False)]
    return df_txt.dropna(subset=["Data", "Valor"])

def categorizar_lancamento(descricao):
    desc = descricao.upper().strip()
    if "PIX" in desc and len(desc) >= 5:
        possivel_data = desc[-5:]
        if "/" in possivel_data and possivel_data.replace("/", "").isdigit():
            desc = desc[:-5].strip()

    contains_map = {
        "SISPAG PIX": "SALÁRIO",
        "REND PAGO APLIC": "INVESTIMENTOS",
        "PAGTO REMUNERACAO": "SALÁRIO",
        "PAGTO SALARIO": "SALÁRIO"
    }
    for trecho, categoria in contains_map.items():
        if trecho in desc:
            return categoria

    categoria_padrao = config.get('PROCESSAMENTO', 'categoria_padrao', fallback='A definir')
    
    for chave in mapa_aprendizado:
        if chave in desc:
            return mapa_aprendizado[chave]

    return categoria_padrao

arquivos = arquivos_recentes(diretorio_arquivos, ["Latam", "Itau", "Pix"])
lancamentos = []

for chave, nome_arquivo in arquivos.items():
    caminho = os.path.join(diretorio_arquivos, nome_arquivo)
    mes_comp = extrair_mes_comp(nome_arquivo)
    df = tratar_extrato_txt(caminho, "Pix") if nome_arquivo.endswith(".txt") else tratar_extrato_excel(pd.read_excel(caminho), chave.split("_")[0])
    df["MesComp"] = mes_comp
    lancamentos.append(df)

df_consolidado = pd.concat(lancamentos, ignore_index=True)
df_consolidado["Categoria"] = df_consolidado["Descricao"].apply(categorizar_lancamento)
df_consolidado = df_consolidado[["Data", "Descricao", "Fonte", "Valor", "Categoria", "MesComp"]]

conn = sqlite3.connect(os.path.join(diretorio_arquivos, "db", "financeiro.db"))
df_consolidado.to_sql("lancamentos", conn, if_exists="append", index=False)
conn.close()

arquivo_excel_nome = config.get('EXCEL', 'arquivo_saida', fallback='consolidado_temp.xlsx')
arquivo_excel = os.path.join(diretorio_arquivos, "planilhas", arquivo_excel_nome)
df_consolidado.to_excel(arquivo_excel, index=False)
print(f"📄 Arquivo Excel temporário gerado: {arquivo_excel}")
print(f"🗄️  Dados salvos no banco: {os.path.join(diretorio_arquivos, 'db', 'financeiro.db')}")
print(f"📊 Total de {len(df_consolidado)} transações processadas")
