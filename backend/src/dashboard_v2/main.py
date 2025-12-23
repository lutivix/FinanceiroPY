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

from dash import Dash, html, dcc, Input, Output, State, callback, ALL
import dash_bootstrap_components as dbc

# Imports locais
from dashboard_v2.config import COLORS, FONTS
from dashboard_v2.components.sidebar import create_sidebar
from dashboard_v2.assets.custom_styles import get_custom_css
from dashboard_v2.pages.dashboard import create_dashboard_page
from dashboard_v2.pages.analytics import create_analytics_page
from dashboard_v2.pages.transacoes import create_transacoes_page
from dashboard_v2.pages.ideals import create_ideals_page
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
    criar_grafico_acumulado,
    criar_grafico_ideals_comparison
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
    elif pathname == '/ideals':
        return create_ideals_page()
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
    df_tabela = df_filtrado[['id', 'data', 'descricao', 'valor_normalizado', 'categoria', 'fonte', 'mes_comp']].copy()
    df_tabela = df_tabela.sort_values(['mes_comp', 'fonte', 'data'], ascending=[True, False, True]).head(100)  # Limitar a 100
    
    # Calcular subtotal
    subtotal = df_tabela['valor_normalizado'].sum()
    
    df_tabela['data'] = pd.to_datetime(df_tabela['data']).dt.strftime('%d/%m/%Y')
    df_tabela['valor'] = df_tabela['valor_normalizado'].apply(lambda x: f"R$ {x:,.2f}")
    
    # Obter listas de categorias disponíveis
    categorias_disponiveis = sorted(df['categoria'].unique().tolist())
    
    # Criar tabela simples com botões de edição
    rows = []
    for idx, row in df_tabela.iterrows():
        categoria_style = {
            'backgroundColor': COLORS['warning'], 
            'color': COLORS['bg_primary'],
            'padding': '4px 8px',
            'borderRadius': '4px',
            'fontWeight': 'bold',
            'display': 'inline-block'
        } if row['categoria'] == 'A definir' else {'display': 'inline-block'}
        
        # Botão de edição apenas para itens "A definir"
        edit_button = html.Button(
            '✏️',
            id={'type': 'btn-edit-transacao', 'index': row['id']},
            n_clicks=0,
            style={
                'backgroundColor': COLORS['primary'],
                'color': 'white',
                'border': 'none',
                'padding': '6px 12px',
                'borderRadius': '6px',
                'cursor': 'pointer',
                'fontSize': '14px'
            }
        ) if row['categoria'] == 'A definir' else ''
        
        rows.append(html.Tr([
            html.Td(row['data'], style={'padding': '12px', 'borderBottom': f"1px solid {COLORS['border']}"}),
            html.Td(row['descricao'], style={'padding': '12px', 'borderBottom': f"1px solid {COLORS['border']}"}),
            html.Td(f"R$ {row['valor_normalizado']:,.2f}", style={'padding': '12px', 'borderBottom': f"1px solid {COLORS['border']}"}),
            html.Td(html.Span(row['categoria'], style=categoria_style), style={'padding': '12px', 'borderBottom': f"1px solid {COLORS['border']}"}),
            html.Td(row['fonte'], style={'padding': '12px', 'borderBottom': f"1px solid {COLORS['border']}"}),
            html.Td(row['mes_comp'], style={'padding': '12px', 'borderBottom': f"1px solid {COLORS['border']}"}),
            html.Td(edit_button, style={'padding': '12px', 'borderBottom': f"1px solid {COLORS['border']}", 'textAlign': 'center'}),
        ]))
    
    return html.Div([
        # Modal de edição
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Editar Categoria")),
            dbc.ModalBody([
                html.Div([
                    html.Label("Transação:", style={'fontWeight': 'bold', 'color': COLORS['text_primary'], 'marginBottom': '8px'}),
                    html.P(id='modal-transacao-descricao', style={'color': COLORS['text_secondary'], 'marginBottom': '16px'}),
                    html.Label("Nova Categoria:", style={'fontWeight': 'bold', 'color': COLORS['text_primary'], 'marginBottom': '8px'}),
                    dcc.Dropdown(
                        id='modal-dropdown-categoria',
                        options=[{'label': cat, 'value': cat} for cat in categorias_disponiveis],
                        value=None,
                        clearable=False,
                        className='dropdown-white-text',
                        style={
                            'marginBottom': '16px',
                        }
                    )
                ])
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancelar", id="modal-btn-cancelar", color="secondary", className="me-2"),
                dbc.Button("Salvar", id="modal-btn-salvar", color="primary")
            ])
        ], id="modal-edit-transacao", is_open=False, backdrop=True),
        
        # Store para guardar ID da transação sendo editada
        dcc.Store(id='store-transacao-id'),
        
        # Estatísticas
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
        
        # Tabela
        html.Div([
            html.Table([
                html.Thead(html.Tr([
                    html.Th('Data', style={'padding': '12px', 'textAlign': 'left', 'borderBottom': f"2px solid {COLORS['border']}", 'color': COLORS['text_primary'], 'fontWeight': 'bold'}),
                    html.Th('Descrição', style={'padding': '12px', 'textAlign': 'left', 'borderBottom': f"2px solid {COLORS['border']}", 'color': COLORS['text_primary'], 'fontWeight': 'bold'}),
                    html.Th('Valor', style={'padding': '12px', 'textAlign': 'left', 'borderBottom': f"2px solid {COLORS['border']}", 'color': COLORS['text_primary'], 'fontWeight': 'bold'}),
                    html.Th('Categoria', style={'padding': '12px', 'textAlign': 'left', 'borderBottom': f"2px solid {COLORS['border']}", 'color': COLORS['text_primary'], 'fontWeight': 'bold'}),
                    html.Th('Fonte', style={'padding': '12px', 'textAlign': 'left', 'borderBottom': f"2px solid {COLORS['border']}", 'color': COLORS['text_primary'], 'fontWeight': 'bold'}),
                    html.Th('Mês', style={'padding': '12px', 'textAlign': 'left', 'borderBottom': f"2px solid {COLORS['border']}", 'color': COLORS['text_primary'], 'fontWeight': 'bold'}),
                    html.Th('Ações', style={'padding': '12px', 'textAlign': 'center', 'borderBottom': f"2px solid {COLORS['border']}", 'color': COLORS['text_primary'], 'fontWeight': 'bold'}),
                ])),
                html.Tbody(rows, style={'color': COLORS['text_primary']})
            ], style={'width': '100%', 'borderCollapse': 'collapse', 'fontSize': FONTS['size']['sm']})
        ], style={'overflowX': 'auto'}),
        
        # Container para armazenar dados da tabela (para atualização após salvar)
        html.Div(id='dummy-output-transacoes', style={'display': 'none'})
    ])

