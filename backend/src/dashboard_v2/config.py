"""
Configurações centralizadas do Dashboard v2
Cores, fontes, espaçamentos baseados em design profissional
"""

# ===== PALETA DE CORES (Baseada na referência Behance) =====
COLORS = {
    # Background e estrutura
    'bg_primary': '#0F0F23',        # Fundo principal (azul escuro profundo)
    'bg_secondary': '#1A1A2E',      # Fundo secundário (cards, sidebar)
    'bg_card': '#16213E',           # Fundo dos cards
    'bg_hover': '#1F2A44',          # Hover states
    
    # Textos
    'text_primary': '#FFFFFF',      # Texto principal (branco)
    'text_secondary': '#A0AEC0',    # Texto secundário (cinza claro)
    'text_muted': '#718096',        # Texto menos importante
    
    # Valores financeiros
    'success': '#06A77D',           # Verde (economia/positivo)
    'danger': '#D62246',            # Vermelho (excesso/negativo)
    'warning': '#FFD369',           # Amarelo (alerta)
    'info': '#4ECDC4',              # Turquesa (informação)
    'primary': '#2E86AB',           # Azul (destaque principal)
    
    # Gráficos (paleta sutil e harmoniosa)
    'chart_1': '#4ECDC4',           # Turquesa
    'chart_2': '#95E1D3',           # Verde água
    'chart_3': '#FFD369',           # Amarelo suave
    'chart_4': '#F38181',           # Rosa suave
    'chart_5': '#AA96DA',           # Roxo suave
    'chart_6': '#2E86AB',           # Azul corporativo
    
    # Bordas e divisores
    'border': '#2D3748',            # Bordas sutis
    'divider': '#1A202C',           # Divisores
    'grid': 'rgba(160, 174, 192, 0.1)',  # Grid dos gráficos (muito sutil)
    
    # Sidebar
    'sidebar_bg': '#16213E',        # Fundo da sidebar
    'sidebar_active': '#2E86AB',    # Item ativo
    'sidebar_hover': '#1F2A44',     # Item hover
}

# ===== TIPOGRAFIA =====
FONTS = {
    'family': 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    
    # Tamanhos (rem) - Drasticamente reduzidos para Full HD
    'size': {
        'xs': '0.625rem',     # 10px - textos muito pequenos
        'sm': '0.75rem',      # 12px - labels, textos secundários
        'base': '0.875rem',   # 14px - texto padrão
        'lg': '1rem',         # 16px - subtítulos
        'xl': '1.125rem',     # 18px - títulos pequenos
        '2xl': '1.25rem',     # 20px - títulos médios
        '3xl': '1.5rem',      # 24px - títulos grandes
        '4xl': '1.75rem',     # 28px - números destaque (era 32px)
    },
    
    # Pesos
    'weight': {
        'normal': 400,
        'medium': 500,
        'semibold': 600,
        'bold': 700,
    }
}

# ===== ESPAÇAMENTOS (px) =====
SPACING = {
    'xs': 4,
    'sm': 8,
    'md': 12,
    'lg': 16,
    'xl': 20,
    '2xl': 24,
    '3xl': 32,
}

# ===== LAYOUT =====
LAYOUT = {
    'sidebar_width': '280px',
    'content_max_width': '1600px',
    'card_border_radius': '12px',
    'button_border_radius': '8px',
    'card_padding': f"{SPACING['lg']}px",
    'section_spacing': f"{SPACING['2xl']}px",
}

# ===== ORÇAMENTOS (mantidos do dashboard anterior) =====
ORCAMENTO_IDEAL = {
    'Mercado': 4200.00,
    'Casa': 3400.00,
    'LF': 2400.00,
    'Nita': 2100.00,
    'Utilidades': 1700.00,
    'Esporte': 1700.00,
    'Faculdade': 1500.00,
    'Pet': 1200.00,
    'Compras': 1200.00,
    'Datas': 1200.00,
    'Estética': 850.00,
    'Estetica': 850.00,
    'Combustível': 650.00,
    'Combustivel': 650.00,
    'Betina': 650.00,
    'Farmácia': 600.00,
    'Farmacia': 600.00,
    'Lazer': 500.00,
    'Stream': 500.00,
    'Carro': 400.00,
    'Seguro': 350.00,
    'Saúde': 350.00,
    'Saude': 350.00,
    'Hobby': 300.00,
    'Padaria': 300.00,
    'Feira': 200.00,
    'Transporte': 140.00,
    'Vestuário': 100.00,
    'Vestuario': 100.00,
    'Eventos': 100.00,
    'Cartão': 80.00,
    'Cartao': 80.00
}

