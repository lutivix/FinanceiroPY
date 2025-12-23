# 🐛 Troubleshooting - Dashboard V2

## Problemas Comuns

### 1. Gráficos Mostrando Valores Errados

**Sintoma**: Dashboard mostra R$ 14.500 em vez de ~R$ 2.000

**Causa**: Filtro de débitos invertido
```python
# ❌ ERRADO
df_debitos = df[df['valor'] < 0]  # Pega créditos!

# ✅ CORRETO
df_debitos = df[df['valor'] > 0]  # Pega débitos
```

**Solução**: Verificar convenção do banco
- Débitos (gastos) = valor POSITIVO (> 0)
- Créditos (receitas) = valor NEGATIVO (< 0)

**Arquivos afetados**:
- `utils/database.py` - linha 147
- `utils/graficos.py` - criar_grafico_evolucao(), criar_grafico_top_categorias(), criar_grafico_top_fontes()

---

### 2. Tabela de Transações Não Carrega

**Sintoma**: "Carregando transações..." infinito

**Causa 1**: `prevent_initial_call=True` no callback
```python
# ❌ ERRADO
@callback(..., prevent_initial_call=True)
def atualizar_tabela(...):
    # Nunca executa na primeira carga!
```

**Solução**: Remover `prevent_initial_call`

**Causa 2**: Validação excessiva
```python
# ❌ ERRADO
if not all([categoria_filtro, fonte_filtro, status_filtro, mes_comp_filtro is not None]):
    return "Carregando..."  # Sempre True se mes_comp_filtro = 'TODOS'
```

**Solução**: Remover validação ou usar null checks individuais

---

### 3. Callback Error: "Component X does not exist"

**Sintoma**: 
```
Callback error updating tabela-transacoes-container.children
Component filtro-categoria-transacoes does not exist
```

**Causa**: Callback referencia componentes que só existem em página específica

**Problema**: 
```python
@callback(
    Output('tabela-transacoes-container', 'children'),
    [Input('filtro-categoria-transacoes', 'value')]  # Só existe em /transacoes
)
```

**Soluções**:

1. **Usar suppress_callback_exceptions** (já feito)
```python
app = Dash(__name__, suppress_callback_exceptions=True)
```

2. **Null checks nos callbacks**
```python
if not categoria_filtro:
    return "Aguardando filtros..."
```

3. **Não usar prevent_initial_call** (permite execução inicial com valores padrão)

---

### 4. DatePicker Aparece Atrás da Tabela

**Sintoma**: Calendário do DatePickerRange fica oculto

**Causa**: z-index insuficiente

**Solução**: CSS com z-index alto
```css
.DateRangePicker_picker {
    z-index: 9999 !important;
}

.Select-menu-outer {
    z-index: 9999 !important;
}
```

---

### 5. Loading chunk 214 failed (async-table.js)

**Sintoma**: 
```
Loading chunk 214 failed
(error: http://localhost:8052/_dash-component-suites/dash/dash_table/async-table.js)
```

**Causa**: DataTable tentando carregar chunk JS assíncrono (falha intermitente)

**Solução**: Substituir por tabela HTML customizada
```python
# ❌ ANTES
from dash import dash_table
return dash_table.DataTable(...)

# ✅ DEPOIS
return html.Table([
    html.Thead(...),
    html.Tbody(rows)
])
```

---

### 6. Filtros Não Atualizam a Tabela

**Sintoma**: Mudar filtro não altera dados exibidos

**Causa**: Comparação com None
```python
# ❌ ERRADO
if categoria_filtro != 'TODOS':  # Falha se categoria_filtro = None
    df = df[df['categoria'] == categoria_filtro]
```

**Solução**: Null checks
```python
# ✅ CORRETO
if categoria_filtro and categoria_filtro != 'TODOS':
    df = df[df['categoria'] == categoria_filtro]
```

---

### 7. Ordenação de Datas Incorreta

**Sintoma**: Tabela ordena datas como strings ("01/12" antes de "30/11")

**Causa**: Formatar data antes de ordenar
```python
# ❌ ERRADO
df['data'] = df['data'].dt.strftime('%d/%m/%Y')  # Vira string
df = df.sort_values('data')  # Ordena strings!
```

**Solução**: Ordenar antes de formatar
```python
# ✅ CORRETO
df = df.sort_values('data')  # Ordena datetime
df['data'] = df['data'].dt.strftime('%d/%m/%Y')  # Depois formata
```

---

### 8. Subtotal Incorreto

**Sintoma**: Subtotal não bate com soma das transações visíveis

**Causa**: Calcular depois de `.head()`
```python
# ❌ ERRADO
df_tabela = df_filtrado.head(100)
subtotal = df_tabela['valor'].sum()  # Soma apenas 100
```

**Solução**: Calcular antes de limitar
```python
# ✅ CORRETO
subtotal = df_filtrado['valor'].sum()  # Soma todas filtradas
df_tabela = df_filtrado.head(100)  # Depois limita
```

---

### 9. Database Locked

**Sintoma**: 
```
sqlite3.OperationalError: database is locked
```

**Causa**: Múltiplas conexões simultâneas

**Soluções**:

1. **Usar timeout**
```python
conn = sqlite3.connect('dados/db/financeiro.db', timeout=30)
```

2. **Fechar conexões explicitamente**
```python
conn = sqlite3.connect(...)
try:
    df = pd.read_sql_query(query, conn)
finally:
    conn.close()
```

3. **Connection pooling** (para produção)

---

### 10. CSS Não Aplicado

**Sintoma**: Sidebar sem estilo, dropdowns com fundo branco

**Causa**: CSS não injetado ou classes incorretas

**Soluções**:

