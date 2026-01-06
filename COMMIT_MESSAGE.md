# Commit v2.9.0

Luciano - feat(deploy): Configuração completa para deploy em produção com WSGI servers (over dash 2 ajustes)

## Resumo

🚀 **DEPLOY PRODUCTION READY!** Dashboard v2 agora pronto para produção com servidores WSGI (Gunicorn/Waitress), scripts automatizados, health check endpoint, e documentação completa incluindo Nginx reverse proxy, HTTPS, Systemd service e troubleshooting.

## Features

### 🚀 Deploy em Produção

**WSGI Entry Point**:
- `backend/src/dashboard_v2/wsgi.py`: Entry point para servidores WSGI
- Exporta `server = app.server` para Gunicorn/Waitress
- Compatível com qualquer servidor WSGI padrão

**Scripts Automatizados**:
- `backend/start-dashboard-prod.bat`: Windows (Waitress, 4 threads)
- `backend/start-dashboard-prod.sh`: Linux/Mac (Gunicorn, 4 workers + 2 threads)
- Execução simples com um comando

**Configuração como Serviço**:
- `backend/dashboard-service.service`: Template Systemd
- Reinicialização automática (restart on failure)
- Logs integrados com journalctl

### 📦 Dependências de Produção

**requirements-dashboard.txt**:
- dash>=2.14.0
- dash-bootstrap-components>=1.5.0
- plotly>=5.18.0
- pandas>=1.5.0
- gunicorn>=21.2.0 (Linux)
- waitress>=2.1.2 (Windows)

### 🔧 Melhorias no Main

**Variáveis de Ambiente**:
- `DASH_DEBUG`: true/false (default: false)
- `DASH_PORT`: porta customizada (default: 8052)
- `DASH_HOST`: host binding (default: 0.0.0.0)

**Health Check Endpoint**:
- `/health`: Status do servidor + teste de DB
- Response: `{'status': 'ok', 'meses_disponiveis': N}`
- Para monitoramento automatizado

**Debug Mode**:
- Desabilitado por padrão em produção
- Habilitável via env var ou código
- Modo visível nos logs de startup

## Documentation

### 📚 Docs Completas

**docs/Deploy/DEPLOY_DASHBOARD_V2.md** (guia completo):
- ✅ Instalação passo a passo
- 🪟 Deploy Windows (Waitress + NSSM)
- 🐧 Deploy Linux (Gunicorn + Systemd)
- 🌐 Nginx Reverse Proxy (config completa)
- 🔒 HTTPS com Let's Encrypt
- 🐛 Troubleshooting (10+ casos comuns)
- 📊 Monitoramento e health checks
- 🎯 Checklist de deploy

**backend/README_DEPLOY.md** (quick start):
- ⚡ Comandos para deploy imediato
- 🛠️ Comandos úteis (dev vs prod)
- 📦 Dependências resumidas
- 🔧 Variáveis de ambiente

## Technical Details

### Servidor WSGI

**Gunicorn (Linux/Mac)**:
```bash
gunicorn wsgi:server --bind 0.0.0.0:8052 --workers 4 --threads 2 --timeout 120
```

**Waitress (Windows)**:
```cmd
waitress-serve --host=0.0.0.0 --port=8052 --threads=4 wsgi:server
```

### Nginx Config

- Reverse proxy para porta 8052
- WebSocket support (Dash callbacks)
- Timeouts ajustados (120s)
- Headers corretos (X-Forwarded-*)

### Systemd Service

- Restart automático (RestartSec=10)
- Logs via journalctl
- Inicialização com boot (enable)

## Files Changed

- `backend/src/dashboard_v2/wsgi.py`: ✨ NEW - WSGI entry point
- `backend/src/dashboard_v2/main.py`: Health check + env vars + debug mode
- `backend/requirements-dashboard.txt`: ✨ NEW - Dependências de produção
- `backend/start-dashboard-prod.bat`: ✨ NEW - Script Windows
- `backend/start-dashboard-prod.sh`: ✨ NEW - Script Linux/Mac
- `backend/dashboard-service.service`: ✨ NEW - Template Systemd
- `docs/Deploy/DEPLOY_DASHBOARD_V2.md`: ✨ NEW - Documentação completa (500+ linhas)
- `backend/README_DEPLOY.md`: ✨ NEW - Quick start guide
- `COMMIT_MESSAGE.md`: Este commit

## Migration Guide

