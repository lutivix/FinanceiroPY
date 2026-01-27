"""
Callbacks para a página de Orçamento
=====================================

Gerencia interações e atualização de dados da página de orçamento semanal.
"""

from dash import Input, Output, html, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from dashboard_v2.config import COLORS
from dashboard_v2.utils.database import (
    obter_resumo_orcamento_semanal,
    obter_meses_orcamento_disponiveis,
    carregar_transacoes
)
import pandas as pd


def register_budget_callbacks(app):
    """Registra todos os callbacks da página de orçamento."""
    
    @app.callback(
        Output('budget-month-selector', 'options'),
        Output('budget-month-selector', 'value'),
        Input('url', 'pathname')
    )
    def update_month_options(pathname):
        """Atualiza opções de meses disponíveis."""
        if pathname != '/budget':
            return [], None
        
        try:
            meses = obter_meses_orcamento_disponiveis()
            # Define o primeiro (mais recente) como padrão
            default_value = meses[0]['value'] if meses else None
            return meses, default_value
        except Exception as e:
            return [{'label': 'Atual', 'value': 'current'}], 'current'
    
    @app.callback(
        Output('budget-summary-cards', 'children'),
        Input('url', 'pathname')
    )
    def update_budget_summary(pathname):
        """Atualiza cards de resumo do orçamento."""
        if pathname != '/budget':
            return []
        
        try:
            data = obter_resumo_orcamento_semanal()
            if not data or 'summary' not in data:
                return html.Div("Nenhum orçamento encontrado. Execute o script de análise primeiro.", 
                               style={'color': COLORS['text_secondary']})
            
            summary = data['summary']
            generated_at = data.get('generated_at', 'N/A')
            
            # Calcula totais
            total_mensal = sum(week['total'] for week in summary.values())
            num_semanas = len(summary)
            media_semanal = total_mensal / num_semanas if num_semanas > 0 else 0
            
            # Semana mais cara
            max_week = max(summary.items(), key=lambda x: x[1]['total'])
            
            cards = dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("💰 Total Mensal", style={'color': COLORS['text_secondary'], 'marginBottom': '8px', 'fontSize': '0.9rem'}),
                            html.H3(f"R$ {total_mensal:,.2f}", style={'color': COLORS['primary'], 'marginBottom': '0'})
                        ])
                    ], className="shadow-sm", style={'backgroundColor': COLORS['bg_card']})
                ], md=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("📅 Média Semanal", style={'color': COLORS['text_secondary'], 'marginBottom': '8px', 'fontSize': '0.9rem'}),
                            html.H3(f"R$ {media_semanal:,.2f}", style={'color': COLORS['success'], 'marginBottom': '0'})
                        ])
                    ], className="shadow-sm", style={'backgroundColor': COLORS['bg_card']})
                ], md=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("⚡ Semana Mais Cara", style={'color': COLORS['text_secondary'], 'marginBottom': '8px', 'fontSize': '0.9rem'}),
                            html.H4(f"Semana {max_week[0]}", style={'color': COLORS['warning'], 'marginBottom': '4px'}),
                            html.P(f"R$ {max_week[1]['total']:,.2f}", style={'color': COLORS['text_secondary'], 'marginBottom': '0', 'fontSize': '0.9rem'})
                        ])
                    ], className="shadow-sm", style={'backgroundColor': COLORS['bg_card']})
                ], md=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("📊 Última Atualização", style={'color': COLORS['text_secondary'], 'marginBottom': '8px', 'fontSize': '0.9rem'}),
                            html.H5(generated_at, style={'color': COLORS['info'], 'fontSize': '1.3rem', 'marginBottom': '0'})
                        ])
                    ], className="shadow-sm", style={'backgroundColor': COLORS['bg_card']})
                ], md=3),
            ])
            
            return cards
        
        except Exception as e:
            return html.Div(f"Erro ao carregar resumo: {e}", style={'color': COLORS['danger']})
    
    
    @app.callback(
        Output('budget-weekly-chart', 'figure'),
        Input('url', 'pathname')
    )
    def update_weekly_chart(pathname):
        """Atualiza gráfico de orçamento por semana."""
        if pathname != '/budget':
            return {}
        
        try:
            data = obter_resumo_orcamento_semanal()
            if not data or 'summary' not in data:
                return {}
            
            summary = data['summary']
            
            # Prepara dados
            weeks = sorted(summary.keys())
            totals = [summary[w]['total'] for w in weeks]
            week_labels = [f"Semana {w}" for w in weeks]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=week_labels,
                y=totals,
                marker=dict(
                    color=totals,
                    colorscale='Blues',
                    showscale=False
                ),
                text=[f"R$ {t:,.2f}" for t in totals],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>'
            ))
            
            fig.update_layout(
                title="Orçamento Esperado por Semana",
                xaxis_title="Semana do Mês",
                yaxis_title="Valor (R$)",
                plot_bgcolor=COLORS['bg_card'],
                paper_bgcolor=COLORS['bg_card'],
                font=dict(color=COLORS['text_primary']),
                hovermode='x unified',
                showlegend=False
            )
            
            return fig
        
        except Exception as e:
            return {}
    
    
    @app.callback(
        Output('budget-vs-actual-chart', 'figure'),
        Input('url', 'pathname')
    )
    def update_budget_vs_actual_chart(pathname):
        """Atualiza gráfico comparativo orçado vs realizado."""
        if pathname != '/budget':
            return {}
        
        try:
            # Busca orçamento
            budget_data = obter_resumo_orcamento_semanal()
            if not budget_data or 'summary' not in budget_data:
                return {}
            
            summary = budget_data['summary']
            weeks = sorted(summary.keys())
            budget_totals = [summary[w]['total'] for w in weeks]
            
            # Busca transações reais do mês atual
            df_trans = carregar_transacoes('TODOS')
            if df_trans.empty:
                actual_totals = [0] * len(weeks)
            else:
                # Calcula semana baseado no dia
                df_trans['data'] = pd.to_datetime(df_trans['data'])
                df_trans['day'] = df_trans['data'].dt.day
                df_trans['week'] = df_trans['day'].apply(lambda d: 
                    1 if d <= 7 else 
                    2 if d <= 14 else 
                    3 if d <= 21 else 
                    4 if d <= 28 else 5
                )
                
                # Soma por semana (apenas valores positivos = débitos)
                actual_by_week = df_trans[df_trans['valor'] > 0].groupby('week')['valor'].sum()
                actual_totals = [actual_by_week.get(w, 0) for w in weeks]
            
            week_labels = [f"Semana {w}" for w in weeks]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Orçado',
                x=week_labels,
                y=budget_totals,
                marker_color=COLORS['primary'],
                text=[f"R$ {t:,.2f}" for t in budget_totals],
                textposition='outside'
            ))
            
            fig.add_trace(go.Bar(
                name='Realizado',
                x=week_labels,
                y=actual_totals,
                marker_color=COLORS['success'],
                text=[f"R$ {t:,.2f}" for t in actual_totals],
                textposition='outside'
            ))
            
            fig.update_layout(
                title="Orçado vs Realizado por Semana",
                xaxis_title="Semana do Mês",
                yaxis_title="Valor (R$)",
                barmode='group',
                plot_bgcolor=COLORS['bg_card'],
                paper_bgcolor=COLORS['bg_card'],
                font=dict(color=COLORS['text_primary']),
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            return fig
        
        except Exception as e:
            return {}
    
    
    @app.callback(
        Output('budget-category-detail', 'children'),
        Input('url', 'pathname')
    )
    def update_category_detail(pathname):
        """Atualiza detalhamento por categoria."""
        if pathname != '/budget':
            return []
        
        try:
            data = obter_resumo_orcamento_semanal()
            if not data or 'summary' not in data:
                return html.Div("Nenhum dado disponível", style={'color': COLORS['text_secondary']})
            
            summary = data['summary']
            
            # Consolida categorias de todas as semanas
            all_categories = {}
            for week_data in summary.values():
                for cat, value in week_data['by_category'].items():
                    all_categories[cat] = all_categories.get(cat, 0) + value
            
            # Ordena por valor
            sorted_cats = sorted(all_categories.items(), key=lambda x: x[1], reverse=True)
            
            # Cria tabela com estilo dark customizado
            total = sum(all_categories.values())
            table_rows = []
            
            for cat, value in sorted_cats:
                percentage = (value / total * 100) if total > 0 else 0
                table_rows.append(html.Tr([
                    html.Td(cat, style={
                        'color': COLORS['text_primary'],
                        'backgroundColor': COLORS['bg_card'],
                        'border': 'none',
                        'padding': '12px',
                        'borderBottom': f"1px solid {COLORS['bg_secondary']}"
                    }),
                    html.Td(f"R$ {value:,.2f}", style={
                        'color': COLORS['success'], 
                        'textAlign': 'right', 
                        'fontWeight': 'bold',
                        'backgroundColor': COLORS['bg_card'],
                        'border': 'none',
                        'padding': '12px',
                        'borderBottom': f"1px solid {COLORS['bg_secondary']}"
                    }),
                    html.Td(f"{percentage:.1f}%", style={
                        'color': COLORS['text_secondary'], 
                        'textAlign': 'right',
                        'backgroundColor': COLORS['bg_card'],
                        'border': 'none',
                        'padding': '12px',
                        'borderBottom': f"1px solid {COLORS['bg_secondary']}"
                    })
                ]))
            
            return html.Table([
                html.Thead(html.Tr([
                    html.Th("Categoria", style={
                        'color': COLORS['text_primary'],
                        'backgroundColor': COLORS['bg_secondary'],
                        'border': 'none',
                        'padding': '12px',
                        'fontWeight': 'bold',
                        'borderBottom': f"2px solid {COLORS['primary']}"
                    }),
                    html.Th("Valor Mensal", style={
                        'color': COLORS['text_primary'], 
                        'textAlign': 'right',
                        'backgroundColor': COLORS['bg_secondary'],
                        'border': 'none',
                        'padding': '12px',
                        'fontWeight': 'bold',
                        'borderBottom': f"2px solid {COLORS['primary']}"
                    }),
                    html.Th("% do Total", style={
                        'color': COLORS['text_primary'], 
                        'textAlign': 'right',
                        'backgroundColor': COLORS['bg_secondary'],
                        'border': 'none',
                        'padding': '12px',
                        'fontWeight': 'bold',
                        'borderBottom': f"2px solid {COLORS['primary']}"
                    })
                ])),
                html.Tbody(table_rows)
            ], style={
                'width': '100%',
                'backgroundColor': COLORS['bg_card'],
                'borderCollapse': 'collapse',
                'border': 'none'
            })
        
        except Exception as e:
            return html.Div(f"Erro ao carregar detalhamento: {e}", style={'color': COLORS['danger']})
