"""
Dashboard Interativo Excel/TXT com Dash
Baseado em extratos processados (Excel/TXT) - Tabela lancamentos
"""

import sqlite3
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, html, dcc, Input, Output, callback, State, ALL, ctx
import dash_bootstrap_components as dbc

# Caminhos
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / 'dados' / 'db' / 'financeiro.db'

# Orçamento Ideal (mensal) - Atualizado conforme Controle_pessoal.xlsm
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
    'Cartão': 80.00
    # Total: 26.670,00 
}

# Orçamento Ideal por Fonte (mensal) - Conforme planilha de controle
ORCAMENTO_IDEAL_FONTE = {
    'PIX': 8900.00,
    'Visa Bia': 4100.00,
    'Master Físico': 3850.00,
    'Visa Recorrente': 3114.00,
    'Visa Físico': 2050.00,
    'Master Recorrente': 1886.00,
    'Visa Mae': 1390.00,
    'Visa Virtual': 880.00,
    'Master Virtual': 500.00
    # Total: 26.670,00 (mesmo total do ORCAMENTO_IDEAL por categoria)
}

# Carregar dados do banco
def carregar_dados():
    """Carrega dados do banco de dados lancamentos (exceto INVESTIMENTOS, SALÁRIO)"""
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT 
        rowid,
        Data as data,
        Descricao as descricao,
        Valor as valor,
        Categoria as categoria,
        Fonte as fonte,
        MesComp as mes_comp
    FROM lancamentos
    WHERE Categoria NOT IN ('INVESTIMENTOS', 'SALÁRIO', 'Salário', 'Investimentos')
      AND (
        Descricao NOT LIKE '%ITAU VISA%'
        AND Descricao NOT LIKE '%ITAU BLACK%'
        AND Descricao NOT LIKE '%ITAU MASTER%'
        AND Descricao NOT LIKE '%PGTO FATURA%'
        AND Descricao NOT LIKE '%PAGAMENTO CARTAO%'
        AND Descricao NOT LIKE '%PAGAMENTO EFETUADO%'
      )
    ORDER BY data
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Processar dados
    if len(df) > 0:
        df['data'] = pd.to_datetime(df['data'], errors='coerce')
        df['valor_normalizado'] = df['valor'].abs()
        
        # Remove duplicatas baseado em Data + Descricao + Valor + Fonte
        df = df.drop_duplicates(subset=['data', 'descricao', 'valor', 'fonte'], keep='first')
        
        # Remove duplicatas de rowid (caso haja)
        df = df.drop_duplicates(subset=['rowid'], keep='first')
    
    return df

def carregar_transacoes_pendentes(mes_filtro='TODOS'):
    """Carrega apenas transações 'A definir' para categorização
    
    Args:
        mes_filtro: Mês para filtrar (ex: 'Dezembro 2025') ou 'TODOS'
    """
    conn = sqlite3.connect(DB_PATH)
    
    # Adiciona filtro de mês se especificado
    filtro_mes_sql = ""
    if mes_filtro != 'TODOS':
        filtro_mes_sql = f"AND MesComp = '{mes_filtro}'"
    
    query = f"""
    SELECT 
        rowid as row_id,
        Data as data,
        Descricao as descricao,
        Valor as valor,
        Fonte as fonte,
        MesComp as mes_comp
    FROM lancamentos
    WHERE Categoria = 'A definir'
      {filtro_mes_sql}
      AND (
        Descricao NOT LIKE '%ITAU VISA%'
        AND Descricao NOT LIKE '%ITAU BLACK%'
        AND Descricao NOT LIKE '%ITAU MASTER%'
        AND Descricao NOT LIKE '%PGTO FATURA%'
        AND Descricao NOT LIKE '%PAGAMENTO CARTAO%'
        AND Descricao NOT LIKE '%PAGAMENTO EFETUADO%'
      )
    ORDER BY data DESC
    LIMIT 100
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if len(df) > 0:
        df['data'] = pd.to_datetime(df['data'], errors='coerce')
        df['valor_normalizado'] = df['valor'].abs()
        
        # Remove duplicatas REAIS baseado em Data + Descricao + Valor + Fonte
        # Mantém o primeiro rowid (mais antigo)
        df = df.drop_duplicates(subset=['data', 'descricao', 'valor', 'fonte'], keep='first')
        
        # Remove duplicatas de row_id (caso haja)
        df = df.drop_duplicates(subset=['row_id'], keep='first')
    
    return df

def atualizar_categoria_banco(rowid, nova_categoria):
    """Atualiza categoria de uma transação no banco"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE lancamentos SET Categoria = ? WHERE rowid = ?",
            (nova_categoria, rowid)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Erro ao atualizar categoria: {e}")
        return False

def obter_categorias_disponiveis():
    """Retorna lista de categorias únicas no banco (exceto as especiais)"""
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT DISTINCT Categoria FROM lancamentos WHERE Categoria NOT IN ('INVESTIMENTOS', 'SALÁRIO', 'A definir', 'Salário', 'Investimentos') ORDER BY Categoria"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df['Categoria'].tolist()

# Carregar dados inicial
df_global = carregar_dados()
df_pendentes = carregar_transacoes_pendentes('TODOS')
categorias_disponiveis = obter_categorias_disponiveis()

# Inicializar app Dash com tema Bootstrap
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Dashboard Financeiro Excel/TXT"