# Callback para abrir modal de edição
@callback(
    [Output('modal-edit-transacao', 'is_open'),
     Output('store-transacao-id', 'data'),
     Output('modal-transacao-descricao', 'children')],
    [Input({'type': 'btn-edit-transacao', 'index': ALL}, 'n_clicks'),
     Input('modal-btn-cancelar', 'n_clicks'),
     Input('modal-btn-salvar', 'n_clicks')],
    [State('modal-edit-transacao', 'is_open'),
     State('store-transacao-id', 'data'),
     State('store-mes-global', 'data')],
    prevent_initial_call=True
)
def toggle_modal_edit(edit_clicks, cancel_clicks, save_clicks, is_open, transacao_id, mes_selecionado):
    """Abre/fecha modal de edição"""
    from dash import ctx
    
    if not ctx.triggered:
        return False, None, ""
    
    trigger_id = ctx.triggered[0]['prop_id']
    
    # Clicou no botão de editar
    if 'btn-edit-transacao' in trigger_id:
        # Pegar ID da transação do botão clicado
        import json
        button_id = json.loads(trigger_id.split('.')[0])
        transacao_id = button_id['index']
        
        # Buscar descrição da transação
        df = carregar_transacoes(mes_selecionado)
        transacao = df[df['id'] == transacao_id].iloc[0]
        descricao = f"{transacao['descricao']} - R$ {transacao['valor_normalizado']:,.2f}"
        
        return True, transacao_id, descricao
    
    # Clicou em cancelar ou salvar - fechar modal
    return False, None, ""

