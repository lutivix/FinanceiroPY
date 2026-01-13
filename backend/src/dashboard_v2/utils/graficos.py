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
    
    # Filtrar apenas débitos (valor positivo = gasto)
    df_debitos = df[df['valor'] > 0].copy()
    
    # Agrupar por mês
    evolucao = df_debitos.groupby('mes_comp')['valor'].sum().reset_index()
    
    # Converter mes_comp para datetime usando mapeamento manual (fix para março no Windows)
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    # Mapeamento manual de meses em português para número
    meses_map = {
        'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
        'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
        'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
    }
    
    def converter_mes_para_data(mes_comp_str):
        """Converte 'Março 2025' para datetime(2025, 3, 1)"""
        try:
            partes = mes_comp_str.split()
            if len(partes) == 2:
                mes_nome = partes[0].lower()
                ano = int(partes[1])
                mes_num = meses_map.get(mes_nome)
                if mes_num:
                    return datetime(ano, mes_num, 1)
        except:
            pass
        return None
    
    evolucao['data_ordenacao'] = evolucao['mes_comp'].apply(converter_mes_para_data)
    
    # Remover linhas onde conversão falhou (None)
    evolucao = evolucao.dropna(subset=['data_ordenacao'])
    
    # Criar dicionário com valores reais
    valores_reais = dict(zip(evolucao['mes_comp'], evolucao['valor']))
    
    # Criar range completo dos últimos 12 meses
    data_mais_recente = evolucao['data_ordenacao'].max()
    data_inicial = data_mais_recente - relativedelta(months=11)
    
    # Mapeamento de meses em português
    meses_pt = {
        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
        5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
        9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
    }
    
    meses_completos = []
    data_atual = data_inicial
    while data_atual <= data_mais_recente:
        # Gerar nome do mês em português com encoding correto
        mes_nome = meses_pt[data_atual.month].capitalize()
        ano = data_atual.year
        mes_formatado = f"{mes_nome} {ano}"
        
        # Procurar mês correspondente nos dados reais (comparação por data usando a função manual)
        valor = 0
        for mes_real, val_real in valores_reais.items():
            data_real = converter_mes_para_data(mes_real)
            if data_real and data_real.year == ano and data_real.month == data_atual.month:
                valor = val_real
                break
        
        meses_completos.append({
            'mes_comp': mes_formatado,
            'data_ordenacao': data_atual,
            'valor': valor
        })
        data_atual += relativedelta(months=1)
    
    evolucao = pd.DataFrame(meses_completos)
    
    # Ordenar por data
    evolucao = evolucao.sort_values('data_ordenacao')
    evolucao = evolucao.reset_index(drop=True)
    
    # Criar labels na ordem correta
    labels_ordenados = evolucao['mes_comp'].tolist()
    
    fig = go.Figure()
    
    # Linha com área preenchida - usar índice numérico no eixo X
    fig.add_trace(go.Scatter(
        x=list(range(len(evolucao))),
        y=evolucao['valor'],
        mode='lines',
        name='Gastos',
        line=dict(color=COLORS['primary'], width=3),
        fill='tozeroy',
        fillcolor='rgba(46, 134, 171, 0.2)',  # primary color with 20% opacity
        hovertemplate='<b>%{text}</b><br>R$ %{y:,.2f}<extra></extra>',
        text=labels_ordenados
    ))
    
    fig.update_layout(
        **PLOTLY_TEMPLATE['layout'],
        showlegend=False,
        margin=dict(l=40, r=20, t=20, b=40)
    )
    
    fig.update_xaxes(
        title='',
        gridcolor=COLORS['grid'],
        showgrid=False,
        tickmode='array',
        tickvals=list(range(len(evolucao))),
        ticktext=labels_ordenados
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
    
    # Converter mes_comp para datetime para ordenação cronológica
    import locale
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
        except:
            pass
    
    # Agrupar por mês primeiro
    mensal = df_debitos.groupby('mes_comp')['valor'].sum().reset_index()
    mensal['data_ordenacao'] = pd.to_datetime(mensal['mes_comp'], format='%B %Y', errors='coerce')
    
    # Remover linhas onde conversão falhou (NaT)
    mensal = mensal.dropna(subset=['data_ordenacao'])
    
    # Ordenar por data
    mensal = mensal.sort_values('data_ordenacao')
    
    # Pegar últimos 6 meses
    mensal = mensal.tail(6)
    mensal = mensal.reset_index(drop=True)
    
    # Calcular acumulado
    mensal['acumulado'] = mensal['valor'].cumsum()
    
    # Criar labels na ordem correta
    labels_ordenados = mensal['mes_comp'].tolist()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=list(range(len(mensal))),
        y=mensal['acumulado'],
        mode='lines+markers',
        line=dict(color=COLORS['success'], width=3),
        marker=dict(size=8, color=COLORS['success']),
        fill='tozeroy',
        fillcolor=f"rgba(6, 167, 125, 0.2)",
        hovertemplate='<b>%{text}</b><br>Acumulado: R$ %{y:,.2f}<extra></extra>',
        text=labels_ordenados
    ))
    
    fig.update_layout(
        **PLOTLY_TEMPLATE['layout'],
        showlegend=False,
        margin=dict(l=60, r=40, t=40, b=80)
    )
    
    fig.update_xaxes(
        title='',
        gridcolor=COLORS['grid'],
        showgrid=False,
        tickmode='array',
        tickvals=list(range(len(mensal))),
        ticktext=labels_ordenados
    )
    
    fig.update_yaxes(
        title='Acumulado (R$)',
        gridcolor=COLORS['grid'],
        showgrid=True,
        tickformat=',.0f'
    )
    
    return fig


