import os
import sys
from pathlib import Path
import sqlite3
import re
from datetime import datetime, date as Date

# Importando do seu ecossistema sem mexer nos arquivos originais
sys.path.insert(0, str(Path(__file__).parent))
try:
    from models import Transaction, TransactionCategory, TransactionSource
    from database.category_repository import CategoryRepository
    from services.categorization_service import CategorizationService
    HAS_MODELS = True
except ImportError:
    HAS_MODELS = False
    print("Aviso: Módulos do projeto não carregados perfeitamente. Tentando workaround interno.")

BASE_DIR = Path(__file__).parent.parent.parent
DB_PATH = BASE_DIR / 'dados' / 'db' / 'financeiro.db'
TXT_DIR = BASE_DIR / 'dados' / 'faturas_txt'

# Expressões Regulares de Extração
REGEX_TRANSACAO = re.compile(r'^(\d{2}\s+[a-zA-ZçÇ]{3,4}\.?)\s+(.*?)\s+(-?R\$\s*[0-9A-Za-z\.,]+)(?:\s*•\s*([A-Za-z\$\€\£]+)\s*([0-9\.,]+))?', re.IGNORECASE)
REGEX_EXTRATO_CSV = re.compile(r'^(\d{2}/\d{2}/\d{4});(.*?);([-\d\,\.]+)$', re.IGNORECASE)
REGEX_DATA_EXTRATO = re.compile(r'^(\d{2}/\d{2}/\d{4})$', re.IGNORECASE)
REGEX_PARCELA = re.compile(r'^parcela\s+(\d+)\s+de\s+(\d+)', re.IGNORECASE)
REGEX_COTACAO = re.compile(r'^valor\s+da\s+cota[cç][aã]o\s+\(R\$\s*([\d\.,]+)\)', re.IGNORECASE)

MESES_PT = {
    'jan': 1, 'fcv': 2, 'fev': 2, 'mar': 3, 'abr': 4,
    'mai': 5, 'jun': 6, 'jul': 7, 'ago': 8,
    'set': 9, 'out': 10, 'nov': 11, 'dez': 12
}

def _limpar_valor(valor_str):
    if not valor_str: return 0.0
    limpo = valor_str.upper().replace('R$', '').replace(' ', '')
    limpo = limpo.replace('.', '').replace(',', '.')
    return float(limpo)

def _normalizar_descricao(descricao):
    """Remove espaços múltiplos e normaliza a descrição para evitar duplicatas"""
    if not descricao: return ''
    # Remove espaços múltiplos (substitui 2+ espaços por 1 espaço)
    return re.sub(r'\s+', ' ', descricao.strip())

def _converter_data(data_bruta_texto, ano_base):
    # Exemplo: "18 abr." ou "18 abr"
    partes = data_bruta_texto.replace('.', '').strip().split()
    if len(partes) >= 2:
        try:
            dia = int(partes[0])
            mes_str = partes[1].lower()[:3]
            mes = MESES_PT.get(mes_str, 1)
            # Se a fatura é de abril, e a compra é dez, provavelmente é ano passado
            ano_final = int(ano_base)
            if mes > 10 and int(ano_base[4:6]) < 3: # Ex: fatura janeiro, compra dezembro
                ano_final -= 1
            return Date(ano_final, mes, dia)
        except:
            return Date.today()
    return Date.today()

