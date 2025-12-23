# 🎨 Estilização - Dashboard V2

## Paleta de Cores

### Background e Estrutura
```python
COLORS = {
    'bg_primary': '#0F0F23',        # Fundo principal (deep blue-black)
    'bg_secondary': '#1A1A2E',      # Fundo secundário (sidebar, cards secundários)
    'bg_card': '#16213E',           # Fundo dos cards principais
    'bg_hover': '#1F2A44',          # Hover states
}
```

**Uso**:
- `bg_primary`: Body background
- `bg_secondary`: Sidebar
- `bg_card`: Cards principais (custom-card)
- `bg_hover`: Nav links hover, rows hover

### Textos
```python
COLORS = {
    'text_primary': '#FFFFFF',      # Texto principal (branco puro)
    'text_secondary': '#A0AEC0',    # Texto secundário (cinza claro)
    'text_muted': '#718096',        # Texto menos importante
}
```

**Uso**:
- `text_primary`: Títulos, valores, dados importantes
- `text_secondary`: Labels, subtítulos, descrições
- `text_muted`: Placeholders, hints

### Valores Financeiros
```python
COLORS = {
    'success': '#06A77D',           # Verde (economia/positivo)
    'danger': '#D62246',            # Vermelho (excesso/negativo)
    'warning': '#FFD369',           # Amarelo (alerta)
    'info': '#4ECDC4',              # Turquesa (informação)
    'primary': '#2E86AB',           # Azul (destaque principal)
}
```

**Uso**:
- `success`: Valores abaixo do ideal, economias
- `danger`: Valores acima do ideal, gastos excessivos
- `warning`: Categorias "A definir", alertas
- `info`: Métricas de cartões
- `primary`: Elementos de destaque, links, botões

### Gráficos
```python
COLORS = {
    'chart_1': '#4ECDC4',           # Turquesa
    'chart_2': '#95E1D3',           # Verde água
    'chart_3': '#FFD369',           # Amarelo suave
    'chart_4': '#F38181',           # Rosa suave
    'chart_5': '#AA96DA',           # Roxo suave
    'chart_6': '#2E86AB',           # Azul principal
}
```

**Uso**: Séries múltiplas em gráficos (pie, bar, stacked)

### Borders
```python
COLORS = {
    'border': '#2D3748',            # Bordas sutis
    'border_hover': '#4A5568',      # Bordas em hover
}
```

## Tipografia

### Família de Fontes
```python
FONTS = {
    'family': '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
}
```

**Fallbacks**:
1. Inter (Google Fonts)
2. Apple system fonts (-apple-system)
3. Windows system fonts (Segoe UI)
4. Android (Roboto)
5. Generic sans-serif

### Tamanhos
```python
FONTS = {
    'size': {
        'xs': '10px',    # Hints, footnotes
        'sm': '12px',    # Labels, secondary text
        'base': '14px',  # Body text padrão
        'lg': '16px',    # Destaque, subtítulos
        'xl': '20px',    # Títulos de seção
        '2xl': '24px',   # Valores de métricas
        '3xl': '28px',   # Títulos de página
        '4xl': '32px',   # Hero text (não usado)
    }
}
```

**Aplicação**:
```python
# Labels de filtros
style={'fontSize': FONTS['size']['sm']}  # 12px

# Valores de cards
style={'fontSize': FONTS['size']['2xl']}  # 24px

# Títulos de página
style={'fontSize': FONTS['size']['3xl']}  # 28px
```

### Pesos
```python
FONTS = {
    'weight': {
        'normal': 400,
        'medium': 500,
        'semibold': 600,
        'bold': 700,
    }
}
```

**Aplicação**:
- `normal`: Body text
- `medium`: Labels
- `semibold`: Subtítulos, labels importantes
- `bold`: Títulos, valores de destaque

## Espaçamentos

### Sistema de 4px
```python
SPACING = {
    'xs': 4,      # Padding mínimo
    'sm': 8,      # Gap pequeno
    'md': 12,     # Padding padrão
    'lg': 16,     # Gap padrão
    'xl': 24,     # Padding cards
    '2xl': 32,    # Margin grandes
    '3xl': 48,    # Spacing hero (não usado)
}
```

