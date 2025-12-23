# 🔧 Filtros e Callbacks - Dashboard V2

## Callbacks Implementados

### Total: 10 callbacks

```
1. display_page()              - Roteamento multi-page
2. atualizar_grafico_evolucao()     - Dashboard: Evolução 12 meses
3. atualizar_grafico_top_categorias() - Dashboard: Top 5 categorias
4. atualizar_grafico_top_fontes()    - Dashboard: Top 5 fontes
5. atualizar_grafico_real_ideal()    - Analytics: Real vs Ideal
6. atualizar_grafico_distribuicao()  - Analytics: Dia da semana
7. atualizar_grafico_acumulado()     - Analytics: Acumulado mensal
8. atualizar_filtros_transacoes()    - Transações: Popula dropdowns
9. atualizar_tabela_transacoes()     - Transações: Filtra e exibe
```

## 1. Roteamento Multi-Page

```python
@callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    """Roteia entre páginas baseado na URL"""
    if pathname == '/analytics':
        return create_analytics_page()
    elif pathname == '/transacoes':
        return create_transacoes_page()
    else:
        return create_dashboard_page()  # Default: "/"
```

**Funcionamento**:
- Escuta mudanças no `dcc.Location(id='url')`
- Sidebar altera pathname via `dcc.Link(href='/analytics')`
- Retorna layout completo da página escolhida

## 2-4. Dashboard - Gráficos

### Estrutura Comum

```python
@callback(
    Output('grafico-evolucao', 'figure'),
    [Input('store-mes-global', 'data')]
)
def atualizar_grafico_evolucao(mes_selecionado):
    """Atualiza gráfico de evolução com filtro de mês"""
    df = carregar_transacoes(mes_selecionado)
    fig = criar_grafico_evolucao(df, mes_selecionado)
    return fig
```

**Fluxo**:
1. Usuário seleciona mês no dropdown
2. Dropdown atualiza `store-mes-global`
3. Callback detecta mudança no Store
4. Carrega dados do banco (filtrados)
5. Cria gráfico Plotly
6. Retorna figura para componente

**Inputs**:
- `store-mes-global` (data): Mês selecionado ou "TODOS"

**Outputs**:
- `grafico-*` (figure): Objeto go.Figure do Plotly

## 5-7. Analytics - Gráficos

### Real vs Ideal

```python
@callback(
    Output('grafico-real-ideal', 'figure'),
    [Input('store-mes-global', 'data')]
)
def atualizar_grafico_real_ideal(mes_selecionado):
    """Compara gastos reais vs limite ideal"""
    df = carregar_transacoes(mes_selecionado)
    fig = criar_grafico_real_ideal(df, mes_selecionado)
    return fig
```

**Lógica**:
- Agrupa débitos por mês
- Compara com ORCAMENTO_IDEAL (R$ 2.000)
- Barras agrupadas: Real (vermelho) + Ideal (verde)

### Distribuição Temporal

```python
@callback(
    Output('grafico-distribuicao', 'figure'),
    [Input('store-mes-global', 'data')]
)
def atualizar_grafico_distribuicao(mes_selecionado):
    """Analisa gastos por dia da semana"""
    df = carregar_transacoes(mes_selecionado)
    fig = criar_grafico_distribuicao_temporal(df, mes_selecionado)
    return fig
```

**Lógica**:
- Extrai dia da semana de cada transação
- Agrupa por dia (Domingo-Sábado)
- Barras horizontais com valores

### Evolução Acumulada

```python
@callback(
    Output('grafico-acumulado', 'figure'),
    [Input('store-mes-global', 'data')]
)
def atualizar_grafico_acumulado(mes_selecionado):
    """Mostra progressão acumulada de gastos no mês"""
    df = carregar_transacoes(mes_selecionado)
    fig = criar_grafico_acumulado(df, mes_selecionado)
    return fig
```

**Lógica**:
- Ordena transações por data
- Calcula soma acumulada (cumsum)
- Linha com área preenchida

## 8. Transações - Populando Filtros