### De Dev para Prod

**Antes (desenvolvimento)**:
```bash
cd backend/src/dashboard_v2
python main.py  # Servidor dev do Flask
```

**Agora (produção)**:
```bash
cd backend
pip install -r requirements-dashboard.txt
start-dashboard-prod.bat  # Windows
# OU
./start-dashboard-prod.sh  # Linux
```

### Configurar como Serviço

**Windows**:
- Usar NSSM (Non-Sucking Service Manager)
- Ou Agendador de Tarefas (schtasks)

**Linux**:
1. Copiar `dashboard-service.service` para `/etc/systemd/system/`
2. Ajustar caminhos no arquivo
3. `sudo systemctl enable dashboard-financeiro`
4. `sudo systemctl start dashboard-financeiro`

## Testing

- [x] Health check endpoint funcionando
- [x] Gunicorn rodando (4 workers)
- [x] Waitress rodando (4 threads)
- [x] Debug desabilitado por padrão
- [x] Env vars funcionando
- [x] Logs sendo gerados
- [x] Syntax OK em main.py

## Notes

- Dashboard agora **production-ready** para deploy real
- Suporta Windows Server, Linux (Ubuntu/Debian/CentOS), Mac
- Escalável (ajustar workers/threads conforme carga)
- Documentação completa com todos os cenários

---

# Commit v2.8.0

Luciano - feat(v2.8): Filtros multi-select com tags/chips para análise multi-critério

## Resumo

🏷️ **FILTROS MULTI-SELECT!** Transações agora com filtros multi-select (tags/chips) para Categoria, Fonte e Mês de Compensação. Selecione múltiplos valores simultaneamente para análises cruzadas (Ex: Pet + Compras + Visa Bia + Janeiro). Visual com pills/chips removíveis, powered by React-Select.

## Features

### 🏷️ Filtros Multi-Select com Tags

**3 filtros convertidos**:
- Categoria: Multi-select com tags
- Fonte: Multi-select com tags
- Mês de Compensação: Multi-select com tags
- Visual: Pills/Chips com X individual
- Lista vazia = "Todos" (sem filtro)

**Lógica atualizada**:
- `atualizar_filtros_transacoes`: Remove opção 'TODOS', lista [] = todos
- `atualizar_tabela_transacoes`: Filtros com `.isin()` para listas
- Suporta combinações múltiplas (Ex: 3 categorias + 2 fontes + 1 mês)
- Dropdowns com `multi=True` (React-Select)

## Fixes

### 🐛 Correções

- **Encoding Windows**: Removidos emojis dos prints (UnicodeEncodeError cp1252)
- **Syntax Error**: Código residual de Checklist em transacoes.py removido
- **NameError**: `dropdown_style` definido no módulo transacoes

## Technical

- `dcc.Dropdown(multi=True, value=[], placeholder='Todas/Todos')`
- React-Select automático para tags
- Filtros: `df[df['column'].isin(list_values)]` ao invés de `==`
- Empty list handling: `if lista and len(lista) > 0`

## Files Changed

- `backend/src/dashboard_v2/pages/transacoes.py`: 3 dropdowns multi-select + dropdown_style
- `backend/src/dashboard_v2/main.py`: Callbacks atualizar_filtros + atualizar_tabela + prints sem emoji
- `CHANGELOG.md`: v2.8.0 documentado
- `COMMIT_MESSAGE.md`: Este commit

---

# Commit v2.7.0

Luciano - feat(v2.7): Budget Ideals + edição transações + orçamento por fonte + fix ordenação cronológica

## Resumo

🎯 **PÁGINA IDEALS + EDIÇÃO + ORÇAMENTOS POR FONTE!** Nova página Budget Ideals com comparação Real vs Ideal, edição de categorias em transações via modal, orçamentos específicos por 5 fontes de pagamento, e correções críticas de ordenação cronológica nos gráficos de evolução e acumulado.

## Features

### 🎯 Página Budget Ideals - Planejamento Orçamentário

**Gráfico de comparação interativo**:
- View By dropdown: Alterna entre Category (vertical) ou Source (horizontal)
- 3 barras por item: Real (azul), Ideal (verde), Difference (vermelho/verde)
- Altura dinâmica: 700px categorias, ajustável para fontes
- Multiplica por 12 quando mês = "TODOS" (visão anual)

**5 filtros simultâneos**:
- Month: Dropdown com opção "TODOS"
- View By: Category ou Source
- Category: Filtro específico
- Source: Filtro específico
- Date Range: Período customizado

