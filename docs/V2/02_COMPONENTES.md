# 🧩 Componentes - Dashboard V2

## Hierarquia de Componentes

```
App (main.py)
├── dcc.Location (url)
├── dcc.Store (store-mes-global)
├── Sidebar (components/sidebar.py)
└── Page Content (pages/*.py)
    ├── Dashboard (pages/dashboard.py)
    │   ├── Header + Dropdown Mês
    │   ├── 3 Cards de Métricas
    │   ├── Gráfico Hero (Evolução)
    │   └── 2 Gráficos Laterais (Top Categorias + Top Fontes)
    │
    ├── Analytics (pages/analytics.py)
    │   ├── Header
    │   ├── Gráfico Real vs Ideal
    │   ├── Gráfico Distribuição Temporal
    │   └── Gráfico Evolução Acumulada
    │
    └── Transações (pages/transacoes.py)
        ├── Header
        ├── Card de Filtros (5 filtros em 2 linhas)
        └── Card com Tabela + Subtotal
```

## Sidebar

**Arquivo**: `components/sidebar.py`

```python
def create_sidebar():
    return html.Div([
        # Logo
        html.Div([
            html.I(className="fas fa-chart-line", style={...}),
            html.Span("Dashboard", style={...})
        ], className="sidebar-header"),
        
        # Menu de Navegação
        html.Nav([
            dcc.Link([
                html.I(className="fas fa-home"),
                html.Span("Dashboard")
            ], href="/", className="nav-link"),
            
            dcc.Link([
                html.I(className="fas fa-chart-bar"),
                html.Span("Analytics")
            ], href="/analytics", className="nav-link"),
            
            dcc.Link([
                html.I(className="fas fa-list"),
                html.Span("Transações")
            ], href="/transacoes", className="nav-link"),
        ])
    ], className="sidebar")
```

**Características**:
- Fixa no lado esquerdo (280px de largura)
- Ícones FontAwesome 6
- 3 links de navegação
- Estilo com hover states

**CSS**:
```css
.sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    width: 280px;
    background-color: #1A1A2E;
    padding: 24px 0;
}

.nav-link {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 24px;
    color: #A0AEC0;
    text-decoration: none;
}

.nav-link:hover {
    background-color: #1F2A44;
    color: #2E86AB;
}
```

## Cards de Métricas (Dashboard)

**Localização**: `pages/dashboard.py` - linhas ~40-120

```python
def create_metric_card(icon_class, label, value, color):
    return html.Div([
        # Container do Ícone
        html.Div(
            html.I(className=icon_class, style={'fontSize': '18px'}),
            style={
                'width': '36px',
                'height': '36px',
                'borderRadius': '8px',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'background': f'linear-gradient(135deg, {color}20, {color}10)'
            }
        ),
        
        # Label e Valor
        html.Div([
            html.P(label, style={'color': COLORS['text_secondary'], 'fontSize': '12px'}),
            html.H3(value, style={'color': COLORS['text_primary'], 'fontSize': '24px'})
        ], style={'flex': '1'})
    ], className="custom-card", style={
        'display': 'flex',
        'alignItems': 'center',
        'gap': '16px',
        'padding': '20px'
    })
```

**3 Cards Criados**:
1. **Total Gasto** - Ícone: wallet, Cor: primary
2. **Cartões** - Ícone: credit-card, Cor: info
3. **Pix + Boletos** - Ícone: money-bill-wave, Cor: success

**Layout**: Grid 3 colunas com gap 16px

## Dropdown de Mês

**Localização**: `pages/dashboard.py` - linha ~30

```python
dcc.Dropdown(
    id='filtro-mes-dashboard',
    options=[{'label': 'Todos os meses', 'value': 'TODOS'}],
    value='TODOS',
    clearable=False,
    style={'width': '200px'}
)
```

**Características**:
- Atualiza `store-mes-global`
- Opções carregadas do banco dinamicamente
- Estilo dark theme via CSS
- Não permite limpar (clearable=False)

## Gráficos

### Estrutura Base

