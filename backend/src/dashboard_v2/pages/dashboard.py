"""
Página Dashboard - Visão geral financeira
3 cards principais + gráfico hero de evolução
"""

from dash import html, dcc
import plotly.graph_objects as go
from dashboard_v2.config import COLORS, FONTS, SPACING, PLOTLY_TEMPLATE, ORCAMENTO_IDEAL, IDEAL_MENSAL_TOTAL

def create_dashboard_page(stats, df_month=None):
    """
    Cria página do dashboard principal
    
    Args:
        stats: Dict com estatísticas (da função calcular_estatisticas)
        df_month: DataFrame do mês selecionado (opcional)
    """
    
    return html.Div([
        # Header
        html.Div([
            html.H1(
                "Dashboard Financeiro",
                style={
                    'color': COLORS['text_primary'],
                    'fontSize': FONTS['size']['2xl'],
                    'fontWeight': FONTS['weight']['bold'],
                    'marginBottom': SPACING['xs']
                }
            ),
            html.P(
                "Visão geral das suas finanças",
                style={
                    'color': COLORS['text_secondary'],
                    'fontSize': FONTS['size']['sm'],
                    'margin': 0
                }
            )
        ], style={'marginBottom': f"{SPACING['lg']}px"}),
        
        # Cards principais (3 grandes)
        html.Div([
            # Card 1: Total Gasto
            html.Div([
                create_main_card(
                    label="Total Gasto",
                    value=f"R$ {stats['total']/1000:.1f}k",
                    subtitle=f"{stats['num_transacoes']:,} transações",
                    icon="wallet",
                    color=COLORS['primary']
                )
            ], style={'flex': '1', 'minWidth': '280px'}),
            
            # Card 2: Ideal Mensal (fixo, não muda com filtro)
            html.Div([
                create_main_card(
                    label="Ideal Mensal",
                    value=f"R$ {IDEAL_MENSAL_TOTAL/1000:.1f}k",
                    subtitle="Orçamento planejado",
                    icon="trending_up",
                    color=COLORS['info']
                )
            ], style={'flex': '1', 'minWidth': '280px'}),
            
            # Card 3: Categorização
            html.Div([
                create_main_card(
                    label="Categorizado",
                    value=f"{stats['perc_categorizado']:.1f}%",
                    subtitle=f"{stats['total_pendente']} pendentes",
                    icon="category",
                    color=COLORS['success'] if stats['perc_categorizado'] >= 95 else COLORS['warning']
                )
            ], style={'flex': '1', 'minWidth': '280px'}),
        ], style={
            'display': 'flex',
            'flexWrap': 'wrap',
            'gap': f"{SPACING['md']}px",
            'marginBottom': f"{SPACING['lg']}px"
        }),
        
        # Gráfico Hero: Evolução 12 meses
        html.Div([
            html.Div([
                html.H3(
                    "Evolução dos Últimos 12 Meses",
                    className="graph-title",
                    style={
                        'color': COLORS['text_primary'],
                        'fontSize': FONTS['size']['lg'],
                        'fontWeight': FONTS['weight']['semibold'],
                        'marginBottom': f"{SPACING['sm']}px"
                    }
                ),
                dcc.Graph(
                    id='grafico-evolucao-hero',
                    config={
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToAdd': ['toImage']
                    },
                    style={'height': '280px'}
                )
            ], className="graph-container")
        ], style={'marginBottom': f"{SPACING['lg']}px"}),
        
        # Segunda linha: 2 gráficos lado a lado
        html.Div([
            # Top 5 Categorias
            html.Div([
                html.Div([
                    html.H3(
                        "Top 5 Categorias",
                        className="graph-title",
                        style={
                            'color': COLORS['text_primary'],
                            'fontSize': FONTS['size']['lg'],
                            'fontWeight': FONTS['weight']['semibold'],
                            'marginBottom': f"{SPACING['md']}px"
                        }
                    ),
                    dcc.Graph(
                        id='grafico-top-categorias',
                        config={
                            'displayModeBar': True,
                            'displaylogo': False,
                            'modeBarButtonsToAdd': ['toImage']
                        },
                        style={'height': '240px'}
                    )
                ], className="graph-container")
            ], style={'flex': '1', 'minWidth': '400px'}),
            
            # Top 5 Fontes
            html.Div([
                html.Div([
                    html.H3(
                        "Top 5 Fontes",
                        className="graph-title",
                        style={
                            'color': COLORS['text_primary'],
                            'fontSize': FONTS['size']['lg'],
                            'fontWeight': FONTS['weight']['semibold'],
                            'marginBottom': f"{SPACING['md']}px"
                        }
                    ),
                    dcc.Graph(
                        id='grafico-top-fontes',
                        config={
                            'displayModeBar': True,
                            'displaylogo': False,
                            'modeBarButtonsToAdd': ['toImage']
                        },
                        style={'height': '240px'}
                    )
                ], className="graph-container")
            ], style={'flex': '1', 'minWidth': '400px'}),
        ], style={
            'display': 'flex',
            'flexWrap': 'wrap',
            'gap': f"{SPACING['md']}px"
        })
        
    ], style={
        'padding': f"{SPACING['md']}px",
        'maxWidth': '1800px',
        'margin': '0 auto'
    })

def create_main_card(label, value, subtitle, icon, color):
    """
    Cria card grande principal
    
    Args:
        label: Rótulo superior
        value: Valor principal (grande)
        subtitle: Texto secundário
        icon: Ícone (chave do ICONS)
        color: Cor do ícone/destaque
    """
    from dashboard_v2.config import ICONS
    
    return html.Div([
        # Header do card
        html.Div([
            html.Div([
                html.I(
                    className=ICONS[icon],
                    style={
                        'fontSize': '1.25rem',
                        'color': color,
                        'opacity': 0.9
                    }
                )
            ], style={
                'width': '36px',
                'height': '36px',
                'borderRadius': '8px',
                'backgroundColor': f"{color}20",
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'marginBottom': f"{SPACING['sm']}px"
            }),
        ]),
        
        # Label
        html.P(
            label,
            className="card-label",
            style={
                'color': COLORS['text_secondary'],
                'fontSize': FONTS['size']['sm'],
                'fontWeight': FONTS['weight']['semibold'],
                'textTransform': 'uppercase',
                'letterSpacing': '0.5px',
                'marginBottom': f"{SPACING['xs']}px"
            }
        ),
        
        # Valor principal
        html.H2(
            value,
            className="card-value",
            style={
                'color': COLORS['text_primary'],
                'fontSize': FONTS['size']['4xl'],
                'fontWeight': FONTS['weight']['bold'],
                'marginBottom': f"{SPACING['xs']}px",
                'lineHeight': 1.2
            }
        ),
        
        # Subtitle
        html.P(
            subtitle,
            className="card-subtitle",
            style={
                'color': COLORS['text_muted'],
                'fontSize': FONTS['size']['xs'],
                'margin': 0
            }
        )
        
    ], className="custom-card animate-fade-in")
