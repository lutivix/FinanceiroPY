"""
Dashboard Interativo Open Finance com Dash
Filtros funcionando em tempo real!
"""

import sqlite3
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc

# Caminhos
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / 'dados' / 'db' / 'financeiro.db'

# Orçamento Ideal (mensal) - Atualizado conforme Controle_pessoal.xlsm
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
    'Estetica': 850.00,
    'Combustível': 650.00,
    'Combustivel': 650.00,
    'Betina': 650.00,
    'Farmácia': 600.00,
    'Farmacia': 600.00,
    'Lazer': 500.00,
    'Stream': 500.00,
    'Carro': 400.00,
    'Seguro': 350.00,
    'Saúde': 350.00,
    'Saude': 350.00,
    'Hobby': 300.00,
    'Padaria': 300.00,
    'Feira': 200.00,
    'Transporte': 140.00,
    'Vestuário': 100.00,
    'Vestuario': 100.00,
    'Eventos': 100.00,
    'Cartão': 80.00,
    'Cartao': 80.00
}

# Orçamento Ideal por Fonte (mensal) - Conforme planilha de controle
ORCAMENTO_IDEAL_FONTE = {
    'PIX': 8900.00,
    'Visa Bia': 4100.00,
    'Master Físico': 3850.00,
    'Visa Recorrente': 3114.00,
    'Visa Físico': 2050.00,
    'Master Recorrente': 1886.00,
    'Visa Mae': 1390.00,
    'Visa Virtual': 880.00,
    'Master Virtual': 500.00
    # Total: 26.670,00 (mesmo total do ORCAMENTO_IDEAL por categoria)
}

# Carregar dados do banco
def carregar_dados():
    """Carrega dados do banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    query = """
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
    WHERE categoria NOT IN ('INVESTIMENTOS', 'SALÁRIO', 'A definir')
    ORDER BY data
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Processar dados
    df['data'] = pd.to_datetime(df['data'])
    df['valor_normalizado'] = df['valor'].abs()
    df = df[df['tipo_transacao'] == 'DEBIT'].copy()
    
    return df

# Carregar dados inicial
df_global = carregar_dados()

# Inicializar app Dash com tema Bootstrap
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Dashboard Financeiro Open Finance"

# Layout do Dashboard
app.layout = dbc.Container([
    # Cabeçalho
    dbc.Row([
        dbc.Col([
            html.H1("💰 Dashboard Financeiro Open Finance", 
                   className="text-center text-primary mb-4 mt-4"),
            html.Hr()
        ])
    ]),
    
    # Filtros
    dbc.Row([
        dbc.Col([
            html.Label("📅 Filtrar por Mês:", className="fw-bold"),
            dcc.Dropdown(
                id='filtro-mes',
                options=[{'label': 'Todos os Meses', 'value': 'TODOS'}] + 
                        [{'label': mes, 'value': mes} for mes in sorted(df_global['mes_comp'].unique())],
                value='TODOS',
                clearable=False,
                className="mb-3"
            )
        ], width=4),
        
        dbc.Col([
            html.Label("🏷️ Filtrar por Categoria:", className="fw-bold"),
            dcc.Dropdown(
                id='filtro-categoria',
                options=[{'label': 'Todas Categorias', 'value': 'TODOS'}] + 
                        [{'label': cat, 'value': cat} for cat in sorted(df_global['categoria'].unique())],
                value='TODOS',
                clearable=False,
                className="mb-3"
            )
        ], width=4),
        
        dbc.Col([
            html.Label("💳 Filtrar por Fonte:", className="fw-bold"),
            dcc.Dropdown(
                id='filtro-fonte',
                options=[{'label': 'Todas Fontes', 'value': 'TODOS'}] + 
                        [{'label': fonte, 'value': fonte} for fonte in sorted(df_global['fonte'].unique())],
                value='TODOS',
                clearable=False,
                className="mb-3"
            )
        ], width=4),
    ], className="mb-4 p-3 bg-light rounded"),
    
    # Cards de resumo
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("💰 Total Geral", className="text-center"),
                    html.H3(id="card-total", className="text-center text-primary")
                ])
            ])
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("📅 Média Mensal", className="text-center"),
                    html.H3(id="card-media", className="text-center text-success")
                ])
            ])
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("📊 Transações", className="text-center"),
                    html.H3(id="card-transacoes", className="text-center text-info")
                ])
            ])
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("📆 Meses", className="text-center"),
                    html.H3(id="card-meses", className="text-center text-warning")
                ])
            ])
        ], width=3),
    ], className="mb-4"),
    
    # Gráficos
    # Linha 1: Real vs Ideal (70%) + Evolução Mensal (30%)
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='grafico-real-ideal')
        ], width=8),
        dbc.Col([
            dcc.Graph(id='grafico-evolucao')
        ], width=4),
    ], className="mb-4"),
    
    # Linha 2: Duas pizzas (Fontes e Categorias)
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='grafico-fontes')
        ], width=6),
        dbc.Col([
            dcc.Graph(id='grafico-categorias')
        ], width=6),
    ], className="mb-4"),
    
    # Linha 3: Gráficos temporais (só aparecem quando vendo todos os meses)
    html.Div(id='graficos-temporais', children=[
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='grafico-distribuicao')
            ], width=6),
            dbc.Col([
                dcc.Graph(id='grafico-acumulado')
            ], width=6),
        ], className="mb-4")
    ]),
    
    # Rodapé
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P("Dashboard gerado automaticamente | Dados: Open Finance", 
                  className="text-center text-muted")
        ])
    ])
], fluid=True)


