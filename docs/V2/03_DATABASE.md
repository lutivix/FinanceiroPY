# 💾 Database - Dashboard V2

## Estrutura do Banco

### Localização
```
dados/db/financeiro.db
```

### Tabela: `lancamentos`

```sql
CREATE TABLE lancamentos (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Data DATE,
    Descricao TEXT,
    Valor REAL,
    Categoria TEXT,
    Fonte TEXT,
    MesComp TEXT,
    -- Outras colunas...
);
```

### Colunas Utilizadas

| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `Data` | DATE | Data da transação | `2025-01-15` |
| `Descricao` | TEXT | Descrição da transação | `UBER *TRIP` |
| `Valor` | REAL | Valor (+ débito, - crédito) | `50.00` ou `-3000.00` |
| `Categoria` | TEXT | Categoria da transação | `Transporte`, `A definir` |
| `Fonte` | TEXT | Fonte da transação | `Nubank`, `PIX`, `BOLETO` |
| `MesComp` | TEXT | Mês de compensação | `2025-01` |

## Convenção de Sinais ⚠️

**CRÍTICO**: O banco usa convenção invertida!

```python
# ✅ DÉBITOS (Gastos) = Valor POSITIVO
valor > 0  # Ex: 50.00 = Gasto de R$ 50

# ✅ CRÉDITOS (Receitas) = Valor NEGATIVO  
valor < 0  # Ex: -3000.00 = Receita de R$ 3.000
```

### Por que essa convenção?

Sistema de dupla entrada contábil:
- Débito na conta bancária = saída de dinheiro = positivo
- Crédito na conta bancária = entrada de dinheiro = negativo

## Queries Principais

### 1. Carregar Transações

```python
# utils/database.py - linha ~20
def carregar_transacoes(mes_filtro=None):
    query = """
    SELECT 
        Data as data,
        Descricao as descricao,
        Valor as valor,
        CAST(SUBSTR(Valor, 3) AS REAL) as valor_normalizado,
        Categoria as categoria,
        Fonte as fonte,
        MesComp as mes_comp
    FROM lancamentos
    WHERE Valor IS NOT NULL
    """
    
    if mes_filtro and mes_filtro != 'TODOS':
        query += f" AND MesComp = '{mes_filtro}'"
    
    df = pd.read_sql_query(query, conn)
    return df
```

**Retorno**:
```python
pd.DataFrame([
    {'data': '2025-01-15', 'descricao': 'UBER *TRIP', 'valor': 50.0, 
     'valor_normalizado': 50.0, 'categoria': 'Transporte', 
     'fonte': 'Nubank', 'mes_comp': '2025-01'},
    ...
])
```

### 2. Calcular Estatísticas

```python
# utils/database.py - linha ~145
def calcular_estatisticas(df):
    # ✅ Filtro correto: valor > 0 (débitos)
    df_debitos = df[df['valor'] > 0].copy()
    
    total = df_debitos['valor_normalizado'].sum()
    
    # Cartões
    cartoes = df_debitos[
        df_debitos['fonte'].isin(['Nubank', 'Itaú', 'BTG'])
    ]['valor_normalizado'].sum()
    
    # Pix + Boleto
    pix_boleto = df_debitos[
        df_debitos['fonte'].isin(['PIX', 'BOLETO'])
    ]['valor_normalizado'].sum()
    
    return {
        'total': total,
        'cartoes': cartoes,
        'pix_boleto': pix_boleto
    }
```

### 3. Obter Meses Disponíveis

```python
# utils/database.py - linha ~180
def obter_meses_disponiveis():
    query = "SELECT DISTINCT MesComp FROM lancamentos ORDER BY MesComp DESC"
    df = pd.read_sql_query(query, conn)
    return df['MesComp'].tolist()
```

**Retorno**: `['2025-01', '2024-12', '2024-11', ...]`

### 4. Obter Categorias/Fontes Únicas

```python
def obter_categorias_unicas(df):
    return sorted(df['categoria'].unique().tolist())

def obter_fontes_unicas(df):
    return sorted(df['fonte'].unique().tolist())
```

## Exemplos de Dados

### Débitos (Gastos)
```sql
SELECT * FROM lancamentos 
WHERE Valor > 0 AND Categoria != 'SALÁRIO' 
LIMIT 5;

-- Resultado:
Data       | Descricao        | Valor  | Categoria   | Fonte
2025-01-15 | UBER *TRIP       | 50.00  | Transporte  | Nubank
2025-01-14 | IFOOD            | 35.50  | Alimentação | Itaú
2025-01-13 | NETFLIX          | 39.90  | Lazer       | BTG
```

### Créditos (Receitas)
```sql
SELECT * FROM lancamentos 
WHERE Valor < 0 
LIMIT 5;

-- Resultado:
Data       | Descricao     | Valor     | Categoria      | Fonte
2025-01-05 | SALÁRIO       | -3000.00  | SALÁRIO        | PIX
2025-01-10 | INVESTIMENTO  | -500.00   | INVESTIMENTOS  | PIX
```

