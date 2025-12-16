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
            ], style={'width': '30%'}),
            
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
            ], style={'width': '30%'}),
            
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
            ], style={'width': '30%'}),
            
        ], className="custom-card", style={
            'display': 'flex',
            'gap': f"{SPACING['lg']}px",
            'marginBottom': f"{SPACING['xl']}px"
        }),
        
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
