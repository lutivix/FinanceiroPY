"""
Página de Orçamento Semanal
===========================

Exibe orçamento semanal com comparação vs realizado
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from dashboard_v2.config import COLORS, FONTS, SPACING


def create_budget_page():
    """Cria página de orçamento semanal."""
    
    return html.Div([
        # Header
        html.Div([
            html.H1("� Médias Semanais", style={
                'color': COLORS['text_primary'],
                'fontFamily': FONTS['family'],
                'marginBottom': SPACING['lg']
            }),
            html.P("Médias calculadas com base em padrões históricos. Compare qualquer mês com essas referências.", style={
                'color': COLORS['text_secondary'],
                'fontSize': '1.1rem'
            })
        ], style={'marginBottom': SPACING['xl']}),
        
        # Seletores
        dbc.Row([
            # Referência de médias
            dbc.Col([
                html.Label("Referência de Médias:", style={
                    'color': COLORS['text_primary'],
                    'fontWeight': 'bold',
                    'marginBottom': '0.5rem',
                    'display': 'block'
                }),
                dcc.Dropdown(
                    id='budget-month-selector',
                    placeholder="Selecione a referência...",
                    style={
                        'backgroundColor': COLORS['bg_card'],
                        'color': COLORS['text_primary']
                    },
                    className='custom-dropdown'
                ),
                html.P(
                    "📈 Médias calculadas com histórico de 12 meses",
                    style={
                        'color': COLORS['text_secondary'],
                        'fontSize': '0.85rem',
                        'marginTop': '0.5rem',
                        'fontStyle': 'italic'
                    }
                )
            ], md=6),
            
            # Mês para comparação
            dbc.Col([
                html.Label("Mês para Comparação:", style={
                    'color': COLORS['text_primary'],
                    'fontWeight': 'bold',
                    'marginBottom': '0.5rem',
                    'display': 'block'
                }),
                dcc.Dropdown(
                    id='budget-comparison-month',
                    placeholder="Selecione o mês...",
                    style={
                        'backgroundColor': COLORS['bg_card'],
                        'color': COLORS['text_primary']
                    },
                    className='custom-dropdown'
                ),
                html.P(
                    "🔍 Escolha qualquer mês para ver seus gastos reais",
                    style={
                        'color': COLORS['text_secondary'],
                        'fontSize': '0.85rem',
                        'marginTop': '0.5rem',
                        'fontStyle': 'italic'
                    }
                )
            ], md=6)
        ], style={'marginBottom': SPACING['xl']}),
        
        # Cards de resumo
        html.Div(id='budget-summary-cards', style={'marginBottom': SPACING['xl']}),
        
        # Gráficos
        dbc.Row([
            # Orçamento por semana
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("📊 Orçamento por Semana", style={
                        'backgroundColor': COLORS['bg_secondary'],
                        'color': COLORS['text_primary'],
                        'fontWeight': 'bold'
                    }),
                    dbc.CardBody([
                        dcc.Graph(id='budget-weekly-chart')
                    ], style={'padding': '0', 'backgroundColor': COLORS['bg_card']})
                ], className="shadow-sm", style={'backgroundColor': COLORS['bg_card']})
            ], md=12, lg=6, style={'marginBottom': SPACING['lg']}),
            
            # Orçado vs Realizado
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("⚖️ Orçado vs Realizado", style={
                        'backgroundColor': COLORS['bg_secondary'],
                        'color': COLORS['text_primary'],
                        'fontWeight': 'bold'
                    }),
                    dbc.CardBody([
                        dcc.Graph(id='budget-vs-actual-chart')
                    ], style={'padding': '0', 'backgroundColor': COLORS['bg_card']})
                ], className="shadow-sm", style={'backgroundColor': COLORS['bg_card']})
            ], md=12, lg=6, style={'marginBottom': SPACING['lg']}),
        ]),
        
        # Detalhamento por categoria
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("📑 Detalhamento por Categoria", style={
                        'backgroundColor': COLORS['bg_secondary'],
                        'color': COLORS['text_primary'],
                        'fontWeight': 'bold'
                    }),
                    dbc.CardBody(
                        id='budget-category-detail',
                        style={
                            'backgroundColor': COLORS['bg_card'],
                            'padding': '0'
                        }
                    )
                ], className="shadow-sm", style={'backgroundColor': COLORS['bg_card']})
            ], md=12)
        ])
    ], style={
        'padding': SPACING['xl'],
        'maxWidth': '1400px',
        'margin': '0 auto'
    })