# Soma total do orçamento ideal mensal (fixo, não muda com filtros)
# Usa apenas valores das categorias principais (com acento), evitando duplicatas
IDEAL_MENSAL_TOTAL = sum([
    4200.00,  # Mercado
    3400.00,  # Casa
    2400.00,  # LF
    2100.00,  # Nita
    1700.00,  # Utilidades
    1700.00,  # Esporte
    1500.00,  # Faculdade
    1200.00,  # Pet
    1200.00,  # Compras
    1200.00,  # Datas
    850.00,   # Estética
    650.00,   # Combustível
    650.00,   # Betina
    600.00,   # Farmácia
    500.00,   # Lazer
    500.00,   # Stream
    400.00,   # Carro
    350.00,   # Seguro
    350.00,   # Saúde
    300.00,   # Hobby
    300.00,   # Padaria
    200.00,   # Feira
    140.00,   # Transporte
    100.00,   # Vestuário
    100.00,   # Eventos
    80.00,    # Cartão
])  # Total: R$ 26.670,00

ORCAMENTO_IDEAL_FONTE = {
    'PIX': 8900.00,
    'Visa Bia': 4100.00,
    'Master Físico': 3850.00,
    'Visa Recorrente': 714.00,
    'Visa Físico': 2050.00,
    'Master Recorrente': 1886.00,
    'Visa Mae': 1390.00,
    'Visa Virtual': 880.00,
    'Master Virtual': 2700.00
}

ORCAMENTO_IDEAL_CAT_VISA_REC = {    
    'Esporte': 414.00,
    'Stream': 300.00
}

ORCAMENTO_IDEAL_CAT_VISA_BIA = {
    'Mercado': 3300.00,
    'Feira': 200.00,
    'Farmácia': 200.00,
    'Pet': 200.00,
    'Lazer': 200.00
}

ORCAMENTO_IDEAL_CAT_VISA_FIS = {
    'Datas': 1200.00,
    'Estética': 450.00,
    'Compras': 200.00,
    'Pet': 200.00
}

ORCAMENTO_IDEAL_CAT_MASTER_VIRTUAL = {
    'LF': 2400.00,
    'Betina': 300.00,
    'Farmácia': 200.00
}

ORCAMENTO_IDEAL_CAT_PIX = {
    'Casa': 3200.00,
    'Nita': 2100.00,
    'Utilidades': 1700.00,
    'Faculdade': 1500.00,
    'Esporte': 400.00
}


# ===== CONFIGURAÇÃO PLOTLY (tema dark consistente) =====
PLOTLY_TEMPLATE = {
    'layout': {
        'paper_bgcolor': COLORS['bg_card'],
        'plot_bgcolor': COLORS['bg_card'],
        'font': {
            'family': FONTS['family'],
            'color': COLORS['text_primary'],
            'size': 14
        },
        'title': {
            'font': {
                'size': 18,
                'color': COLORS['text_primary'],
                'family': FONTS['family']
            }
        },
        'xaxis': {
            'gridcolor': COLORS['grid'],
            'linecolor': COLORS['border'],
            'tickfont': {'color': COLORS['text_secondary'], 'size': 12},
            'title': {'font': {'color': COLORS['text_primary'], 'size': 14}}
        },
        'yaxis': {
            'gridcolor': COLORS['grid'],
            'linecolor': COLORS['border'],
            'tickfont': {'color': COLORS['text_secondary'], 'size': 12},
            'title': {'font': {'color': COLORS['text_primary'], 'size': 14}}
        },
        'hovermode': 'closest',
        'hoverlabel': {
            'bgcolor': COLORS['bg_secondary'],
            'font': {'color': COLORS['text_primary'], 'size': 13}
        }
    }
}

# ===== ÍCONES (FontAwesome 6) =====
ICONS = {
    'dashboard': 'fas fa-chart-line',
    'analytics': 'fas fa-chart-pie',
    'transactions': 'fas fa-list',
    'ideals': 'fas fa-bullseye',
    'calendar': 'fas fa-calendar-alt',
    'filter': 'fas fa-filter',
    'wallet': 'fas fa-wallet',
    'trending_up': 'fas fa-arrow-trend-up',
    'trending_down': 'fas fa-arrow-trend-down',
    'category': 'fas fa-tag',
    'source': 'fas fa-credit-card',
}
