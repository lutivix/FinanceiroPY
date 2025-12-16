"""
Página Analytics - Análises detalhadas
Gráficos comparativos e análises profundas
"""

from dash import html, dcc
from dashboard_v2.config import COLORS, FONTS, SPACING

def create_analytics_page():
    """Cria página de Analytics"""
    
    return html.Div([
        # Header
        html.Div([
            html.H1(
                "Analytics",
                style={
                    'color': COLORS['text_primary'],
                    'fontSize': FONTS['size']['3xl'],
                    'fontWeight': FONTS['weight']['bold'],
                    'marginBottom': SPACING['xs']
                }
            ),
            html.P(
                "Análises detalhadas e comparações",
                style={
                    'color': COLORS['text_secondary'],
                    'fontSize': FONTS['size']['base'],
                    'margin': 0
                }
            )
        ], style={'marginBottom': f"{SPACING['xl']}px"}),
        
        # Gráfico Real vs Ideal
        html.Div([
            html.Div([
                html.H3(
                    "Real vs Ideal por Categoria",
                    className="graph-title",
                    style={
                        'color': COLORS['text_primary'],
                        'fontSize': FONTS['size']['xl'],
                        'fontWeight': FONTS['weight']['semibold'],
                        'marginBottom': f"{SPACING['md']}px"
                    }
                ),
                dcc.Graph(
                    id='grafico-real-ideal-analytics',
                    config={
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToAdd': ['toImage']
                    },
                    style={'height': '500px'}
                )
            ], className="graph-container")
        ], style={'marginBottom': f"{SPACING['2xl']}px"}),
        
        # Linha de gráficos complementares
        html.Div([
            # Distribuição temporal
            html.Div([
                html.Div([
                    html.H3(
                        "Distribuição Temporal",
                        className="graph-title",
                        style={
                            'color': COLORS['text_primary'],
                            'fontSize': FONTS['size']['lg'],
                            'fontWeight': FONTS['weight']['semibold'],
                            'marginBottom': f"{SPACING['md']}px"
                        }
                    ),
                    dcc.Graph(
                        id='grafico-distribuicao-temporal',
                        config={
                            'displayModeBar': True,
                            'displaylogo': False,
                            'modeBarButtonsToAdd': ['toImage']
                        },
                        style={'height': '350px'}
                    )
                ], className="graph-container")
            ], style={'width': '48%'}),
            
            # Acumulado
            html.Div([
                html.Div([
                    html.H3(
                        "Acumulado Mensal",
                        className="graph-title",
                        style={
                            'color': COLORS['text_primary'],
                            'fontSize': FONTS['size']['lg'],
                            'fontWeight': FONTS['weight']['semibold'],
                            'marginBottom': f"{SPACING['md']}px"
                        }
                    ),
                    dcc.Graph(
                        id='grafico-acumulado',
                        config={
                            'displayModeBar': True,
                            'displaylogo': False,
                            'modeBarButtonsToAdd': ['toImage']
                        },
                        style={'height': '350px'}
                    )
                ], className="graph-container")
            ], style={'width': '48%'}),
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'gap': f"{SPACING['lg']}px"
        })
        
    ], style={
        'padding': f"{SPACING['xl']}px",
        'maxWidth': '1600px',
        'margin': '0 auto'
    })