def criar_tabela():
    """Tabela INDEPENDENTE do sistema primário para evitar estragar o que funciona."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS lancamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            MesComp TEXT,
            Fonte TEXT,
            Data DATE,
            Descricao TEXT,
            Valor REAL,
            Categoria TEXT,
            data_orig TEXT,
            tipo_cartao TEXT,
            compra_parcelada BOOLEAN,
            parcela_atual INTEGER,
            qtd_parcelas INTEGER,
            moeda_estrangeira BOOLEAN,
            simbolo_moeda TEXT,
            valor_moeda_estrangeira REAL,
            cotacao REAL,
            raw_data TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def mapear_fonte(filename):
    nome = filename.lower()
    if 'extrato' in nome or 'conta corrente' in nome or 'pix' in nome: return 'PIX'
    if 'bia' in nome: return 'Visa Bia'
    if 'mae' in nome or 'mãe' in nome: return 'Visa Mae'
    if 'master' in nome: return 'Master Físico'
    if 'visa' in nome: return 'Visa Físico'
    return 'Desconhecido'

def formatar_mes_comp(mes_comp_str):
    if len(mes_comp_str) != 6: return mes_comp_str
    ano = mes_comp_str[:4]
    mes = mes_comp_str[4:]
    meses = {
        '01': 'Janeiro', '02': 'Fevereiro', '03': 'Março', '04': 'Abril',
        '05': 'Maio', '06': 'Junho', '07': 'Julho', '08': 'Agosto',
        '09': 'Setembro', '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'
    }
    return f"{meses.get(mes, '')} {ano}".strip()

def processar_extrato_novo_formato(linhas, filename, ano_base):
    """
    Processa extratos no novo formato onde:
    - Linha 1: Data (DD/MM/AAAA)
    - Linha 2: Descrição
    - Linha 3: Valor
    - Separador: linha em branco OU próxima data
    """
    transacoes = []
    i = 0
    meses_str = {'01':'Janeiro', '02':'Fevereiro', '03':'Março', '04':'Abril', '05':'Maio', '06':'Junho', 
                 '07':'Julho', '08':'Agosto', '09':'Setembro', '10':'Outubro', '11':'Novembro', '12':'Dezembro'}
    
    # Lista de nomes de meses para ignorar
    nomes_meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 
                   'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
    
    while i < len(linhas):
        linha = linhas[i].strip()
        
        # Ignora linhas vazias
        if not linha:
            i += 1
            continue
            
        # Ignora cabeçalhos
        if 'data' in linha.lower() and 'lançamentos' in linha.lower():
            i += 1
            continue
            
        # Ignora linhas de saldo
        if 'SALDO TOTAL' in linha.upper():
            i += 1
            continue
            
        # Ignora linhas que são apenas nomes de meses
        if linha.lower().strip() in nomes_meses or any(linha.lower().strip().startswith(mes) for mes in nomes_meses):
            i += 1
            continue
            
        # Verifica se é uma linha de data
        match_data = REGEX_DATA_EXTRATO.match(linha)
        if match_data:
            data_str = match_data.group(1)
            
            # Próxima linha deve ser a descrição
            i += 1
            if i >= len(linhas):
                break
            desc_bruta = linhas[i].strip()
            
            # Se a descrição for vazia, SALDO TOTAL ou uma data, pula essa transação
            if not desc_bruta or 'SALDO TOTAL' in desc_bruta.upper() or REGEX_DATA_EXTRATO.match(desc_bruta):
                # Precisa pular também a próxima linha (valor) antes de continuar
                i += 1
                continue
                
            # Próxima linha deve ser o valor
            i += 1
            if i >= len(linhas):
                break
            valor_str = linhas[i].strip()
            
            # Valida se é um valor numérico (pode ter - no início, dígitos, vírgula e ponto)
            if not valor_str or not re.match(r'^-?[\d\.,]+$', valor_str):
                # Se não for um valor válido, pula essa transação
                continue
            
            # Parse da data
            dia, mes, ano = data_str.split('/')
            data_obj = Date(int(ano), int(mes), int(dia))
            comp_extrato = f"{meses_str.get(mes, '')} {ano}"
            
            # Parse do valor (inverte sinal: débito=positivo, crédito=negativo)
            valor_limpo = valor_str.replace('.', '').replace(',', '.')
            
            transacao = {
                'mes_comp': comp_extrato,
                'cartao_nome': 'PIX',
                'data_orig': data_str,
                'data_obj': data_obj,
                'descricao': _normalizar_descricao(desc_bruta),
                'tipo_cartao': 'Principal',
                'valor': float(valor_limpo) * -1,
                'compra_parcelada': False,
                'parcela_atual': None,
                'qtd_parcelas': None,
                'moeda_estrangeira': False,
                'simbolo_moeda': None,
                'valor_moeda_estrangeira': None,
                'cotacao': None,
                'raw_data': f"origem: {filename} : ---\n{data_str}\n{desc_bruta}\n{valor_str}"
            }
            transacoes.append(transacao)
        
        i += 1
    
    return transacoes

def processar_faturas():
    criar_tabela()
    
    if not TXT_DIR.exists():
        print(f"DIRETÓRIO NÃO ENCONTRADO: {TXT_DIR}")
        return
        
    arquivos = list(TXT_DIR.glob('*.txt'))
    print(f"💰 {len(arquivos)} arquivos de fatura TXT encontrados para processar.")
    
    # Inicializa Categorizador Oficial sem mexer nas lógicas antigas!
    categoria_repo = CategoryRepository(DB_PATH)
    categorizador = CategorizationService(categoria_repo)
    
    total_inseridos = 0
    tabelas_prontas_para_inserir = []
    assinaturas_em_memoria = set()
    
    for arquivo in arquivos:
        print(f"\n📄 Analisando: {arquivo.name}...")
        
        filename = arquivo.name
        parts = filename.replace('.txt', '').split('_', 1)
        mes_comp_str = parts[0] if len(parts) > 1 else '202601'
        mes_comp_fmt = formatar_mes_comp(mes_comp_str)
        cartao_nome = mapear_fonte(filename)
        ano_base = mes_comp_str[:4] if len(mes_comp_str) >= 4 else str(Date.today().year)
        
        # Conexão de checagem para deduplicação da fatura atual
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        transacoes = []
        transacao_atual = None
        
        with open(arquivo, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        
        # Detecta se é o novo formato de extrato (verifica se tem cabeçalho ou padrão de linhas)
        is_novo_extrato = False
        if cartao_nome == 'PIX' or 'extrato' in filename.lower():
            # Verifica se tem o padrão do novo formato (data sozinha, depois descrição, depois valor)
            for i, linha in enumerate(linhas[:10]):  # Checa primeiras 10 linhas
                if REGEX_DATA_EXTRATO.match(linha.strip()):
                    is_novo_extrato = True
                    break
        
        if is_novo_extrato:
            # Usa o parser do novo formato de extrato
            transacoes = processar_extrato_novo_formato(linhas, filename, ano_base)
        else:
            # Usa o parser antigo (faturas de cartão ou extrato CSV)
            for linha in linhas:
                linha_original = linha # Guarda o raw data intacto
                linha = linha.strip()
                if not linha: continue
                
                match_tx = REGEX_TRANSACAO.match(linha)
                match_extrato = REGEX_EXTRATO_CSV.match(linha)
                if match_tx:
                    if transacao_atual:
                        transacoes.append(transacao_atual)
                        
                    data_str = match_tx.group(1).strip()
                    desc_bruta = match_tx.group(2).strip()
                    valor_str = match_tx.group(3).strip()
                    moeda_simbolo = match_tx.group(4)
                    moeda_valor_str = match_tx.group(5)
                    
                    # Identifica se é virtual (Regra extraída do comportamento do usuário)
                    tipo_cartao = 'Principal'
                    if cartao_nome in ['Visa Bia', 'Visa Mae']:
                        tipo_cartao = 'Adicional'
                    
                    if desc_bruta.lower().endswith('virtual'):
                        tipo_cartao = 'Virtual'
                        desc_bruta = desc_bruta[:-7].strip()
                    
                    desc_bruta = re.sub(r'\s+\d{2}/\d{2}$', '', desc_bruta).strip()
                    valor = _limpar_valor(valor_str)
                    data_obj = _converter_data(data_str, ano_base)
                    
                    transacao_atual = {
                        'mes_comp': mes_comp_fmt,
                        'cartao_nome': cartao_nome,
                        'data_orig': data_str,
                        'data_obj': data_obj,
                        'descricao': _normalizar_descricao(desc_bruta),
                        'tipo_cartao': tipo_cartao,
                        'valor': float(valor),
                        'compra_parcelada': False,
                        'parcela_atual': None,
                        'qtd_parcelas': None,
                        'moeda_estrangeira': False,
                        'simbolo_moeda': None,
                        'valor_moeda_estrangeira': None,
                        'cotacao': None,
                        'raw_data': f"origem: {filename} : ---\n{linha_original.strip()}"
                    }
                    
                    if moeda_simbolo and moeda_valor_str:
                        transacao_atual['moeda_estrangeira'] = True
                        transacao_atual['simbolo_moeda'] = moeda_simbolo.strip()
                        transacao_atual['valor_moeda_estrangeira'] = _limpar_valor(moeda_valor_str)
                        
                elif match_extrato:
                    if transacao_atual:
                        transacoes.append(transacao_atual)
                        
                    data_str = match_extrato.group(1).strip()
                    desc_bruta = match_extrato.group(2).strip()
                    valor_str = match_extrato.group(3).strip()
                    
                    dia, mes, ano = data_str.split('/')
                    data_obj = Date(int(ano), int(mes), int(dia))
                    
                    # Definir MesComp correto pro Extrato com base na data da transação se tiver nome ruim
                    meses_str = {'01':'Janeiro', '02':'Fevereiro', '03':'Março', '04':'Abril', '05':'Maio', '06':'Junho', '07':'Julho', '08':'Agosto', '09':'Setembro', '10':'Outubro', '11':'Novembro', '12':'Dezembro'}
                    comp_extrato = f"{meses_str.get(mes, '')} {ano}"
                    
                    valor_limpo = valor_str.replace('.', '').replace(',', '.')
                    
                    transacao_atual = {
                        'mes_comp': comp_extrato,
                        'cartao_nome': cartao_nome,
                        'data_orig': data_str,
                        'data_obj': data_obj,
                        'descricao': _normalizar_descricao(desc_bruta),
                        'tipo_cartao': 'Principal',
                        'valor': float(valor_limpo) * -1,
                        'compra_parcelada': False,
                        'parcela_atual': None,
                        'qtd_parcelas': None,
                        'moeda_estrangeira': False,
                        'simbolo_moeda': None,
                        'valor_moeda_estrangeira': None,
                        'cotacao': None,
                        'raw_data': f"origem: {filename} : ---\n{linha_original.strip()}"
                    }
                    
                else:
                    if transacao_atual:
                        transacao_atual['raw_data'] += f"\n{linha_original.strip()}"
                        match_parc = REGEX_PARCELA.match(linha)
                        if match_parc:
                            transacao_atual['compra_parcelada'] = True
                            transacao_atual['parcela_atual'] = int(match_parc.group(1))
                            transacao_atual['qtd_parcelas'] = int(match_parc.group(2))
                            
                        match_cot = REGEX_COTACAO.match(linha)
                        if match_cot:
                            transacao_atual['cotacao'] = _limpar_valor(match_cot.group(1))
                            
            if transacao_atual:
                transacoes.append(transacao_atual)
            
        # PULAR VERIFICAÇÃO DE DUPLICATAS NA BASE (Lógica do agente_financeiro)
        transacoes_unicas = []
        for tx in transacoes:
            assinatura = (tx['data_obj'].isoformat(), tx['valor'], cartao_nome, tx['descricao'], tx['mes_comp'])
            if assinatura in assinaturas_em_memoria:
                print(f"  ⏭️ Ignorando duplicata (na própria leitura atual): {tx['descricao']} | R$ {tx['valor']:>8.2f}")
                continue
                
            c.execute('''
                SELECT 1 FROM lancamentos
                WHERE Data = ? AND ABS(Valor - ?) < 0.01 AND (Fonte = ? OR Fonte = ?) AND Descricao = ? AND (MesComp = ? OR MesComp IS NULL)
            ''', (tx['data_obj'].isoformat(), tx['valor'], cartao_nome, tx['tipo_cartao'], tx['descricao'], tx['mes_comp']))
            
            if c.fetchone():
                # Ignora duplicada exata que já está no banco atual 
                print(f"  ⏭️ Ignorando duplicata (no banco de dados): {tx['descricao']} | R$ {tx['valor']:>8.2f}")
                continue
                
            assinaturas_em_memoria.add(assinatura)
            transacoes_unicas.append(tx)
            
        # Gravar no BD e passar pelo Categorizador Oficial somente as únicas
        for tx in transacoes_unicas:
            try:
                # Usa os modelos originais limpos do projeto!
                # Fake transaction object just for categorization logic
                dummy_transaction = Transaction(
                    date=tx['data_obj'],
                    description=tx['descricao'],
                    amount=tx['valor'],
                    source=TransactionSource.PIX, # Not critical for categorization engine mapping
                    category=TransactionCategory.A_DEFINIR
                )
                cat_final = categorizador.categorize_transaction(dummy_transaction)
                categoria_nome = cat_final.value
            except Exception as e:
                categoria_nome = "Erro Categorização"
            
            # Formatação de campos para o BD
            valores_banco = (
                tx['mes_comp'], tx['cartao_nome'], tx['data_orig'], tx['data_obj'].isoformat(), tx['descricao'],
                tx['tipo_cartao'], tx['valor'],
                1 if tx['compra_parcelada'] else 0, tx['parcela_atual'], tx['qtd_parcelas'],
                1 if tx['moeda_estrangeira'] else 0, tx['simbolo_moeda'],
                tx['valor_moeda_estrangeira'], tx['cotacao'], tx['raw_data'], categoria_nome
            )
            tabelas_prontas_para_inserir.append(valores_banco)
            
            # Printa legal pra você ver qual foi a categoria que o sistema antigo escolheu!
            if total_inseridos < 10 or 'estrangeira' in repr(tx).lower(): # Printa as 10 primeiras + algumas pra gente ver
                print(f"  ➜ {tx['descricao'][:20].ljust(20)} | R$ {tx['valor']:>8.2f} | Categ: {categoria_nome}")
            
            total_inseridos += 1
            
        conn.close() # Fecha conn da verificação
            
    # Executa todas as gravações no banco SOMENTE APÓS TODAS AS CATEGORIZAÇÕES TEREM OCORRIDO.
    # Evita o erro 'database is locked' de transações concorrentes na base SQLite.
    print(f"\n⚙️ Gravando tudo consolidado na tabela de forma segura...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executemany('''
        INSERT INTO lancamentos (
            MesComp, Fonte, data_orig, Data, Descricao, tipo_cartao, Valor,
            compra_parcelada, parcela_atual, qtd_parcelas,
            moeda_estrangeira, simbolo_moeda, valor_moeda_estrangeira, cotacao, raw_data, Categoria
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', tabelas_prontas_para_inserir)
    
    conn.commit()
    conn.close()
    print(f"\n✅ SUCESSO! {total_inseridos} transações processadas com as regras originais consolidadas na tabela principal 'lancamentos'.")

if __name__ == '__main__':
    processar_faturas()
