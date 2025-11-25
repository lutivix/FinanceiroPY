"""
Sincronização Open Finance - Busca transações do Pluggy
Permite escolher quantos dias retroativos buscar
Salva em transacoes_openfinance
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import requests
from datetime import datetime, timedelta, date as Date
import json
import sqlite3
from models import get_card_source, Transaction, TransactionSource, TransactionCategory
from database import CategoryRepository
from services.categorization_service import CategorizationService

# Configurações Pluggy
CLIENT_ID = '0774411c-feca-44dc-83df-b5ab7a1735a6'
CLIENT_SECRET = '3bd7389d-72d6-419a-804a-146e3e0eaacf'
BASE_URL = 'https://api.pluggy.ai'

# Contas conectadas
ITAU_ITEM_ID = '60cbf151-aaed-45c7-afac-f2aab15e6299'
MERCADOPAGO_ITEM_ID = '879f822e-ad2b-48bb-8137-cf761ab1a1a3'

# Banco de dados
DB_PATH = Path(__file__).parent / '../../dados/db/financeiro.db'

class OpenFinanceSync:
    def __init__(self):
        self.api_key = None
        self.headers = None
        
        # Inicializar CategoryRepository e CategorizationService
        self.category_repository = CategoryRepository(DB_PATH)
        self.categorization_service = CategorizationService(self.category_repository)
        self.stats = {
            'total_importadas': 0,
            'total_duplicadas': 0,
            'total_categorizadas': 0,
            'total_a_definir': 0,
            'por_mes': {},
            'por_fonte': {},
            'por_categoria': {}
        }
    
    def autenticar(self):
        """Autenticar no Pluggy"""
        print("🔐 Autenticando no Pluggy...")
        auth_response = requests.post(f'{BASE_URL}/auth', json={
            'clientId': CLIENT_ID,
            'clientSecret': CLIENT_SECRET
        })
        self.api_key = auth_response.json()['apiKey']
        self.headers = {'X-API-KEY': self.api_key}
        print("✅ Autenticado com sucesso!")
    
    def criar_tabela(self):
        """Criar tabela transacoes_openfinance se não existir"""
        print("\n📊 Criando tabela transacoes_openfinance...")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transacoes_openfinance (
                -- Identificação
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_id TEXT UNIQUE NOT NULL,
                account_id TEXT NOT NULL,
                
                -- Dados da Transação
                data DATE NOT NULL,
                descricao TEXT NOT NULL,
                valor REAL NOT NULL,
                
                -- Categorização
                categoria TEXT NOT NULL,
                categoria_banco TEXT,
                tag TEXT,
                
                -- Fonte/Origem
                fonte TEXT NOT NULL,
                pagador TEXT,
                cartao_final TEXT,
                
                -- Período Contábil
                mes_comp TEXT NOT NULL,
                
                -- Metadados Bancários
                tipo_transacao TEXT,
                tipo_conta TEXT,
                origem_banco TEXT,
                
                -- Parcelas
                parcela_numero INTEGER,
                parcela_total INTEGER,
                data_compra DATE,
                
                -- Moeda
                moeda_original TEXT DEFAULT 'BRL',
                valor_moeda_original REAL,
                
                -- Controle/Origem
                origem_dado TEXT DEFAULT 'openfinance',
                sincronizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Dados RAW
                metadata_json TEXT,
                
                -- Auditoria
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Criar índices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_provider_id ON transacoes_openfinance(provider_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_data ON transacoes_openfinance(data)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mes_comp ON transacoes_openfinance(mes_comp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_categoria ON transacoes_openfinance(categoria)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_fonte ON transacoes_openfinance(fonte)")
        
        conn.commit()
        conn.close()
        
        print("✅ Tabela criada com sucesso!")
    
    def buscar_contas(self, item_id):
        """Buscar contas de um Item"""
        response = requests.get(
            f'{BASE_URL}/accounts?itemId={item_id}',
            headers=self.headers
        )
        return response.json().get('results', [])
    
    def buscar_transacoes(self, account_id, date_from, date_to):
        """Buscar transações de uma conta"""
        todas_transacoes = []
        page = 1
        
        while True:
            params = {
                'accountId': account_id,
                'from': date_from.strftime('%Y-%m-%d'),
                'to': date_to.strftime('%Y-%m-%d'),
                'page': page,
                'pageSize': 500
            }
            
            response = requests.get(
                f'{BASE_URL}/transactions',
                headers=self.headers,
                params=params
            )
            
            data = response.json()
            results = data.get('results', [])
            
            if not results:
                break
            
            todas_transacoes.extend(results)
            
            # Verificar se tem mais páginas
            if len(results) < 500:
                break
            
            page += 1
        
        return todas_transacoes
    
    def calcular_mes_comp(self, data_transacao):
        """Calcular MesComp baseado no ciclo 19-18"""
        from datetime import datetime
        
        if isinstance(data_transacao, str):
            data = datetime.strptime(data_transacao, '%Y-%m-%d')
        else:
            data = data_transacao
        
        dia = data.day
        mes = data.month
        ano = data.year
        
        # Ciclo 19-18: transações de dia 19 a dia 18 do próximo mês
        # Se dia >= 19, pertence ao PRÓXIMO mês
        # Se dia <= 18, pertence ao mês ATUAL
        if dia >= 19:
            mes_comp_num = mes + 1
            ano_comp = ano
            if mes_comp_num == 13:
                mes_comp_num = 1
                ano_comp += 1
        else:
            mes_comp_num = mes
            ano_comp = ano
        
        meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        
        return f"{meses[mes_comp_num - 1]} {ano_comp}"
    
    def processar_transacao(self, trans, account_info):
        """Processar uma transação e preparar para inserção"""
        # Dados básicos
        provider_id = trans['id']
        account_id = trans['accountId']
        data = trans['date'][:10]  # YYYY-MM-DD
        descricao = trans['description']
        
        # Valor (usar amountInAccountCurrency se disponível, senão amount)
        valor_original = trans['amount']
        valor = trans.get('amountInAccountCurrency') or valor_original
        
        # Moeda
        moeda_original = trans.get('currencyCode', 'BRL')
        valor_moeda_original = valor_original if moeda_original != 'BRL' else None
        
        # Adicionar info de moeda na descrição se não for BRL
        if moeda_original != 'BRL':
            descricao = f"{descricao} ({moeda_original} {abs(valor_original):.2f})"
        
        # Categoria do banco
        categoria_banco = trans.get('category')
        
        # Metadata de cartão (pode ser None para PIX)
        card_metadata = trans.get('creditCardMetadata') or {}
        cartao_final = card_metadata.get('cardNumber', '').replace('*', '')[-4:] if card_metadata.get('cardNumber') else None
        
        # Parcelas
        parcela_numero = card_metadata.get('installmentNumber')
        parcela_total = card_metadata.get('totalInstallments')
        data_compra = card_metadata.get('purchaseDate')
        
        # Origem banco (do account)
        origem_banco = account_info['name'].split()[0] if account_info['name'] else 'Desconhecido'
        
        # Fonte (mapear cartão para fonte baseado em origem_banco)
        # origem_banco: LATAM = Visa, PERSON = Master, itau = PIX
        if cartao_final:
            if origem_banco == 'LATAM':
                fonte_enum = get_card_source(cartao_final, 'Latam')
            elif origem_banco == 'PERSON':
                fonte_enum = get_card_source(cartao_final, 'Itau')
            else:
                fonte_enum = TransactionSource.PIX
        else:
            fonte_enum = TransactionSource.PIX
        
        fonte = fonte_enum.value if isinstance(fonte_enum, TransactionSource) else str(fonte_enum)
        
        # Tipo de transação e conta
        tipo_transacao = trans.get('type', 'DEBIT')
        tipo_conta = account_info['type']
        
        # MesComp
        mes_comp = self.calcular_mes_comp(data)
        
        # Categorização inteligente - criar objeto Transaction temporário
        temp_transaction = Transaction(
            date=datetime.strptime(data, '%Y-%m-%d').date(),
            description=descricao,
            amount=valor,
            source=TransactionSource.PIX  # Temporário, será ajustado
        )
        categoria_obj = self.categorization_service.categorize_transaction(temp_transaction)
        categoria = categoria_obj.value if categoria_obj else "A definir"
        
        # Atualizar stats
        if categoria != "A definir":
            self.stats['total_categorizadas'] += 1
        else:
            self.stats['total_a_definir'] += 1
        
        self.stats['por_mes'][mes_comp] = self.stats['por_mes'].get(mes_comp, 0) + 1
        self.stats['por_fonte'][fonte] = self.stats['por_fonte'].get(fonte, 0) + 1
        self.stats['por_categoria'][categoria] = self.stats['por_categoria'].get(categoria, 0) + 1
        
        # Metadata JSON completo
        metadata_json = json.dumps(trans, ensure_ascii=False)
        
        return {
            'provider_id': provider_id,
            'account_id': account_id,
            'data': data,
            'descricao': descricao,
            'valor': valor,
            'categoria': categoria,
            'categoria_banco': categoria_banco,
            'tag': None,
            'fonte': fonte,
            'pagador': None,
            'cartao_final': cartao_final,
            'mes_comp': mes_comp,
            'tipo_transacao': tipo_transacao,
            'tipo_conta': tipo_conta,
            'origem_banco': origem_banco,
            'parcela_numero': parcela_numero,
            'parcela_total': parcela_total,
            'data_compra': data_compra,
            'moeda_original': moeda_original,
            'valor_moeda_original': valor_moeda_original,
            'origem_dado': 'openfinance',
            'metadata_json': metadata_json
        }
    
    def salvar_transacao(self, transacao):
        """Salvar transação no banco"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO transacoes_openfinance (
                    provider_id, account_id, data, descricao, valor,
                    categoria, categoria_banco, tag,
                    fonte, pagador, cartao_final,
                    mes_comp,
                    tipo_transacao, tipo_conta, origem_banco,
                    parcela_numero, parcela_total, data_compra,
                    moeda_original, valor_moeda_original,
                    origem_dado, metadata_json
                ) VALUES (
                    :provider_id, :account_id, :data, :descricao, :valor,
                    :categoria, :categoria_banco, :tag,
                    :fonte, :pagador, :cartao_final,
                    :mes_comp,
                    :tipo_transacao, :tipo_conta, :origem_banco,
                    :parcela_numero, :parcela_total, :data_compra,
                    :moeda_original, :valor_moeda_original,
                    :origem_dado, :metadata_json
                )
            """, transacao)
            
            conn.commit()
            self.stats['total_importadas'] += 1
            
        except sqlite3.IntegrityError:
            # Duplicata (provider_id já existe)
            self.stats['total_duplicadas'] += 1
        
        finally:
            conn.close()
    
    def sincronizar_item(self, item_id, nome_item):
        """Sincronizar todas as contas de um Item"""
        print(f"\n🏦 Sincronizando {nome_item}...")
        
        # Buscar contas
        contas = self.buscar_contas(item_id)
        print(f"   Encontradas {len(contas)} contas")
        
        # Período: N meses retroativos
        date_to = datetime.now()
        date_from = date_to - timedelta(days=self.meses_retroativos * 30)
        
        print(f"   Período: {date_from.strftime('%d/%m/%Y')} a {date_to.strftime('%d/%m/%Y')}")
        print(f"   (Aprox. {self.meses_retroativos} meses retroativos)")

        
        for conta in contas:
            account_id = conta['id']
            account_name = conta['name']
            
            print(f"\n   📇 Conta: {account_name}")
            
            # Buscar transações
            transacoes = self.buscar_transacoes(account_id, date_from, date_to)
            print(f"      {len(transacoes)} transações encontradas")
            
            # Processar e salvar cada transação
            for trans in transacoes:
                transacao_processada = self.processar_transacao(trans, conta)
                self.salvar_transacao(transacao_processada)
            
            print(f"      ✅ Processadas")
    
    def gerar_relatorio(self):
        """Gerar relatório da sincronização"""
        print("\n" + "="*70)
        print("📊 RELATÓRIO DE SINCRONIZAÇÃO")
        print("="*70)
        
        print(f"\n✅ Total importadas: {self.stats['total_importadas']}")
        print(f"⚠️  Total duplicadas (ignoradas): {self.stats['total_duplicadas']}")
        
        if self.stats['total_importadas'] > 0:
            print(f"🎯 Categorizadas automaticamente: {self.stats['total_categorizadas']} ({self.stats['total_categorizadas']/self.stats['total_importadas']*100:.1f}%)")
            print(f"❓ A definir: {self.stats['total_a_definir']} ({self.stats['total_a_definir']/self.stats['total_importadas']*100:.1f}%)")
            
            print("\n📅 Por Mês:")
            for mes in sorted(self.stats['por_mes'].keys()):
                print(f"   {mes}: {self.stats['por_mes'][mes]}")
            
            print("\n💳 Por Fonte:")
            for fonte in sorted(self.stats['por_fonte'].items(), key=lambda x: x[1], reverse=True):
                print(f"   {fonte[0]}: {fonte[1]}")
            
            print("\n🏷️  Top 10 Categorias:")
            top_categorias = sorted(self.stats['por_categoria'].items(), key=lambda x: x[1], reverse=True)[:10]
            for cat, count in top_categorias:
                print(f"   {cat}: {count}")
        else:
            print("\nℹ️  Nenhuma transação nova foi importada (todas já existiam no banco)")
        
        print("\n" + "="*70)
    
    def executar(self, meses_retroativos=None):
        """Executar sincronização completa"""
        print("🚀 SINCRONIZAÇÃO OPEN FINANCE")
        print("="*70)
        
        # Definir período
        if meses_retroativos is None:
            try:
                meses_input = input("\n📅 Quantos meses retroativos buscar? (padrão: 1): ").strip()
                self.meses_retroativos = int(meses_input) if meses_input else 1
            except ValueError:
                print("⚠️  Valor inválido, usando padrão de 1 mês")
                self.meses_retroativos = 1
        else:
            self.meses_retroativos = meses_retroativos
        
        print(f"🔍 Buscando transações dos últimos {self.meses_retroativos} meses...\n")
        
        # 1. Autenticar
        self.autenticar()
        
        # 2. Criar tabela
        self.criar_tabela()
        
        # 3. Sincronizar Itaú
        self.sincronizar_item(ITAU_ITEM_ID, "Itaú")
        
        # 4. Sincronizar Mercado Pago
        self.sincronizar_item(MERCADOPAGO_ITEM_ID, "Mercado Pago")
        
        # 5. Relatório
        self.gerar_relatorio()
        
        print("\n✅ Sincronização concluída com sucesso!")
        print(f"💾 Dados salvos em: {DB_PATH}")

if __name__ == '__main__':
    sync = OpenFinanceSync()
    sync.executar()