# Callback para salvar alteração de categoria
@callback(
    Output('tabela-transacoes-container', 'children', allow_duplicate=True),
    Input('modal-btn-salvar', 'n_clicks'),
    [State('store-transacao-id', 'data'),
     State('modal-dropdown-categoria', 'value'),
     State('store-mes-global', 'data'),
     State('filtro-categoria-transacoes', 'value'),
     State('filtro-fonte-transacoes', 'value'),
     State('filtro-status-transacoes', 'value'),
     State('filtro-mes-comp-transacoes', 'value'),
     State('filtro-data-transacoes', 'start_date'),
     State('filtro-data-transacoes', 'end_date')],
    prevent_initial_call=True
)
def salvar_categoria(n_clicks, transacao_id, nova_categoria, mes_selecionado, categoria_filtro, 
                    fonte_filtro, status_filtro, mes_comp_filtro, data_inicio, data_fim):
    """Salva nova categoria no banco e recarrega tabela"""
    from dash import no_update
    
    # Se não houver clique válido, não fazer nada
    if not n_clicks:
        return no_update
        
    # Se não houver dados válidos, não fazer nada
    if not transacao_id or not nova_categoria:
        return no_update
    
    import sqlite3
    
    # Caminho correto do banco (raiz do projeto: dados/db/financeiro.db)
    db_path = BASE_DIR.parent.parent / 'dados' / 'db' / 'financeiro.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE lancamentos SET Categoria = ? WHERE rowid = ?',
            (nova_categoria, transacao_id)
        )
        
        conn.commit()
        conn.close()
        
        # Recarregar tabela com filtros atuais
        return atualizar_tabela_transacoes(
            mes_selecionado, categoria_filtro, fonte_filtro, status_filtro,
            mes_comp_filtro, data_inicio, data_fim
        )
        
    except Exception as e:
        print(f"Erro ao salvar categoria: {e}")
        print(f"DB Path: {db_path}")
        return html.P(
            f"Erro ao salvar: {str(e)}",
            style={'color': COLORS['danger'], 'textAlign': 'center', 'padding': '20px'}
        )

# ===== IDEALS PAGE CALLBACKS =====

@callback(
    Output('filtro-mes-ideals', 'options'),
    Input('url', 'pathname')
)
def atualizar_meses_ideals(pathname):
    """Popula dropdown de meses (Ideals)"""
    if pathname != '/ideals':
        return []
    
    meses = obter_meses_disponiveis()
    return [{'label': 'All (Last 12 months)', 'value': 'TODOS'}] + \
           [{'label': mes, 'value': mes} for mes in meses]

@callback(
    [Output('filtro-categoria-ideals', 'options'),
     Output('filtro-fonte-ideals', 'options')],
    Input('filtro-mes-ideals', 'value')
)
def atualizar_filtros_ideals(mes_selecionado):
    """Popula dropdowns de categoria e fonte (Ideals)"""
    df = carregar_transacoes(mes_selecionado)
    df_debitos = df[df['valor'] > 0].copy()
    
    # Categorias
    categorias = [{'label': 'All Categories', 'value': 'TODOS'}]
    categorias += [
        {'label': cat, 'value': cat} 
        for cat in sorted(df_debitos['categoria'].unique()) 
        if cat != 'A definir'
    ]
    
    # Fontes
    fontes = [{'label': 'All Sources', 'value': 'TODOS'}]
    fontes += [
        {'label': fonte, 'value': fonte} 
        for fonte in sorted(df_debitos['fonte'].unique())
    ]
    
    return categorias, fontes

@callback(
    Output('grafico-ideals-comparison', 'figure'),
    [Input('filtro-mes-ideals', 'value'),
     Input('filtro-view-by-ideals', 'value'),
     Input('filtro-categoria-ideals', 'value'),
     Input('filtro-fonte-ideals', 'value'),
     Input('filtro-data-ideals', 'start_date'),
     Input('filtro-data-ideals', 'end_date')]
)
def atualizar_grafico_ideals(mes_selecionado, view_by, categoria_filtro, fonte_filtro, data_inicio, data_fim):
    """Atualiza gráfico de comparação Real vs Ideal"""
    df = carregar_transacoes(mes_selecionado)
    
    # Aplicar filtro de data se fornecido
    if data_inicio:
        try:
            df = df[df['data'] >= pd.to_datetime(data_inicio)]
        except:
            pass
    if data_fim:
        try:
            df = df[df['data'] <= pd.to_datetime(data_fim)]
        except:
            pass
    
    fig = criar_grafico_ideals_comparison(
        df, 
        mes_selecionado or 'TODOS', 
        categoria_filtro or 'TODOS', 
        fonte_filtro or 'TODOS',
        view_by or 'category'
    )
    return fig