### Distribuição Atual
```python
# 2.256 transações totais
débitos = 65    # Valor > 0 (gastos ~R$ 2.000)
créditos = 2.191  # Valor < 0 (receitas)
```

## Transformações de Dados

### Formatação de Valores

```python
# Formatação monetária
df['valor_formatado'] = df['valor_normalizado'].apply(
    lambda x: f"R$ {x:,.2f}"
)
# Resultado: "R$ 1.234,56"
```

### Formatação de Datas

```python
# String para datetime
df['data'] = pd.to_datetime(df['data'])

# Datetime para string formatada
df['data_formatada'] = df['data'].dt.strftime('%d/%m/%Y')
# Resultado: "15/01/2025"
```

### Agrupamentos

```python
# Por categoria
por_categoria = df.groupby('categoria')['valor_normalizado'].sum()

# Por mês
df['mes'] = df['data'].dt.to_period('M')
por_mes = df.groupby('mes')['valor_normalizado'].sum()

# Por fonte
por_fonte = df.groupby('fonte')['valor_normalizado'].sum()
```

## Filtros Combinados

```python
# Exemplo de filtro completo (transacoes.py callback)
df_filtrado = df[df['valor'] > 0].copy()  # Apenas débitos

# Categoria
if categoria_filtro and categoria_filtro != 'TODOS':
    df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_filtro]

# Fonte
if fonte_filtro and fonte_filtro != 'TODOS':
    df_filtrado = df_filtrado[df_filtrado['fonte'] == fonte_filtro]

# Status (categorizadas vs pendentes)
if status_filtro == 'CATEGORIZADAS':
    df_filtrado = df_filtrado[df_filtrado['categoria'] != 'A definir']
elif status_filtro == 'PENDENTES':
    df_filtrado = df_filtrado[df_filtrado['categoria'] == 'A definir']

# Mês de compensação
if mes_comp_filtro and mes_comp_filtro != 'TODOS':
    df_filtrado = df_filtrado[df_filtrado['mes_comp'] == mes_comp_filtro]

# Período (data range)
if data_inicio:
    df_filtrado = df_filtrado[df_filtrado['data'] >= pd.to_datetime(data_inicio)]
if data_fim:
    df_filtrado = df_filtrado[df_filtrado['data'] <= pd.to_datetime(data_fim)]
```

## Ordenação

```python
# Ordenação inteligente (transacoes.py)
df_tabela = df_filtrado.sort_values(
    ['mes_comp', 'fonte', 'data'],  # Colunas
    ascending=[True, False, True]    # Direções
)

# Resultado:
# mes_comp: 2024-11, 2024-12, 2025-01 (crescente)
#   ├─ fonte: Nubank, Itaú, BTG, PIX (decrescente alfabético)
#   │   └─ data: 01/01, 05/01, 15/01 (crescente)
```

## Performance

### Queries Lentas
```sql
-- ❌ LENTO (full scan)
SELECT * FROM lancamentos WHERE Valor > 0;

-- ✅ RÁPIDO (com índice)
CREATE INDEX idx_valor ON lancamentos(Valor);
SELECT * FROM lancamentos WHERE Valor > 0;
```

### Otimizações Recomendadas

```sql
-- Índices sugeridos
CREATE INDEX idx_mescomp ON lancamentos(MesComp);
CREATE INDEX idx_categoria ON lancamentos(Categoria);
CREATE INDEX idx_fonte ON lancamentos(Fonte);
CREATE INDEX idx_data ON lancamentos(Data);

-- Índice composto para filtros combinados
CREATE INDEX idx_filtros ON lancamentos(MesComp, Categoria, Fonte);
```

## Backup e Manutenção

### Backup Manual
```bash
# Windows
copy dados\db\financeiro.db dados\db\backup\financeiro_2025-01-23.db

# Linux/Mac
cp dados/db/financeiro.db dados/db/backup/financeiro_2025-01-23.db
```

### Vacuum (Otimização)
```python
import sqlite3
conn = sqlite3.connect('dados/db/financeiro.db')
conn.execute('VACUUM')
conn.close()
```

## Troubleshooting

### Erro: "database is locked"
```python
# Solução: Usar timeout
conn = sqlite3.connect('dados/db/financeiro.db', timeout=30)
```

### Erro: "no such table: lancamentos"
```python
# Verificar caminho do banco
from pathlib import Path
DB_PATH = Path(__file__).parent.parent.parent.parent / 'dados' / 'db' / 'financeiro.db'
assert DB_PATH.exists(), f"Banco não encontrado: {DB_PATH}"
```

### Valores zerados nos gráficos
```python
# ✅ Verificar convenção de sinais
df_debitos = df[df['valor'] > 0]  # NÃO < 0!
```