```python
dcc.Graph(
    id='grafico-evolucao',
    figure=go.Figure(),  # Placeholder vazio
    config={'displayModeBar': False},  # Sem barra de ferramentas
    style={'height': '280px'}
)
```

### Layout de Gráficos

**Dashboard**:
```python
# Hero (full width)
html.Div([
    dcc.Graph(id='grafico-evolucao', ...)
], className="custom-card", style={'marginBottom': '16px'})

# 2 laterais (grid 2 colunas)
html.Div([
    html.Div([dcc.Graph(id='grafico-top-categorias', ...)]),
    html.Div([dcc.Graph(id='grafico-top-fontes', ...)])
], style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '16px'})
```

**Analytics**:
```python
# 3 gráficos empilhados (full width cada)
html.Div([dcc.Graph(id='grafico-real-ideal', ...)], style={'marginBottom': '24px'})
html.Div([dcc.Graph(id='grafico-distribuicao', ...)], style={'marginBottom': '24px'})
html.Div([dcc.Graph(id='grafico-acumulado', ...)])
```

## Filtros (Transações)

### Layout 2 Linhas

```python
html.Div([
    # Linha 1: Categoria, Fonte, Status
    html.Div([
        # Categoria
        html.Div([
            html.Label("Categoria", style={...}),
            dcc.Dropdown(id='filtro-categoria-transacoes', ...)
        ], style={'flex': '1', 'minWidth': '200px'}),
        
        # Fonte
        html.Div([
            html.Label("Fonte", style={...}),
            dcc.Dropdown(id='filtro-fonte-transacoes', ...)
        ], style={'flex': '1', 'minWidth': '200px'}),
        
        # Status
        html.Div([
            html.Label("Status", style={...}),
            dcc.Dropdown(id='filtro-status-transacoes', ...)
        ], style={'flex': '1', 'minWidth': '200px'}),
    ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '16px'}),
    
    # Linha 2: Mês Compensação, Data Range
    html.Div([
        # Mês Compensação
        html.Div([
            html.Label("Mês de Compensação", style={...}),
            dcc.Dropdown(id='filtro-mes-comp-transacoes', ...)
        ], style={'flex': '1', 'minWidth': '200px'}),
        
        # Data Range
        html.Div([
            html.Label("Período (Data)", style={...}),
            dcc.DatePickerRange(id='filtro-data-transacoes', ...)
        ], style={'flex': '1', 'minWidth': '300px'}),
    ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '16px'})
], className="custom-card")
```

### Tipos de Filtros

1. **Dropdown simples** (Categoria, Fonte, Mês Comp)
   ```python
   dcc.Dropdown(
       options=[{'label': 'Todas', 'value': 'TODOS'}],
       value='TODOS',
       clearable=False
   )
   ```

2. **Dropdown fixo** (Status)
   ```python
   dcc.Dropdown(
       options=[
           {'label': 'Todas', 'value': 'TODOS'},
           {'label': 'Categorizadas', 'value': 'CATEGORIZADAS'},
           {'label': 'Pendentes', 'value': 'PENDENTES'}
       ],
       value='TODOS',
       clearable=False
   )
   ```

3. **DatePickerRange** (Período)
   ```python
   dcc.DatePickerRange(
       display_format='DD/MM/YYYY',
       start_date_placeholder_text='Data Inicial',
       end_date_placeholder_text='Data Final',
       className='custom-datepicker'
   )
   ```

## Tabela (Transações)

### Estrutura HTML

```python
html.Div([
    # Subtotal
    html.Div([
        html.Span(f"Mostrando {len(df_tabela)} de {len(df_filtrado)}"),
        html.Span(f" • Subtotal: R$ {subtotal:,.2f}", 
                  style={'color': COLORS['primary'], 'fontWeight': 'bold'})
    ], style={'marginBottom': '16px'}),
    
    # Tabela
    html.Div([
        html.Table([
            # Header
            html.Thead(html.Tr([
                html.Th('Data', style={...}),
                html.Th('Descrição', style={...}),
                html.Th('Valor', style={...}),
                html.Th('Categoria', style={...}),
                html.Th('Fonte', style={...}),
                html.Th('Mês', style={...}),
            ])),
            
            # Body
            html.Tbody(rows, style={'color': COLORS['text_primary']})
        ], style={'width': '100%', 'borderCollapse': 'collapse'})
    ], style={'overflowX': 'auto'})
])
```