# Callback para atualizar todos os gráficos
@callback(
    [Output('card-total', 'children'),
     Output('card-media', 'children'),
     Output('card-transacoes', 'children'),
     Output('card-meses', 'children'),
     Output('grafico-evolucao', 'figure'),
     Output('grafico-real-ideal', 'figure'),
     Output('grafico-fontes', 'figure'),
     Output('grafico-categorias', 'figure'),
     Output('grafico-distribuicao', 'figure'),
     Output('grafico-acumulado', 'figure'),
     Output('graficos-temporais', 'style')],  # Controlar visibilidade
    [Input('filtro-mes', 'value'),
     Input('filtro-categoria', 'value'),
     Input('filtro-fonte', 'value')]
)
def atualizar_dashboard(mes_selecionado, categoria_selecionada, fonte_selecionada):
    """Atualiza todos os componentes do dashboard baseado nos filtros"""
    
    # ===== CARDS: SEMPRE COM BASE NO TOTAL (IGNORAR FILTROS) =====
    total_geral_global = df_global['valor_normalizado'].sum()
    num_meses_global = len(df_global['mes_comp'].unique())
    media_mensal_global = total_geral_global / num_meses_global if num_meses_global > 0 else 0
    num_transacoes_global = len(df_global)
    
    card_total = f"R$ {total_geral_global:,.2f}"
    card_media = f"R$ {media_mensal_global:,.2f}"
    card_transacoes = f"{num_transacoes_global:,}"
    card_meses = str(num_meses_global)
    
    # ===== APLICAR FILTROS PARA OS GRÁFICOS =====
    df = df_global.copy()
    
    # Verificar se está filtrando por um único mês
    mostrar_graficos_temporais = (mes_selecionado == 'TODOS')
    
    if mes_selecionado != 'TODOS':
        df = df[df['mes_comp'] == mes_selecionado]
    
    if categoria_selecionada != 'TODOS':
        df = df[df['categoria'] == categoria_selecionada]
    
    if fonte_selecionada != 'TODOS':
        df = df[df['fonte'] == fonte_selecionada]
    
    # Calcular métricas para os gráficos (com filtro aplicado)
    num_meses = len(df['mes_comp'].unique()) if len(df) > 0 else 1
    
    # Lista de todos os meses (necessária para vários gráficos)
    todos_meses = ['Janeiro 2025', 'Fevereiro 2025', 'Março 2025', 'Abril 2025', 
                   'Maio 2025', 'Junho 2025', 'Julho 2025', 'Agosto 2025',
                   'Setembro 2025', 'Outubro 2025', 'Novembro 2025', 'Dezembro 2025']
    
    # Gráfico 1: Evolução Mensal OU Real vs Ideal por Fonte (depende do filtro)
    if mostrar_graficos_temporais:
        # Mostrar Evolução Mensal (quando vendo todos os meses)
        gastos_por_mes = df.groupby('mes_comp')['valor_normalizado'].sum().sort_index()
        
        # Garantir 12 meses
        gastos_12meses = pd.Series(index=todos_meses, dtype=float)
        for mes in todos_meses:
            gastos_12meses[mes] = gastos_por_mes.get(mes, 0)
        
        media = gastos_12meses.mean()
        
        fig_evolucao = go.Figure()
        fig_evolucao.add_trace(go.Bar(
            x=gastos_12meses.index,
            y=gastos_12meses.values,
            name='Gastos',
            marker_color='rgb(55, 83, 109)',
            text=[f'R$ {v:,.0f}' for v in gastos_12meses.values],
            textposition='outside'
        ))
        fig_evolucao.add_trace(go.Scatter(
            x=gastos_12meses.index,
            y=[media] * 12,
            mode='lines',
            name=f'Média: R$ {media:,.2f}',
            line=dict(color='red', dash='dash')
        ))
        fig_evolucao.update_layout(
            title='📊 Evolução Mensal',
            xaxis_title='Mês',
            yaxis_title='Valor (R$)',
            height=500,
            hovermode='x unified',
            showlegend=True
        )
    else:
        # Mostrar Real vs Ideal por Fonte (quando filtrando um mês)
        gastos_por_fonte = df.groupby('fonte')['valor_normalizado'].sum().sort_values(ascending=False)
        
        # Calcular ideal por fonte usando orçamento mapeado
        ideal_por_fonte = []
        diferenca_por_fonte = []
        diferenca_colors_fonte = []
        
        for i, fonte in enumerate(gastos_por_fonte.index):
            # Buscar ideal mapeado ou usar 0 se fonte não mapeada
            ideal_valor = ORCAMENTO_IDEAL_FONTE.get(fonte, 0) * num_meses
            ideal_por_fonte.append(ideal_valor)
            
            # Calcular diferença
            real_valor = gastos_por_fonte.values[i]
            diferenca = real_valor - ideal_valor
            diferenca_por_fonte.append(abs(diferenca))
            
            # Cor: Verde se economizou, Vermelho se excedeu
            if diferenca > 0:
                diferenca_colors_fonte.append('rgb(220, 53, 69)')  # Vermelho (excedeu)
            else:
                diferenca_colors_fonte.append('rgb(40, 167, 69)')  # Verde (economizou)
        
        fig_evolucao = go.Figure()
        
        # Barra 1: Real (Laranja)
        fig_evolucao.add_trace(go.Bar(
            x=gastos_por_fonte.index,
            y=gastos_por_fonte.values,
            name='Real',
            marker_color='rgb(255, 140, 0)',
            text=[f'R$ {v:,.0f}' for v in gastos_por_fonte.values],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Real: R$ %{y:,.2f}<extra></extra>'
        ))
        
        # Barra 2: Ideal (Azul)
        fig_evolucao.add_trace(go.Bar(
            x=gastos_por_fonte.index,
            y=ideal_por_fonte,
            name='Ideal',
            marker_color='rgb(0, 123, 255)',
            text=[f'R$ {v:,.0f}' for v in ideal_por_fonte],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Ideal: R$ %{y:,.2f}<extra></extra>'
        ))
        
        # Barra 3: Diferença (Verde/Vermelho)
        hover_texts_fonte = []
        for i, fonte in enumerate(gastos_por_fonte.index):
            real = gastos_por_fonte.values[i]
            ideal = ideal_por_fonte[i]
            dif = real - ideal
            status = "Excedeu" if dif > 0 else "Economizou"
            hover_texts_fonte.append(f'<b>{fonte}</b><br>{status}: R$ {abs(dif):,.2f}')
        
        fig_evolucao.add_trace(go.Bar(
            x=gastos_por_fonte.index,
            y=diferenca_por_fonte,
            name='Diferença',
            marker_color=diferenca_colors_fonte,
            text=[f'{"+" if gastos_por_fonte.values[i] > ideal_por_fonte[i] else "-"}R$ {v:,.0f}' 
                  for i, v in enumerate(diferenca_por_fonte)],
            textposition='outside',
            hovertemplate='%{customdata}<extra></extra>',
            customdata=hover_texts_fonte
        ))
        
        fig_evolucao.update_layout(
            title=f'💳 Real vs Ideal por Fonte - {mes_selecionado}',
            xaxis_title='Fonte',
            yaxis_title='Valor (R$)',
            height=500,
            barmode='group',
            hovermode='x unified'
        )
    
    # Gráfico 2: Real vs Ideal (MAIOR E PRINCIPAL - VERTICAL)
    gastos_por_categoria = df.groupby('categoria')['valor_normalizado'].sum().sort_values(ascending=False)
    
    ideal_values = []
    diferenca_values = []
    diferenca_colors = []
    
    for cat in gastos_por_categoria.index:
        orcamento_cat = ORCAMENTO_IDEAL.get(cat, 0)
        ideal_total = orcamento_cat * num_meses
        ideal_values.append(ideal_total)
        
        # Calcular diferença (Real - Ideal)
        real_valor = gastos_por_categoria[cat]
        diferenca = real_valor - ideal_total
        diferenca_values.append(abs(diferenca))
        
        # Cor: Verde se economizou, Vermelho se excedeu
        if diferenca > 0:
            diferenca_colors.append('rgb(220, 53, 69)')  # Vermelho (excedeu)
        else:
            diferenca_colors.append('rgb(40, 167, 69)')  # Verde (economizou)
    
    fig_real_ideal = go.Figure()
    
    # Barra 1: Real (Laranja)
    fig_real_ideal.add_trace(go.Bar(
        x=gastos_por_categoria.index,
        y=gastos_por_categoria.values,
        name='Real',
        marker_color='rgb(255, 140, 0)',  # Laranja
        text=[f'R$ {v:,.0f}' for v in gastos_por_categoria.values],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Real: R$ %{y:,.2f}<extra></extra>'
    ))
    
    # Barra 2: Ideal (Azul)
    fig_real_ideal.add_trace(go.Bar(
        x=gastos_por_categoria.index,
        y=ideal_values,
        name='Ideal',
        marker_color='rgb(0, 123, 255)',  # Azul
        text=[f'R$ {v:,.0f}' for v in ideal_values],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Ideal: R$ %{y:,.2f}<extra></extra>'
    ))
    
    # Barra 3: Diferença (Verde/Vermelho)
    hover_texts = []
    for i, cat in enumerate(gastos_por_categoria.index):
        real = gastos_por_categoria.values[i]
        ideal = ideal_values[i]
        dif = real - ideal
        status = "Excedeu" if dif > 0 else "Economizou"
        hover_texts.append(f'<b>{cat}</b><br>{status}: R$ {abs(dif):,.2f}')
    
    fig_real_ideal.add_trace(go.Bar(
        x=gastos_por_categoria.index,
        y=diferenca_values,
        name='Diferença',
        marker_color=diferenca_colors,
        text=[f'{"+" if gastos_por_categoria.values[i] > ideal_values[i] else "-"}R$ {v:,.0f}' 
              for i, v in enumerate(diferenca_values)],
        textposition='outside',
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_texts
    ))
    fig_real_ideal.update_layout(
        title=f'💰 Real vs Ideal - {num_meses} meses',
        xaxis_title='Categoria',
        yaxis_title='Valor (R$)',
        height=500,
        barmode='group',
        hovermode='x unified',
        xaxis_tickangle=-45
    )
    
    # Gráfico 3: Gastos por Fonte (PIZZA)
    gastos_por_fonte = df.groupby('fonte')['valor_normalizado'].sum().sort_values(ascending=False)
    
    fig_fontes = go.Figure(data=[go.Pie(
        labels=gastos_por_fonte.index,
        values=gastos_por_fonte.values,
        hole=0.3,
        textinfo='label+percent',
        textposition='outside'
    )])
    fig_fontes.update_layout(
        title='💳 Gastos por Fonte',
        height=450
    )
    
    # Gráfico 4: Categorias (PIZZA TAMBÉM)
    gastos_todas_cat = df.groupby('categoria')['valor_normalizado'].sum().sort_values(ascending=False)
    
    fig_categorias = go.Figure(data=[go.Pie(
        labels=gastos_todas_cat.index,
        values=gastos_todas_cat.values,
        hole=0.3,
        textinfo='label+percent',
        textposition='outside'
    )])
    fig_categorias.update_layout(
        title='🏷️ Gastos por Categoria',
        height=450
    )
    
    # Gráfico 5: Distribuição de Transações
    transacoes_por_mes = df.groupby('mes_comp').size()
    transacoes_12meses = pd.Series(index=todos_meses, dtype=int)
    for mes in todos_meses:
        transacoes_12meses[mes] = transacoes_por_mes.get(mes, 0)
    
    fig_distribuicao = go.Figure(data=[go.Scatter(
        x=transacoes_12meses.index,
        y=transacoes_12meses.values,
        mode='lines+markers',
        marker=dict(size=10),
        line=dict(width=3)
    )])
    fig_distribuicao.update_layout(
        title='📅 Distribuição de Transações por Mês',
        xaxis_title='Mês',
        yaxis_title='Número de Transações',
        height=400
    )
    
    # Gráfico 6: Acumulado Anual
    df_sorted = df.sort_values('data')
    df_sorted['acumulado'] = df_sorted['valor_normalizado'].cumsum()
    
    fig_acumulado = go.Figure(data=[go.Scatter(
        x=df_sorted['data'],
        y=df_sorted['acumulado'],
        mode='lines',
        fill='tozeroy',
        line=dict(color='rgb(111, 231, 219)')
    )])
    fig_acumulado.update_layout(
        title='📈 Acumulado Anual',
        xaxis_title='Data',
        yaxis_title='Valor Acumulado (R$)',
        height=400
    )
    
    # Controlar visibilidade dos gráficos temporais
    estilo_graficos_temporais = {'display': 'block'} if mostrar_graficos_temporais else {'display': 'none'}
    
    return (card_total, card_media, card_transacoes, card_meses,
            fig_evolucao, fig_real_ideal, fig_fontes, fig_categorias,
            fig_distribuicao, fig_acumulado, estilo_graficos_temporais)


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 DASHBOARD INTERATIVO OPEN FINANCE")
    print("="*70)
    print(f"📊 {len(df_global):,} transações carregadas")
    print(f"💰 Total: R$ {df_global['valor_normalizado'].sum():,.2f}")
    print("="*70)
    print("\n🌐 Acesso local: http://localhost:8050")
    print("🌐 Acesso rede: http://<IP_DESTA_MAQUINA>:8050")
    print("⌨️  Pressione CTRL+C para encerrar\n")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=8050)