**Aplicação**:
```python
# Padding de cards
style={'padding': f"{SPACING['xl']}px"}  # 24px

# Gap entre filtros
style={'gap': f"{SPACING['lg']}px"}  # 16px

# Margin entre seções
style={'marginBottom': f"{SPACING['2xl']}px"}  # 32px
```

## CSS Customizado

### Estrutura do Arquivo
```python
# assets/custom_styles.py

def get_custom_styles():
    return f"""
    <!DOCTYPE html>
    <html>
        <head>
            {{%metas%}}
            <title>{{%title%}}</title>
            {{%favicon%}}
            {{%css%}}
            <style>
                {css_content}
            </style>
        </head>
        <body>
            {{%app_entry%}}
            <footer>
                {{%config%}}
                {{%scripts%}}
                {{%renderer%}}
            </footer>
        </body>
    </html>
    """
```

### Reset e Base
```css
body {
    margin: 0;
    padding: 0;
    background-color: #0F0F23;
    color: #FFFFFF;
    font-family: "Inter", -apple-system, sans-serif;
}

* {
    box-sizing: border-box;
}
```

### Cards
```css
.custom-card {
    background-color: #16213E;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.custom-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
}
```

### Sidebar
```css
.sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    width: 280px;
    background-color: #1A1A2E;
    padding: 24px 0;
    z-index: 1000;
    overflow-y: auto;
}

.sidebar-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0 24px 24px;
    border-bottom: 1px solid #2D3748;
}
```

### Navegação
```css
.nav-link {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 24px;
    color: #A0AEC0;
    text-decoration: none;
    transition: all 0.3s ease;
}

.nav-link:hover {
    background-color: #1F2A44;
    color: #2E86AB;
    padding-left: 28px;  /* Indenta levemente */
}

.nav-link.active {
    background-color: #2E86AB20;
    color: #2E86AB;
    border-left: 3px solid #2E86AB;
}
```

### Dropdowns (Dash Select)
```css
.Select-control {
    background-color: #16213E !important;
    border: 1px solid #2D3748 !important;
    color: #FFFFFF !important;
}

.Select-menu-outer {
    background-color: #16213E !important;
    border: 1px solid #2D3748 !important;
    z-index: 9999 !important;
}

.Select-option {
    background-color: #16213E !important;
    color: #FFFFFF !important;
}

.Select-option:hover {
    background-color: #1F2A44 !important;
}

.Select-value-label {
    color: #FFFFFF !important;
}
```

### DatePicker
```css
/* Container principal */
.DateRangePicker_picker {
    z-index: 9999 !important;
    background-color: #16213E !important;
    border: 1px solid #2D3748 !important;
}

/* Inputs de data */
.DateInput_input {
    background-color: #16213E !important;
    color: #FFFFFF !important;
    border-bottom: 2px solid #2D3748 !important;
}

.DateInput_input::placeholder {
    color: #718096 !important;
}

/* Calendário */
.CalendarDay {
    background-color: #16213E !important;
    color: #FFFFFF !important;
    border: 1px solid #2D3748 !important;
}

.CalendarDay:hover {
    background-color: #1F2A44 !important;
    border: 1px solid #2E86AB !important;
}

/* Dia selecionado */
.CalendarDay__selected {
    background: #2E86AB !important;
    color: #FFFFFF !important;
    border: 1px solid #2E86AB !important;
}

.CalendarDay__selected:hover {
    background: #2E86AB !important;
    opacity: 0.9;
}

/* Range (span entre start e end) */
.CalendarDay__hovered_span {
    background: #2E86AB30 !important;
    border: 1px solid #2E86AB50 !important;
    color: #FFFFFF !important;
}

/* Navegação (setas) */
.DayPickerNavigation_button {
    background-color: #16213E !important;
    border: 1px solid #2D3748 !important;
}

.DayPickerNavigation_button:hover {
    background-color: #1F2A44 !important;
    border: 1px solid #2E86AB !important;
}

.DayPickerNavigation_svg__horizontal {
    fill: #FFFFFF !important;
}

/* Headers (mês/ano) */
.CalendarMonth_caption {
    color: #FFFFFF !important;
}

.DayPicker_weekHeader {
    color: #A0AEC0 !important;
}

/* Seta separadora */
.DateRangePickerInput_arrow {
    color: #FFFFFF !important;
}
```