def criar_grafico_ideals_comparison(df, mes_filtro, categoria_filtro='TODOS', fonte_filtro='TODOS', view_by='category'):
    """
    Cria gráfico de comparação Real vs Ideal com Diferença
    
    Args:
        df: DataFrame com transações
        mes_filtro: Filtro de mês ('TODOS' ou 'YYYY-MM')
        categoria_filtro: Filtro de categoria
        fonte_filtro: Filtro de fonte
        view_by: 'category' ou 'source' (determina agrupamento quando ambos filtros = TODOS)
    
    Returns:
        Figure do Plotly
    """
    from dashboard_v2.config import (
        ORCAMENTO_IDEAL, ORCAMENTO_IDEAL_FONTE,
        ORCAMENTO_IDEAL_CAT_VISA_REC, ORCAMENTO_IDEAL_CAT_VISA_BIA, ORCAMENTO_IDEAL_CAT_VISA_FIS,
        ORCAMENTO_IDEAL_CAT_PIX, ORCAMENTO_IDEAL_CAT_MASTER_VIRTUAL
    )
    
    # Mapear fontes para seus orçamentos específicos
    ORCAMENTO_POR_FONTE = {
        'Visa Recorrente': ORCAMENTO_IDEAL_CAT_VISA_REC,
        'Visa Bia': ORCAMENTO_IDEAL_CAT_VISA_BIA,
        'Visa Físico': ORCAMENTO_IDEAL_CAT_VISA_FIS,
        'PIX': ORCAMENTO_IDEAL_CAT_PIX,
        'Master Virtual': ORCAMENTO_IDEAL_CAT_MASTER_VIRTUAL,
    }
    
    if len(df) == 0:
        return go.Figure().update_layout(
            **PLOTLY_TEMPLATE['layout'],
            title="No data available"
        )
    
    # Filtrar apenas débitos
    df_debitos = df[df['valor'] > 0].copy()
    
    # Determinar se é visão anual (12 meses)
    is_annual = (mes_filtro == 'TODOS')
    multiplier = 12 if is_annual else 1
    
    # Decidir agrupamento baseado nos filtros e view_by
    if categoria_filtro != 'TODOS':
        # Categoria específica selecionada - mostrar apenas ela
        grupo = df_debitos[df_debitos['categoria'] == categoria_filtro]
        
        # Aplicar filtro de fonte se houver
        if fonte_filtro != 'TODOS':
            grupo = grupo[grupo['fonte'] == fonte_filtro]
            title_suffix = f" - {categoria_filtro} ({fonte_filtro})"
        else:
            title_suffix = f" - {categoria_filtro}"
        
        real_total = grupo['valor_normalizado'].sum()
        ideal_total = ORCAMENTO_IDEAL.get(categoria_filtro, 0) * multiplier
        labels = [categoria_filtro]
        real_values = [real_total]
        ideal_values = [ideal_total]
        
    elif fonte_filtro != 'TODOS' and view_by == 'source':
        # Fonte específica selecionada E view_by=source - mostrar apenas ela
        grupo = df_debitos[df_debitos['fonte'] == fonte_filtro]
        real_total = grupo['valor_normalizado'].sum()
        ideal_total = ORCAMENTO_IDEAL_FONTE.get(fonte_filtro, 0) * multiplier
        labels = [fonte_filtro]
        real_values = [real_total]
        ideal_values = [ideal_total]
        title_suffix = f" - {fonte_filtro}"
        
    else:
        # Visão geral: baseado no view_by
        # Aplicar filtro de fonte se houver (mas manter agrupamento por categoria)
        df_filtrado = df_debitos
        if fonte_filtro != 'TODOS':
            df_filtrado = df_filtrado[df_filtrado['fonte'] == fonte_filtro]
        
        if view_by == 'source':
            # TODAS as fontes (ordenadas por valor)
            por_fonte = df_filtrado.groupby('fonte')['valor_normalizado'].sum()
            todas = por_fonte.sort_values(ascending=True)  # Menor para maior (bottom to top)
            
            labels = todas.index.tolist()
            real_values = todas.values.tolist()
            ideal_values = [ORCAMENTO_IDEAL_FONTE.get(fonte, 0) * multiplier for fonte in labels]
            title_suffix = " - All Sources"
        else:
            # TODAS as categorias (ordenadas por valor)
            por_categoria = df_filtrado.groupby('categoria')['valor_normalizado'].sum()
            todas = por_categoria.sort_values(ascending=True)  # Menor para maior (bottom to top)
            
            labels = todas.index.tolist()
            real_values = todas.values.tolist()
            
            # Usar orçamento específico da fonte se disponível
            if fonte_filtro != 'TODOS' and fonte_filtro in ORCAMENTO_POR_FONTE:
                orcamento_categorias = ORCAMENTO_POR_FONTE[fonte_filtro]
                ideal_values = [orcamento_categorias.get(cat, 0) * multiplier for cat in labels]
            else:
                ideal_values = [ORCAMENTO_IDEAL.get(cat, 0) * multiplier for cat in labels]
            
            # Ajustar título se houver filtro de fonte
            if fonte_filtro != 'TODOS':
                title_suffix = f" - All Categories (Source: {fonte_filtro})"
            else:
                title_suffix = " - All Categories"
    
    # Calcular diferenças (positivo = excesso, negativo = economia)
    diff_values = [real - ideal for real, ideal in zip(real_values, ideal_values)]
    
    # Cores para diferença (verde se economia, vermelho se excesso)
    diff_colors = [COLORS['danger'] if d > 0 else COLORS['success'] for d in diff_values]
    
    fig = go.Figure()
    
    # Determinar orientação: vertical para categories, horizontal para sources
    is_vertical = (view_by == 'category' and categoria_filtro == 'TODOS')
    
    if is_vertical:
        # Barras VERTICAIS (para categorias)
        fig.add_trace(go.Bar(
            x=labels,
            y=real_values,
            name='Real',
            marker=dict(color=COLORS['primary']),
            hovertemplate='<b>%{x}</b><br>Real: R$ %{y:,.2f}<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            x=labels,
            y=ideal_values,
            name='Ideal',
            marker=dict(color=COLORS['success'], opacity=0.6),
            hovertemplate='<b>%{x}</b><br>Ideal: R$ %{y:,.2f}<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            x=labels,
            y=diff_values,
            name='Difference',
            marker=dict(color=diff_colors),
            hovertemplate='<b>%{x}</b><br>Diff: R$ %{y:,.2f}<extra></extra>'
        ))
    else:
        # Barras HORIZONTAIS (para fontes ou itens individuais)
        fig.add_trace(go.Bar(
            y=labels,
            x=real_values,
            name='Real',
            orientation='h',
            marker=dict(color=COLORS['primary']),
            hovertemplate='<b>%{y}</b><br>Real: R$ %{x:,.2f}<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            y=labels,
            x=ideal_values,
            name='Ideal',
            orientation='h',
            marker=dict(color=COLORS['success'], opacity=0.6),
            hovertemplate='<b>%{y}</b><br>Ideal: R$ %{x:,.2f}<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            y=labels,
            x=diff_values,
            name='Difference',
            orientation='h',
            marker=dict(color=diff_colors),
            hovertemplate='<b>%{y}</b><br>Diff: R$ %{x:,.2f}<extra></extra>'
        ))
    
    period_text = "Last 12 Months" if is_annual else mes_filtro
    
    # Apply template and then override specific settings
    fig.update_layout(**PLOTLY_TEMPLATE['layout'])
    
    if is_vertical:
        # Layout para barras verticais
        fig.update_layout(
            title=f"Budget Comparison{title_suffix} ({period_text})",
            barmode='group',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=60, r=40, t=80, b=120),
            height=700
        )
        
        fig.update_xaxes(
            title='',
            gridcolor=COLORS['grid'],
            showgrid=False,
            tickangle=-45
        )
        
        fig.update_yaxes(
            title='Amount (R$)',
            gridcolor=COLORS['grid'],
            showgrid=True,
            tickformat=',.0f'
        )
    else:
        # Layout para barras horizontais
        fig.update_layout(
            title=f"Budget Comparison{title_suffix} ({period_text})",
            barmode='group',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=150, r=40, t=80, b=60),
            height=max(600, len(labels) * 60)
        )
        
        fig.update_xaxes(
            title='Amount (R$)',
            gridcolor=COLORS['grid'],
            showgrid=True,
            tickformat=',.0f'
        )
        
        fig.update_yaxes(
            title='',
            gridcolor=COLORS['grid'],
            showgrid=False
        )
    
    return fig