**4 cards de métricas**: Total Real, Total Ideal, Difference, Status (Over Budget/On Track)

**Orçamentos específicos por fonte** (5 fontes):
- VISA_REC: LF, Esporte, Stream
- VISA_BIA: Mercado, Feira, Farmácia, Pet, Lazer
- VISA_FIS: Datas, Estética, Compras, Pet
- PIX: Casa, Nita, Utilidades, Faculdade, Esporte
- MASTER_VIRTUAL: Betina, Farmácia

### ✏️ Edição de Transações

**Modal approach**: Botão "✏️" por linha abre modal de edição
**Campos**: ID, Data, Descrição, Valor, Fonte (readonly), Categoria (editável)
**Persistência**: Salva no SQLite, recarrega tabela automaticamente
**Apenas categoria editável**: Fonte read-only para evitar inconsistências

### 🎨 Melhorias UI/UX

**Dropdown sidebar**: Abre para cima (bottom: 100%, top: auto)
**Texto modal**: Classe .dropdown-white-text para contraste em fundo escuro
**Sidebar link**: "Ideals" com ícone fa-bullseye

## Fixes

### 📊 Ordenação Cronológica nos Gráficos

**Problema**: Meses em ordem alfabética (Abril, Agosto, Dezembro) ao invés de cronológica

**Solução implementada**:
1. Conversão `pd.to_datetime(format='%B %Y')` com locale pt_BR
2. `.dropna(subset=['data_ordenacao'])` remove conversões falhas (NaT)
3. Índices numéricos no eixo X + `ticktext` para labels
4. `.tail(12)` após ordenação para últimos 12 meses

**Aplicado em**:
- Dashboard: Evolução últimos 12 meses (Fev 2025 → Jan 2026)
- Analytics: Acumulado últimos 6 meses (Ago 2025 → Jan 2026)

**Resultado**: Gráficos agora respeitam ordem temporal correta

### 💾 Save de Transações

**Problema**: Botão salvar não persistia no banco
**Causa**: Path incorreto (backend/src/dados vs dados)
**Solução**: BASE_DIR.parent.parent / 'dados' / 'db' / 'financeiro.db'

### 🔍 Filtro por Fonte em Ideals

**Problema**: Filtrar por fonte mudava view_by para "source"
**Solução**: Mantém view_by inalterado, aplica orçamento específico da fonte

## Arquivos Modificados

### Novos
- `backend/src/dashboard_v2/pages/ideals.py` (200+ linhas)

### Modificados
- `backend/src/dashboard_v2/utils/graficos.py`
  - criar_grafico_ideals_comparison() com view_by e fontes
  - criar_grafico_evolucao() com ordenação cronológica
  - criar_grafico_acumulado() com ordenação cronológica
  - ORCAMENTO_POR_FONTE mapping

- `backend/src/dashboard_v2/main.py`
  - Imports: State, ALL
  - Route: /ideals
  - Callbacks: atualizar_meses/filtros/grafico/metricas_ideals
  - Modal editing: toggle_modal_edit, salvar_categoria

- `backend/src/dashboard_v2/config.py`
  - ORCAMENTO_IDEAL_CAT_VISA_REC/BIA/FIS/PIX/MASTER_VIRTUAL
  - ICONS['ideals']

- `backend/src/dashboard_v2/components/sidebar.py`
  - Link Ideals + className='dropdown-sidebar'

- `backend/src/dashboard_v2/assets/custom_styles.py`
  - .dropdown-white-text, .dropdown-sidebar

- `backend/src/dashboard_v2/utils/database.py`
  - rowid → id rename

## Validação

✅ Página Ideals renderiza corretamente
✅ View By alterna entre category/source
✅ Orçamentos por fonte aplicados corretamente
✅ Modal de edição abre e salva
✅ Evolução mostra Fev 2025 → Jan 2026 (12 meses)
✅ Acumulado mostra Ago 2025 → Jan 2026 (6 meses)
✅ Sidebar dropdown abre para cima
✅ Filtros mantêm consistência (view_by não muda ao filtrar fonte)

## Breaking Changes

Nenhuma

## Notas

- UI em inglês (preparação para i18n futuro)
- Locale handling para meses em português (Janeiro, Fevereiro...)
- Índices numéricos resolvem definitivamente problema de reordenação do Plotly
- Modal approach mais confiável que inline DataTable editing