```python
@callback(
    [Output('filtro-categoria-transacoes', 'options'),
     Output('filtro-fonte-transacoes', 'options'),
     Output('filtro-mes-comp-transacoes', 'options')],
    [Input('store-mes-global', 'data')]
)
def atualizar_filtros_transacoes(mes_selecionado):
    """Popula dropdowns com valores únicos do banco"""
    df = carregar_transacoes(mes_selecionado)
    
    # Apenas débitos
    df_debitos = df[df['valor'] > 0].copy()
    
    # Categorias únicas
    categorias = [{'label': 'Todas', 'value': 'TODOS'}]
    categorias += [
        {'label': cat, 'value': cat} 
        for cat in sorted(df_debitos['categoria'].unique())
    ]
    
    # Fontes únicas
    fontes = [{'label': 'Todas', 'value': 'TODOS'}]
    fontes += [
        {'label': fonte, 'value': fonte} 
        for fonte in sorted(df_debitos['fonte'].unique())
    ]
    
    # Meses de compensação únicos
    meses = [{'label': 'Todos', 'value': 'TODOS'}]
    meses += [
        {'label': mes, 'value': mes} 
        for mes in sorted(df_debitos['mes_comp'].unique(), reverse=True)
    ]
    
    return categorias, fontes, meses
```

**Outputs** (3 simultâneos):
- `filtro-categoria-transacoes` (options)
- `filtro-fonte-transacoes` (options)
- `filtro-mes-comp-transacoes` (options)

## 9. Transações - Filtrando e Exibindo

### Callback Completo

```python
@callback(
    Output('tabela-transacoes-container', 'children'),
    [Input('store-mes-global', 'data'),
     Input('filtro-categoria-transacoes', 'value'),
     Input('filtro-fonte-transacoes', 'value'),
     Input('filtro-status-transacoes', 'value'),
     Input('filtro-mes-comp-transacoes', 'value'),
     Input('filtro-data-transacoes', 'start_date'),
     Input('filtro-data-transacoes', 'end_date')]
)
def atualizar_tabela_transacoes(
    mes_selecionado, 
    categoria_filtro, 
    fonte_filtro, 
    status_filtro, 
    mes_comp_filtro, 
    data_inicio, 
    data_fim
):
    """Filtra e exibe transações com 7 inputs"""
    # ...lógica de filtros...
```

### Fluxo de Filtros

```python
# 1. Carregar dados
df = carregar_transacoes(mes_selecionado)

# 2. Apenas débitos
df_filtrado = df[df['valor'] > 0].copy()

# 3. Filtro de Categoria
if categoria_filtro and categoria_filtro != 'TODOS':
    df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_filtro]

# 4. Filtro de Fonte
if fonte_filtro and fonte_filtro != 'TODOS':
    df_filtrado = df_filtrado[df_filtrado['fonte'] == fonte_filtro]

# 5. Filtro de Status
if status_filtro == 'CATEGORIZADAS':
    df_filtrado = df_filtrado[df_filtrado['categoria'] != 'A definir']
elif status_filtro == 'PENDENTES':
    df_filtrado = df_filtrado[df_filtrado['categoria'] == 'A definir']

# 6. Filtro de Mês de Compensação
if mes_comp_filtro and mes_comp_filtro != 'TODOS':
    df_filtrado = df_filtrado[df_filtrado['mes_comp'] == mes_comp_filtro]

# 7. Filtro de Data Início
if data_inicio:
    try:
        df_filtrado = df_filtrado[
            df_filtrado['data'] >= pd.to_datetime(data_inicio)
        ]
    except:
        pass  # Ignora erros de parsing

# 8. Filtro de Data Fim
if data_fim:
    try:
        df_filtrado = df_filtrado[
            df_filtrado['data'] <= pd.to_datetime(data_fim)
        ]
    except:
        pass
```

### Ordenação e Limite

```python
# Ordenação: mes_comp (↑), fonte (↓), data (↑)
df_tabela = df_filtrado.sort_values(
    ['mes_comp', 'fonte', 'data'],
    ascending=[True, False, True]
).head(100)  # Limita a 100
```

### Cálculo de Subtotal

```python
# Subtotal ANTES de formatar datas
subtotal = df_tabela['valor_normalizado'].sum()

# Formatar data após ordenação
df_tabela['data'] = pd.to_datetime(df_tabela['data']).dt.strftime('%d/%m/%Y')
```

### Construção da Tabela HTML

