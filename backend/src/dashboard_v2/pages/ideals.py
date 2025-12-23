"""
Ideals Page - Budget Planning & Comparison
Real vs Ideal spending with filters and detailed analysis
"""

from dash import html, dcc
from dashboard_v2.config import COLORS, FONTS, SPACING

def create_ideals_page():
    """Creates Ideals (Budget Planning) page"""
    
    return html.Div([
        # Header
        html.Div([
            html.H1(
                "Budget Ideals",
                style={
                    'color': COLORS['text_primary'],
                    'fontSize': FONTS['size']['3xl'],
                    'fontWeight': FONTS['weight']['bold'],
                    'marginBottom': f"{SPACING['sm']}px"
                }
            ),
            html.P(
                "Compare actual spending vs budget targets",
                style={
                    'color': COLORS['text_secondary'],
                    'fontSize': FONTS['size']['base'],
                    'marginBottom': f"{SPACING['xl']}px"
                }
            ),
        ]),
        
        # Filters Card
        html.Div([
            html.H3(
                "Filters",
                style={
                    'color': COLORS['text_primary'],
                    'fontSize': FONTS['size']['lg'],
                    'fontWeight': FONTS['weight']['semibold'],
                    'marginBottom': f"{SPACING['lg']}px"
                }
            ),
            
            # Filters Grid: 3 rows x 2 columns
            html.Div([
                # Row 1
                html.Div([
                    # Month
                    html.Div([
                        html.Label(
                            "Month",
                            style={
                                'color': COLORS['text_secondary'],
                                'fontSize': FONTS['size']['sm'],
                                'fontWeight': FONTS['weight']['semibold'],
                                'marginBottom': '8px',
                                'display': 'block'
                            }
                        ),
                        dcc.Dropdown(
                            id='filtro-mes-ideals',
                            options=[{'label': 'All (Last 12 months)', 'value': 'TODOS'}],
                            value='TODOS',
                            clearable=False
                        )
                    ], style={'flex': '1', 'minWidth': '200px'}),
                    
                    # View By (NEW)
                    html.Div([
                        html.Label(
                            "View By",
                            style={
                                'color': COLORS['text_secondary'],
                                'fontSize': FONTS['size']['sm'],
                                'fontWeight': FONTS['weight']['semibold'],
                                'marginBottom': '8px',
                                'display': 'block'
                            }
                        ),
                        dcc.Dropdown(
                            id='filtro-view-by-ideals',
                            options=[
                                {'label': 'By Category', 'value': 'category'},
                                {'label': 'By Source', 'value': 'source'}
                            ],
                            value='category',
                            clearable=False
                        )
                    ], style={'flex': '1', 'minWidth': '200px'}),
                ], style={
                    'display': 'flex',
                    'flexWrap': 'wrap',
                    'gap': f"{SPACING['lg']}px",
                    'marginBottom': f"{SPACING['lg']}px"
                }),
                
                # Row 2
                html.Div([
                    # Category
                    html.Div([
                        html.Label(
                            "Category",
                            style={
                                'color': COLORS['text_secondary'],
                                'fontSize': FONTS['size']['sm'],
                                'fontWeight': FONTS['weight']['semibold'],
                                'marginBottom': '8px',
                                'display': 'block'
                            }
                        ),
                        dcc.Dropdown(
                            id='filtro-categoria-ideals',
                            options=[{'label': 'All Categories', 'value': 'TODOS'}],
                            value='TODOS',
                            clearable=False
                        )
                    ], style={'flex': '1', 'minWidth': '200px'}),
                    
                    # Source
                    html.Div([
                        html.Label(
                            "Source",
                            style={
                                'color': COLORS['text_secondary'],
                                'fontSize': FONTS['size']['sm'],
                                'fontWeight': FONTS['weight']['semibold'],
                                'marginBottom': '8px',
                                'display': 'block'
                            }
                        ),
                        dcc.Dropdown(
                            id='filtro-fonte-ideals',
                            options=[{'label': 'All Sources', 'value': 'TODOS'}],
                            value='TODOS',
                            clearable=False
                        )
                    ], style={'flex': '1', 'minWidth': '200px'}),
                ], style={
                    'display': 'flex',
                    'flexWrap': 'wrap',
                    'gap': f"{SPACING['lg']}px",
                    'marginBottom': f"{SPACING['lg']}px"
                }),
                
                # Row 3
                html.Div([
                    # Date Range
                    html.Div([
                        html.Label(
                            "Date Range",
                            style={
                                'color': COLORS['text_secondary'],
                                'fontSize': FONTS['size']['sm'],
                                'fontWeight': FONTS['weight']['semibold'],
                                'marginBottom': '8px',
                                'display': 'block'
                            }
                        ),
                        dcc.DatePickerRange(
                            id='filtro-data-ideals',
                            display_format='DD/MM/YYYY',
                            start_date_placeholder_text='Start Date',
                            end_date_placeholder_text='End Date',
                            className='custom-datepicker',
                            style={'width': '100%'}
                        )
                    ], style={'flex': '1', 'minWidth': '300px'}),
                ], style={
                    'display': 'flex',
                    'flexWrap': 'wrap',
                    'gap': f"{SPACING['lg']}px"
                })
            ])
            
        ], className="custom-card", style={'marginBottom': f"{SPACING['2xl']}px"}),
        
        # Metrics Cards (3 columns)
        html.Div(
            id='ideals-metrics-cards',
            children=[
                html.P(
                    "Select filters to view metrics",
                    style={'color': COLORS['text_secondary'], 'textAlign': 'center'}
                )
            ],
            style={'marginBottom': f"{SPACING['2xl']}px"}
        ),
        
        # Main Chart: Real vs Ideal with Difference
        html.Div([
            html.H3(
                "Budget Comparison",
                style={
                    'color': COLORS['text_primary'],
                    'fontSize': FONTS['size']['lg'],
                    'fontWeight': FONTS['weight']['semibold'],
                    'marginBottom': f"{SPACING['lg']}px"
                }
            ),
            dcc.Graph(
                id='grafico-ideals-comparison',
                figure={},
                config={'displayModeBar': False},
                style={'height': '400px'}
            )
        ], className="custom-card")
        
    ], style={
        'padding': f"{SPACING['xl']}px",
        'maxWidth': '1600px',
        'margin': '0 auto'
    })