---

# Commit v2.6.0

Luciano - feat(v2.6): Analytics + Transações completas + filtros avançados + subtotal

## Resumo

📊 **FUNCIONALIDADES COMPLETAS DO DASHBOARD V2!** Implementa páginas Analytics e Transações com 3 gráficos analíticos, 5 filtros simultâneos, tabela HTML customizada, subtotal dinâmico e correções críticas de filtros de débitos/créditos.

## Features

### 📈 Página Analytics - Análises Avançadas

**3 gráficos analíticos interativos**:

1. **Real vs Ideal** (barras agrupadas)
   - Compara gastos reais vs limites ideais por mês
   - Limite ideal: R$ 2.000/mês
   - Cores: Real (#D62246), Ideal (#06A77D)
   - Height: 300px

2. **Distribuição Temporal** (barras horizontais)
   - Análise de gastos por dia da semana
   - Identifica padrões de consumo semanal
   - Ordenado de Domingo a Sábado
   - Height: 300px

3. **Evolução Acumulada** (linha + área)
   - Progressão acumulada de gastos no mês
   - Linha azul (#2E86AB) com área preenchida
   - Útil para tracking de orçamento mensal
   - Height: 300px

**Implementação**:
- 3 novas funções em `graficos.py`: criar_grafico_real_ideal(), criar_grafico_distribuicao_temporal(), criar_grafico_acumulado()
- 3 novos callbacks em `main.py`: atualizar_grafico_real_ideal, atualizar_grafico_distribuicao, atualizar_grafico_acumulado
- Layout: 3 cards empilhados verticalmente com margin-bottom 24px

### 📋 Página Transações - Gerenciamento Completo

**5 filtros simultâneos em layout 2 linhas**:

**Linha 1** (flex, gap 16px):
- **Categoria**: Dropdown com todas categorias + "Todas" (TODOS)
- **Fonte**: Dropdown com fontes (Nubank, Itaú, BTG, PIX, BOLETO) + "Todas"
- **Status**: Categorizadas / Pendentes / Todas

**Linha 2** (flex, gap 16px):
- **Mês de Compensação**: Dropdown com meses únicos + "Todos"
- **Período (Data)**: DatePickerRange com start_date e end_date
  - Display format: DD/MM/YYYY
  - Placeholders: "Data Inicial" e "Data Final"
  - className: 'custom-datepicker'

**Tabela HTML customizada**:
- **Substituiu DataTable** (evita erro de chunk JS async-table.js)
- **6 colunas**: Data, Descrição, Valor, Categoria, Fonte, Mês
- **Formatação**: 
  - Data: DD/MM/YYYY
  - Valor: R$ 1.234,56 (2 decimais)
- **Destaque visual**: Categorias "A definir" com badge amarelo (background #FFD369)
- **Limite**: 100 transações exibidas
- **Ordenação**: mes_comp (↑) → fonte (↓) → data (↑)

**Subtotal dinâmico**:
- Exibido acima da tabela: "Mostrando X transações de Y encontradas • Subtotal: R$ Z"
- Subtotal em destaque: cor primary (#2E86AB), bold, fontSize base
- Calcula soma dos valores das transações visíveis (df_tabela['valor_normalizado'].sum())

**Callback modificado**:
- 7 Inputs: store-mes-global + 6 filtros de página
- Filtros aplicados sequencialmente com null checks
- Retorna html.Div com subtotal + html.Table (não mais DataTable)

### 🎨 Estilização DatePicker

**CSS completo para DatePickerRange** (~100 linhas em `custom_styles.py`):

```css
.DateRangePicker_picker {
    z-index: 9999 !important;
    background-color: #16213E !important;
    border: 1px solid #2D3748 !important;
}

.CalendarDay {
    background-color: #16213E !important;
    color: #FFFFFF !important;
}

.CalendarDay__selected {
    background: #2E86AB !important;
    color: #FFFFFF !important;
}
```

**Componentes estilizados**:
- `.DateRangePicker_picker`: z-index 9999 (sempre visível)
- `.CalendarDay`: fundo card (#16213E), texto branco
- `.CalendarDay__selected`: cor primária (#2E86AB)
- `.CalendarDay__hovered_span`: hover com opacity 0.5
- `.DayPickerNavigation_button`: setas de navegação com hover brightness 1.1
- `.DateInput_input`: input fields com fundo card
- `.DateRangePickerInput_arrow`: seta separadora estilizada

## Bug Fixes

### 🐛 Correção crítica: Filtro de débitos invertido

**Problema**: Dashboard mostrava R$ 14.5k ao invés de ~R$ 2k (gastos)

**Causa raiz**: Banco de dados usa convenção:
- **Débitos (gastos)** = valor **POSITIVO** (> 0)
- **Créditos (receitas)** = valor **NEGATIVO** (< 0)

**Correções em 4 locais**:

1. `database.py` - linha 147:
```python
# ANTES: df_debitos = df[df['valor'] < 0].copy()
# DEPOIS: df_debitos = df[df['valor'] > 0].copy()
```

2. `graficos.py` - criar_grafico_evolucao():
```python
# ANTES: df_filtrado = df[df['valor'] < 0].copy()
# DEPOIS: df_filtrado = df[df['valor'] > 0].copy()
```

3. `graficos.py` - criar_grafico_top_categorias() (mesmo fix)

4. `graficos.py` - criar_grafico_top_fontes() (mesmo fix)

**Validação**: 65 débitos (R$ ~2k) vs 2.191 créditos confirmam correção

### 🐛 Callback error na página Transações

**Erro**: "Callback error updating tabela-transacoes-container.children"

**Causa**: 
- Callback com 6 Inputs de componentes que só existem em /transacoes
- Dash tentava disparar callback em outras páginas (Dashboard, Analytics)
- Components não existiam → None values → erro de comparação

**Tentativa inicial** (FALHOU):
```python
prevent_initial_call=True  # Impediu carregamento inicial da tabela
```

**Solução final**: Remover prevent_initial_call + adicionar null checks:
```python
if categoria_filtro and categoria_filtro != 'TODOS':
if fonte_filtro and fonte_filtro != 'TODOS':
if mes_comp_filtro and mes_comp_filtro != 'TODOS':
if data_inicio:  # try/except para parsing
```

### 🐛 DatePicker fora do padrão

**Problema**: DatePickerRange com fundo branco, sem estilização

**Solução**:
- Adicionar `className='custom-datepicker'`
- Criar ~100 linhas de CSS em `custom_styles.py`
- z-index 9999 para aparecer sobre tabela

### 🐛 Loading chunk 214 failed

**Erro**: `http://localhost:8052/_dash-component-suites/dash/dash_table/async-table.js`

**Causa**: DataTable tentando carregar chunk JS assíncrono (falha intermitente)

**Solução**: Substituir por tabela HTML customizada:
```python
# ANTES: return dash_table.DataTable(...)
# DEPOIS: return html.Table([html.Thead(...), html.Tbody(rows)])
```

**Trade-offs**:
- ❌ Perde: sort_action='native', filter_action='native', page_size
- ✅ Ganha: Estabilidade, controle total de estilo, sem dependência JS

## Technical Details

### Arquivos Modificados

1. **backend/src/dashboard_v2/main.py** (+50 linhas):
   - Import pandas as pd (linha ~10)
   - 3 novos callbacks Analytics (linhas ~180-243)
   - Modificado atualizar_tabela_transacoes (linhas 244-354)
   - Substituiu DataTable por html.Table + subtotal

2. **backend/src/dashboard_v2/utils/graficos.py** (+120 linhas):
   - criar_grafico_real_ideal() - novo
   - criar_grafico_distribuicao_temporal() - novo
   - criar_grafico_acumulado() - novo
   - Corrigido filtro valor > 0 em 3 funções existentes

3. **backend/src/dashboard_v2/utils/database.py** (1 linha):
   - Linha 147: df['valor'] < 0 → df['valor'] > 0

4. **backend/src/dashboard_v2/pages/transacoes.py** (+30 linhas):
   - Adicionado filtro-mes-comp-transacoes (dropdown)
   - Adicionado filtro-data-transacoes (DatePickerRange)
   - Layout 2 linhas com flexbox (wrap, gap 16px)

5. **backend/src/dashboard_v2/assets/custom_styles.py** (+100 linhas):
   - CSS completo para DatePickerRange
   - z-index 9999 para .DateRangePicker_picker
   - Estilos dark theme para calendar, inputs, navigation

### Estrutura de Dados

**Banco SQLite**: `dados/db/financeiro.db`
- Tabela: `lancamentos`
- Registros: 2.256 (65 débitos, 2.191 créditos)
- Colunas usadas: Data, Descricao, Valor, Categoria, Fonte, MesComp

**Convenção de sinais**:
```python
débitos (gastos) = valor > 0   # Ex: 50.00 (gasto de R$ 50)
créditos (receitas) = valor < 0  # Ex: -3000.00 (receita de R$ 3k)
```

### Callbacks

**Total de callbacks no app**: 10
1. display_page() - roteamento
2-4. Dashboard: 3 gráficos
5-7. Analytics: 3 gráficos (NOVO)
8. atualizar_filtros_transacoes() - popula dropdowns
9. atualizar_tabela_transacoes() - tabela (MODIFICADO)

**suppress_callback_exceptions**: True (necessário para multi-page)

## Testing

**Validações realizadas**:
- ✅ Dashboard: Exibe R$ ~2k (65 transações débito)
- ✅ Analytics: 3 gráficos carregam com filtro de mês
- ✅ Transações: Tabela carrega com "Carregando..." → dados
- ✅ Filtros: Categoria, Fonte, Status, MesComp, Data funcionam
- ✅ Subtotal: Atualiza dinamicamente com filtros
- ✅ DatePicker: Aparece sobre tabela (z-index 9999)
- ✅ Ordenação: mes_comp → fonte → data funciona
- ✅ Destaque: "A definir" com badge amarelo

**Performance**:
- Limite 100 transações exibidas (de 2.256 total)
- Tabela HTML renderiza instantaneamente
- Filtros aplicam em < 100ms

## Next Steps

**Próximas melhorias sugeridas**:
1. Paginação na tabela (atualmente limitado a 100)
2. Categorização inline com dropdown por linha
3. Edição de transações diretamente na tabela
4. Exportar transações filtradas para CSV
5. Gráfico adicional: Comparativo mensal YoY
6. Alertas quando próximo do limite mensal

## Version

- **Versão anterior**: v2.5.0 (16/12/2025) - Estrutura base Dashboard V2
- **Versão atual**: v2.6.0 (23/12/2025) - Funcionalidades completas
- **Python**: 3.13+
- **Dash**: 3.2.0
- **Dash Bootstrap Components**: instalado
- **Porta**: 8052 (Dashboard v2) / 8051 (Dashboard v1)

### 🏗️ Estrutura Organizada (MVC-style)

- `backend/src/dashboard_v2/` - Diretório isolado do dashboard antigo
- **Pages**: `dashboard.py` (funcional), `analytics.py` (placeholder), `transacoes.py` (placeholder)
- **Components**: `sidebar.py` (navegação lateral com ícones FontAwesome)
- **Utils**: `database.py` (queries SQLite), `graficos.py` (funções Plotly)
- **Assets**: `custom_styles.py` (CSS dark theme injetado via app.index_string)
- **Config**: `config.py` - Centralização de COLORS, FONTS, SPACING, PLOTLY_TEMPLATE
- Todos os subdiretórios com `__init__.py` para imports corretos

### 🎨 Design Dark Theme (Behance-inspired)

- **Paleta de cores**:
  - Background: `#0F0F23` (deep blue-black), Cards: `#16213E`
  - Primary: `#2E86AB` (azul), Success: `#06A77D` (verde), Danger: `#D62246` (vermelho)
  - Charts: 6 cores vibrantes (`#4ECDC4`, `#95E1D3`, `#FFD369`, `#F38181`, `#AA96DA`, `#2E86AB`)
- **Tipografia Inter**: 10px (xs) a 28px (4xl) - escala reduzida para Full HD
- **Espaçamentos compactos**: 4px (xs) a 32px (3xl)
- **Hover states**: transformY(-2px), brightness(1.05)

### 📊 Dashboard Principal (funcional na porta 8052)

- **3 cards de métricas**: Total gasto, Cartões, Pix + Boletos
  - Ícones FontAwesome 6 (wallet, credit-card, money-bill-wave)
  - Container 36×36px com gradiente sutil
- **Dropdown filtro**: Meses disponíveis carregados do banco + opção "TODOS"
- **Gráfico hero**: Evolução últimos 12 meses
  - Linha azul (`#2E86AB`) com área preenchida (`rgba(46, 134, 171, 0.2)`)
  - Altura 280px, hover unified
- **2 gráficos laterais**: Top 5 Categorias e Top 5 Fontes
  - Barras horizontais com valores formatados (R$ 1.234)
  - Altura 240px cada, flex layout responsivo

### 🔌 Integração Banco de Dados

- **carregar_transacoes(mes_filtro)**: Query SQLite com filtro opcional por mês
- **calcular_estatisticas(df)**: Total, Cartões (Nubank/Itaú/BTG), Pix/Boleto
- **obter_meses_disponiveis()**: Lista única de meses ordenados DESC
- **Callbacks interativos**: 3 gráficos atualizam dinamicamente com dropdown

### 🐛 Correções Técnicas

- **ModuleNotFoundError**: `sys.path.insert(0, backend_path)` + `__init__.py` em todas pastas
- **CSS injection**: `app.index_string` (método correto, não `html.Style()`)
- **TypeError duplicate 'xaxis'**: Separado `update_layout()` de `update_xaxes()`/`update_yaxes()`
- **ValueError duplicate 'hovermode'**: Removido do layout (já em `PLOTLY_TEMPLATE`)
- **Invalid 'titlefont'**: Mudado para `title: {font: {...}}` (Plotly moderno)
- **Invalid fillcolor**: Hex+alpha (`#2E86AB30`) → rgba (`rgba(46, 134, 171, 0.2)`)

## Problemas Conhecidos

⚠️ **Layout não otimizado** - Componentes funcionais mas proporções visuais ainda não ideais comparado ao design de referência
⚠️ **Analytics page** - Apenas placeholder, sem gráficos (Real vs Ideal, Distribuição, Acumulado)
⚠️ **Transações page** - Apenas placeholder, sem tabela interativa nem categorização inline
⚠️ **Responsividade** - Ajustado para Full HD mas precisa refinamento de tamanhos relativos

## Próximos Passos

1. **Refinar layout visual**: comparar proporções com Behance, ajustar tamanhos cards vs gráficos
2. **Implementar Analytics**: gráficos Real vs Ideal, distribuição temporal, acumulado mensal
3. **Implementar Transações**: tabela com filtros, categorização inline, paginação
4. **Melhorias UX**: animações sutis, indicadores de progresso, dark/light toggle

## Arquivos Modificados

- `backend/src/dashboard_v2/` - Estrutura completa criada
- `dashboard_v2.bat` - Script execução Windows
- `CHANGELOG.md` - Documentação v2.5.0

## Execução

```bash
py backend/src/dashboard_v2/main.py
# ou
dashboard_v2.bat
# Acesso: http://localhost:8052
```

---

# Commit v2.3.0

Luciano - feat(v2.3): Dashboard interativo completo + categorização inline + otimizações QHD

## Resumo

🚀 **DASHBOARD INTERATIVO COMPLETO!** Implementa visualização em tempo real com análise gráfica, categorização inline e filtros dinâmicos otimizados para telas QHD (2560×1440).

## Features

### 📊 Dashboard Dash + Plotly (`dashboard_dash.py`)

- 6 cards informativos compactos (Total, Média 12M, Categorizado, Pendentes, Transações, Meses)
- Categorização inline de transações "A definir" direto no dashboard
- 3 filtros dinâmicos (Mês, Categoria, Fonte) com refresh automático
- 7 gráficos interativos: Real vs Ideal, Evolução Mensal, Fontes (pizza), Categorias (pizza), Distribuição, Acumulado
- Pattern-matching callbacks para múltiplos botões de categorização
- dcc.Store para gerenciamento de estado e refresh
- Acesso via http://localhost:8050

### 🎨 Otimizações UX para QHD (2560×1440)

- Layout compacto: 6 cards ao invés de 4 (width=2 cada)
- Fontes ajustadas: textfont 10pt, legend 14pt, title 24pt, tickfont 18pt
- uniformtext: minsize=10, mode='show' (força tamanho configurado)
- Valores normalizados: R$ 14.400 → 14.4k (formato k para milhares)
- Cores inteligentes na 3ª barra: Verde (economizou) / Vermelho (excedeu)
- Filtros compactos: padding p-2, labels curtos

### 📈 Resultados Dashboard

```
Transações: 2.096 (após filtrar 24 transferências)
Total: R$ 328.943,96
Categorizadas: 97.2% (2.038/2.096)
Pendentes: 0 (0.0% do total)
Média 12M: R$ 27.412,00 (fixo)
Período: 12 meses (Jan-Dez 2025)
```

### 🔧 Melhorias Técnicas

- Database filtering: Exclusão automática de transferências internas (ITAU VISA/BLACK/MASTER/PGTO FATURA/PAGAMENTO CARTAO)
- Callbacks otimizados: 11 outputs no callback principal
- Plotly config: displayModeBar sempre visível com ferramentas (zoom, pan, download PNG, reset)
- Pattern-matching: Botões e dropdowns dinâmicos com IDs JSON-serializáveis
- Média 12M fixa: Sempre mostra média de 12 meses independente de filtros

### 🐛 Correções

- titlefont inválido: Mudado para title={'font': {'size': 24}}
- Fontes não aplicando: Adicionado uniformtext para forçar Plotly a respeitar tamanhos
- Transferências internas: Filtradas 24 transações (R$ 237k) de pagamentos de cartão
- Row ID inconsistente: Usado alias rowid as row_id no SQLite para compatibilidade pandas

### 📝 Documentação

- Criado docs/DASHBOARD_INTERATIVO.md (450+ linhas) - Documentação completa do dashboard
- Criado docs/SESSAO_2025-11-25_DASHBOARD.md - Resumo da sessão de desenvolvimento
- README.md atualizado para v2.3
- CHANGELOG.md com entrada completa v2.3.0

## Arquivos Modificados

**Novos:**

- `backend/src/dashboard_dash.py` - Dashboard interativo completo
- `docs/DASHBOARD_INTERATIVO.md` - Documentação completa (450+ linhas)
- `docs/SESSAO_2025-11-25_DASHBOARD.md` - Resumo da sessão

**Modificados:**

- `README.md` - Versão 2.3, seção Dashboard Interativo
- `CHANGELOG.md` - Entrada v2.3.0 completa
- `COMMIT_MESSAGE.md` - Atualizado para v2.3.0

## Impacto

✨ **Dashboard interativo completo para análise financeira em tempo real**

- Visualização gráfica otimizada para tela QHD
- Categorização inline de pendências direto no dashboard
- Filtros dinâmicos com atualização instantânea
- 7 gráficos interativos com ferramentas Plotly
- 97.2% das transações categorizadas
- 2.096 transações analisadas em tempo real

---

🎊 **DASHBOARD FINALIZADO - VISUALIZAÇÃO PERFEITA!**

### Open Finance

- REST API Pluggy implementada
- Conta Mercado Pago conectada (saldo + transações)
- Sandbox Nubank configurado
- Segurança OAuth2 + read-only access
- Conformidade LGPD documentada

### Reorganização Documentação

- 3 categorias: Desenvolvimento (8 docs), Integração (4 docs), Testing (4 docs)
- 21 documentos organizados com padrão XXX_NOME.md
- 9 novos documentos criados (READMEs + guias técnicos)
- 12 documentos renumerados e categorizados

### Estrutura

- `/config/` - Configurações centralizadas
- `/docs/{categoria}/` - Documentação organizada
- READMEs de navegação em cada categoria
- `Integracao_PROXIMO_CHAT.md` - Contexto rápido para IA

## Arquivos

**Novos (9):**

- config/README.md
- docs/README.md + Integracao_PROXIMO_CHAT.md
- docs/{Desenvolvimento,Integracao,Testing}/README.md
- docs/Desenvolvimento/007_REORGANIZACAO_COMPLETA.md
- docs/Desenvolvimento/008_COMMIT_V2.0.2_CICLO_19-18.md
- docs/Integracao/003_ARQUITETURA_PLUGGY.md
- docs/Integracao/004_SEGURANCA_OPENFINANCE.md

**Modificados:**

- README.md - v2.1, badges Open Finance, roadmap com Mobile (v2.3)
- CHANGELOG.md - entrada v2.1.0 completa
- 12 docs movidos para categorias temáticas

## Breaking Changes

- Docs movidos: `docs/*.md` → `docs/{categoria}/XXX_*.md`
- Config movido: `backend/src/config.ini` → `config/config.ini`
- Links atualizados no README

## Documentação

Ver detalhes em:

- CHANGELOG.md [2.1.0]
- docs/Integracao_PROXIMO_CHAT.md
- docs/Desenvolvimento/007_REORGANIZACAO_COMPLETA.md
- docs/Desenvolvimento/008_COMMIT_V2.0.2_CICLO_19-18.md (bugfix anterior)

---

v2.1.0 | 2025-01-27 | Luciano

**Relates to:** Ciclo mensal 19-18
**Version:** v2.0.2-dev
**Date:** 2025-10-28

```

```