### Linhas da Tabela

```python
rows = []
for _, row in df_tabela.iterrows():
    # Badge amarelo para "A definir"
    categoria_style = {
        'backgroundColor': COLORS['warning'], 
        'color': COLORS['bg_primary'],
        'padding': '4px 8px',
        'borderRadius': '4px',
        'fontWeight': 'bold'
    } if row['categoria'] == 'A definir' else {}
    
    rows.append(html.Tr([
        html.Td(row['data'], style={'padding': '12px', 'borderBottom': f"1px solid {COLORS['border']}"}),
        html.Td(row['descricao'], style={...}),
        html.Td(f"R$ {row['valor_normalizado']:,.2f}", style={...}),
        html.Td(html.Span(row['categoria'], style=categoria_style), style={...}),
        html.Td(row['fonte'], style={...}),
        html.Td(row['mes_comp'], style={...}),
    ]))
```

## Classes CSS Customizadas

### .custom-card
```css
.custom-card {
    background-color: #16213E;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}
```

### .sidebar
```css
.sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    width: 280px;
    background-color: #1A1A2E;
}
```

### .nav-link
```css
.nav-link {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 24px;
    color: #A0AEC0;
    transition: all 0.3s ease;
}
```

### .custom-datepicker
```css
.custom-datepicker .DateRangePicker_picker {
    z-index: 9999 !important;
    background-color: #16213E !important;
}
```

## Responsividade

### Breakpoints

```python
# Mobile: width < 768px
style={'display': 'block'}  # Stack vertical

# Tablet: 768px - 1024px
style={'gridTemplateColumns': '1fr'}  # 1 coluna

# Desktop: > 1024px
style={'gridTemplateColumns': '1fr 1fr'}  # 2 colunas
```

### Flexbox com Wrap

```python
style={
    'display': 'flex',
    'flexWrap': 'wrap',  # Quebra linha se necessário
    'gap': '16px',
    'minWidth': '200px'  # Largura mínima antes de quebrar
}
```

## Ícones FontAwesome

### CDN
```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
```

### Uso
```python
html.I(className="fas fa-home")          # Home
html.I(className="fas fa-chart-bar")     # Analytics
html.I(className="fas fa-list")          # Transações
html.I(className="fas fa-wallet")        # Total
html.I(className="fas fa-credit-card")   # Cartões
html.I(className="fas fa-money-bill-wave") # Pix+Boleto
```

## Store (Estado Global)

```python
dcc.Store(
    id='store-mes-global',
    data='TODOS',  # Valor inicial
    storage_type='memory'  # Não persiste refresh
)
```

**Uso**:
- Input de 7 callbacks
- Compartilhado entre todas as páginas
- Atualizado pelo dropdown de mês

## Location (Roteamento)

```python
dcc.Location(
    id='url',
    refresh=False  # SPA (sem reload de página)
)
```

**Funcionamento**:
- Escuta mudanças na URL
- Sidebar usa `dcc.Link(href='/analytics')`
- Callback `display_page` retorna conteúdo baseado no pathname

## Boas Práticas

### Separação de Concerns
```python
# ✅ BOM: Função reutilizável
def create_metric_card(icon, label, value, color):
    return html.Div([...])

# ❌ RUIM: Código duplicado
html.Div([...])  # Card 1
html.Div([...])  # Card 2 (repetido)
```

### IDs Únicos
```python
# ✅ BOM: IDs descritivos com página
id='filtro-categoria-transacoes'
id='grafico-evolucao-dashboard'

# ❌ RUIM: IDs genéricos
id='dropdown1'
id='graph'
```

### Estilos Inline vs CSS
```python
# ✅ Use CSS para estilos repetidos
className="custom-card"

# ✅ Use inline para estilos únicos
style={'marginBottom': '24px'}
```
