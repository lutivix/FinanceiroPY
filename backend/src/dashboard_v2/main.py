"""
Dashboard Financeiro v2.0
App principal com sidebar e navegação entre páginas
"""

import sys
from pathlib import Path
import pandas as pd

# Adicionar pasta src ao PATH para imports funcionarem
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc

# Imports locais
from dashboard_v2.config import COLORS, FONTS
from dashboard_v2.components.sidebar import create_sidebar
from dashboard_v2.assets.custom_styles import get_custom_css
from dashboard_v2.pages.dashboard import create_dashboard_page
from dashboard_v2.pages.analytics import create_analytics_page
from dashboard_v2.pages.transacoes import create_transacoes_page
from dashboard_v2.utils.database import (
    carregar_transacoes, 
    obter_meses_disponiveis, 
    calcular_estatisticas,
    obter_categorias,
    obter_fontes
)
from dashboard_v2.utils.graficos import (
    criar_grafico_evolucao,
    criar_grafico_top_categorias,
    criar_grafico_top_fontes,
    criar_grafico_real_ideal,
    criar_grafico_distribuicao_temporal,
    criar_grafico_acumulado
)

# Inicializar app
app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    ],
    suppress_callback_exceptions=True
)

app.title = "FinancePro - Dashboard v2.0"

# Injetar CSS customizado
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
''' + get_custom_css() + '''
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Layout principal
app.layout = html.Div([
    # Store para dados globais
    dcc.Store(id='store-mes-global', data='TODOS'),
    dcc.Store(id='store-dados-transacoes', data={}),
    
    # Location para navegação
    dcc.Location(id='url', refresh=False),
    
    # Estrutura: Sidebar + Conteúdo
    html.Div([
        # Sidebar fixa
        create_sidebar(),
        
        # Área de conteúdo (à direita da sidebar)
        html.Div(
            id='page-content',
            style={
                'marginLeft': '280px',  # Largura da sidebar
                'minHeight': '100vh',
                'backgroundColor': COLORS['bg_primary']
            }
        )
    ])
])

# ===== CALLBACKS =====

@callback(
    Output('store-mes-global', 'data'),
    Input('filtro-mes-global', 'value')
)
def atualizar_mes_global(mes_selecionado):
    """Atualiza o mês selecionado globalmente"""
    return mes_selecionado

@callback(
    Output('filtro-mes-global', 'options'),
    Input('url', 'pathname')
)
def atualizar_opcoes_mes(pathname):
    """Carrega opções de meses disponíveis"""
    meses = obter_meses_disponiveis()
    return [{'label': 'Todos os meses', 'value': 'TODOS'}] + \
           [{'label': mes, 'value': mes} for mes in meses]

@callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'),
     Input('store-mes-global', 'data')]
)
def display_page(pathname, mes_selecionado):
    """Renderiza a página correta baseado na URL"""
    
    # Carregar dados baseado no mês selecionado
    df = carregar_transacoes(mes_selecionado)
    stats = calcular_estatisticas(df)
    
    # Roteamento
    if pathname == '/analytics':
        return create_analytics_page()
    elif pathname == '/transacoes':
        return create_transacoes_page()
    else:  # Default: dashboard
        return create_dashboard_page(stats, df)

@callback(
    Output('filtro-categoria-transacoes', 'options'),
    Output('filtro-fonte-transacoes', 'options'),
    Output('filtro-mes-comp-transacoes', 'options'),
    Input('url', 'pathname')
)
def atualizar_filtros_transacoes(pathname):
    """Atualiza opções de filtros na página de transações"""
    if pathname == '/transacoes':
        categorias = obter_categorias()
        fontes = obter_fontes()
        meses = obter_meses_disponiveis()
        
        opcoes_cat = [{'label': 'Todas', 'value': 'TODOS'}] + \
                     [{'label': cat, 'value': cat} for cat in categorias]
        
        opcoes_fonte = [{'label': 'Todas', 'value': 'TODOS'}] + \
                       [{'label': fonte, 'value': fonte} for fonte in fontes]
        
        opcoes_mes = [{'label': 'Todos', 'value': 'TODOS'}] + \
                     [{'label': mes, 'value': mes} for mes in meses]
        
        return opcoes_cat, opcoes_fonte, opcoes_mes
    
    return [], [], []

