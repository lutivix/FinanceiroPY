# 📊 Dashboard Interativo Open Finance

> **Visualização em tempo real + Categorização inline + Análise inteligente**

Dashboard desenvolvido com Dash e Plotly para análise visual e interativa de transações financeiras, com capacidade de categorizar pendências diretamente na interface.

---

## 🎯 **Visão Geral**

O Dashboard Interativo foi desenvolvido para otimizar a análise financeira em telas QHD (2560×1440), oferecendo:

- ✅ **6 cards informativos** compactos e dinâmicos
- ✅ **Categorização inline** de transações "A definir"
- ✅ **Filtros dinâmicos** (Mês, Categoria, Fonte)
- ✅ **7 gráficos interativos** com Plotly
- ✅ **Valores normalizados** em formato k (14.4k)
- ✅ **Cores inteligentes** (verde/vermelho)
- ✅ **Ferramentas nativas** (zoom, pan, download)

---

## 🚀 **Como Executar**

### Método 1: Terminal

```bash
cd backend/src
python dashboard_dash.py
```

### Método 2: Arquivo BAT (Windows)

```bash
# Criar arquivo executar_dashboard.bat
cd backend\src
py dashboard_dash.py
pause
```

**Acesso:** <http://localhost:8050>

---

## 📋 **Componentes**

### 1. Cards Superiores (6 cards compactos)

| Card | Descrição | Comportamento |
|------|-----------|---------------|
| **💰 Total** | Valor total filtrado | Dinâmico com filtros |
| **📊 Média 12M** | Média fixa de 12 meses | Sempre R$ 27,412 (fixo) |
| **✅ Categorizado** | % de transações categorizadas | Ex: 97.2% (2,038/2,096) |
| **⚠️ Pendentes** | Quantidade "A definir" | Ex: 0 (0.0% do total) |
| **📝 Transações** | Total de registros | Ex: 2,096 transações |
| **📅 Meses** | Período analisado | Ex: 12 meses |

**Características:**
- Padding reduzido (p-2) para telas QHD
- Fonte 24pt para valores principais
- Atualização automática com filtros

### 2. Seção de Categorização Inline

Permite categorizar transações "A definir" diretamente no dashboard:

```python
# Funcionalidades
- Tabela dinâmica com dropdowns
- Botões individuais de salvar
- Refresh automático após salvar
- Pattern-matching callbacks (Dash ALL)
```

**Estado atual:** 0 transações pendentes (100% categorizado)

### 3. Filtros Dinâmicos

Três dropdowns compactos na lateral:

- **📅 Mês:** Todos os meses ou específico (Jan-Dez 2025)
- **🏷️ Categoria:** Todas ou específica (Mercado, Casa, LF, etc.)
- **💳 Fonte:** Todas ou específica (PIX, Visa Bla, Master Físico, etc.)

**Comportamento:**
- Labels curtos para economia de espaço
- Padding reduzido (p-2)
- Atualização instantânea nos gráficos

---

## 📊 **Gráficos Interativos**

### Linha 1: Principais (70% + 30%)

#### **1. 💰 Real vs Ideal - 12 meses** (70% largura)

Gráfico de barras agrupadas comparando gastos reais com orçamento ideal:

- **Barra Laranja:** Valor real gasto
- **Barra Azul:** Valor ideal (orçamento)
- **Barra Verde/Vermelho:** Diferença
  - Verde = Economizou (real < ideal)
  - Vermelho = Excedeu (real > ideal)

**Fontes configuradas:**
- textfont: 10pt (valores nas barras)
- titlefont: 24pt (título do gráfico)
- tickfont: 18pt (eixos X/Y)
- uniformtext: minsize=10, mode='show'

**Valores normalizados:**
- R$ 50.400 → **50.4k**
- R$ 14.400 → **14.4k**
- R$ 1.400 → **1.4k**

#### **2. 📊 Evolução Mensal OU Real vs Ideal por Fonte** (30% largura)

**Quando filtro = "Todos":**
- Mostra evolução dos 12 meses
- Linha vermelha tracejada = média
- Formato: barras azuis + linha

**Quando filtro = "Mês específico":**
- Mostra Real vs Ideal por Fonte (PIX, Visa, Master)
- Mesmo formato do gráfico principal
- Título: "💳 Real vs Ideal por Fonte - Agosto 2025"

### Linha 2: Distribuição (50% + 50%)

#### **3. 💳 Gastos por Fonte** (Pizza)

Gráfico de pizza (donut) mostrando distribuição por fonte:

- **PIX:** 35.8%
- **Visa Bla:** 17.1%
- **Master Físico:** 16%
- Demais fontes: porcentagens menores

**Configuração:**
- hole=0.3 (donut style)
- textinfo='label+percent'
- textposition='outside'
- font: 18pt

#### **4. 🏷️ Gastos por Categoria** (Pizza)

Distribuição por categoria de gasto:

- **Mercado, Casa, LF, Nita:** maiores fatias
- Categorias menores: Padaria, Cartão, Feira, etc.

