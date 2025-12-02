"""
Dashboard Automático Open Finance - Fase 2
Gera dashboard HTML interativo com análise Real vs Ideal
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import sqlite3
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import json

# Configurações
DB_PATH = Path(__file__).parent / '../../dados/db/financeiro.db'
OUTPUT_HTML = Path(__file__).parent / '../../dados/planilhas/dashboard_openfinance.html'

# Orçamento ideal por categoria (PROJEÇÃO IDEAL - Controle_pessoal.xlsm)
ORCAMENTO_IDEAL = {
    'Mercado': 4200.00,
    'Casa': 3400.00,
    'LF': 2400.00,
    'Nita': 2100.00,
    'Utilidades': 1700.00,
    'Esporte': 1700.00,
    'Faculdade': 1500.00,
    'Pet': 1200.00,
    'Compras': 1200.00,
    'Datas': 1200.00,
    'Estética': 850.00,
    'Estetica': 850.00,  # Variação de escrita
    'Combustível': 650.00,
    'Combustivel': 650.00,  # Sem acento
    'Betina': 650.00,
    'Farmácia': 600.00,
    'Farmacia': 600.00,  # Sem acento
    'Lazer': 560.00,
    'Stream': 500.00,
    'Carro': 400.00,
    'Seguro': 350.00,
    'Saúde': 350.00,
    'Saude': 350.00,  # Sem acento
    'Hobby': 300.00,
    'Padaria': 300.00,
    'Feira': 200.00,
    'Transporte': 140.00,
    'Vestuário': 100.00,
    'Vestuario': 100.00,  # Sem acento
    'Eventos': 100.00,
    'Cartão': 80.00,
    'Cartao': 80.00,  # Sem acento
    'Roupa': 0.00,  # Incluído em Vestuário
}

class DashboardGenerator:
    def __init__(self, filtro_mes=None, filtro_categoria=None, filtro_fonte=None):
        self.conn = sqlite3.connect(DB_PATH)
        self.df = None
        self.fig = None
        self.filtro_mes = filtro_mes
        self.filtro_categoria = filtro_categoria
        self.filtro_fonte = filtro_fonte
        
    def carregar_dados(self):
        """Carregar dados da tabela transacoes_openfinance"""
        print("📊 Carregando dados do banco...")
        
        # Base query
        where_clauses = ["categoria NOT IN ('INVESTIMENTOS', 'SALÁRIO', 'A definir')"]
        
        # Adicionar filtros se fornecidos
        if self.filtro_mes:
            where_clauses.append(f"mes_comp = '{self.filtro_mes}'")
        if self.filtro_categoria:
            where_clauses.append(f"categoria = '{self.filtro_categoria}'")
        if self.filtro_fonte:
            where_clauses.append(f"fonte = '{self.filtro_fonte}'")
        
        where_sql = " AND ".join(where_clauses)
        
        query = f"""
        SELECT 
            data,
            descricao,
            valor,
            categoria,
            categoria_banco,
            fonte,
            mes_comp,
            parcela_numero,
            parcela_total,
            cartao_final,
            origem_banco,
            tipo_transacao
        FROM transacoes_openfinance
        WHERE {where_sql}
        ORDER BY data
        """
        
        self.df = pd.read_sql_query(query, self.conn)
        self.df['data'] = pd.to_datetime(self.df['data'])
        
        # Normalizar valores: sempre trabalhar com valores absolutos (positivos)
        # tipo_transacao = 'DEBIT' já filtra apenas débitos
        self.df['valor_normalizado'] = self.df['valor'].abs()
        
        # Filtrar apenas débitos usando tipo_transacao
        self.df = self.df[self.df['tipo_transacao'] == 'DEBIT'].copy()
        
        print(f"✅ {len(self.df)} transações carregadas (apenas débitos)")
        print(f"📅 Período: {self.df['data'].min().strftime('%d/%m/%Y')} a {self.df['data'].max().strftime('%d/%m/%Y')}")
        
        return self.df
    
    def calcular_metricas(self):
        """Calcular métricas principais"""
        # Já filtramos apenas débitos, usar valor_normalizado (sempre positivo)
        gastos = self.df.copy()
        
        # Total por mês
        gastos_por_mes = gastos.groupby('mes_comp')['valor_normalizado'].sum().sort_index()
        
        # Total por categoria
        gastos_por_categoria = gastos.groupby('categoria')['valor_normalizado'].sum().sort_values(ascending=False)
        
        # Total por fonte
        gastos_por_fonte = gastos.groupby('fonte')['valor_normalizado'].sum().sort_values(ascending=False)
        
        # Média mensal
        media_mensal = gastos_por_mes.mean()
        
        # Total geral
        total_geral = gastos['valor_normalizado'].sum()
        
        return {
            'gastos_por_mes': gastos_por_mes,
            'gastos_por_categoria': gastos_por_categoria,
            'gastos_por_fonte': gastos_por_fonte,
            'media_mensal': media_mensal,
            'total_geral': total_geral,
            'gastos_df': gastos
        }
    
    def criar_dashboard(self):
        """Criar dashboard completo com múltiplos gráficos"""
        print("📈 Gerando dashboard...")
        
        metricas = self.calcular_metricas()
        
        # Criar subplots (3 linhas x 2 colunas)
        self.fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                '📊 Evolução Mensal de Gastos (12 meses)',
                '💰 Real vs Ideal - Todas as Categorias',
                '💳 Gastos por Fonte',
                '🏷️ Todas as Categorias',
                '📅 Distribuição de Transações por Mês',
                '📈 Acumulado Anual'
            ),
            specs=[
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "pie"}, {"type": "bar"}],
                [{"type": "scatter"}, {"type": "scatter"}]
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.15
        )
        
        # 1. Evolução Mensal (forçar 12 meses)
        self._add_evolucao_mensal(metricas['gastos_por_mes'])
        
        # 2. Real vs Ideal (TODAS as categorias)
        self._add_real_vs_ideal(metricas['gastos_por_categoria'])
        
        # 3. Gastos por Fonte (TODAS as fontes incluindo PIX)
        self._add_gastos_por_fonte(metricas['gastos_por_fonte'])
        
        # 4. Todas Categorias (horizontal, mais espaço)
        self._add_todas_categorias(metricas['gastos_por_categoria'])
        
        # 5. Distribuição de Transações
        self._add_distribuicao_transacoes(metricas['gastos_df'])
        
        # 6. Acumulado Anual
        self._add_acumulado_anual(metricas['gastos_df'])
        
        # Calcular total de meses para ajustar orçamento ideal
        num_meses = len(metricas['gastos_por_mes'])
        
        # Preparar título com filtros ativos
        filtros_ativos = []
        if self.filtro_mes:
            filtros_ativos.append(f"Mês: {self.filtro_mes}")
        if self.filtro_categoria:
            filtros_ativos.append(f"Categoria: {self.filtro_categoria}")
        if self.filtro_fonte:
            filtros_ativos.append(f"Fonte: {self.filtro_fonte}")
        
        filtro_texto = f" | <b>Filtros:</b> {' | '.join(filtros_ativos)}" if filtros_ativos else ""
        
        # Layout geral
        self.fig.update_layout(
            title={
                'text': f"<b>Dashboard Financeiro Open Finance</b><br><sub>Período: {self.df['data'].min().strftime('%d/%m/%Y')} a {self.df['data'].max().strftime('%d/%m/%Y')} | Total: R$ {metricas['total_geral']:,.2f} | {num_meses} meses{filtro_texto}</sub>",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            showlegend=True,
            height=1600,
            template='plotly_white',
            font=dict(family="Arial", size=11)
        )
        
        # Ajustar eixos para melhor visualização
        self.fig.update_xaxes(tickangle=-45, row=2, col=2)  # Todas categorias
        
        return self.fig
    
    def _add_evolucao_mensal(self, gastos_por_mes):
        """Gráfico de evolução mensal - FORÇAR 12 MESES"""
        # Garantir 12 meses (preencher meses faltantes com 0)
        meses_ordem = ['Janeiro 2025', 'Fevereiro 2025', 'Março 2025', 'Abril 2025', 
                       'Maio 2025', 'Junho 2025', 'Julho 2025', 'Agosto 2025',
                       'Setembro 2025', 'Outubro 2025', 'Novembro 2025', 'Dezembro 2025']
        
        # Criar série completa com 12 meses
        gastos_12meses = pd.Series(0.0, index=meses_ordem)
        for mes in gastos_por_mes.index:
            if mes in meses_ordem:
                gastos_12meses[mes] = gastos_por_mes[mes]
        
        self.fig.add_trace(
            go.Bar(
                x=gastos_12meses.index,
                y=gastos_12meses.values,
                name='Gastos Mensais',
                marker_color='rgb(55, 83, 109)',
                text=[f'R$ {v:,.2f}' if v > 0 else '' for v in gastos_12meses.values],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Linha de média (apenas meses com dados)
        media = gastos_por_mes.mean()
        self.fig.add_trace(
            go.Scatter(
                x=gastos_12meses.index,
                y=[media] * 12,
                mode='lines',
                name=f'Média: R$ {media:,.2f}',
                line=dict(color='red', dash='dash'),
                hovertemplate='Média: R$ %{y:,.2f}<extra></extra>'
            ),
            row=1, col=1
        )
    
    def _add_real_vs_ideal(self, gastos_por_categoria):
        """Gráfico Real vs Ideal - TODAS AS CATEGORIAS"""
        # Ordenar por valor real (maior primeiro)
        categorias_ordenadas = gastos_por_categoria.sort_values(ascending=True)  # Menor no topo para gráfico horizontal
        
        # Real
        self.fig.add_trace(
            go.Bar(
                y=categorias_ordenadas.index,
                x=categorias_ordenadas.values,
                name='Real',
                marker_color='rgb(55, 83, 109)',
                orientation='h',
                text=[f'R$ {v:,.0f}' for v in categorias_ordenadas.values],
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Real: R$ %{x:,.2f}<extra></extra>'
            ),
            row=1, col=2
        )
        
        # Ideal (orçamento) - multiplicar pelo número de meses
        num_meses = len(self.df['mes_comp'].unique())
        ideal_values = [ORCAMENTO_IDEAL.get(cat, 0) * num_meses for cat in categorias_ordenadas.index]
        self.fig.add_trace(
            go.Bar(
                y=categorias_ordenadas.index,
                x=ideal_values,
                name=f'Ideal ({num_meses} meses)',
                marker_color='rgba(55, 200, 83, 0.5)',
                orientation='h',
                text=[f'R$ {v:,.0f}' for v in ideal_values],
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Ideal: R$ %{x:,.2f}<extra></extra>'
            ),
            row=1, col=2
        )
    
    def _add_gastos_por_fonte(self, gastos_por_fonte):
        """Gráfico de pizza - Gastos por Fonte (TODAS)"""
        self.fig.add_trace(
            go.Pie(
                labels=gastos_por_fonte.index,
                values=gastos_por_fonte.values,
                name='Fonte',
                hole=0.3,
                hovertemplate='<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>'
            ),
            row=2, col=1
        )
    
    def _add_todas_categorias(self, gastos_por_categoria):
        """Todas as categorias (horizontal com mais espaço)"""
        categorias_ordenadas = gastos_por_categoria.sort_values(ascending=True)
        
        self.fig.add_trace(
            go.Bar(
                y=categorias_ordenadas.index,
                x=categorias_ordenadas.values,
                orientation='h',
                name='Gastos',
                marker_color='rgb(26, 118, 255)',
                text=[f'R$ {v:,.2f}' for v in categorias_ordenadas.values],
                textposition='auto',  # Mudado para 'auto' para não cortar
                textfont=dict(size=9),  # Fonte menor
                hovertemplate='<b>%{y}</b><br>R$ %{x:,.2f}<extra></extra>'
            ),
            row=2, col=2
        )
    
    def _add_distribuicao_transacoes(self, gastos_df):
        """Distribuição de número de transações por mês"""
        trans_por_mes = gastos_df.groupby('mes_comp').size().sort_index()
        
        self.fig.add_trace(
            go.Scatter(
                x=trans_por_mes.index,
                y=trans_por_mes.values,
                mode='lines+markers',
                name='Nº Transações',
                line=dict(color='rgb(255, 127, 14)', width=3),
                marker=dict(size=10),
                fill='tozeroy',
                text=[f'{v} transações' for v in trans_por_mes.values],
                hovertemplate='<b>%{x}</b><br>%{y} transações<extra></extra>'
            ),
            row=3, col=1
        )
    
    def _add_acumulado_anual(self, gastos_df):
        """Gráfico de gastos acumulados no ano"""
        gastos_df_sorted = gastos_df.sort_values('data').copy()
        gastos_df_sorted['acumulado'] = gastos_df_sorted['valor_normalizado'].cumsum()
        
        self.fig.add_trace(
            go.Scatter(
                x=gastos_df_sorted['data'],
                y=gastos_df_sorted['acumulado'],
                mode='lines',
                name='Acumulado',
                line=dict(color='rgb(200, 50, 50)', width=2),
                fill='tozeroy',
                hovertemplate='<b>%{x|%d/%m/%Y}</b><br>Acumulado: R$ %{y:,.2f}<extra></extra>'
            ),
            row=3, col=2
        )
    
    def salvar_html(self):
        """Salvar dashboard como HTML com navegação de filtros"""
        print(f"💾 Salvando dashboard em: {OUTPUT_HTML}")
        
        # Criar diretório se não existir
        OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
        
        # Obter listas de filtros disponíveis
        conn_temp = sqlite3.connect(DB_PATH)
        meses = pd.read_sql_query("SELECT DISTINCT mes_comp FROM transacoes_openfinance WHERE categoria NOT IN ('INVESTIMENTOS', 'SALÁRIO', 'A definir') ORDER BY mes_comp", conn_temp)['mes_comp'].tolist()
        categorias = pd.read_sql_query("SELECT DISTINCT categoria FROM transacoes_openfinance WHERE categoria NOT IN ('INVESTIMENTOS', 'SALÁRIO', 'A definir') ORDER BY categoria", conn_temp)['categoria'].tolist()
        fontes = pd.read_sql_query("SELECT DISTINCT fonte FROM transacoes_openfinance WHERE categoria NOT IN ('INVESTIMENTOS', 'SALÁRIO', 'A definir') ORDER BY fonte", conn_temp)['fonte'].tolist()
        conn_temp.close()
        
        # Criar HTML dos filtros com JavaScript funcional
        filtro_html = """
        <div class="filtros-container">
            <div class="filtro-info">
                <h3>🎯 Filtros Interativos</h3>
                <p>Selecione os filtros e clique em "Gerar Dashboard Filtrado"</p>
            </div>
            <div class="filtros-form">
                <div class="filtro-grupo">
                    <label>📅 Mês:</label>
                    <select id="filtro_mes">
                        <option value="">Todos os Meses</option>
        """ + ''.join([f'                <option value="{m}">{m}</option>\n' for m in meses]) + """
                    </select>
                </div>
                <div class="filtro-grupo">
                    <label>🏷️ Categoria:</label>
                    <select id="filtro_categoria">
                        <option value="">Todas Categorias</option>
        """ + ''.join([f'                <option value="{c}">{c}</option>\n' for c in categorias]) + """
                    </select>
                </div>
                <div class="filtro-grupo">
                    <label>💳 Fonte:</label>
                    <select id="filtro_fonte">
                        <option value="">Todas Fontes</option>
        """ + ''.join([f'                <option value="{f}">{f}</option>\n' for f in fontes]) + """
                    </select>
                </div>
                <button class="btn-filtrar" onclick="aplicarFiltros()">🔍 Gerar Dashboard Filtrado</button>
                <button class="btn-limpar" onclick="limparFiltros()">🔄 Limpar Filtros</button>
            </div>
        </div>
        <div style="margin-top: 180px;"></div>
        
        <script>
        function aplicarFiltros() {
            const mes = document.getElementById('filtro_mes').value;
            const categoria = document.getElementById('filtro_categoria').value;
            const fonte = document.getElementById('filtro_fonte').value;
            
            const params = [];
            if (mes) params.push(`--mes "${mes}"`);
            if (categoria) params.push(`--categoria "${categoria}"`);
            if (fonte) params.push(`--fonte "${fonte}"`);
            
            const comando = `py backend/src/gerar_dashboard.py ${params.join(' ')}`;
            
            alert(`📋 Execute este comando no terminal:\\n\\n${comando}\\n\\nIsso gerará um novo dashboard com os filtros aplicados.`);
        }
        
        function limparFiltros() {
            document.getElementById('filtro_mes').value = '';
            document.getElementById('filtro_categoria').value = '';
            document.getElementById('filtro_fonte').value = '';
        }
        </script>
        
        <style>
        .filtros-container {
            position: fixed;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            z-index: 1000;
            width: 90%;
            max-width: 1000px;
        }
        .filtro-info {
            text-align: center;
            margin-bottom: 15px;
        }
        .filtro-info h3 {
            margin: 0 0 5px 0;
            font-size: 20px;
        }
        .filtro-info p {
            margin: 0;
            font-size: 14px;
            opacity: 0.9;
        }
        .filtros-form {
            display: flex;
            gap: 15px;
            align-items: flex-end;
            justify-content: center;
            flex-wrap: wrap;
        }
        .filtro-grupo {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        .filtro-grupo label {
            font-weight: bold;
            font-size: 13px;
        }
        .filtro-grupo select {
            padding: 10px 15px;
            border-radius: 6px;
            border: none;
            font-size: 14px;
            min-width: 180px;
            background: white;
            color: #333;
        }
        .btn-filtrar, .btn-limpar {
            padding: 10px 25px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: transform 0.2s;
        }
        .btn-filtrar {
            background: #4CAF50;
            color: white;
        }
        .btn-limpar {
            background: #ff9800;
            color: white;
        }
        .btn-filtrar:hover, .btn-limpar:hover {
            transform: scale(1.05);
        }
        </style>
        """
        
        # Salvar HTML
        self.fig.write_html(
            str(OUTPUT_HTML),
            config={'displayModeBar': True, 'displaylogo': False}
        )
        
        # Ler e modificar HTML
        with open(OUTPUT_HTML, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Inserir filtros após <body>
        html_content = html_content.replace('<body>', f'<body>\n{filtro_html}')
        
        # Salvar HTML modificado
        with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Dashboard gerado com sucesso!")
        print(f"🌐 Abra no navegador: {OUTPUT_HTML}")
        
        return OUTPUT_HTML
    
    def gerar_estatisticas(self):
        """Gerar resumo estatístico em texto"""
        metricas = self.calcular_metricas()
        
        print("\n" + "="*70)
        print("📊 RESUMO ESTATÍSTICO")
        print("="*70)
        
        print(f"\n💰 Total Geral: R$ {metricas['total_geral']:,.2f}")
        print(f"📅 Média Mensal: R$ {metricas['media_mensal']:,.2f}")
        print(f"📊 Total de Transações: {len(metricas['gastos_df'])}")
        
        print("\n🏆 Top 5 Categorias:")
        for i, (cat, valor) in enumerate(metricas['gastos_por_categoria'].head(5).items(), 1):
            ideal = ORCAMENTO_IDEAL.get(cat, 0)
            diff = valor - ideal
            status = "🔴" if diff > 0 else "🟢"
            print(f"   {i}. {cat}: R$ {valor:,.2f} (Ideal: R$ {ideal:,.2f}) {status} {diff:+,.2f}")
        
        print("\n💳 Top 3 Fontes:")
        for i, (fonte, valor) in enumerate(metricas['gastos_por_fonte'].head(3).items(), 1):
            pct = (valor / metricas['total_geral']) * 100
            print(f"   {i}. {fonte}: R$ {valor:,.2f} ({pct:.1f}%)")
        
        print("\n📅 Mês com Maior Gasto:")
        mes_max = metricas['gastos_por_mes'].idxmax()
        valor_max = metricas['gastos_por_mes'].max()
        print(f"   {mes_max}: R$ {valor_max:,.2f}")
        
        print("\n📅 Mês com Menor Gasto:")
        mes_min = metricas['gastos_por_mes'].idxmin()
        valor_min = metricas['gastos_por_mes'].min()
        print(f"   {mes_min}: R$ {valor_min:,.2f}")
        
        print("\n" + "="*70)
    
    def executar(self):
        """Executar geração completa do dashboard"""
        print("🚀 GERADOR DE DASHBOARD OPEN FINANCE")
        print("="*70)
        
        try:
            # Carregar dados
            self.carregar_dados()
            
            # Gerar estatísticas
            self.gerar_estatisticas()
            
            # Criar dashboard
            self.criar_dashboard()
            
            # Salvar HTML
            output_path = self.salvar_html()
            
            print("\n✅ Dashboard gerado com sucesso!")
            
            return output_path
            
        except Exception as e:
            print(f"\n❌ Erro ao gerar dashboard: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        finally:
            self.conn.close()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerar dashboard financeiro Open Finance')
    parser.add_argument('--mes', type=str, help='Filtrar por mês específico (ex: Janeiro 2025)')
    parser.add_argument('--categoria', type=str, help='Filtrar por categoria específica (ex: Mercado)')
    parser.add_argument('--fonte', type=str, help='Filtrar por fonte específica (ex: PIX, Visa Virtual)')
    
    args = parser.parse_args()
    
    # Criar dashboard com filtros
    dashboard = DashboardGenerator(
        filtro_mes=args.mes,
        filtro_categoria=args.categoria,
        filtro_fonte=args.fonte
    )
    dashboard.executar()
