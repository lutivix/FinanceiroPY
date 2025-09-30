"""
Módulo de debug para o Agente Financeiro IA
Funções auxiliares para debugging e desenvolvimento
"""

import pandas as pd
import os
import sqlite3
from datetime import datetime

def debug_info(diretorio_arquivos):
    """Mostra informações de debug sobre o ambiente."""
    print("\n" + "="*50)
    print("🐛 DEBUG - AGENTE FINANCEIRO IA")
    print("="*50)
    
    print(f"📁 Diretório base: {diretorio_arquivos}")
    print(f"📅 Data atual: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Verifica estrutura de diretórios
    print("\n📂 Estrutura de diretórios:")
    dirs_necessarios = [
        os.path.join(diretorio_arquivos, "db"),
        os.path.join(diretorio_arquivos, "planilhas"),
    ]
    
    for dir_path in dirs_necessarios:
        status = "✅" if os.path.exists(dir_path) else "❌"
        print(f"{status} {dir_path}")
    
    # Verifica banco de dados
    db_path = os.path.join(diretorio_arquivos, "db", "financeiro.db")
    print(f"\n🗄️  Banco de dados: {db_path}")
    
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verifica tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tabelas = cursor.fetchall()
            print(f"📊 Tabelas encontradas: {[t[0] for t in tabelas]}")
            
            # Conta registros
            for tabela in tabelas:
                cursor.execute(f"SELECT COUNT(*) FROM {tabela[0]}")
                count = cursor.fetchone()[0]
                print(f"   - {tabela[0]}: {count} registros")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Erro ao acessar banco: {e}")
    else:
        print("❌ Banco de dados não encontrado")
    
    # Lista arquivos de planilhas
    planilhas_dir = os.path.join(diretorio_arquivos, "planilhas")
    print(f"\n📈 Planilhas em {planilhas_dir}:")
    
    if os.path.exists(planilhas_dir):
        arquivos = os.listdir(planilhas_dir)
        arquivos.sort()
        
        if arquivos:
            for arquivo in arquivos[:10]:  # Mostra só os 10 primeiros
                size = os.path.getsize(os.path.join(planilhas_dir, arquivo))
                print(f"   📄 {arquivo} ({size} bytes)")
            
            if len(arquivos) > 10:
                print(f"   ... e mais {len(arquivos) - 10} arquivos")
        else:
            print("   📭 Nenhum arquivo encontrado")
    else:
        print("   ❌ Diretório não existe")
    
    print("\n" + "="*50)

def debug_arquivo(caminho_arquivo):
    """Debug específico de um arquivo de extrato."""
    print(f"\n🔍 DEBUG ARQUIVO: {caminho_arquivo}")
    print("-" * 40)
    
    if not os.path.exists(caminho_arquivo):
        print(f"❌ Arquivo não encontrado: {caminho_arquivo}")
        return
    
    # Informações básicas
    size = os.path.getsize(caminho_arquivo)
    print(f"📏 Tamanho: {size} bytes")
    
    # Tenta ler como TXT primeiro
    if caminho_arquivo.endswith('.txt'):
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
            
            print(f"📝 Tipo: TXT com {len(linhas)} linhas")
            print("📋 Primeiras 5 linhas:")
            for i, linha in enumerate(linhas[:5]):
                print(f"   {i+1}: {linha.strip()}")
                
        except Exception as e:
            print(f"❌ Erro ao ler TXT: {e}")
    
    # Tenta ler como Excel
    elif caminho_arquivo.endswith(('.xls', '.xlsx')):
        try:
            df = pd.read_excel(caminho_arquivo)
            print(f"📊 Tipo: Excel com {len(df)} linhas e {len(df.columns)} colunas")
            print(f"📋 Colunas: {list(df.columns)}")
            print("📋 Primeiras 3 linhas:")
            print(df.head(3).to_string(index=False))
            
        except Exception as e:
            print(f"❌ Erro ao ler Excel: {e}")

def debug_categorias(diretorio_arquivos):
    """Debug do sistema de categorização."""
    print(f"\n🏷️  DEBUG CATEGORIAS")
    print("-" * 40)
    
    db_path = os.path.join(diretorio_arquivos, "db", "financeiro.db")
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Categorias aprendidas
        df_categorias = pd.read_sql_query("SELECT * FROM categorias_aprendidas ORDER BY categoria", conn)
        
        if len(df_categorias) > 0:
            print(f"📚 Total de categorias aprendidas: {len(df_categorias)}")
            
            # Agrupa por categoria
            por_categoria = df_categorias.groupby('categoria').size().sort_values(ascending=False)
            print("\n📊 Distribuição por categoria:")
            for categoria, count in por_categoria.items():
                print(f"   {categoria}: {count} descrições")
            
            print("\n📋 Algumas descrições aprendidas:")
            for categoria in por_categoria.head(3).index:
                exemplos = df_categorias[df_categorias['categoria'] == categoria]['descricao'].head(3)
                print(f"\n   🏷️  {categoria}:")
                for desc in exemplos:
                    print(f"      - {desc}")
        else:
            print("📭 Nenhuma categoria aprendida ainda")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao acessar categorias: {e}")

def debug_processamento(diretorio_arquivos, limite_arquivos=3):
    """Debug do processamento completo com limite de arquivos."""
    print(f"\n⚙️  DEBUG PROCESSAMENTO (máx {limite_arquivos} arquivos)")
    print("-" * 50)
    
    # Importa as funções necessárias
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    
    try:
        from agente_financeiro import arquivos_recentes, tratar_extrato_excel, tratar_extrato_txt
        
        # Busca arquivos
        arquivos = arquivos_recentes(diretorio_arquivos, ["Latam", "Itau", "Pix"])
        
        if not arquivos:
            print("❌ Nenhum arquivo encontrado para processar")
            return
        
        print(f"📁 Arquivos encontrados: {len(arquivos)}")
        
        # Processa alguns arquivos para teste
        lancamentos_debug = []
        count = 0
        
        for chave, nome_arquivo in arquivos.items():
            if count >= limite_arquivos:
                break
            
            caminho = os.path.join(diretorio_arquivos, nome_arquivo)
            print(f"\n🔄 Processando: {chave} -> {nome_arquivo}")
            
            try:
                if nome_arquivo.endswith(".txt"):
                    df = tratar_extrato_txt(caminho, "Pix")
                else:
                    df_excel = pd.read_excel(caminho)
                    df = tratar_extrato_excel(df_excel, chave.split("_")[0])
                
                print(f"   ✅ {len(df)} transações extraídas")
                if len(df) > 0:
                    print(f"   💰 Valores: R$ {df['Valor'].min():.2f} a R$ {df['Valor'].max():.2f}")
                    print(f"   📅 Período: {df['Data'].min()} a {df['Data'].max()}")
                
                lancamentos_debug.append(df)
                count += 1
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
        
        if lancamentos_debug:
            df_total = pd.concat(lancamentos_debug, ignore_index=True)
            print(f"\n📊 RESUMO TOTAL:")
            print(f"   📈 Total de transações: {len(df_total)}")
            print(f"   💰 Valor total: R$ {df_total['Valor'].sum():.2f}")
            print(f"   🏪 Fontes: {df_total['Fonte'].unique()}")
            
    except Exception as e:
        print(f"❌ Erro no debug de processamento: {e}")

if __name__ == "__main__":
    # Exemplo de uso
    diretorio = "../../dados"  # Ajuste conforme necessário
    debug_info(diretorio)