# Callback para highlighting do item ativo na sidebar
app.clientside_callback(
    """
    function(pathname) {
        // Remove active de todos
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Adiciona active no correto
        let activeId = 'nav-dashboard';
        if (pathname === '/analytics') activeId = 'nav-analytics';
        if (pathname === '/transacoes') activeId = 'nav-transactions';
        
        const activeItem = document.getElementById(activeId);
        if (activeItem) {
            activeItem.classList.add('active');
        }
        
        return '';
    }
    """,
    Output('url', 'search'),  # Output dummy
    Input('url', 'pathname')
)

# Callbacks dos gráficos do Dashboard
@callback(
    Output('grafico-evolucao-hero', 'figure'),
    Input('store-mes-global', 'data')
)
def atualizar_grafico_evolucao(mes_selecionado):
    """Atualiza gráfico de evolução mensal"""
    return criar_grafico_evolucao(mes_selecionado)

@callback(
    Output('grafico-top-categorias', 'figure'),
    Input('store-mes-global', 'data')
)
def atualizar_grafico_categorias(mes_selecionado):
    """Atualiza gráfico de top categorias"""
    return criar_grafico_top_categorias(mes_selecionado)

@callback(
    Output('grafico-top-fontes', 'figure'),
    Input('store-mes-global', 'data')
)
def atualizar_grafico_fontes(mes_selecionado):
    """Atualiza gráfico de top fontes"""
    return criar_grafico_top_fontes(mes_selecionado)

# Callbacks dos gráficos da página Analytics
@callback(
    Output('grafico-real-ideal-analytics', 'figure'),
    Input('store-mes-global', 'data')
)
def atualizar_grafico_real_ideal(mes_selecionado):
    """Atualiza gráfico Real vs Ideal"""
    return criar_grafico_real_ideal(mes_selecionado)

@callback(
    Output('grafico-distribuicao-temporal', 'figure'),
    Input('store-mes-global', 'data')
)
def atualizar_grafico_distribuicao(mes_selecionado):
    """Atualiza gráfico de distribuição temporal"""
    return criar_grafico_distribuicao_temporal(mes_selecionado)

@callback(
    Output('grafico-acumulado', 'figure'),
    Input('store-mes-global', 'data')
)
def atualizar_grafico_acumulado(mes_selecionado):
    """Atualiza gráfico de acumulado mensal"""
    return criar_grafico_acumulado(mes_selecionado)

