import re
import os
import sqlite3
from pathlib import Path

# Definindo caminhos
BASE_DIR = Path(__file__).parent.parent.parent.parent
DB_PATH = BASE_DIR / 'dados' / 'db' / 'financeiro.db'
TXT_DIR = BASE_DIR / 'dados' / 'faturas_txt'

# Expressões Regulares de Extração
# Pega: Data (18 abr.), Descrição (uber virtual), Valor (-R$ 10,00) e Opcionalmente Moeda (US$ 4,99)
REGEX_TRANSACAO = re.compile(r'^(\d{2}\s+[a-zA-ZçÇ]{3,4}\.)\s+(.*?)\s+(-?R\$\s*[0-9A-Za-z\.,]+)(?:\s*•\s*([A-Za-z\$\€\£]+)\s*([0-9\.,]+))?', re.IGNORECASE)
# Pega: parcela 5 de 6
REGEX_PARCELA = re.compile(r'^parcela\s+(\d+)\s+de\s+(\d+)', re.IGNORECASE)
# Pega: valor da cotação (R$ 5,58)
REGEX_COTACAO = re.compile(r'^valor\s+da\s+cota[cç][aã]o\s+\(R\$\s*([\d\.,]+)\)', re.IGNORECASE)

def _limpar_valor(valor_str):
    """Converte 'R$ 1.190,10' ou '-R$ 62,00' para float(1190.10)"""
    if not valor_str: return 0.0
    # Remove R$ e espaços
    limpo = valor_str.upper().replace('R$', '').replace(' ', '')
    # Trata milhar e decimal
    limpo = limpo.replace('.', '').replace(',', '.')
    return float(limpo)

def criar_tabela():
    """Cria tabela lancamentos_faturas_txt independente das demais"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS lancamentos_faturas_txt (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes_comp TEXT,
            cartao_nome TEXT,
            data_orig TEXT,
            descricao TEXT,
            tipo_cartao TEXT,
            valor REAL,
            compra_parcelada BOOLEAN,
            parcela_atual INTEGER,
            qtd_parcelas INTEGER,
            moeda_estrangeira BOOLEAN,
            simbolo_moeda TEXT,
            valor_moeda_estrangeira REAL,
            cotacao REAL,
            categoria_sistema TEXT,
            data_importacao DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def parse_arquivo_fatura(filepath):
    filename = Path(filepath).name
    # Ex: 202604_visa_luciano.txt
    parts = filename.replace('.txt', '').split('_', 1)
    mes_comp = parts[0] if len(parts) > 1 else 'DESCONHECIDO'
    cartao_nome = parts[1] if len(parts) > 1 else filename
    
    transacoes = []
    transacao_atual = None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
        
    for linha in linhas:
        linha = linha.strip()
        if not linha: continue
        
        # 1. Tentar casar com linha principal (Data | Descrição | Valor)
        match_tx = REGEX_TRANSACAO.match(linha)
        if match_tx:
            # Se já tinha uma transação montando, salva ela antes de abrir uma nova
            if transacao_atual:
                transacoes.append(transacao_atual)
                
            data_str = match_tx.group(1).strip()
            desc_bruta = match_tx.group(2).strip()
            valor_str = match_tx.group(3).strip()
            moeda_simbolo = match_tx.group(4)
            moeda_valor_str = match_tx.group(5)
            
            # Limpezas
            tipo_cartao = 'Físico/Adicional'
            if desc_bruta.lower().endswith('virtual'):
                tipo_cartao = 'Virtual'
                desc_bruta = desc_bruta[:-7].strip() # Remove palavra 'virtual' do fim
            
            # Limpa ruído das parcelas no título "10/10"
            desc_bruta = re.sub(r'\s+\d{2}/\d{2}$', '', desc_bruta).strip()
                
            valor = _limpar_valor(valor_str)
            
            # Inicia objeto
            transacao_atual = {
                'mes_comp': mes_comp,
                'cartao_nome': cartao_nome,
                'data_orig': data_str,
                'descricao': desc_bruta,
                'tipo_cartao': tipo_cartao,
                'valor': valor,
                'compra_parcelada': False,
                'parcela_atual': None,
                'qtd_parcelas': None,
                'moeda_estrangeira': False,
                'simbolo_moeda': None,
                'valor_moeda_estrangeira': None,
                'cotacao': None,
                'categoria_sistema': 'Não Categorizado'
            }
            
            # Se tem cotação na mesma linha (Ex: US$ 4.99)
            if moeda_simbolo and moeda_valor_str:
                transacao_atual['moeda_estrangeira'] = True
                transacao_atual['simbolo_moeda'] = moeda_simbolo.strip()
                transacao_atual['valor_moeda_estrangeira'] = _limpar_valor(moeda_valor_str)
                
        else:
            # 2. Se não bateu Data, é informação adicional da transação de cima
            if transacao_atual:
                # Checa Parcela
                match_parc = REGEX_PARCELA.match(linha)
                if match_parc:
                    transacao_atual['compra_parcelada'] = True
                    transacao_atual['parcela_atual'] = int(match_parc.group(1))
                    transacao_atual['qtd_parcelas'] = int(match_parc.group(2))
                    
                # Checa Cotação Dólar
                match_cot = REGEX_COTACAO.match(linha)
                if match_cot:
                    transacao_atual['cotacao'] = _limpar_valor(match_cot.group(1))
                    
    # Salvar a última transação lida
    if transacao_atual:
        transacoes.append(transacao_atual)
        
    return transacoes

def processar_todas_as_faturas():
    criar_tabela()
    
    if not TXT_DIR.exists():
        print(f"DIRETÓRIO NÃO ENCONTRADO: {TXT_DIR}")
        return
        
    arquivos = list(TXT_DIR.glob('*.txt'))
    print(f"💰 {len(arquivos)} arquivos de fatura TXT encontrados para processar.")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    total_inseridos = 0
    for arquivo in arquivos:
        print(f"\n📄 Analisando: {arquivo.name}...")
        lista_tx = parse_arquivo_fatura(arquivo)
        
        # Inserindo no Banco
        for tx in lista_tx:
            c.execute('''
                INSERT INTO lancamentos_faturas_txt (
                    mes_comp, cartao_nome, data_orig, descricao, tipo_cartao, valor,
                    compra_parcelada, parcela_atual, qtd_parcelas,
                    moeda_estrangeira, simbolo_moeda, valor_moeda_estrangeira, cotacao, categoria_sistema
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                tx['mes_comp'], tx['cartao_nome'], tx['data_orig'], tx['descricao'],
                tx['tipo_cartao'], tx['valor'],
                1 if tx['compra_parcelada'] else 0, tx['parcela_atual'], tx['qtd_parcelas'],
                1 if tx['moeda_estrangeira'] else 0, tx['simbolo_moeda'],
                tx['valor_moeda_estrangeira'], tx['cotacao'], tx['categoria_sistema']
            ))
            print(f"  ➜ Extraído: {tx['data_orig']} | {tx['descricao'][:20].ljust(20)} | R$ {tx['valor']:>8.2f} | Tipo: {tx['tipo_cartao']} | Parc: {tx['parcela_atual']}/{tx['qtd_parcelas']} | US: {tx['simbolo_moeda']}")
            total_inseridos += 1
            
    conn.commit()
    conn.close()
    print(f"\n✅ SUCESSO! {total_inseridos} transações foram desmembradas e salvas na tabela 'lancamentos_faturas_txt'.")

if __name__ == '__main__':
    processar_todas_as_faturas()