### Linha 3: Temporais (Visível apenas em "Todos")

#### **5. 📅 Distribuição de Transações por Mês**

Linha + marcadores mostrando quantidade de transações/mês:

- Janeiro: ~167 transações
- Pico: Março/Abril (~180)
- Útil para identificar meses atípicos

#### **6. 📈 Acumulado Anual**

Área preenchida mostrando acumulado ano a ano:

- Início: R$ 0
- Fim: R$ 328k (total anual)
- Crescimento gradual mês a mês

---

## 🎨 **Otimizações UX**

### Para Telas QHD (2560×1440)

#### **1. Cards Compactos (6 ao invés de 4)**

```python
# Antes: 4 cards grandes
dbc.Col([...], width=3)  # 25% largura cada

# Depois: 6 cards compactos
dbc.Col([...], width=2)  # 16.6% largura cada
```

#### **2. Fontes Ajustadas**

| Elemento | Tamanho | Uso |
|----------|---------|-----|
| Valores nas barras | 10pt | textfont (com uniformtext) |
| Legendas | 14pt | legend font |
| Títulos gráficos | 24pt | title font |
| Eixos (ticks) | 18pt | tickfont |
| Títulos eixos | 20pt | title font (xaxis/yaxis) |
| Fonte geral | 18pt | layout font |

#### **3. Valores Normalizados**

```python
# Formato k para valores >= 1000
text=[f'{v/1000:.1f}k' if v >= 1000 else f'R$ {v:.0f}' 
      for v in valores]

# Exemplos
50400 → "50.4k"
14400 → "14.4k"
1400  → "1.4k"
800   → "R$ 800"
```

#### **4. Cores Inteligentes (3ª barra)**

```python
# Verde: economizou (real < ideal)
# Vermelho: excedeu (real > ideal)
text=[f'<b style="color: {'red' if real > ideal else 'green'}">{v/1000:.1f}k</b>']
```

**Características:**
- Sem sinais (+/-)
- Negrito para destaque
- Fonte 12pt (maior que outras barras)
- HTML inline para cores

---

## 🔧 **Configurações Técnicas**

### Database Filtering

```python
# Exclusões automáticas
WHERE categoria NOT IN ('INVESTIMENTOS', 'SALÁRIO')
  AND tipo_transacao = 'DEBIT'
  AND descricao NOT LIKE '%ITAU VISA%'
  AND descricao NOT LIKE '%ITAU BLACK%'
  AND descricao NOT LIKE '%ITAU MASTER%'
  AND descricao NOT LIKE '%PGTO FATURA%'
  AND descricao NOT LIKE '%PAGAMENTO CARTAO%'
```

**Resultado:** 2.096 transações (após filtrar 24 transferências internas)

### Plotly Config

```python
config={
    'displayModeBar': True,      # Sempre visível
    'displaylogo': False,        # Sem logo Plotly
    'modeBarButtonsToAdd': ['toImage']  # + Botão download
}
```

**Ferramentas disponíveis:**
- 📷 Download PNG
- 🔍 Zoom Box (arrastar área)
- 🔍➕ Zoom In/Out
- ↔️ Pan (mover gráfico)
- 🏠 Reset Axes (voltar ao original)
- ⚙️ Autoscale

### Uniformtext (Importante!)

```python
uniformtext={'minsize': 10, 'mode': 'show'}
```

**Função:**
- Força Plotly a **respeitar** o tamanho configurado
- Sem isso, Plotly auto-redimensiona textos
- minsize=10: nunca menor que 10pt
- mode='show': sempre exibir (mesmo que saia da área)

---

## 📊 **Estatísticas Atuais**

```python
📊 DASHBOARD STATISTICS (Nov 2025)
├─ Total Transactions: 2,096
├─ Total Value: R$ 328,943.96
├─ Categorized: 97.2% (2,038/2,096)
├─ Pending: 0.0% (0 transactions)
├─ Average 12M: R$ 27,412.00
├─ Period: 12 months (Jan-Dec 2025)
└─ Internal Transfers Filtered: 24 (R$ 237k)
```

### Breakdown por Fonte

| Fonte | Transações | Valor | % Total |
|-------|------------|-------|---------|
| PIX | 750 | R$ 117k | 35.8% |
| Visa Bla | 360 | R$ 56k | 17.1% |
| Master Físico | 335 | R$ 52k | 16.0% |
| Demais | 651 | R$ 103k | 31.1% |

### Top 5 Categorias

| Categoria | Valor | % Total |
|-----------|-------|---------|
| Mercado | R$ 50,400 | 15.3% |
| Casa | R$ 44,300 | 13.5% |
| Esporte | R$ 26,200 | 8.0% |
| LF | R$ 28,800 | 8.8% |
| Nita | R$ 25,200 | 7.7% |

---

## 🚧 **Limitações Conhecidas**

### 1. Fullscreen Nativo

