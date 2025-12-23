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
    
    # Filtrar apenas débitos (valor POSITIVO = gastos) e categorias válidas
    df_debitos = df[(df['valor'] > 0) & (df['categoria'] != 'A definir')].copy()
    
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
    
    # Filtrar apenas débitos (valor POSITIVO = gastos)
    df_debitos = df[df['valor'] > 0].copy()
    
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

def criar_grafico_real_ideal(mes_selecionado='TODOS'):
    """
    Cria gráfico Real vs Ideal por categoria (barras horizontais agrupadas)
    
    Args:
        mes_selecionado: Filtro de mês
    
    Returns:
        Figure do Plotly
    """
    from dashboard_v2.config import ORCAMENTO_IDEAL
    
    df = carregar_transacoes(mes_selecionado)
    
    if len(df) == 0:
        return go.Figure().update_layout(
            **PLOTLY_TEMPLATE['layout'],
            title="Sem dados disponíveis"
        )
    
    # Filtrar débitos e agrupar por categoria
    df_debitos = df[(df['valor'] > 0) & (df['categoria'] != 'A definir')].copy()
    real = df_debitos.groupby('categoria')['valor_normalizado'].sum().reset_index()
    real.columns = ['categoria', 'real']
    
    # Criar DataFrame com orçamento ideal
    ideal = pd.DataFrame(list(ORCAMENTO_IDEAL.items()), columns=['categoria', 'ideal'])
    
    # Merge
    comparacao = pd.merge(real, ideal, on='categoria', how='outer').fillna(0)
    comparacao['diferenca'] = comparacao['real'] - comparacao['ideal']
    comparacao = comparacao.sort_values('real', ascending=True)
    
    # Top 10 categorias com maior gasto
    comparacao = comparacao.nlargest(10, 'real')
    
    fig = go.Figure()
    
    # Barra Real
    fig.add_trace(go.Bar(
        y=comparacao['categoria'],
        x=comparacao['real'],
        name='Real',
        orientation='h',
        marker=dict(color=COLORS['primary']),
        text=comparacao['real'].apply(lambda x: f'R$ {x:,.0f}'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Real: R$ %{x:,.2f}<extra></extra>'
    ))
    
    # Barra Ideal
    fig.add_trace(go.Bar(
        y=comparacao['categoria'],
        x=comparacao['ideal'],
        name='Ideal',
        orientation='h',
        marker=dict(color=COLORS['info'], opacity=0.6),
        text=comparacao['ideal'].apply(lambda x: f'R$ {x:,.0f}'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Ideal: R$ %{x:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        **PLOTLY_TEMPLATE['layout'],
        barmode='group',
        margin=dict(l=120, r=100, t=40, b=60),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    
    fig.update_xaxes(
        title='Valor (R$)',
        gridcolor=COLORS['grid'],
        showgrid=True,
        tickformat=',.0f'
    )
    
    fig.update_yaxes(
        title='',
        gridcolor=COLORS['grid']
    )
    
    return fig

def criar_grafico_distribuicao_temporal(mes_selecionado='TODOS'):
    """
    Cria gráfico de distribuição por dia da semana
    
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
    
    # Filtrar débitos
    df_debitos = df[df['valor'] > 0].copy()
    
    # Extrair dia da semana
    df_debitos['dia_semana'] = pd.to_datetime(df_debitos['data']).dt.day_name()
    dias_ordem = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dias_pt = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    
    # Agrupar por dia da semana
    dist = df_debitos.groupby('dia_semana')['valor_normalizado'].sum().reindex(dias_ordem).fillna(0)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=dias_pt,
        y=dist.values,
        marker=dict(
            color=dist.values,
            colorscale='Blues',
            showscale=False
        ),
        text=[f'R$ {v:,.0f}' for v in dist.values],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        **PLOTLY_TEMPLATE['layout'],
        showlegend=False,
        margin=dict(l=60, r=40, t=40, b=80)
    )
    
    fig.update_xaxes(
        title='',
        gridcolor=COLORS['grid'],
        showgrid=False
    )
    
    fig.update_yaxes(
        title='Gastos (R$)',
        gridcolor=COLORS['grid'],
        showgrid=True,
        tickformat=',.0f'
    )
    
    return fig

def criar_grafico_acumulado(mes_selecionado='TODOS'):
    """
    Cria gráfico de gastos acumulados no mês
    
    Args:
        mes_selecionado: Filtro de mês
    
    Returns:
        Figure do Plotly
    """
    df = carregar_transacoes('TODOS')  # Sempre pegar todos para calcular acumulado
    
    if len(df) == 0:
        return go.Figure().update_layout(
            **PLOTLY_TEMPLATE['layout'],
            title="Sem dados disponíveis"
        )
    
    # Filtrar débitos e últimos 6 meses
    df_debitos = df[df['valor'] > 0].copy()
    meses_unicos = sorted(df_debitos['mes_comp'].unique(), reverse=True)[:6]
    df_debitos = df_debitos[df_debitos['mes_comp'].isin(meses_unicos)]
    
    # Agrupar por mês e calcular acumulado
    mensal = df_debitos.groupby('mes_comp')['valor_normalizado'].sum().reset_index()
    mensal = mensal.sort_values('mes_comp')
    mensal['acumulado'] = mensal['valor_normalizado'].cumsum()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=mensal['mes_comp'],
        y=mensal['acumulado'],
        mode='lines+markers',
        line=dict(color=COLORS['success'], width=3),
        marker=dict(size=8, color=COLORS['success']),
        fill='tozeroy',
        fillcolor=f"rgba(6, 167, 125, 0.2)",
        hovertemplate='<b>%{x}</b><br>Acumulado: R$ %{y:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        **PLOTLY_TEMPLATE['layout'],
        showlegend=False,
        margin=dict(l=60, r=40, t=40, b=80)
    )
    
    fig.update_xaxes(
        title='',
        gridcolor=COLORS['grid'],
        showgrid=False
    )
    
    fig.update_yaxes(
        title='Acumulado (R$)',
        gridcolor=COLORS['grid'],
        showgrid=True,
        tickformat=',.0f'
    )
    
    return fig
