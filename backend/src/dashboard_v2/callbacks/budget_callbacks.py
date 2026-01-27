"""
Callbacks para a página de Médias Semanais
==========================================

Gerencia interações e atualização de dados da página de médias semanais.
Médias são calculadas com histórico e usadas como referência para comparar qualquer mês.
"""

from dash import Input, Output, html, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from dashboard_v2.config import COLORS
from dashboard_v2.utils.database import (
    obter_resumo_orcamento_semanal,
    obter_meses_orcamento_disponiveis,
    obter_resumo_orcamento_por_data,
    obter_meses_disponiveis_para_comparacao,
    carregar_transacoes
)
import pandas as pd


def register_budget_callbacks(app):
    """Registra todos os callbacks da página de médias."""
    
    @app.callback(
        Output('budget-month-selector', 'options'),
        Output('budget-month-selector', 'value'),
        Output('budget-comparison-month', 'options'),
        Output('budget-comparison-month', 'value'),
        Input('url', 'pathname')
    )
    def update_dropdown_options(pathname):
        """Atualiza opções dos dropdowns."""
        if pathname != '/budget':
            return [], None, [], None
        
        try:
            # Dropdown 1: Referências de médias (gerações do orçamento)
            referencias = obter_meses_orcamento_disponiveis()
            ref_default = referencias[0]['value'] if referencias else None
            
            # Dropdown 2: Meses disponíveis para comparação (meses com transações)
            meses_comp = obter_meses_disponiveis_para_comparacao()
            # Por padrão, seleciona o mês mais recente
            comp_default = meses_comp[0]['value'] if meses_comp else None
            
            return referencias, ref_default, meses_comp, comp_default
        except Exception as e:
            print(f"Erro ao carregar dropdowns: {e}")
            return [], None, [], None
    
    @app.callback(
        Output('budget-summary-cards', 'children'),
        Input('url', 'pathname'),
        Input('budget-month-selector', 'value')
    )
    def update_budget_summary(pathname, selected_reference):
        """Atualiza cards de resumo (baseado nas MÉDIAS, não muda com mês de comparação)."""
        if pathname != '/budget' or not selected_reference:
            return []
        
        try:
            # Busca MÉDIAS da referência selecionada
            data = obter_resumo_orcamento_por_data(selected_reference)
            if not data or 'summary' not in data:
                return html.Div("Nenhuma média encontrada. Execute o script de análise primeiro.", 
                               style={'color': COLORS['text_secondary']})
            
            summary = data['summary']
            generated_at = data.get('generated_at', 'N/A')
            
            # Calcula totais DAS MÉDIAS
            total_mensal = sum(week['total'] for week in summary.values())
            num_semanas = len(summary)
            media_semanal = total_mensal / num_semanas if num_semanas > 0 else 0
            
            # Semana mais cara DAS MÉDIAS
            max_week = max(summary.items(), key=lambda x: x[1]['total'])
            
            cards = dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("💰 Média Mensal Esperada", style={'color': COLORS['text_secondary'], 'marginBottom': '8px', 'fontSize': '0.9rem'}),
                            html.H3(f"R$ {total_mensal:,.2f}", style={'color': COLORS['primary'], 'marginBottom': '0'}),
                            html.P(f"Ref: {generated_at[:10]}", style={'color': COLORS['text_secondary'], 'fontSize': '0.75rem', 'marginTop': '4px'})
                        ])
                    ], className="shadow-sm", style={'backgroundColor': COLORS['bg_card']})
                ], md=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("📅 Média Semanal", style={'color': COLORS['text_secondary'], 'marginBottom': '8px', 'fontSize': '0.9rem'}),
                            html.H3(f"R$ {media_semanal:,.2f}", style={'color': COLORS['success'], 'marginBottom': '0'}),
                            html.P("Por semana", style={'color': COLORS['text_secondary'], 'fontSize': '0.75rem', 'marginTop': '4px'})
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
        Input('url', 'pathname'),
        Input('budget-month-selector', 'value')
    )
    def update_weekly_chart(pathname, selected_reference):
        """Atualiza gráfico de MÉDIAS por semana (não muda com mês de comparação)."""
        if pathname != '/budget' or not selected_reference:
            return {}
        
        try:
            # Busca MÉDIAS da referência selecionada
            data = obter_resumo_orcamento_por_data(selected_reference)
            if not data or 'summary' not in data:
                return {}
            
            summary = data['summary']
            
            # Prepara dados DAS MÉDIAS
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
                title="Médias Esperadas por Semana",
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
        Input('url', 'pathname'),
        Input('budget-month-selector', 'value'),
        Input('budget-comparison-month', 'value')
    )
    def update_budget_vs_actual_chart(pathname, selected_reference, comparison_month):
        """Atualiza gráfico comparativo MÉDIAS vs REALIZADO do mês escolhido."""
        if pathname != '/budget' or not selected_reference or not comparison_month:
            return {}
        
        try:
            # 1. Busca MÉDIAS da referência selecionada
            budget_data = obter_resumo_orcamento_por_data(selected_reference)
            if not budget_data or 'summary' not in budget_data:
                return {}
            
            summary = budget_data['summary']
            weeks = sorted(summary.keys())
            budget_totals = [summary[w]['total'] for w in weeks]
            
            # 2. Busca transações REAIS do mês de comparação escolhido
            df_trans = carregar_transacoes('TODOS')
            if df_trans.empty:
                actual_totals = [0] * len(weeks)
            else:
                # Filtra transações do mês de comparação usando MesComp
                df_trans['data'] = pd.to_datetime(df_trans['data'])
                # Converte mes_comp para formato YYYY-MM para comparação
                meses_map = {
                    'Janeiro': '01', 'Fevereiro': '02', 'Março': '03', 'Abril': '04',
                    'Maio': '05', 'Junho': '06', 'Julho': '07', 'Agosto': '08',
                    'Setembro': '09', 'Outubro': '10', 'Novembro': '11', 'Dezembro': '12'
                }
                
                def mescomp_to_yearmonth(mescomp):
                    if pd.isna(mescomp):
                        return None
                    parts = mescomp.split()
                    if len(parts) == 2:
                        mes_nome, ano = parts
                        mes_num = meses_map.get(mes_nome, '00')
                        return f"{ano}-{mes_num}"
                    return None
                
                df_trans['year_month'] = df_trans['mes_comp'].apply(mescomp_to_yearmonth)
                df_month = df_trans[df_trans['year_month'] == comparison_month]
                
                if df_month.empty:
                    actual_totals = [0] * len(weeks)
                else:
                    # Calcula semana baseado no dia
                    df_month['day'] = df_month['data'].dt.day
                    df_month['week'] = df_month['day'].apply(lambda d: 
                        1 if d <= 7 else 
                        2 if d <= 14 else 
                        3 if d <= 21 else 
                        4 if d <= 28 else 5
                    )
                    
                    # Soma por semana (apenas valores positivos = débitos)
                    actual_by_week = df_month[df_month['valor'] > 0].groupby('week')['valor'].sum()
                    actual_totals = [actual_by_week.get(w, 0) for w in weeks]
            
            week_labels = [f"Semana {w}" for w in weeks]
            
            # Traduz mês para português
            meses_pt = {
                '01': 'Janeiro', '02': 'Fevereiro', '03': 'Março', '04': 'Abril',
                '05': 'Maio', '06': 'Junho', '07': 'Julho', '08': 'Agosto',
                '09': 'Setembro', '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'
            }
            ano, mes = comparison_month.split('-')
            mes_nome = meses_pt.get(mes, mes)
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Média Esperada',
                x=week_labels,
                y=budget_totals,
                marker_color=COLORS['primary'],
                text=[f"R$ {t:,.2f}" for t in budget_totals],
                textposition='outside'
            ))
            
            fig.add_trace(go.Bar(
                name='Gasto Real',
                x=week_labels,
                y=actual_totals,
                marker_color=COLORS['success'],
                text=[f"R$ {t:,.2f}" for t in actual_totals],
                textposition='outside'
            ))
            
            # Formata mês para título
            
            fig.update_layout(
                title=f"Médias vs Real - {mes_nome} {ano}",
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
        Input('url', 'pathname'),
        Input('budget-month-selector', 'value'),
        Input('budget-comparison-month', 'value')
    )
    def update_category_detail(pathname, selected_reference, comparison_month):
        """Atualiza detalhamento por categoria - MÉDIAS vs REAL do mês escolhido."""
        if pathname != '/budget' or not selected_reference or not comparison_month:
            return []
        
        try:
            # Busca MÉDIAS da referência selecionada
            data = obter_resumo_orcamento_por_data(selected_reference)
            if not data or 'summary' not in data:
                return html.Div("Nenhum dado disponível", style={'color': COLORS['text_secondary']})
            
            summary = data['summary']
            
            # Consolida categorias de todas as semanas DAS MÉDIAS
            all_categories = {}
            for week_data in summary.values():
                for cat, value in week_data['by_category'].items():
                    all_categories[cat] = all_categories.get(cat, 0) + value
            
            # Busca gastos REAIS do mês de comparação
            df_trans = carregar_transacoes('TODOS')
            real_categories = {}
            if not df_trans.empty:
                # Converte mes_comp para formato YYYY-MM
                meses_map = {
                    'Janeiro': '01', 'Fevereiro': '02', 'Março': '03', 'Abril': '04',
                    'Maio': '05', 'Junho': '06', 'Julho': '07', 'Agosto': '08',
                    'Setembro': '09', 'Outubro': '10', 'Novembro': '11', 'Dezembro': '12'
                }
                
                def mescomp_to_yearmonth(mescomp):
                    if pd.isna(mescomp):
                        return None
                    parts = mescomp.split()
                    if len(parts) == 2:
                        mes_nome, ano = parts
                        mes_num = meses_map.get(mes_nome, '00')
                        return f"{ano}-{mes_num}"
                    return None
                
                df_trans['year_month'] = df_trans['mes_comp'].apply(mescomp_to_yearmonth)
                df_month = df_trans[df_trans['year_month'] == comparison_month]
                
                # Soma por categoria (apenas débitos = valores positivos)
                df_debitos = df_month[df_month['valor'] > 0]
                if not df_debitos.empty:
                    real_by_cat = df_debitos.groupby('categoria')['valor'].sum()
                    real_categories = real_by_cat.to_dict()
            
            # Une todas as categorias (médias + reais)
            all_cats_union = set(all_categories.keys()) | set(real_categories.keys())
            
            # Ordena por valor médio
            sorted_cats = sorted(all_cats_union, key=lambda x: all_categories.get(x, 0), reverse=True)
            
            # Calcula totais
            total_medio = sum(all_categories.values())
            total_real = sum(real_categories.values())
            
            # Cria tabela com 5 colunas
            table_rows = []
            
            for cat in sorted_cats:
                value_medio = all_categories.get(cat, 0)
                value_real = real_categories.get(cat, 0)
                perc_medio = (value_medio / total_medio * 100) if total_medio > 0 else 0
                perc_real = (value_real / total_real * 100) if total_real > 0 else 0
                
                # Define cor baseada na diferença (vermelho se gastou mais que média)
                diff = value_real - value_medio
                real_color = COLORS['danger'] if diff > 0 else COLORS['success']
                
                table_rows.append(html.Tr([
                    html.Td(cat, style={
                        'color': COLORS['text_primary'],
                        'backgroundColor': COLORS['bg_card'],
                        'border': 'none',
                        'padding': '12px',
                        'borderBottom': f"1px solid {COLORS['bg_secondary']}"
                    }),
                    html.Td(f"R$ {value_medio:,.2f}", style={
                        'color': COLORS['primary'], 
                        'textAlign': 'right', 
                        'fontWeight': 'bold',
                        'backgroundColor': COLORS['bg_card'],
                        'border': 'none',
                        'padding': '12px',
                        'borderBottom': f"1px solid {COLORS['bg_secondary']}"
                    }),
                    html.Td(f"{perc_medio:.1f}%", style={
                        'color': COLORS['text_secondary'], 
                        'textAlign': 'right',
                        'backgroundColor': COLORS['bg_card'],
                        'border': 'none',
                        'padding': '12px',
                        'borderBottom': f"1px solid {COLORS['bg_secondary']}"
                    }),
                    html.Td(f"R$ {value_real:,.2f}", style={
                        'color': real_color, 
                        'textAlign': 'right', 
                        'fontWeight': 'bold',
                        'backgroundColor': COLORS['bg_card'],
                        'border': 'none',
                        'padding': '12px',
                        'borderBottom': f"1px solid {COLORS['bg_secondary']}"
                    }),
                    html.Td(f"{perc_real:.1f}%", style={
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
                    html.Th("Média Mensal", style={
                        'color': COLORS['text_primary'], 
                        'textAlign': 'right',
                        'backgroundColor': COLORS['bg_secondary'],
                        'border': 'none',
                        'padding': '12px',
                        'fontWeight': 'bold',
                        'borderBottom': f"2px solid {COLORS['primary']}"
                    }),
                    html.Th("% Média", style={
                        'color': COLORS['text_primary'], 
                        'textAlign': 'right',
                        'backgroundColor': COLORS['bg_secondary'],
                        'border': 'none',
                        'padding': '12px',
                        'fontWeight': 'bold',
                        'borderBottom': f"2px solid {COLORS['primary']}"
                    }),
                    html.Th("Valor Real", style={
                        'color': COLORS['text_primary'], 
                        'textAlign': 'right',
                        'backgroundColor': COLORS['bg_secondary'],
                        'border': 'none',
                        'padding': '12px',
                        'fontWeight': 'bold',
                        'borderBottom': f"2px solid {COLORS['primary']}"
                    }),
                    html.Th("% Real", style={
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
