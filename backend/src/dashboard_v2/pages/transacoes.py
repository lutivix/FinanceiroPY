"""
Página Transações - Lista e categorização
Tabela interativa com filtros
"""

from dash import html, dcc, dash_table
from dashboard_v2.config import COLORS, FONTS, SPACING

def create_transacoes_page():
    """Cria página de Transações"""
    
    return html.Div([
        # Header
        html.Div([
            html.H1(
                "Transações",
                style={
                    'color': COLORS['text_primary'],
                    'fontSize': FONTS['size']['3xl'],
                    'fontWeight': FONTS['weight']['bold'],
                    'marginBottom': SPACING['xs']
                }
            ),
            html.P(
                "Gerencie e categorize suas transações",
                style={
                    'color': COLORS['text_secondary'],
                    'fontSize': FONTS['size']['base'],
                    'margin': 0
                }
            )
        ], style={'marginBottom': f"{SPACING['xl']}px"}),
        
        # Filtros
        html.Div([
            # Linha 1: Categoria, Fonte, Status
            html.Div([
                html.Div([
                    html.Label(
                        "Categoria",
                        style={
                            'color': COLORS['text_secondary'],
                            'fontSize': FONTS['size']['sm'],
                            'fontWeight': FONTS['weight']['semibold'],
                            'marginBottom': '8px',
                            'display': 'block'
                        }
                    ),
                    dcc.Dropdown(
                        id='filtro-categoria-transacoes',
                        options=[{'label': 'Todas', 'value': 'TODOS'}],
                        value='TODOS',
                        clearable=False
                    )
                ], style={'flex': '1', 'minWidth': '200px'}),
                
                html.Div([
                    html.Label(
                        "Fonte",
                        style={
                            'color': COLORS['text_secondary'],
                            'fontSize': FONTS['size']['sm'],
                            'fontWeight': FONTS['weight']['semibold'],
                            'marginBottom': '8px',
                            'display': 'block'
                        }
                    ),
                    dcc.Dropdown(
                        id='filtro-fonte-transacoes',
                        options=[{'label': 'Todas', 'value': 'TODOS'}],
                        value='TODOS',
                        clearable=False
                    )
                ], style={'flex': '1', 'minWidth': '200px'}),
                
                html.Div([
                    html.Label(
                        "Status",
                        style={
                            'color': COLORS['text_secondary'],
                            'fontSize': FONTS['size']['sm'],
                            'fontWeight': FONTS['weight']['semibold'],
                            'marginBottom': '8px',
                            'display': 'block'
                        }
                    ),
                    dcc.Dropdown(
                        id='filtro-status-transacoes',
                        options=[
                            {'label': 'Todas', 'value': 'TODOS'},
                            {'label': 'Categorizadas', 'value': 'CATEGORIZADAS'},
                            {'label': 'Pendentes', 'value': 'PENDENTES'}
                        ],
                        value='TODOS',
                        clearable=False
                    )
                ], style={'flex': '1', 'minWidth': '200px'}),
            ], style={
                'display': 'flex',
                'flexWrap': 'wrap',
                'gap': f"{SPACING['lg']}px",
                'marginBottom': f"{SPACING['md']}px"
            }),
            
            # Linha 2: Mês de Compensação e Data
            html.Div([
                html.Div([
                    html.Label(
                        "Mês de Compensação",
                        style={
                            'color': COLORS['text_secondary'],
                            'fontSize': FONTS['size']['sm'],
                            'fontWeight': FONTS['weight']['semibold'],
                            'marginBottom': '8px',
                            'display': 'block'
                        }
                    ),
                    dcc.Dropdown(
                        id='filtro-mes-comp-transacoes',
                        options=[{'label': 'Todos', 'value': 'TODOS'}],
                        value='TODOS',
                        clearable=False
                    )
                ], style={'flex': '1', 'minWidth': '200px'}),
                
                html.Div([
                    html.Label(
                        "Período (Data)",
                        style={
                            'color': COLORS['text_secondary'],
                            'fontSize': FONTS['size']['sm'],
                            'fontWeight': FONTS['weight']['semibold'],
                            'marginBottom': '8px',
                            'display': 'block'
                        }
                    ),
                    dcc.DatePickerRange(
                        id='filtro-data-transacoes',
                        display_format='DD/MM/YYYY',
                        start_date_placeholder_text='Data Inicial',
                        end_date_placeholder_text='Data Final',
                        className='custom-datepicker',
                        style={'width': '100%'}
                    )
                ], style={'flex': '1', 'minWidth': '300px'}),
            ], style={
                'display': 'flex',
                'flexWrap': 'wrap',
                'gap': f"{SPACING['lg']}px"
            })
            
        ], className="custom-card", style={'marginBottom': f"{SPACING['xl']}px"}),
        
        # Tabela de transações
        html.Div([
            html.Div(
                id='tabela-transacoes-container',
                children=[
                    html.P(
                        "Carregando transações...",
                        style={'color': COLORS['text_secondary'], 'textAlign': 'center'}
                    )
                ]
            )
        ], className="custom-card")
        
    ], style={
        'padding': f"{SPACING['xl']}px",
        'maxWidth': '1600px',
        'margin': '0 auto'
    })
