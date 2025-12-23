# 🏗️ Arquitetura - Dashboard V2

## Estrutura de Diretórios

```
backend/src/dashboard_v2/
├── __init__.py                    # Pacote principal
├── main.py                        # ⚙️ Aplicação Dash + Callbacks
├── config.py                      # 📝 Configurações centralizadas
│
├── assets/                        # 🎨 Arquivos estáticos
│   ├── __init__.py
│   └── custom_styles.py          # CSS customizado (dark theme)
│
├── components/                    # 🧩 Componentes reutilizáveis
│   ├── __init__.py
│   └── sidebar.py                # Sidebar com navegação
│
├── pages/                         # 📄 Páginas do dashboard
│   ├── __init__.py
│   ├── dashboard.py              # Página principal (overview)
│   ├── analytics.py              # Análises detalhadas
│   └── transacoes.py             # Lista/categorização
│
└── utils/                         # 🔧 Utilitários
    ├── __init__.py
    ├── database.py               # Queries SQLite
    └── graficos.py               # Funções Plotly
```

## Padrão MVC Adaptado

### Model (Data Layer)
**Localização**: `utils/database.py`

```python
def carregar_transacoes(mes_filtro=None)
def calcular_estatisticas(df)
def obter_meses_disponiveis()
def obter_categorias_unicas(df)
def obter_fontes_unicas(df)
```

**Responsabilidades**:
- Conexão com SQLite
- Queries de leitura
- Transformação de dados (pandas)
- Cálculos de estatísticas

### View (Presentation Layer)
**Localização**: `pages/*.py` + `components/*.py`

```python
# pages/dashboard.py
def create_dashboard_page() -> html.Div

# pages/analytics.py
def create_analytics_page() -> html.Div

# pages/transacoes.py
def create_transacoes_page() -> html.Div

# components/sidebar.py
def create_sidebar() -> html.Div
```

**Responsabilidades**:
- Layout HTML/Dash
- Estrutura de componentes
- Estilos inline
- Placeholders para callbacks

### Controller (Logic Layer)
**Localização**: `main.py` (callbacks)

```python
@callback(...)
def display_page(pathname): ...

@callback(...)
def atualizar_grafico_evolucao(mes_selecionado): ...

@callback(...)
def atualizar_tabela_transacoes(...): ...
```

**Responsabilidades**:
- Lógica de negócio
- Interações usuário
- Filtros e transformações
- Orquestração Model ↔ View

### Utilities (Shared Layer)
**Localização**: `utils/graficos.py` + `config.py`

```python
# graficos.py
def criar_grafico_evolucao(df) -> go.Figure
def criar_grafico_top_categorias(df) -> go.Figure
# ...

# config.py
COLORS = {...}
FONTS = {...}
SPACING = {...}
```

**Responsabilidades**:
- Criação de gráficos Plotly
- Configurações globais
- Helpers reutilizáveis

## Fluxo de Dados

```
┌─────────────┐
│   Browser   │ ← Renderiza HTML/CSS/JS
└──────┬──────┘
       │ HTTP Request (pathname: "/")
       ▼
┌─────────────────────────────────────┐
│         main.py (Dash App)          │
│  ┌───────────────────────────────┐  │
│  │  @callback: display_page()    │  │ ← Roteamento
│  │  pathname → create_*_page()   │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │   pages/dashboard.py          │  │ ← View
│  │   create_dashboard_page()     │  │
│  └───────────┬───────────────────┘  │
│              │ Components (Sidebar, Cards, Graphs)
│              ▼
│  ┌───────────────────────────────┐  │
│  │  @callback: atualizar_*()     │  │ ← Controller
│  │  Input: dropdown, filters     │  │
│  │  ├─→ carregar_transacoes()    │  │
│  │  ├─→ calcular_estatisticas()  │  │
│  │  └─→ criar_grafico_*()        │  │
│  └───────────┬───────────────────┘  │
└──────────────┼───────────────────────┘
               │
       ┌───────▼───────┐
       │  SQLite3 DB   │ ← Model
       │  lancamentos  │
       └───────────────┘
```

