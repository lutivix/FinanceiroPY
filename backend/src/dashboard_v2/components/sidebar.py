"""
Componente Sidebar - Navegação lateral
Design baseado em dashboard moderno com tema dark
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from dashboard_v2.config import COLORS, FONTS, SPACING, LAYOUT, ICONS

def create_sidebar():
    """Cria sidebar com navegação"""
    
    return html.Div(
        [
            # Logo/Header
            html.Div(
                [
                    html.I(className="fas fa-wallet", style={
                        'fontSize': '2rem',
                        'color': COLORS['primary'],
                        'marginRight': '12px'
                    }),
                    html.H3(
                        "FinancePro",
                        style={
                            'color': COLORS['text_primary'],
                            'margin': 0,
                            'fontSize': FONTS['size']['2xl'],
                            'fontWeight': FONTS['weight']['bold']
                        }
                    )
                ],
                style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'padding': f"{SPACING['xl']}px {SPACING['lg']}px",
                    'borderBottom': f"1px solid {COLORS['border']}"
                }
            ),
            
            # Navegação
            html.Div(
                [
                    create_nav_item('Dashboard', 'dashboard', '/'),
                    create_nav_item('Analytics', 'analytics', '/analytics'),
                    create_nav_item('Transações', 'transactions', '/transacoes'),
                    create_nav_item('Ideals', 'ideals', '/ideals'),
                ],
                style={
                    'padding': f"{SPACING['lg']}px 0"
                }
            ),
            
            # Filtro de mês (fixo na sidebar)
            html.Div(
                [
                    html.Div(
                        [
                            html.I(className=ICONS['calendar'], style={
                                'fontSize': '1rem',
                                'color': COLORS['text_secondary'],
                                'marginRight': '8px'
                            }),
                            html.Label(
                                "Período",
                                style={
                                    'color': COLORS['text_secondary'],
                                    'fontSize': FONTS['size']['sm'],
                                    'fontWeight': FONTS['weight']['semibold'],
                                    'marginBottom': '8px',
                                    'textTransform': 'uppercase',
                                    'letterSpacing': '0.5px'
                                }
                            )
                        ],
                        style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '8px'}
                    ),
                    dcc.Dropdown(
                        id='filtro-mes-global',
                        options=[{'label': 'Todos os meses', 'value': 'TODOS'}],
                        value='TODOS',
                        clearable=False,
                        className='dropdown-sidebar',
                        style={
                            'backgroundColor': COLORS['bg_card'],
                            'borderRadius': '8px'
                        }
                    )
                ],
                style={
                    'padding': f"{SPACING['lg']}px",
                    'borderTop': f"1px solid {COLORS['border']}",
                    'marginTop': 'auto'
                }
            ),
            
            # Footer
            html.Div(
                [
                    html.P(
                        "Dashboard v2.0",
                        style={
                            'color': COLORS['text_muted'],
                            'fontSize': FONTS['size']['xs'],
                            'margin': 0
                        }
                    )
                ],
                style={
                    'padding': f"{SPACING['md']}px {SPACING['lg']}px",
                    'borderTop': f"1px solid {COLORS['border']}"
                }
            )
        ],
        style={
            'position': 'fixed',
            'top': 0,
            'left': 0,
            'bottom': 0,
            'width': LAYOUT['sidebar_width'],
            'backgroundColor': COLORS['sidebar_bg'],
            'display': 'flex',
            'flexDirection': 'column',
            'zIndex': 1000,
            'boxShadow': '2px 0 10px rgba(0,0,0,0.3)'
        }
    )

def create_nav_item(label, icon_key, href):
    """
    Cria item de navegação
    
    Args:
        label: Texto do item
        icon_key: Chave do ícone em ICONS
        href: URL de navegação
    """
    return dcc.Link(
        html.Div(
            [
                html.I(
                    className=ICONS[icon_key],
                    style={
                        'fontSize': '1.25rem',
                        'marginRight': '16px',
                        'width': '24px',
                        'textAlign': 'center'
                    }
                ),
                html.Span(
                    label,
                    style={
                        'fontSize': FONTS['size']['base'],
                        'fontWeight': FONTS['weight']['medium']
                    }
                )
            ],
            id=f'nav-{icon_key}',
            className='nav-item',
            style={
                'display': 'flex',
                'alignItems': 'center',
                'padding': f"{SPACING['md']}px {SPACING['lg']}px",
                'color': COLORS['text_secondary'],
                'cursor': 'pointer',
                'transition': 'all 0.2s ease',
                'borderLeft': '3px solid transparent'
            }
        ),
        href=href,
        style={'textDecoration': 'none'}
    )