# Layout do Dashboard
app.layout = dbc.Container([
    # Store para controlar refresh
    dcc.Store(id='refresh-trigger', data=0),
    
    # Cabeçalho
    dbc.Row([
        dbc.Col([
            html.H1("💰 Dashboard Financeiro (Excel/TXT)", 
                   className="text-center text-primary mb-4 mt-4"),
            html.Hr()
        ])
    ]),
    
    # Filtros - COMPACTOS
    dbc.Row([
        dbc.Col([
            html.Label("📅 Mês:", className="fw-bold", style={'fontSize': '0.9rem'}),
            dcc.Dropdown(
                id='filtro-mes',
                options=[{'label': 'Todos', 'value': 'TODOS'}] + 
                        [{'label': mes, 'value': mes} for mes in sorted(df_global['mes_comp'].unique())] if len(df_global) > 0 else [],
                value='TODOS',
                clearable=False
            )
        ], width=4),
        
        dbc.Col([
            html.Label("🏷️ Categoria:", className="fw-bold", style={'fontSize': '0.9rem'}),
            dcc.Dropdown(
                id='filtro-categoria',
                options=[{'label': 'Todas', 'value': 'TODOS'}] + 
                        [{'label': cat, 'value': cat} for cat in sorted(df_global['categoria'].unique())] if len(df_global) > 0 else [],
                value='TODOS',
                clearable=False
            )
        ], width=4),
        
        dbc.Col([
            html.Label("💳 Fonte:", className="fw-bold", style={'fontSize': '0.9rem'}),
            dcc.Dropdown(
                id='filtro-fonte',
                options=[{'label': 'Todas', 'value': 'TODOS'}] + 
                        [{'label': fonte, 'value': fonte} for fonte in sorted(df_global['fonte'].unique())] if len(df_global) > 0 else [],
                value='TODOS',
                clearable=False
            )
        ], width=4),
    ], className="mb-2 p-2 bg-light rounded"),
    
    # Primeira linha: 6 cards principais
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("💰 Total", className="text-center mb-1", style={'fontSize': '0.85rem'}),
                    html.H4(id="card-total", className="text-center text-primary mb-0", style={'fontSize': '1.3rem'})
                ], style={'padding': '0.75rem'})
            ])
        ], width=2),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("📅 Média 12M", className="text-center mb-1", style={'fontSize': '0.85rem'}),
                    html.H4(id="card-media", className="text-center text-success mb-0", style={'fontSize': '1.3rem'})
                ], style={'padding': '0.75rem'})
            ])
        ], width=2),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("✅ Categorizado", className="text-center mb-1", style={'fontSize': '0.85rem'}),
                    html.H4(id="card-categorizado", className="text-center text-success mb-0", style={'fontSize': '1.3rem'})
                ], style={'padding': '0.75rem'})
            ], id="card-categorizado-border")
        ], width=2),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("⚠️ Pendentes", className="text-center mb-1", style={'fontSize': '0.85rem'}),
                    html.H4(id="card-pendentes", className="text-center text-warning mb-0", style={'fontSize': '1.3rem'})
                ], style={'padding': '0.75rem'})
            ], id="card-pendentes-border")
        ], width=2),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("📊 Transações", className="text-center mb-1", style={'fontSize': '0.85rem'}),
                    html.H4(id="card-transacoes", className="text-center text-info mb-0", style={'fontSize': '1.3rem'})
                ], style={'padding': '0.75rem'})
            ])
        ], width=2),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("📆 Meses", className="text-center mb-1", style={'fontSize': '0.85rem'}),
                    html.H4(id="card-meses", className="text-center text-secondary mb-0", style={'fontSize': '1.3rem'})
                ], style={'padding': '0.75rem'})
            ])
        ], width=2),
    ], className="mb-2"),
    
    # Segunda linha: Cards condicionais (Ideal e Diferença) - aparecem apenas quando filtrar por mês
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("🎯 Ideal do Mês", className="text-center mb-1", style={'fontSize': '0.85rem'}),
                    html.H4(id="card-ideal-mes", className="text-center text-info mb-0", style={'fontSize': '1.3rem'})
                ], style={'padding': '0.75rem'})
            ], style={'height': '100%'})
        ], width=2, id="col-ideal-mes", style={'display': 'none'}),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6(id="card-diferenca-titulo", className="text-center mb-1", style={'fontSize': '0.85rem'}),
                    html.H4(id="card-diferenca-mes", className="text-center mb-0", style={'fontSize': '1.3rem'})
                ], style={'padding': '0.75rem'})
            ], id="card-diferenca-border", style={'height': '100%'})
        ], width=2, id="col-diferenca-mes", style={'display': 'none'}),
    ], className="mb-3", id="row-cards-mes-especifico"),
    
    # Seção de Categorização (aparece se houver pendentes)
    html.Div(id='secao-categorizacao', children=[
        dbc.Card([
            dbc.CardHeader([
                html.H4("⚠️ Transações Pendentes de Categorização", className="text-danger mb-0")
            ]),
            dbc.CardBody([
                html.Div(id='tabela-pendentes-container'),
                html.Div(id='feedback-categorizacao', className="mt-3")
            ])
        ], className="mb-4")
    ], style={'display': 'none'}),
    
    # Gráficos
    # Linha 1: Real vs Ideal (70%) + Evolução Mensal (30%)
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='grafico-real-ideal', config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToAdd': ['toImage']})
        ], width=8),
        dbc.Col([
            dcc.Graph(id='grafico-evolucao', config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToAdd': ['toImage']})
        ], width=4),
    ], className="mb-4"),
    
    # Linha 2: Duas pizzas (Fontes e Categorias)
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='grafico-fontes', config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToAdd': ['toImage']})
        ], width=6),
        dbc.Col([
            dcc.Graph(id='grafico-categorias', config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToAdd': ['toImage']})
        ], width=6),
    ], className="mb-4"),
    
    # Linha 3: Gráficos temporais (só aparecem quando vendo todos os meses)
    html.Div(id='graficos-temporais', children=[
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='grafico-distribuicao', config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToAdd': ['toImage']})
            ], width=6),
            dbc.Col([
                dcc.Graph(id='grafico-acumulado', config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToAdd': ['toImage']})
            ], width=6),
        ], className="mb-4")
    ]),
    
    # Rodapé
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P("Dashboard gerado automaticamente | Dados: Extratos Excel/TXT", 
                  className="text-center text-muted")
        ])
    ])
], fluid=True)