❌ Plotly não tem botão nativo de fullscreen  
✅ **Workarounds:**
- F11 no navegador (fullscreen do browser)
- Duplo clique no gráfico (expande contexto)
- Ferramentas de zoom para ampliar áreas

### 2. Dropdown Visibility

⚠️ Quando tabela de categorização é pequena, dropdown pode ficar cortado  
✅ **Solução futura:** Usar modal ou tooltip expandido

### 3. Performance com Muitos Dados

⚠️ Com +5000 transações, gráficos podem ficar lentos  
✅ **Mitigação atual:**
- Filtros reduzem dataset
- Refresh manual (não automático)
- SQLite otimizado com índices

---

## 🔮 **Melhorias Futuras**

### Fase 1: UX Enhancements

- [ ] Botão "Atualizar Dados" explícito
- [ ] Modo escuro (dark theme)
- [ ] Persistência de filtros (localStorage)
- [ ] Exportar gráfico atual (PNG/PDF)

### Fase 2: Análise Avançada

- [ ] Comparação ano a ano (2024 vs 2025)
- [ ] Projeção de gastos futuros (ML)
- [ ] Alertas de orçamento (notificações)
- [ ] Insights automáticos (anomalias, tendências)

### Fase 3: Integração

- [ ] Open Finance em tempo real (Pluggy sync)
- [ ] Multi-usuário com login
- [ ] Mobile responsive (viewport adaptativo)
- [ ] API REST para consumo externo

---

## 📝 **Changelog Dashboard**

### v2.3.0 (25/Nov/2025)

**✨ Features:**
- Dashboard completo com 6 cards + 7 gráficos
- Categorização inline de transações pendentes
- Filtros dinâmicos com refresh automático
- Valores normalizados em formato k
- Cores inteligentes (verde/vermelho) na 3ª barra
- Fontes otimizadas para tela QHD (10-24pt)
- Ferramentas Plotly sempre visíveis

**🐛 Fixes:**
- Corrigido titlefont inválido → title.font
- Uniformtext forçando tamanho de fonte
- Pattern-matching callbacks com row_id
- Filtros de transferências internas (ITAU VISA/BLACK)

**🔧 Technical:**
- Dash 2.x + Plotly + Bootstrap
- SQLite com 2.096 transações
- Callbacks otimizados (11 outputs)
- Config displayModeBar sempre visível

---

## 👨‍💻 **Arquitetura Técnica**

### Stack

```python
# Backend
- Python 3.13+
- SQLite (financeiro.db)
- Pandas (processamento)

# Frontend
- Dash 2.x (framework)
- Plotly (gráficos)
- Bootstrap 5 (layout)

# Dependências
pip install dash plotly pandas dash-bootstrap-components
```

### Estrutura de Arquivos

```plaintext
backend/src/
├── dashboard_dash.py          # Dashboard principal
├── agente_financeiro.py       # Processamento base
└── atualiza_dicionario.py     # Manutenção categorias

dados/db/
└── financeiro.db              # Database SQLite
    ├── transacoes_openfinance # Tabela principal
    └── categorias_openfinance # Mapeamento categorias
```

### Callbacks Principais

```python
# 1. Atualizar seção pendentes (categorização)
@callback(Output('secao-pendentes', 'children'),
          Input('refresh-trigger', 'data'))

# 2. Salvar categorização
@callback(Output('refresh-trigger', 'data', allow_duplicate=True),
          Input({'type': 'btn-salvar', 'index': ALL}, 'n_clicks'),
          State({'type': 'dropdown-cat', 'index': ALL}, 'value'))

# 3. Atualizar dashboard (11 outputs)
@callback([Output('card-total', 'children'), ...],
          [Input('filtro-mes', 'value'),
           Input('filtro-categoria', 'value'),
           Input('filtro-fonte', 'value'),
           Input('refresh-trigger', 'data')])
```

---

## 📚 **Referências**

- **Dash Framework:** <https://dash.plotly.com/>
- **Plotly Python:** <https://plotly.com/python/>
- **Bootstrap Components:** <https://dash-bootstrap-components.opensource.faculty.ai/>
- **SQLite:** <https://www.sqlite.org/>

---

## 💡 **Dicas de Uso**

### Análise Rápida

1. **Filtrar por mês** para ver gastos específicos
2. **Clicar nas legendas** para ocultar/mostrar barras
3. **Zoom box** (arrastar) para ampliar área
4. **Download PNG** para relatórios

### Identificação de Problemas

- **Vermelho excessivo?** Categoria excedeu orçamento
- **Picos no gráfico temporal?** Mês atípico para investigar
- **Pendentes > 0?** Categorizar diretamente no dashboard

### Performance

- Filtrar por **mês específico** reduz processamento
- **Evitar** "Todos" + "Todas" simultaneamente com muitos dados
- Refresh manual (não automático) mantém controle

---

**Desenvolvido com ❤️ por Luciano Costa Fernandes**  
📧 luti_vix@hotmail.com  
⭐ Se ajudou, dê uma estrela no GitHub!
