"""
Callbacks para gráficos do Dashboard
Funções que geram os gráficos Plotly baseado nos dados
"""

import pandas as pd
import plotly.graph_objects as go
from dashboard_v2.config import COLORS, PLOTLY_TEMPLATE
from dashboard_v2.utils.database import carregar_transacoes

def criar_grafico_evolucao(mes_selecionado='TODOS'):
    """
    Cria gráfico de evolução mensal (linha com área)
    
    Args:
        mes_selecionado: Filtro de mês (não usado aqui, sempre mostra últimos 12)
    
    Returns:
        Figure do Plotly
    """
    df = carregar_transacoes('TODOS')
    
    if len(df) == 0:
        return go.Figure().update_layout(
            **PLOTLY_TEMPLATE['layout'],
            title="Sem dados disponíveis"
        )
    
    # Filtrar apenas débitos
    df_debitos = df[df['valor'] < 0].copy()
    
    # Agrupar por mês
    evolucao = df_debitos.groupby('mes_comp')['valor_normalizado'].sum().reset_index()
    evolucao = evolucao.sort_values('mes_comp')
    
    # Pegar últimos 12 meses
    evolucao = evolucao.tail(12)
    
    fig = go.Figure()
    
    # Linha com área preenchida
    fig.add_trace(go.Scatter(
        x=evolucao['mes_comp'],
        y=evolucao['valor_normalizado'],
        mode='lines',
        name='Gastos',
        line=dict(color=COLORS['primary'], width=3),
        fill='tozeroy',
        fillcolor='rgba(46, 134, 171, 0.2)',  # primary color with 20% opacity
        hovertemplate='<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        **PLOTLY_TEMPLATE['layout'],
        showlegend=False,
        margin=dict(l=40, r=20, t=20, b=40)
    )
    
    fig.update_xaxes(
        title='',
        gridcolor=COLORS['grid'],
        showgrid=False
    )
    
    fig.update_yaxes(
        title='',
        gridcolor=COLORS['grid'],
        tickformat=',.0f',
        tickprefix='R$ '
    )
    
    return fig

def criar_grafico_top_categorias(mes_selecionado='TODOS'):
    """
    Cria gráfico de top 5 categorias (barras horizontais)
    
    Args:
        mes_selecionado: Filtro de mês
    
    Returns:
        Figure do Plotly
    """
    df = carregar_transacoes(mes_selecionado)
    
    if len(df) == 0:
        return go.Figure().update_layout(
            **PLOTLY_TEMPLATE['layout'],
            title="Sem dados disponíveis"
        )
    
    # Filtrar apenas débitos e categorias válidas
    df_debitos = df[(df['valor'] < 0) & (df['categoria'] != 'A definir')].copy()
    
    # Top 5 categorias
    top_cat = df_debitos.groupby('categoria')['valor_normalizado'].sum().nlargest(5).reset_index()
    top_cat = top_cat.sort_values('valor_normalizado')  # Ordem crescente para barras horizontais
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=top_cat['categoria'],
        x=top_cat['valor_normalizado'],
        orientation='h',
        marker=dict(
            color=COLORS['chart_1'],
            line=dict(color=COLORS['border'], width=1)
        ),
        text=top_cat['valor_normalizado'].apply(lambda x: f'R$ {x:,.0f}'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>R$ %{x:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        **PLOTLY_TEMPLATE['layout'],
        showlegend=False,
        margin=dict(l=100, r=80, t=20, b=40)
    )
    
    fig.update_xaxes(
        title='',
        gridcolor=COLORS['grid'],
        showgrid=True,
        tickformat=',.0f'
    )
    
    fig.update_yaxes(
        title='',
        gridcolor=COLORS['grid']
    )
    
    return fig

def criar_grafico_top_fontes(mes_selecionado='TODOS'):
    """
    Cria gráfico de top 5 fontes (barras horizontais)
    
    Args:
        mes_selecionado: Filtro de mês
    
    Returns:
        Figure do Plotly
    """
    df = carregar_transacoes(mes_selecionado)
    
    if len(df) == 0:
        return go.Figure().update_layout(
            **PLOTLY_TEMPLATE['layout'],
            title="Sem dados disponíveis"
        )
    
    # Filtrar apenas débitos
    df_debitos = df[df['valor'] < 0].copy()
    
    # Top 5 fontes
    top_fontes = df_debitos.groupby('fonte')['valor_normalizado'].sum().nlargest(5).reset_index()
    top_fontes = top_fontes.sort_values('valor_normalizado')  # Ordem crescente
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=top_fontes['fonte'],
        x=top_fontes['valor_normalizado'],
        orientation='h',
        marker=dict(
            color=COLORS['chart_3'],
            line=dict(color=COLORS['border'], width=1)
        ),
        text=top_fontes['valor_normalizado'].apply(lambda x: f'R$ {x:,.0f}'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>R$ %{x:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        **PLOTLY_TEMPLATE['layout'],
        showlegend=False,
        margin=dict(l=120, r=80, t=20, b=40)
    )
    
    fig.update_xaxes(
        title='',
        gridcolor=COLORS['grid'],
        showgrid=True,
        tickformat=',.0f'
    )
    
    fig.update_yaxes(
        title='',
        gridcolor=COLORS['grid']
    )
    
    return fig