# Callback para atualizar seção de categorização
@callback(
    [Output('secao-categorizacao', 'style'),
     Output('tabela-pendentes-container', 'children'),
     Output('card-pendentes', 'children'),
     Output('card-categorizado', 'children'),
     Output('card-pendentes-border', 'className'),
     Output('card-categorizado-border', 'className')],
    [Input('refresh-trigger', 'data'),
     Input('filtro-mes', 'value')],
    prevent_initial_call=False
)
def atualizar_secao_pendentes(refresh, mes_selecionado):
    """Atualiza a seção de transações pendentes"""
    df_pend = carregar_transacoes_pendentes(mes_selecionado)
    
    print(f"\n🔍 DEBUG: Pendentes encontradas: {len(df_pend)}")
    if len(df_pend) > 0:
        print(f"🔍 DEBUG: Primeiras linhas:")
        print(df_pend.head())
    
    # Calcular totais
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM lancamentos
        WHERE Categoria NOT IN ('INVESTIMENTOS', 'SALÁRIO', 'Salário', 'Investimentos')
          AND Descricao NOT LIKE '%ITAU VISA%'
          AND Descricao NOT LIKE '%ITAU BLACK%'
          AND Descricao NOT LIKE '%ITAU MASTER%'
          AND Descricao NOT LIKE '%PGTO FATURA%'
          AND Descricao NOT LIKE '%PAGAMENTO CARTAO%'
          AND Descricao NOT LIKE '%PAGAMENTO EFETUADO%'
    """)
    total = cursor.fetchone()[0]
    cursor.execute("""
        SELECT COUNT(*) FROM lancamentos
        WHERE Valor < 0
          AND Categoria = 'A definir'
          AND Descricao NOT LIKE '%ITAU VISA%'
          AND Descricao NOT LIKE '%ITAU BLACK%'
          AND Descricao NOT LIKE '%ITAU MASTER%'
          AND Descricao NOT LIKE '%PGTO FATURA%'
          AND Descricao NOT LIKE '%PAGAMENTO CARTAO%'
          AND Descricao NOT LIKE '%PAGAMENTO EFETUADO%'
    """)
    pendentes = cursor.fetchone()[0]
    conn.close()
    
    print(f"🔍 DEBUG: Total={total}, Pendentes={pendentes}")
    
    categorizados = total - pendentes
    perc_categorizado = (categorizados / total * 100) if total > 0 else 0
    perc_pendente = (pendentes / total * 100) if total > 0 else 0
    
    # Card de categorizados
    card_cat_text = html.Div([
        html.Div(f"{perc_categorizado:.1f}%", style={'fontSize': '2rem', 'fontWeight': 'bold'}),
        html.Small(f"{categorizados:,}/{total:,} transações")
    ])
    
    # Card de pendentes
    card_pend_text = html.Div([
        html.Div(str(pendentes), style={'fontSize': '2rem', 'fontWeight': 'bold'}),
        html.Small(f"{perc_pendente:.1f}% do total")
    ])
    
    # Classes dos cards (bordas coloridas)
    card_cat_class = "border-success" if perc_categorizado >= 95 else "border-warning"
    card_pend_class = "border-danger" if pendentes > 10 else "border-warning" if pendentes > 0 else "border-success"
    
    if len(df_pend) == 0:
        return (
            {'display': 'none'},
            html.Div("✅ Nenhuma transação pendente!", className="text-success text-center"),
            card_pend_text,
            card_cat_text,
            card_pend_class,
            card_cat_class
        )
    
    # Controles de categorização em lote
    controles_lote = html.Div([
        dbc.Row([
            dbc.Col([
                html.Label("🏷️ Categoria para Selecionados:", className="fw-bold"),
                dcc.Dropdown(
                    id='categoria-lote',
                    options=[{'label': cat, 'value': cat} for cat in sorted(categorias_disponiveis)],
                    placeholder="Escolha a categoria...",
                    clearable=True
                )
            ], width=8),
            dbc.Col([
                html.Label(" ", className="d-block"),  # Espaçador para alinhar
                dbc.Button(
                    "Aplicar aos Selecionados",
                    id='btn-aplicar-lote',
                    color="primary",
                    className="w-100"
                )
            ], width=4)
        ], className="mb-3 p-3 bg-light rounded")
    ])
    
    # Criar tabela de categorização
    rows = []
    for idx, row in df_pend.iterrows():
        rowid_val = int(row['row_id'])
        rows.append(
            html.Tr([
                html.Td([
                    dcc.Checklist(
                        id={'type': 'checkbox-item', 'index': rowid_val},
                        options=[{'label': '', 'value': rowid_val}],
                        value=[]
                    )
                ], style={'width': '3%', 'textAlign': 'center'}),
                html.Td(row['data'].strftime('%d/%m/%Y'), style={'width': '9%'}),
                html.Td(row['descricao'], style={'width': '33%', 'maxWidth': '300px', 'overflow': 'hidden', 'textOverflow': 'ellipsis'}),
                html.Td(f"R$ {row['valor_normalizado']:,.2f}", style={'width': '11%', 'textAlign': 'right'}),
                html.Td(row['fonte'], style={'width': '14%'}),
                html.Td([
                    dcc.Dropdown(
                        id={'type': 'dropdown-categoria', 'index': rowid_val},
                        options=[{'label': cat, 'value': cat} for cat in sorted(categorias_disponiveis)],
                        placeholder="Selecione...",
                        style={'minWidth': '180px'}
                    )
                ], style={'width': '22%'}),
                html.Td([
                    dbc.Button(
                        "Salvar",
                        id={'type': 'btn-salvar', 'index': rowid_val},
                        color="success",
                        size="sm",
                        className="w-100"
                    )
                ], style={'width': '8%'})
            ])
        )
    
    tabela = dbc.Table([
        html.Thead([
            html.Tr([
                html.Th([
                    dcc.Checklist(
                        id='checkbox-selecionar-todos',
                        options=[{'label': '', 'value': 'all'}],
                        value=[]
                    )
                ], style={'textAlign': 'center'}),
                html.Th("Data"),
                html.Th("Descrição"),
                html.Th("Valor", style={'textAlign': 'right'}),
                html.Th("Fonte"),
                html.Th("Nova Categoria"),
                html.Th("Ação")
            ])
        ]),
        html.Tbody(rows)
    ], striped=True, bordered=True, hover=True, responsive=True, size="sm")
    
    return (
        {'display': 'block'},
        html.Div([controles_lote, tabela]),
        card_pend_text,
        card_cat_text,
        card_pend_class,
        card_cat_class
    )

# Callback para salvar categorização
@callback(
    [Output('feedback-categorizacao', 'children'),
     Output('refresh-trigger', 'data')],
    [Input({'type': 'btn-salvar', 'index': ALL}, 'n_clicks')],
    [State({'type': 'dropdown-categoria', 'index': ALL}, 'value'),
     State({'type': 'btn-salvar', 'index': ALL}, 'id'),
     State('refresh-trigger', 'data')],
    prevent_initial_call=True
)
def salvar_categorizacao(n_clicks, valores, ids, current_refresh):
    """Salva a categoria selecionada no banco de dados"""
    
    if not n_clicks or not any(n_clicks):
        return "", current_refresh
    
    # Identificar qual botão foi clicado
    if not ctx.triggered:
        return "", current_refresh
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    try:
        import json
        button_data = json.loads(button_id)
        rowid = button_data['index']
        
        # Encontrar o índice correspondente
        idx = None
        for i, id_dict in enumerate(ids):
            if id_dict['index'] == rowid:
                idx = i
                break
        
        if idx is None or valores[idx] is None:
            return dbc.Alert("⚠️ Selecione uma categoria antes de salvar!", color="warning", dismissable=True, duration=4000), current_refresh
        
        nova_categoria = valores[idx]
        
        # Atualizar no banco
        if atualizar_categoria_banco(rowid, nova_categoria):
            # Recarregar dados globais
            global df_global, df_pendentes
            df_global = carregar_dados()
            df_pendentes = carregar_transacoes_pendentes('TODOS')
            
            return (
                dbc.Alert(f"✅ Categoria '{nova_categoria}' salva com sucesso!", color="success", dismissable=True, duration=4000),
                current_refresh + 1  # Trigger refresh
            )
        else:
            return dbc.Alert("❌ Erro ao salvar categoria!", color="danger", dismissable=True, duration=4000), current_refresh
            
    except Exception as e:
        return dbc.Alert(f"❌ Erro: {str(e)}", color="danger", dismissable=True, duration=4000), current_refresh

# Callback para "Selecionar Todos"
@callback(
    Output({'type': 'checkbox-item', 'index': ALL}, 'value'),
    Input('checkbox-selecionar-todos', 'value'),
    State({'type': 'checkbox-item', 'index': ALL}, 'id'),
    prevent_initial_call=True
)
def selecionar_todos(selecionar_todos, checkbox_ids):
    """Seleciona ou desmarca todos os checkboxes"""
    if 'all' in selecionar_todos:
        # Selecionar todos
        return [[cb_id['index']] for cb_id in checkbox_ids]
    else:
        # Desmarcar todos
        return [[] for _ in checkbox_ids]

# Callback para aplicar categoria em lote
@callback(
    [Output('feedback-categorizacao', 'children', allow_duplicate=True),
     Output('refresh-trigger', 'data', allow_duplicate=True)],
    Input('btn-aplicar-lote', 'n_clicks'),
    [State('categoria-lote', 'value'),
     State({'type': 'checkbox-item', 'index': ALL}, 'value'),
     State({'type': 'checkbox-item', 'index': ALL}, 'id'),
     State('refresh-trigger', 'data')],
    prevent_initial_call=True
)
def aplicar_categoria_lote(n_clicks, categoria, checkboxes_values, checkboxes_ids, current_refresh):
    """Aplica categoria aos itens selecionados"""
    
    if not n_clicks or not categoria:
        if not categoria:
            return dbc.Alert("⚠️ Selecione uma categoria antes de aplicar!", color="warning", dismissable=True, duration=4000), current_refresh
        return "", current_refresh
    
    # Identificar rowids selecionados
    rowids_selecionados = []
    for i, checkbox_value in enumerate(checkboxes_values):
        if checkbox_value:  # Se o checkbox está marcado
            rowids_selecionados.append(checkboxes_ids[i]['index'])
    
    if not rowids_selecionados:
        return dbc.Alert("⚠️ Selecione ao menos uma transação!", color="warning", dismissable=True, duration=4000), current_refresh
    
    try:
        # Atualizar todos os selecionados
        sucesso = 0
        falhas = 0
        
        for rowid in rowids_selecionados:
            if atualizar_categoria_banco(rowid, categoria):
                sucesso += 1
            else:
                falhas += 1
        
        # Recarregar dados globais
        global df_global, df_pendentes
        df_global = carregar_dados()
        df_pendentes = carregar_transacoes_pendentes('TODOS')
        
        if falhas == 0:
            return (
                dbc.Alert(f"✅ Categoria '{categoria}' aplicada a {sucesso} transações!", color="success", dismissable=True, duration=4000),
                current_refresh + 1
            )
        else:
            return (
                dbc.Alert(f"⚠️ {sucesso} sucesso(s), {falhas} falha(s)", color="warning", dismissable=True, duration=4000),
                current_refresh + 1
            )
            
    except Exception as e:
        return dbc.Alert(f"❌ Erro: {str(e)}", color="danger", dismissable=True, duration=4000), current_refresh

# Callback para atualizar todos os gráficos
@callback(
    [Output('card-total', 'children'),
     Output('card-media', 'children'),
     Output('card-transacoes', 'children'),
     Output('card-meses', 'children'),
     Output('card-ideal-mes', 'children'),
     Output('card-diferenca-mes', 'children'),
     Output('card-diferenca-titulo', 'children'),
     Output('card-diferenca-border', 'style'),
     Output('col-ideal-mes', 'style'),
     Output('col-diferenca-mes', 'style'),
     Output('grafico-evolucao', 'figure'),
     Output('grafico-real-ideal', 'figure'),
     Output('grafico-fontes', 'figure'),
     Output('grafico-categorias', 'figure'),
     Output('grafico-distribuicao', 'figure'),
     Output('grafico-acumulado', 'figure'),
     Output('graficos-temporais', 'style')],
    [Input('filtro-mes', 'value'),
     Input('filtro-categoria', 'value'),
     Input('filtro-fonte', 'value'),
     Input('refresh-trigger', 'data')]
)
def atualizar_dashboard(mes_selecionado, categoria_selecionada, fonte_selecionada, refresh):
    """Atualiza todos os componentes do dashboard baseado nos filtros"""
    
    # Recarregar dados se houve atualização
    global df_global
    df_global = carregar_dados()
    
    if len(df_global) == 0:
        # Retornar valores padrão se não houver dados
        fig_vazio = go.Figure()
        fig_vazio.add_annotation(text="Sem dados disponíveis", showarrow=False, font=dict(size=20))
        return ("R$ 0", "R$ 0", "0", "0", "", "", "", {}, {'display': 'none'}, {'display': 'none'},
                fig_vazio, fig_vazio, fig_vazio, fig_vazio, fig_vazio, fig_vazio, {'display': 'none'})
    
    # ===== MÉDIA MENSAL: SEMPRE DOS ÚLTIMOS 12 MESES (NÃO AFETADA POR FILTROS) =====
    total_geral_global = df_global['valor_normalizado'].sum()
    num_meses_global = len(df_global['mes_comp'].unique())
    media_mensal_12m = total_geral_global / 12  # Sempre 12 meses como referência
    
    card_media = f"R$ {media_mensal_12m:,.0f}"
    
    # ===== APLICAR FILTROS =====
    df = df_global.copy()
    
    # Verificar se está filtrando por um único mês
    mostrar_graficos_temporais = (mes_selecionado == 'TODOS')
    
    if mes_selecionado != 'TODOS':
        df = df[df['mes_comp'] == mes_selecionado]
    
    if categoria_selecionada != 'TODOS':
        df = df[df['categoria'] == categoria_selecionada]
    
    if fonte_selecionada != 'TODOS':
        df = df[df['fonte'] == fonte_selecionada]
    
    # ===== CARDS DINÂMICOS (baseados no filtro aplicado) =====
    total_filtrado = df['valor_normalizado'].sum()
    num_transacoes = len(df)
    num_meses = len(df['mes_comp'].unique()) if len(df) > 0 else 1
    
    # Card Total - mostra "período" se filtrado
    if mes_selecionado != 'TODOS':
        card_total = html.Div([
            html.Div(f"R$ {total_filtrado:,.0f}", style={'fontWeight': 'bold'}),
            html.Small(mes_selecionado, style={'fontSize': '0.7rem'})
        ])
    else:
        card_total = f"R$ {total_filtrado:,.0f}"
    
    card_transacoes = f"{num_transacoes:,}"
    card_meses = str(num_meses)
    
    # ===== CARDS EXTRAS QUANDO MÊS ESPECÍFICO =====
    if mes_selecionado != 'TODOS':
        # Calcular orçamento ideal do mês (usando ORCAMENTO_IDEAL_FONTE = R$ 26.670)
        ideal_mes = sum(ORCAMENTO_IDEAL_FONTE.values())
        diferenca_mes = total_filtrado - ideal_mes
        
        card_ideal_mes = f"R$ {ideal_mes:,.0f}"
        
        # Card Diferença com cor e título dinâmico
        if diferenca_mes > 0:
            # Excedeu
            card_diferenca_mes = html.Div([
                html.Div(f"R$ {abs(diferenca_mes):,.0f}", style={'fontWeight': 'bold', 'color': '#dc3545'}),
                html.Small("acima do ideal", style={'fontSize': '0.7rem'})
            ])
            card_diferenca_titulo = "🔴 Excedeu"
            card_diferenca_border_style = {'border': '2px solid #dc3545', 'padding': '0.75rem'}
        else:
            # Economizou
            card_diferenca_mes = html.Div([
                html.Div(f"R$ {abs(diferenca_mes):,.0f}", style={'fontWeight': 'bold', 'color': '#28a745'}),
                html.Small("abaixo do ideal", style={'fontSize': '0.7rem'})
            ])
            card_diferenca_titulo = "🟢 Economizou"
            card_diferenca_border_style = {'border': '2px solid #28a745', 'padding': '0.75rem'}
        
        col_ideal_mes_style = {'display': 'block'}
        col_diferenca_mes_style = {'display': 'block'}
    else:
        # Esconder cards quando ver todos os meses
        card_ideal_mes = ""
        card_diferenca_mes = ""
        card_diferenca_titulo = ""
        card_diferenca_border_style = {'padding': '0.75rem'}
        col_ideal_mes_style = {'display': 'none'}
        col_diferenca_mes_style = {'display': 'none'}
    
    # Lista de todos os meses (extrair dos dados disponíveis)
    todos_meses = sorted(df_global['mes_comp'].unique())
    
    # Gráfico 1: Evolução Mensal OU Real vs Ideal por Fonte (depende do filtro)
    if mostrar_graficos_temporais:
        # Mostrar Evolução Mensal (quando vendo todos os meses)
        gastos_por_mes = df.groupby('mes_comp')['valor_normalizado'].sum()
        
        media = gastos_por_mes.mean()
        
        fig_evolucao = go.Figure()
        fig_evolucao.add_trace(go.Bar(
            x=gastos_por_mes.index,
            y=gastos_por_mes.values,
            name='Gastos',
            marker_color='rgb(55, 83, 109)',
            text=[f'{v/1000:.1f}k' if v >= 1000 else f'R$ {v:.0f}' for v in gastos_por_mes.values],
            textposition='outside',
            textfont={'size': 10, 'family': 'Arial, sans-serif'}
        ))
        fig_evolucao.add_trace(go.Scatter(
            x=gastos_por_mes.index,
            y=[media] * len(gastos_por_mes),
            mode='lines',
            name=f'Média: R$ {media:,.2f}',
            line=dict(color='red', dash='dash', width=3)
        ))
        fig_evolucao.update_layout(
            title={'text': '📊 Evolução Mensal', 'font': {'size': 24}},
            xaxis_title='Mês',
            yaxis_title='Valor (R$)',
            height=500,
            hovermode='x unified',
            showlegend=True,
            font={'size': 18},
            xaxis={'tickfont': {'size': 18}, 'title': {'font': {'size': 20}}},
            yaxis={'tickfont': {'size': 18}, 'title': {'font': {'size': 20}}},
            legend={'font': {'size': 14}},
            uniformtext={'minsize': 10, 'mode': 'show'}
        )
    else:
        # Mostrar Real vs Ideal por Fonte (quando filtrando um mês)
        gastos_por_fonte = df.groupby('fonte')['valor_normalizado'].sum().sort_values(ascending=False)
        
        # Calcular ideal por fonte usando orçamento mapeado
        ideal_por_fonte = []
        diferenca_por_fonte = []
        diferenca_colors_fonte = []
        
        for i, fonte in enumerate(gastos_por_fonte.index):
            # Buscar ideal mapeado ou usar 0 se fonte não mapeada
            ideal_valor = ORCAMENTO_IDEAL_FONTE.get(fonte, 0) * num_meses
            ideal_por_fonte.append(ideal_valor)
            
            # Calcular diferença
            real_valor = gastos_por_fonte.values[i]
            diferenca = real_valor - ideal_valor
            diferenca_por_fonte.append(abs(diferenca))
            
            # Cor: Verde se economizou, Vermelho se excedeu
            if diferenca > 0:
                diferenca_colors_fonte.append('rgb(220, 53, 69)')  # Vermelho (excedeu)
            else:
                diferenca_colors_fonte.append('rgb(40, 167, 69)')  # Verde (economizou)
        
        fig_evolucao = go.Figure()
        
        # Barra 1: Real (Laranja)
        fig_evolucao.add_trace(go.Bar(
            x=gastos_por_fonte.index,
            y=gastos_por_fonte.values,
            name='Real',
            marker_color='rgb(255, 140, 0)',
            text=[f'{v/1000:.1f}k' if v >= 1000 else f'R$ {v:.0f}' for v in gastos_por_fonte.values],
            textposition='outside',
            textfont={'size': 10, 'family': 'Arial, sans-serif'},
            hovertemplate='<b>%{x}</b><br>Real: R$ %{y:,.2f}<extra></extra>'
        ))
        
        # Barra 2: Ideal (Azul)
        fig_evolucao.add_trace(go.Bar(
            x=gastos_por_fonte.index,
            y=ideal_por_fonte,
            name='Ideal',
            marker_color='rgb(0, 123, 255)',
            text=[f'{v/1000:.1f}k' if v >= 1000 else f'R$ {v:.0f}' for v in ideal_por_fonte],
            textposition='outside',
            textfont={'size': 10, 'family': 'Arial, sans-serif'},
            hovertemplate='<b>%{x}</b><br>Ideal: R$ %{y:,.2f}<extra></extra>'
        ))
        
        # Barra 3: Diferença (Verde/Vermelho)
        hover_texts_fonte = []
        for i, fonte in enumerate(gastos_por_fonte.index):
            real = gastos_por_fonte.values[i]
            ideal = ideal_por_fonte[i]
            dif = real - ideal
            status = "Excedeu" if dif > 0 else "Economizou"
            hover_texts_fonte.append(f'<b>{fonte}</b><br>{status}: R$ {abs(dif):,.2f}')
        
        fig_evolucao.add_trace(go.Bar(
            x=gastos_por_fonte.index,
            y=diferenca_por_fonte,
            name='Diferença',
            marker_color=diferenca_colors_fonte,
            text=[f'<b style="color: {"red" if gastos_por_fonte.values[i] > ideal_por_fonte[i] else "green"}">{v/1000:.1f}k</b>' if v >= 1000 else f'<b style="color: {"red" if gastos_por_fonte.values[i] > ideal_por_fonte[i] else "green"}">R$ {v:.0f}</b>'
                  for i, v in enumerate(diferenca_por_fonte)],
            textposition='outside',
            textfont={'size': 12, 'family': 'Arial, sans-serif'},
            hovertemplate='%{customdata}<extra></extra>',
            customdata=hover_texts_fonte
        ))
        
        fig_evolucao.update_layout(
            title={'text': f'💳 Real vs Ideal por Fonte - {mes_selecionado}', 'font': {'size': 24}},
            xaxis_title='Fonte',
            yaxis_title='Valor (R$)',
            height=500,
            barmode='group',
            hovermode='x unified',
            font={'size': 18},
            xaxis={'tickfont': {'size': 18}, 'title': {'font': {'size': 20}}},
            yaxis={'tickfont': {'size': 18}, 'title': {'font': {'size': 20}}},
            legend={'font': {'size': 14}},
            uniformtext={'minsize': 10, 'mode': 'show'}
        )
    
    # Gráfico 2: Real vs Ideal (MAIOR E PRINCIPAL - VERTICAL)
    gastos_por_categoria = df.groupby('categoria')['valor_normalizado'].sum().sort_values(ascending=False)
    
    ideal_values = []
    diferenca_values = []
    diferenca_colors = []
    
    for cat in gastos_por_categoria.index:
        orcamento_cat = ORCAMENTO_IDEAL.get(cat, 0)
        ideal_total = orcamento_cat * num_meses
        ideal_values.append(ideal_total)
        
        # Calcular diferença (Real - Ideal)
        real_valor = gastos_por_categoria.loc[cat]
        diferenca = real_valor - ideal_total
        diferenca_values.append(abs(diferenca))
        
        # Cor: Verde se economizou, Vermelho se excedeu
        if diferenca > 0:
            diferenca_colors.append('rgb(220, 53, 69)')  # Vermelho (excedeu)
        else:
            diferenca_colors.append('rgb(40, 167, 69)')  # Verde (economizou)
    
    fig_real_ideal = go.Figure()
    
    # Barra 1: Real (Laranja)
    fig_real_ideal.add_trace(go.Bar(
        x=gastos_por_categoria.index,
        y=gastos_por_categoria.values,
        name='Real',
        marker_color='rgb(255, 140, 0)',  # Laranja
        text=[f'{v/1000:.1f}k' if v >= 1000 else f'R$ {v:.0f}' for v in gastos_por_categoria.values],
        textposition='outside',
        textfont={'size': 10, 'family': 'Arial, sans-serif'},
        hovertemplate='<b>%{x}</b><br>Real: R$ %{y:,.2f}<extra></extra>'
    ))
    
    # Barra 2: Ideal (Azul)
    fig_real_ideal.add_trace(go.Bar(
        x=gastos_por_categoria.index,
        y=ideal_values,
        name='Ideal',
        marker_color='rgb(0, 123, 255)',  # Azul
        text=[f'{v/1000:.1f}k' if v >= 1000 else f'R$ {v:.0f}' for v in ideal_values],
        textposition='outside',
        textfont={'size': 10, 'family': 'Arial, sans-serif'},
        hovertemplate='<b>%{x}</b><br>Ideal: R$ %{y:,.2f}<extra></extra>'
    ))
    
    # Barra 3: Diferença (Verde/Vermelho)
    hover_texts = []
    for i, cat in enumerate(gastos_por_categoria.index):
        real = gastos_por_categoria.values[i]
        ideal = ideal_values[i]
        dif = real - ideal
        status = "Excedeu" if dif > 0 else "Economizou"
        hover_texts.append(f'<b>{cat}</b><br>{status}: R$ {abs(dif):,.2f}')
    
    fig_real_ideal.add_trace(go.Bar(
        x=gastos_por_categoria.index,
        y=diferenca_values,
        name='Diferença',
        marker_color=diferenca_colors,
        text=[f'<b style="color: {"red" if gastos_por_categoria.values[i] > ideal_values[i] else "green"}">{v/1000:.1f}k</b>' if v >= 1000 else f'<b style="color: {"red" if gastos_por_categoria.values[i] > ideal_values[i] else "green"}">R$ {v:.0f}</b>'
              for i, v in enumerate(diferenca_values)],
        textposition='outside',
        textfont={'size': 12, 'family': 'Arial, sans-serif'},
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_texts
    ))
    fig_real_ideal.update_layout(
        title={'text': f'💰 Real vs Ideal - {num_meses} meses', 'font': {'size': 24}},
        xaxis_title='Categoria',
        yaxis_title='Valor (R$)',
        height=500,
        barmode='group',
        hovermode='x unified',
        xaxis_tickangle=-45,
        font={'size': 18},
        xaxis={'tickfont': {'size': 18}, 'title': {'font': {'size': 20}}},
        yaxis={'tickfont': {'size': 18}, 'title': {'font': {'size': 20}}},
        legend={'font': {'size': 14}},
        uniformtext={'minsize': 10, 'mode': 'show'}
    )
    
    # Gráfico 3: Gastos por Fonte (PIZZA)
    gastos_por_fonte = df.groupby('fonte')['valor_normalizado'].sum().sort_values(ascending=False)
    
    fig_fontes = go.Figure(data=[go.Pie(
        labels=gastos_por_fonte.index,
        values=gastos_por_fonte.values,
        hole=0.3,
        textinfo='label+percent',
        textposition='outside'
    )])
    fig_fontes.update_layout(
        title={'text': '💳 Gastos por Fonte', 'font': {'size': 24}},
        height=450,
        font={'size': 18}
    )
    
    # Gráfico 4: Categorias (PIZZA TAMBÉM)
    gastos_todas_cat = df.groupby('categoria')['valor_normalizado'].sum().sort_values(ascending=False)
    
    fig_categorias = go.Figure(data=[go.Pie(
        labels=gastos_todas_cat.index,
        values=gastos_todas_cat.values,
        hole=0.3,
        textinfo='label+percent',
        textposition='outside'
    )])
    fig_categorias.update_layout(
        title={'text': '🏷️ Gastos por Categoria', 'font': {'size': 24}},
        height=450,
        font={'size': 18}
    )
    
    # Gráfico 5: Distribuição de Transações
    transacoes_por_mes = df.groupby('mes_comp').size()
    
    fig_distribuicao = go.Figure(data=[go.Scatter(
        x=transacoes_por_mes.index,
        y=transacoes_por_mes.values,
        mode='lines+markers',
        marker=dict(size=10),
        line=dict(width=3)
    )])
    fig_distribuicao.update_layout(
        title={'text': '📅 Distribuição de Transações por Mês', 'font': {'size': 24}},
        xaxis_title='Mês',
        yaxis_title='Número de Transações',
        height=400,
        font={'size': 18},
        xaxis={'tickfont': {'size': 18}, 'title': {'font': {'size': 20}}},
        yaxis={'tickfont': {'size': 18}, 'title': {'font': {'size': 20}}}
    )
    
    # Gráfico 6: Acumulado Anual
    df_sorted = df.sort_values('data')
    df_sorted['acumulado'] = df_sorted['valor_normalizado'].cumsum()
    
    fig_acumulado = go.Figure(data=[go.Scatter(
        x=df_sorted['data'],
        y=df_sorted['acumulado'],
        mode='lines',
        fill='tozeroy',
        line=dict(color='rgb(111, 231, 219)')
    )])
    fig_acumulado.update_layout(
        title={'text': '📈 Acumulado Anual', 'font': {'size': 24}},
        xaxis_title='Data',
        yaxis_title='Valor Acumulado (R$)',
        height=400,
        font={'size': 18},
        xaxis={'tickfont': {'size': 18}, 'title': {'font': {'size': 20}}},
        yaxis={'tickfont': {'size': 18}, 'title': {'font': {'size': 20}}}
    )
    
    # Controlar visibilidade dos gráficos temporais
    estilo_graficos_temporais = {'display': 'block'} if mostrar_graficos_temporais else {'display': 'none'}
    
    return (card_total, card_media, card_transacoes, card_meses,
            card_ideal_mes, card_diferenca_mes, card_diferenca_titulo, card_diferenca_border_style,
            col_ideal_mes_style, col_diferenca_mes_style,
            fig_evolucao, fig_real_ideal, fig_fontes, fig_categorias,
            fig_distribuicao, fig_acumulado, estilo_graficos_temporais)


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 DASHBOARD INTERATIVO EXCEL/TXT")
    print("="*70)
    print(f"📊 {len(df_global):,} transações carregadas")
    if len(df_global) > 0:
        print(f"💰 Total: R$ {df_global['valor_normalizado'].sum():,.2f}")
    else:
        print("⚠️  Nenhuma transação encontrada. Execute agente_financeiro.py primeiro!")
    print("="*70)
    print("\n🌐 Acesso local: http://localhost:8051")
    print("🌐 Acesso rede: http://<IP_DESTA_MAQUINA>:8051")
    print("⌨️  Pressione CTRL+C para encerrar\n")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=8051)