1. **Verificar injeção no main.py**
```python
from dashboard_v2.assets.custom_styles import get_custom_styles
app.index_string = get_custom_styles()
```

2. **Verificar className**
```python
html.Div(..., className="custom-card")  # Deve corresponder ao CSS
```

3. **Hard refresh no browser** (Ctrl+Shift+R)

---

## Debugging

### Imprimir Inputs de Callbacks

```python
@callback(...)
def atualizar_tabela(mes, categoria, fonte, ...):
    print(f"""
    DEBUG INPUTS:
    mes={mes}
    categoria={categoria}
    fonte={fonte}
    """)
    # ... resto do código
```

### Verificar Triggered

```python
from dash import ctx

@callback(...)
def atualizar_tabela(...):
    print(f"Triggered by: {ctx.triggered_id}")
    print(f"Triggered prop: {ctx.triggered_prop_ids}")
    # Mostra qual input disparou o callback
```

### Contar Registros em Cada Filtro

```python
print(f"Inicial: {len(df)} registros")

df = df[df['valor'] > 0]
print(f"Após filtro débitos: {len(df)} registros")

df = df[df['categoria'] == categoria_filtro]
print(f"Após filtro categoria: {len(df)} registros")
```

### Verificar Tipos de Dados

```python
print(f"Tipo de data: {df['data'].dtype}")
print(f"Tipo de valor: {df['valor'].dtype}")

# Se não for datetime/float, converter:
df['data'] = pd.to_datetime(df['data'])
df['valor'] = df['valor'].astype(float)
```

---

## Performance Issues

### Queries Lentas

**Sintoma**: Dashboard demora >3s para carregar

**Diagnóstico**:
```python
import time
start = time.time()
df = carregar_transacoes()
print(f"Query took: {time.time() - start:.2f}s")
```

**Soluções**:

1. **Criar índices**
```sql
CREATE INDEX idx_mescomp ON lancamentos(MesComp);
CREATE INDEX idx_valor ON lancamentos(Valor);
CREATE INDEX idx_categoria ON lancamentos(Categoria);
```

2. **Filtrar no SQL**
```python
# ❌ LENTO
df = carregar_transacoes()  # Carrega tudo
df = df[df['mes_comp'] == '2025-01']  # Filtra em Python

# ✅ RÁPIDO
df = carregar_transacoes(mes_filtro='2025-01')  # Filtra no SQL
```

3. **Limitar registros**
```python
query += " LIMIT 1000"
```

---

### Tabela Pesada

**Sintoma**: Scroll lento, browser trava

**Causa**: Muitos elementos HTML (>1000 linhas)

**Soluções**:

1. **Limitar registros**
```python
df_tabela = df_filtrado.head(100)
```

2. **Paginação** (futuro)
```python
# TODO: Implementar com dash_table.DataTable pagination
```

3. **Virtual scrolling** (avançado)

---

## Erros de Instalação

### Dash Import Error

**Erro**: `ModuleNotFoundError: No module named 'dash'`

**Solução**:
```bash
pip install dash>=3.2.0
pip install dash-bootstrap-components>=1.5.0
```

### Plotly Version Conflict

**Erro**: `AttributeError: module 'plotly' has no attribute 'graph_objects'`

**Solução**:
```bash
pip install --upgrade plotly>=5.18.0
```

### Pandas DateTime Error

**Erro**: `TypeError: Cannot convert input to Timestamp`

**Solução**: Verificar formato de data no banco
```python
df['data'] = pd.to_datetime(df['data'], errors='coerce')  # Ignora erros
```

---

## Verificações Rápidas

### Checklist de Diagnóstico

```python
# 1. Banco de dados existe?
from pathlib import Path
DB_PATH = Path('dados/db/financeiro.db')
assert DB_PATH.exists(), f"Banco não encontrado: {DB_PATH}"

# 2. Tabela existe?
import sqlite3
conn = sqlite3.connect(DB_PATH)
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
assert 'lancamentos' in tables, f"Tabela não encontrada. Tabelas: {tables}"

# 3. Colunas corretas?
cursor = conn.execute("PRAGMA table_info(lancamentos)")
columns = [row[1] for row in cursor.fetchall()]
required = ['Data', 'Valor', 'Categoria', 'Fonte', 'MesComp']
for col in required:
    assert col in columns, f"Coluna {col} não encontrada. Colunas: {columns}"

# 4. Dados existem?
cursor = conn.execute("SELECT COUNT(*) FROM lancamentos")
count = cursor.fetchone()[0]
assert count > 0, f"Tabela vazia! Registros: {count}"

conn.close()
print("✅ Todas as verificações passaram!")
```

---

## Logs Úteis

### Habilitar Debug Mode

```python
# main.py - linha final
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8052,
        debug=True  # ← Habilita hot reload e stack traces
    )
```

### Logs de Callbacks

```python
import logging
logging.basicConfig(level=logging.DEBUG)

@callback(...)
def atualizar_tabela(...):
    logging.debug(f"Callback executado com mes={mes_selecionado}")
    # ...
```

---

## Recursos Externos

### Documentação Oficial
- [Dash Docs](https://dash.plotly.com/)
- [Plotly Python](https://plotly.com/python/)
- [Pandas Docs](https://pandas.pydata.org/docs/)

### Comunidade
- [Dash Community Forum](https://community.plotly.com/c/dash/)
- [Stack Overflow - Dash Tag](https://stackoverflow.com/questions/tagged/plotly-dash)

### Ferramentas
- [Chrome DevTools](https://developer.chrome.com/docs/devtools/) - Inspecionar CSS/JS
- [DB Browser for SQLite](https://sqlitebrowser.org/) - Visualizar banco
- [Postman](https://www.postman.com/) - Testar APIs (se adicionar backend REST)