# Callback para tabela de transações
@callback(
    Output('tabela-transacoes-container', 'children'),
    [Input('store-mes-global', 'data'),
     Input('filtro-categoria-transacoes', 'value'),
     Input('filtro-fonte-transacoes', 'value'),
     Input('filtro-status-transacoes', 'value'),
     Input('filtro-mes-comp-transacoes', 'value'),
     Input('filtro-data-transacoes', 'start_date'),
     Input('filtro-data-transacoes', 'end_date')]
)
def atualizar_tabela_transacoes(mes_selecionado, categoria_filtro, fonte_filtro, status_filtro, 
                                mes_comp_filtro, data_inicio, data_fim):
    """Atualiza tabela de transações com filtros"""
    from dash import dash_table
    
    df = carregar_transacoes(mes_selecionado)
    
    if len(df) == 0:
        return html.P(
            "Nenhuma transação encontrada",
            style={'color': COLORS['text_secondary'], 'textAlign': 'center', 'padding': '20px'}
        )
    
    # Aplicar filtros
    df_filtrado = df[df['valor'] > 0].copy()  # Apenas débitos
    
    if categoria_filtro and categoria_filtro != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_filtro]
    
    if fonte_filtro and fonte_filtro != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['fonte'] == fonte_filtro]
    
    if status_filtro == 'CATEGORIZADAS':
        df_filtrado = df_filtrado[df_filtrado['categoria'] != 'A definir']
    elif status_filtro == 'PENDENTES':
        df_filtrado = df_filtrado[df_filtrado['categoria'] == 'A definir']
    
    # Filtro de mês de compensação
    if mes_comp_filtro and mes_comp_filtro != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['mes_comp'] == mes_comp_filtro]
    
    # Filtro de data
    if data_inicio:
        try:
            df_filtrado = df_filtrado[df_filtrado['data'] >= pd.to_datetime(data_inicio)]
        except:
            pass
    if data_fim:
        try:
            df_filtrado = df_filtrado[df_filtrado['data'] <= pd.to_datetime(data_fim)]
        except:
            pass
    
    if len(df_filtrado) == 0:
        return html.P(
            "Nenhuma transação encontrada com os filtros aplicados",
            style={'color': COLORS['text_secondary'], 'textAlign': 'center', 'padding': '20px'}
        )
    
    # Preparar dados para tabela
    df_tabela = df_filtrado[['data', 'descricao', 'valor_normalizado', 'categoria', 'fonte', 'mes_comp']].copy()
    df_tabela = df_tabela.sort_values(['mes_comp', 'fonte', 'data'], ascending=[True, False, True]).head(100)  # Limitar a 100
    
    # Calcular subtotal
    subtotal = df_tabela['valor_normalizado'].sum()
    
    df_tabela['data'] = pd.to_datetime(df_tabela['data']).dt.strftime('%d/%m/%Y')
    
    # Criar tabela HTML simples
    rows = []
    for _, row in df_tabela.iterrows():
        categoria_style = {
            'backgroundColor': COLORS['warning'], 
            'color': COLORS['bg_primary'],
            'padding': '4px 8px',
            'borderRadius': '4px',
            'fontWeight': 'bold'
        } if row['categoria'] == 'A definir' else {}
        
        rows.append(html.Tr([
            html.Td(row['data'], style={'padding': '12px', 'borderBottom': f"1px solid {COLORS['border']}"}),
            html.Td(row['descricao'], style={'padding': '12px', 'borderBottom': f"1px solid {COLORS['border']}"}),
            html.Td(f"R$ {row['valor_normalizado']:,.2f}", style={'padding': '12px', 'borderBottom': f"1px solid {COLORS['border']}"}),
            html.Td(html.Span(row['categoria'], style=categoria_style), style={'padding': '12px', 'borderBottom': f"1px solid {COLORS['border']}"}),
            html.Td(row['fonte'], style={'padding': '12px', 'borderBottom': f"1px solid {COLORS['border']}"}),
            html.Td(row['mes_comp'], style={'padding': '12px', 'borderBottom': f"1px solid {COLORS['border']}"}),
        ]))
    
    return html.Div([
        html.Div([
            html.Span(
                f"Mostrando {len(df_tabela)} transações de {len(df_filtrado)} encontradas",
                style={'color': COLORS['text_secondary'], 'fontSize': FONTS['size']['sm']}
            ),
            html.Span(
                f" • Subtotal: R$ {subtotal:,.2f}",
                style={'color': COLORS['primary'], 'fontSize': FONTS['size']['base'], 'fontWeight': FONTS['weight']['bold'], 'marginLeft': '16px'}
            )
        ], style={'marginBottom': '16px'}),
        html.Div([
            html.Table([
                html.Thead(html.Tr([
                    html.Th('Data', style={'padding': '12px', 'textAlign': 'left', 'borderBottom': f"2px solid {COLORS['border']}", 'color': COLORS['text_primary'], 'fontWeight': 'bold'}),
                    html.Th('Descrição', style={'padding': '12px', 'textAlign': 'left', 'borderBottom': f"2px solid {COLORS['border']}", 'color': COLORS['text_primary'], 'fontWeight': 'bold'}),
                    html.Th('Valor', style={'padding': '12px', 'textAlign': 'left', 'borderBottom': f"2px solid {COLORS['border']}", 'color': COLORS['text_primary'], 'fontWeight': 'bold'}),
                    html.Th('Categoria', style={'padding': '12px', 'textAlign': 'left', 'borderBottom': f"2px solid {COLORS['border']}", 'color': COLORS['text_primary'], 'fontWeight': 'bold'}),
                    html.Th('Fonte', style={'padding': '12px', 'textAlign': 'left', 'borderBottom': f"2px solid {COLORS['border']}", 'color': COLORS['text_primary'], 'fontWeight': 'bold'}),
                    html.Th('Mês', style={'padding': '12px', 'textAlign': 'left', 'borderBottom': f"2px solid {COLORS['border']}", 'color': COLORS['text_primary'], 'fontWeight': 'bold'}),
                ])),
                html.Tbody(rows, style={'color': COLORS['text_primary']})
            ], style={'width': '100%', 'borderCollapse': 'collapse', 'fontSize': FONTS['size']['sm']})
        ], style={'overflowX': 'auto'})
    ])

# ===== MAIN =====
if __name__ == '__main__':
    print("🚀 Iniciando Dashboard Financeiro v2.0...")
    print("📊 Acesse: http://localhost:8052")
    print("🎨 Design: Dark Theme Professional")
    print("📱 Páginas: Dashboard | Analytics | Transações")
    print("\n✨ Desenvolvido com Dash + Plotly\n")
    
    app.run(
        host='0.0.0.0',
        port=8052,
        debug=True
    )