## Inicialização da Aplicação

```python
# main.py (linha ~15-40)
app = Dash(
    __name__,
    suppress_callback_exceptions=True,  # Multi-page
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    ]
)

# Layout principal com Store e Sidebar
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='store-mes-global', data='TODOS'),  # Estado global
    create_sidebar(),
    html.Div(id='page-content', ...)
])

# CSS customizado injetado
app.index_string = get_custom_styles()
```

## Gerenciamento de Estado

### Estado Global
```python
dcc.Store(id='store-mes-global', data='TODOS')
```
- Compartilhado entre todas as páginas
- Atualizado pelo dropdown de mês
- Usado como Input em múltiplos callbacks

### Estado Local (Transações)
```python
# 5 filtros locais (só existem em /transacoes)
Input('filtro-categoria-transacoes', 'value')
Input('filtro-fonte-transacoes', 'value')
Input('filtro-status-transacoes', 'value')
Input('filtro-mes-comp-transacoes', 'value')
Input('filtro-data-transacoes', 'start_date')
Input('filtro-data-transacoes', 'end_date')
```

## Navegação Multi-Page

```python
@callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/analytics':
        return create_analytics_page()
    elif pathname == '/transacoes':
        return create_transacoes_page()
    else:
        return create_dashboard_page()
```

**Rotas**:
- `/` → Dashboard principal
- `/analytics` → Análises avançadas
- `/transacoes` → Gerenciamento de transações

## Convenções de Código

### Nomenclatura
- **Funções**: `snake_case` (create_dashboard_page, carregar_transacoes)
- **Classes**: `PascalCase` (não usado neste projeto)
- **Constantes**: `UPPER_SNAKE_CASE` (COLORS, FONTS, SPACING)
- **IDs Dash**: `kebab-case` (filtro-categoria-transacoes, store-mes-global)

### Imports
```python
# 1. Built-in
from pathlib import Path
import sqlite3

# 2. Third-party
from dash import Dash, html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go

# 3. Local
from dashboard_v2.config import COLORS, FONTS
from dashboard_v2.utils.database import carregar_transacoes
from dashboard_v2.pages.dashboard import create_dashboard_page
```

### Docstrings
```python
def criar_grafico_evolucao(df, mes_filtro=None):
    """
    Cria gráfico de evolução de gastos ao longo dos meses
    
    Args:
        df (pd.DataFrame): DataFrame com colunas [data, valor, mes_comp]
        mes_filtro (str, optional): Filtro de mês (YYYY-MM). Defaults to None.
    
    Returns:
        go.Figure: Gráfico Plotly de linha com área preenchida
    """
```

## Dependências

```
dash>=3.2.0
dash-bootstrap-components>=1.5.0
plotly>=5.18.0
pandas>=2.1.0
```

## Performance

### Otimizações Implementadas
1. **Limite de registros**: Tabela limitada a 100 transações
2. **Cálculos no backend**: Estatísticas calculadas em Python (não JS)
3. **Cache implícito**: Dash cacheia callbacks não modificados
4. **HTML Table**: Substituiu DataTable (mais leve, sem chunk JS)

### Bottlenecks Conhecidos
- Query SQLite sem índices (todas as colunas usadas em WHERE devem ter índice)
- Sort em memória para 2.256 registros (considerar SQL ORDER BY)
- Sem paginação (carrega todas as transações do mês)

## Segurança

### Vulnerabilidades Mitigadas
- ✅ SQL Injection: Usa pandas `read_sql_query` (parametrizado)
- ✅ XSS: Dash escapa HTML automaticamente
- ✅ Path Traversal: Usa `Path.resolve()` para DB

### TODO
- [ ] Autenticação (atualmente sem login)
- [ ] HTTPS (atualmente HTTP)
- [ ] Rate limiting (sem proteção contra abuse)