```python
# Criar linhas da tabela
rows = []
for _, row in df_tabela.iterrows():
    # Destaque para "A definir"
    categoria_style = {
        'backgroundColor': COLORS['warning'], 
        'color': COLORS['bg_primary'],
        'padding': '4px 8px',
        'borderRadius': '4px',
        'fontWeight': 'bold'
    } if row['categoria'] == 'A definir' else {}
    
    rows.append(html.Tr([
        html.Td(row['data'], style={...}),
        html.Td(row['descricao'], style={...}),
        html.Td(f"R$ {row['valor_normalizado']:,.2f}", style={...}),
        html.Td(html.Span(row['categoria'], style=categoria_style), style={...}),
        html.Td(row['fonte'], style={...}),
        html.Td(row['mes_comp'], style={...}),
    ]))

# Montar estrutura completa
return html.Div([
    # Subtotal
    html.Div([
        html.Span(f"Mostrando {len(df_tabela)} de {len(df_filtrado)}"),
        html.Span(f" • Subtotal: R$ {subtotal:,.2f}", style={'color': COLORS['primary'], 'fontWeight': 'bold'})
    ]),
    
    # Tabela
    html.Table([
        html.Thead(...),
        html.Tbody(rows)
    ])
])
```

## Estado Global vs Local

### Estado Global
```python
dcc.Store(id='store-mes-global', data='TODOS')
```
- Compartilhado entre TODAS as páginas
- Atualizado pelo dropdown de mês
- Input de 7 callbacks (Dashboard + Analytics + Transações)

### Estado Local (Transações)
```python
# Componentes que SÓ existem em /transacoes
'filtro-categoria-transacoes'
'filtro-fonte-transacoes'
'filtro-status-transacoes'
'filtro-mes-comp-transacoes'
'filtro-data-transacoes'
```
- Não acessíveis de outras páginas
- Callback precisa lidar com valores None

## Problemas Comuns

### 1. Callback Error com Componentes Inexistentes

**Erro**: "Callback error updating component X"

**Causa**: Callback referencia componente que não existe na página atual

**Solução**: 
```python
# ❌ NÃO use prevent_initial_call=True (impede carregamento)
# ✅ Use null checks
if not all([categoria_filtro, fonte_filtro, status_filtro]):
    return "Carregando..."
```

### 2. Filtros Não Atualizam

**Causa**: Valores None passados para comparações

**Solução**:
```python
# ❌ ERRADO
if categoria_filtro != 'TODOS':

# ✅ CORRETO
if categoria_filtro and categoria_filtro != 'TODOS':
```

### 3. Ordenação Quebra Após Formatação

**Causa**: `sort_values()` depois de `.dt.strftime()`

**Solução**:
```python
# ✅ CORRETO: Ordenar ANTES de formatar
df = df.sort_values(['mes_comp', 'fonte', 'data'])
df['data'] = df['data'].dt.strftime('%d/%m/%Y')
```

### 4. Subtotal Incorreto

**Causa**: Calcular subtotal depois de `.head(100)`

**Solução**:
```python
# ✅ CORRETO: Subtotal ANTES de limitar
subtotal = df_filtrado['valor_normalizado'].sum()
df_tabela = df_filtrado.head(100)
```

## Performance Tips

### Otimizar Queries
```python
# ❌ LENTO: Carregar tudo e filtrar em Python
df = carregar_transacoes()  # 2.256 registros
df = df[df['mes_comp'] == '2025-01']

# ✅ RÁPIDO: Filtrar no SQL
df = carregar_transacoes(mes_filtro='2025-01')  # ~100 registros
```

### Limitar Registros
```python
# Sempre usar .head() para tabelas
df_tabela = df_filtrado.sort_values(...).head(100)
```

### Cache de Callbacks
```python
# Dash cacheia automaticamente callbacks não modificados
# Se inputs não mudarem, callback não executa
```

## Debug

### Imprimir Inputs
```python
@callback(...)
def atualizar_tabela(...):
    print(f"DEBUG: mes={mes_selecionado}, cat={categoria_filtro}")
    # ...
```

### Verificar Filtros
```python
print(f"Antes: {len(df)} registros")
df_filtrado = df[df['categoria'] == categoria_filtro]
print(f"Depois: {len(df_filtrado)} registros")
```

### Ctx.triggered
```python
from dash import ctx

@callback(...)
def atualizar_tabela(...):
    print(f"Triggered by: {ctx.triggered_id}")
    # Mostra qual input disparou o callback
```
