"""
Dashboard Financeiro v2.0
App principal com sidebar e navegação entre páginas
"""

import sys
from pathlib import Path

# Adicionar pasta src ao PATH para imports funcionarem
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc

# Imports locais
from dashboard_v2.config import COLORS
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
    criar_grafico_top_fontes
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
    Input('url', 'pathname')
)
def atualizar_filtros_transacoes(pathname):
    """Atualiza opções de filtros na página de transações"""
    if pathname == '/transacoes':
        categorias = obter_categorias()
        fontes = obter_fontes()
        
        opcoes_cat = [{'label': 'Todas', 'value': 'TODOS'}] + \
                     [{'label': cat, 'value': cat} for cat in categorias]
        
        opcoes_fonte = [{'label': 'Todas', 'value': 'TODOS'}] + \
                       [{'label': fonte, 'value': fonte} for fonte in fontes]
        
        return opcoes_cat, opcoes_fonte
    
    return [], []

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