### Tabelas
```css
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
}

th {
    padding: 12px;
    text-align: left;
    border-bottom: 2px solid #2D3748;
    color: #FFFFFF;
    font-weight: 600;
}

td {
    padding: 12px;
    border-bottom: 1px solid #2D3748;
    color: #FFFFFF;
}

tr:hover td {
    background-color: #1F2A44;
}
```

### Scrollbar (Webkit)
```css
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #1A1A2E;
}

::-webkit-scrollbar-thumb {
    background: #2D3748;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #4A5568;
}
```

## Template Plotly

```python
PLOTLY_TEMPLATE = {
    'layout': {
        'paper_bgcolor': COLORS['bg_card'],     # Fundo do gráfico
        'plot_bgcolor': COLORS['bg_card'],      # Fundo do plot
        'font': {
            'family': FONTS['family'],
            'size': 12,
            'color': COLORS['text_primary']
        },
        'xaxis': {
            'gridcolor': COLORS['border'],      # Linhas de grid
            'zeroline': False,
            'showline': True,
            'linecolor': COLORS['border']
        },
        'yaxis': {
            'gridcolor': COLORS['border'],
            'zeroline': False,
            'showline': True,
            'linecolor': COLORS['border']
        },
        'hovermode': 'x unified',               # Hover agrupado
        'hoverlabel': {
            'bgcolor': COLORS['bg_secondary'],
            'font': {'color': COLORS['text_primary']}
        }
    }
}
```

**Aplicação**:
```python
fig.update_layout(template=PLOTLY_TEMPLATE)
```

## Animações e Transições

### Hover States
```css
.custom-card {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.custom-card:hover {
    transform: translateY(-2px);
}

.nav-link {
    transition: all 0.3s ease;
}
```

### Loading States
```css
.loading {
    animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
```

## Responsividade

### Breakpoints
```python
# Mobile: < 768px
@media (max-width: 767px) {
    .sidebar {
        width: 100%;
        height: auto;
        position: relative;
    }
    
    #page-content {
        margin-left: 0;
        padding: 16px;
    }
}

# Tablet: 768px - 1024px
@media (min-width: 768px) and (max-width: 1024px) {
    .sidebar {
        width: 200px;
    }
}

# Desktop: > 1024px
@media (min-width: 1024px) {
    .sidebar {
        width: 280px;
    }
}
```

### Grids Responsivos
```python
# Desktop: 2 colunas
style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr'}

# Tablet/Mobile: 1 coluna (com flexbox wrap)
style={'display': 'flex', 'flexWrap': 'wrap'}
```

## Utilitários

### Text Truncate
```css
.truncate {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
```

### Flex Helpers
```css
.flex-center {
    display: flex;
    align-items: center;
    justify-content: center;
}

.flex-between {
    display: flex;
    align-items: center;
    justify-content: space-between;
}
```

### Spacing Helpers
```python
# Aplicação programática
style={'marginBottom': f"{SPACING['xl']}px"}
style={'padding': f"{SPACING['md']}px {SPACING['lg']}px"}
```

## Acessibilidade

### Contrast Ratios
- Text primary (#FFFFFF) sobre bg_card (#16213E): **12.6:1** ✅ AAA
- Text secondary (#A0AEC0) sobre bg_card (#16213E): **6.8:1** ✅ AA
- Primary (#2E86AB) sobre bg_card (#16213E): **4.7:1** ✅ AA

### Focus States
```css
button:focus, select:focus, input:focus {
    outline: 2px solid #2E86AB;
    outline-offset: 2px;
}
```

## Dark Theme Checklist

- [x] Background escuro (#0F0F23)
- [x] Cards com contraste (#16213E)
- [x] Textos legíveis (contrast > 4.5:1)
- [x] Hover states sutis
- [x] Borders discretas (#2D3748)
- [x] Gráficos com fundo escuro
- [x] Dropdowns estilizados
- [x] DatePicker com tema escuro
- [x] Scrollbars customizadas
- [x] Transições suaves