@callback(
    Output('ideals-metrics-cards', 'children'),
    [Input('filtro-mes-ideals', 'value'),
     Input('filtro-view-by-ideals', 'value'),
     Input('filtro-categoria-ideals', 'value'),
     Input('filtro-fonte-ideals', 'value'),
     Input('filtro-data-ideals', 'start_date'),
     Input('filtro-data-ideals', 'end_date')]
)
def atualizar_metricas_ideals(mes_selecionado, view_by, categoria_filtro, fonte_filtro, data_inicio, data_fim):
    """Atualiza cards de métricas (Total Real, Ideal, Diff, Status)"""
    from dashboard_v2.config import ORCAMENTO_IDEAL, ORCAMENTO_IDEAL_FONTE, SPACING
    
    df = carregar_transacoes(mes_selecionado)
    
    # Aplicar filtros
    if data_inicio:
        try:
            df = df[df['data'] >= pd.to_datetime(data_inicio)]
        except:
            pass
    if data_fim:
        try:
            df = df[df['data'] <= pd.to_datetime(data_fim)]
        except:
            pass
    
    df_debitos = df[df['valor'] > 0].copy()
    
    # Determinar multiplicador (anual ou mensal)
    is_annual = (mes_selecionado == 'TODOS' or not mes_selecionado)
    multiplier = 12 if is_annual else 1
    
    # Calcular totais baseado nos filtros
    if categoria_filtro and categoria_filtro != 'TODOS':
        df_filtrado = df_debitos[df_debitos['categoria'] == categoria_filtro]
        real_total = df_filtrado['valor_normalizado'].sum()
        ideal_total = ORCAMENTO_IDEAL.get(categoria_filtro, 0) * multiplier
    elif fonte_filtro and fonte_filtro != 'TODOS':
        df_filtrado = df_debitos[df_debitos['fonte'] == fonte_filtro]
        real_total = df_filtrado['valor_normalizado'].sum()
        ideal_total = ORCAMENTO_IDEAL_FONTE.get(fonte_filtro, 0) * multiplier
    else:
        real_total = df_debitos['valor_normalizado'].sum()
        # Somar todos os ideais de categorias presentes nos dados
        categorias_presentes = df_debitos['categoria'].unique()
        ideal_total = sum(ORCAMENTO_IDEAL.get(cat, 0) for cat in categorias_presentes) * multiplier
    
    diff_total = real_total - ideal_total
    diff_percent = (diff_total / ideal_total * 100) if ideal_total > 0 else 0
    
    # Status
    if diff_total <= 0:
        status_text = "✅ Within Budget"
        status_color = COLORS['success']
    else:
        status_text = "⚠️ Over Budget"
        status_color = COLORS['danger']
    
    # Criar cards
    def create_metric_card(label, value, color):
        return html.Div([
            html.P(label, style={'color': COLORS['text_secondary'], 'fontSize': FONTS['size']['sm'], 'marginBottom': '8px'}),
            html.H3(value, style={'color': color, 'fontSize': FONTS['size']['2xl'], 'fontWeight': FONTS['weight']['bold'], 'margin': '0'})
        ], className="custom-card", style={'flex': '1', 'minWidth': '200px', 'textAlign': 'center', 'padding': f"{SPACING['lg']}px"})
    
    return html.Div([
        create_metric_card("Total Real", f"R$ {real_total:,.2f}", COLORS['primary']),
        create_metric_card("Total Ideal", f"R$ {ideal_total:,.2f}", COLORS['success']),
        create_metric_card("Difference", f"R$ {diff_total:,.2f} ({diff_percent:+.1f}%)", COLORS['danger'] if diff_total > 0 else COLORS['success']),
        create_metric_card("Status", status_text, status_color),
    ], style={'display': 'flex', 'gap': f"{SPACING['lg']}px", 'flexWrap': 'wrap'})

# ===== MAIN =====
if __name__ == '__main__':
    print("🚀 Iniciando Dashboard Financeiro v2.0...")
    print("📊 Acesse: http://localhost:8052")
    print("🎨 Design: Dark Theme Professional")
    print("📱 Páginas: Dashboard | Analytics | Transações | Ideals")
    print("\n✨ Desenvolvido com Dash + Plotly\n")
    
    app.run(
        host='0.0.0.0',
        port=8052,
        debug=True
    )
