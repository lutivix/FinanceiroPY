# 📋 Changelog - Agente Financeiro IA

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [2.7.0] - 2025-12-23 🎯

### 🎯 Principais Mudanças

**PÁGINA IDEALS + EDIÇÃO DE TRANSAÇÕES + ORÇAMENTOS POR FONTE!** Nova página Budget Ideals com comparação Real vs Ideal, edição de categorias em transações via modal, orçamentos específicos por fonte de pagamento, e correções críticas de ordenação cronológica nos gráficos.

### ✨ Adicionado

#### **🎯 Página Budget Ideals - Planejamento Orçamentário**

- **Gráfico de comparação Real vs Ideal + Diferença**
  - View By: Alterna entre visualização por Category ou Source
  - Barras verticais para categorias, horizontais para fontes específicas
  - 3 barras por item: Real (azul), Ideal (verde), Diferença (vermelha/verde)
  - Altura dinâmica: 700px (categorias verticais), ajustável (horizontais)
  
- **5 filtros interativos**
  - Month: Dropdown com meses disponíveis + "TODOS" (anual × 12)
  - View By: Category ou Source (controla tipo de visualização)
  - Category: Filtro específico por categoria
  - Source: Filtro específico por fonte
  - Date Range: Seleção de período customizado
  
- **4 cards de métricas**
  - Total Real: Soma dos gastos reais
  - Total Ideal: Soma dos orçamentos ideais
  - Difference: Real - Ideal
  - Status: "Over Budget" (vermelho) ou "On Track" (verde)
  
- **Orçamentos específicos por fonte** (5 fontes configuradas)
  - VISA_REC: LF, Esporte, Stream (3 categorias)
  - VISA_BIA: Mercado, Feira, Farmácia, Pet, Lazer (5 categorias)
  - VISA_FIS: Datas, Estética, Compras, Pet (4 categorias)
  - PIX: Casa, Nita, Utilidades, Faculdade, Esporte (5 categorias)
  - MASTER_VIRTUAL: Betina, Farmácia (2 categorias)
  
- **Lógica de filtros inteligente**
  - Mantém view_by="category" mesmo quando filtrando por fonte
  - Aplica orçamento específico da fonte quando disponível
  - Multiplica por 12 quando mês = "TODOS" (visão anual)

#### **✏️ Edição de Transações**

- **Modal de edição com botão por linha**
  - Botão "✏️" em cada transação na tabela
  - Modal com campos: ID, Data, Descrição, Valor, Fonte (readonly)
  - Dropdown de categoria com texto branco (.dropdown-white-text)
  - Botão "Salvar" persiste no banco de dados
  
- **Database path corrigido**
  - Path correto: BASE_DIR.parent.parent / 'dados' / 'db' / 'financeiro.db'
  - Evita erro de "database not found"
  
- **Apenas categoria editável**
  - Campo fonte é read-only para evitar inconsistências
  - Foco em categorização de transações pendentes

#### **🎨 Melhorias de UI/UX**

- **Dropdown no sidebar abre para cima**
  - CSS: .dropdown-sidebar com bottom: 100%, top: auto
  - Evita cortar opções na parte inferior da tela
  
- **Texto branco em dropdowns do modal**
  - Classe .dropdown-white-text resolve problema de contraste
  - Visível em fundo escuro do modal

### 🔧 Corrigido

#### **📊 Ordenação Cronológica nos Gráficos**

- **Problema**: Meses exibidos em ordem alfabética (Abril, Agosto, Dezembro) ao invés de cronológica
- **Solução**: 
  - Conversão de `mes_comp` para datetime com `pd.to_datetime(format='%B %Y')`
  - Locale handling (pt_BR.UTF-8 ou Portuguese_Brazil.1252)
  - `.dropna(subset=['data_ordenacao'])` remove conversões falhas
  - Uso de índices numéricos no eixo X com `ticktext` para labels
  - Aplicado em: Dashboard (evolução 12 meses), Analytics (acumulado 6 meses)
  
- **Resultado**: Gráficos agora mostram meses em ordem cronológica correta
  - Dashboard: Fevereiro 2025 → Janeiro 2026 (últimos 12 meses)
  - Analytics: Agosto 2025 → Janeiro 2026 (últimos 6 meses)

#### **💾 Save de Transações**

- **Problema**: Botão salvar não persistia mudanças no banco
- **Causa**: Database path incorreto (backend/src/dados vs dados)
- **Solução**: Path absoluto correto usando BASE_DIR.parent.parent

#### **🔍 Filtro por Fonte em Ideals**

- **Problema**: Filtrar por fonte mudava view_by automaticamente para "source"
- **Solução**: Lógica mantém view_by inalterado, apenas filtra dados

### 📝 Alterado

- **database.py**: Renomeado `rowid` → `id` no DataFrame de transações
- **graficos.py**: Filtro `valor > 0` para débitos (antes era `< 0`)
- **config.py**: Adicionados 5 dicionários de orçamento por fonte
- **sidebar.py**: Link "Ideals" com ícone fa-bullseye
- **main.py**: 4 novos callbacks para página Ideals + edição de transações

### 🗑️ Removido

- Tentativa de inline editing no DataTable (substituído por modal)
- categoryorder sem índices numéricos (causava reordenação alfabética)

---

## [2.6.0] - 2025-12-23 📊

### 🎯 Principais Mudanças

**FUNCIONALIDADES COMPLETAS DO DASHBOARD V2!** Páginas Analytics e Transações totalmente implementadas com gráficos avançados, filtros múltiplos, ordenação inteligente e subtotal.

### ✨ Adicionado

#### **📈 Página Analytics - Análises Avançadas**

- **3 gráficos analíticos interativos**
  - **Real vs Ideal**: Comparação mensal entre gastos reais e limites ideais (barras agrupadas)
  - **Distribuição Temporal**: Análise de gastos por dia da semana (barras horizontais)
  - **Evolução Acumulada**: Progressão acumulada de gastos no mês (linha com área)
  
- **Callbacks dinâmicos**: Todos os gráficos atualizam com filtro de mês global
- **Layout responsivo**: 3 gráficos empilhados em cards, altura 300px cada

#### **📋 Página Transações - Gerenciamento Completo**

- **5 filtros simultâneos**
  - **Categoria**: Dropdown com todas as categorias disponíveis + opção "Todas"
  - **Fonte**: Dropdown com todas as fontes (Nubank, Itaú, BTG, etc.) + opção "Todas"
  - **Status**: Categorizadas, Pendentes ou Todas
  - **Mês de Compensação**: Dropdown com meses únicos + opção "Todos"
  - **Período (Data)**: DatePickerRange para filtro por intervalo de datas
  
- **Tabela HTML customizada** (substitui DataTable para evitar erro de chunk JS)
  - 6 colunas: Data, Descrição, Valor, Categoria, Fonte, Mês
  - Destaque visual para categorias "A definir" (fundo amarelo)
  - Limite de 100 transações exibidas
  - Formatação de valores: R$ 1.234,56
  
- **Ordenação inteligente**: mes_comp (crescente) → fonte (decrescente) → data (crescente)
- **Subtotal dinâmico**: Exibe soma dos valores das transações visíveis com destaque
- **Layout de filtros**: 2 linhas com flexbox responsivo (wrap), gap 16px

#### **🎨 Estilização DatePicker**

- **Tema escuro completo** para DatePickerRange
  - Background: `#16213E`, border: `#2D3748`
  - Calendário: z-index 9999 (sempre visível sobre tabela)
  - Dias selecionados: cor primária `#2E86AB`
  - Navegação e headers estilizados (setas, labels)
  - Hover states sutis (brightness 1.1)
  
- **CSS injetado** em `assets/custom_styles.py` (~100 linhas)

### 🐛 Corrigido

- **Filtro de débitos invertido**: Corrigido `df['valor'] < 0` → `df['valor'] > 0` em 4 locais
  - `database.py`: calcular_estatisticas()
  - `graficos.py`: criar_grafico_evolucao(), criar_grafico_top_categorias(), criar_grafico_top_fontes()
  - **Razão**: No banco, débitos (gastos) têm valor POSITIVO, créditos (receitas) têm valor NEGATIVO
  
- **Callback error na página Transações**: Removido `prevent_initial_call=True` e validação excessiva que impedia carregamento inicial

- **DatePicker fora do padrão**: Adicionado className e estilos CSS completos para combinar com tema escuro

- **Erro de chunk JavaScript**: Substituído `dash_table.DataTable` por tabela HTML customizada (html.Table)

- **Validação de filtros**: Adicionados null checks para evitar comparações com None

### 🔧 Alterado

- **Formatação de data**: Movida para depois da ordenação em atualizar_tabela_transacoes() para evitar problemas de sort
- **Filtros de transações**: Callback agora suporta 7 inputs (mes_global + 6 filtros de página)
- **Estrutura de retorno**: Tabela retorna div com subtotal + tabela HTML ao invés de DataTable

### 📝 Técnico

- **Arquivos modificados**:
  - `backend/src/dashboard_v2/main.py`: 3 novos callbacks (Analytics), 1 modificado (Transações)
  - `backend/src/dashboard_v2/utils/graficos.py`: 3 novas funções + 3 correções de filtro
  - `backend/src/dashboard_v2/utils/database.py`: Correção de filtro débitos
  - `backend/src/dashboard_v2/pages/transacoes.py`: 2 novos filtros + layout 2 linhas
  - `backend/src/dashboard_v2/assets/custom_styles.py`: +100 linhas DatePicker CSS
  
- **Commits anteriores**: v2.5.0 (16/12) - Dashboard V2 estrutura base

---

## [2.5.0] - 2025-12-16 🎨

### 🎯 Principais Mudanças

**NOVO DASHBOARD V2 (DARK THEME)!** Interface moderna inspirada em Behance, estrutura MVC organizada, e gráficos interativos com dados reais.

### ✨ Adicionado

#### **🎨 Dashboard V2 - Interface Moderna**

- **Estrutura organizada (MVC-style)**
  - `backend/src/dashboard_v2/` - Novo diretório isolado do dashboard antigo
  - `pages/` - dashboard.py, analytics.py (placeholder), transacoes.py (placeholder)
  - `components/` - sidebar.py (navegação lateral)
  - `utils/` - database.py (queries SQLite), graficos.py (Plotly charts)
  - `assets/` - custom_styles.py (CSS dark theme)
  - `config.py` - Configuração centralizada (cores, fontes, espaçamentos)

- **Tema dark profissional (Behance-inspired)**
  - Background: `#0F0F23`, Cards: `#16213E`, Primary: `#2E86AB`
  - Success: `#06A77D`, Danger: `#D62246`
  - Tipografia Inter com escala reduzida (10-28px)
  - Espaçamentos compactos (12-32px)

- **Dashboard principal funcional (porta 8052)**
  - 3 cards de métricas (Total, Cartões, Pix + Boletos) com ícones FontAwesome
  - Gráfico hero: Evolução últimos 12 meses (linha com área preenchida)
  - 2 gráficos laterais: Top 5 Categorias e Top 5 Fontes (barras horizontais)
  - Dropdown de filtro por mês (carrega meses disponíveis do banco)

- **Integração com banco de dados**
  - `carregar_transacoes(mes_filtro)` - Carrega do SQLite com filtro opcional
  - `calcular_estatisticas(df)` - Total gasto, por cartões, por pix/boleto
  - `obter_meses_disponiveis()` - Lista de meses únicos do banco

- **Callbacks interativos**
  - Roteamento entre páginas (Dashboard, Analytics, Transações)
  - Atualização dinâmica dos 3 gráficos baseado no filtro de mês
  - Cálculo de estatísticas em tempo real

- **Execução**
  - Script: `dashboard_v2.bat` ou `py backend/src/dashboard_v2/main.py`
  - Porta: 8052 (evita conflito com dashboard antigo na 8051)

### 🐛 Corrigido

#### **Erros técnicos do Dashboard V2**

- **ModuleNotFoundError** - `sys.path.insert(0, ...)` + `__init__.py` em todas subpastas
- **CSS injection** - Substituído `html.Style()` por `app.index_string` (método correto Dash)
- **Gráficos sem dados** - Criados callbacks em `main.py` + funções em `utils/graficos.py`
- **TypeError: duplicate 'xaxis'** - Separado `update_layout()` de `update_xaxes()`/`update_yaxes()`
- **ValueError: duplicate 'hovermode'** - Removido do `update_layout()` (já em `PLOTLY_TEMPLATE`)
- **Invalid 'titlefont'** - Mudado para `title: {font: {...}}` (sintaxe Plotly moderna)
- **Invalid fillcolor '#2E86AB30'** - Convertido para `rgba(46, 134, 171, 0.2)`

### 🔧 Melhorado

#### **Responsividade e escala visual**

- **Dimensões reduzidas para Full HD (1920×1080)**
  - Fontes: 10px (xs) a 28px (4xl) - redução ~40%
  - Espaçamentos: 4px (xs) a 32px (3xl) - redução ~30%
  - Ícones: 36×36px (antes 56×56px)
  - Gráficos: 240-280px altura (antes 350-400px)
  - Padding cards/container: 12px (antes 24px)

- **Layout flexbox**
  - Cards com `flex: 1, minWidth: 200px`
  - Gráficos com `flexWrap: wrap` para responsividade
  - Gap reduzido entre elementos (12px)

### ⚠️ Problemas Conhecidos

- **Layout ainda não está otimizado** - Componentes funcionais mas proporções não ideais
- **Analytics page** - Apenas placeholder, sem gráficos implementados
- **Transações page** - Apenas placeholder, sem tabela implementada
- **Categorização inline** - Não implementada ainda (presente apenas no dashboard antigo)

### 📝 Próximos Passos

1. **Refinar layout visual**
   - Comparar proporções com design de referência Behance
   - Ajustar tamanhos relativos entre cards e gráficos
   - Melhorar espaçamento vertical/horizontal

2. **Implementar Analytics**
   - Gráfico Real vs Ideal por categoria
   - Distribuição temporal de gastos
   - Acumulado mensal comparativo

3. **Implementar Transações**
   - Tabela interativa com todas transações
   - Filtros por categoria, fonte, status
   - Categorização inline (dropdown por linha)
   - Paginação

4. **Melhorias visuais**
   - Animações sutis (hover, transitions)
   - Indicadores de progresso (budget usage)
   - Tooltips informativos
   - Dark/light mode toggle

---

## [2.4.0] - 2025-12-10 🔧

### 🎯 Principais Mudanças

**CORREÇÕES CRÍTICAS + FERRAMENTAS DE MANUTENÇÃO!** Sistema de limpeza de dados, categorização em lote, e redução de 97,9% no banco de dados.

### ✅ Corrigido

#### **🐛 Correções no Dashboard**

- **Duplicatas visuais removidas** - Implementado `drop_duplicates()` em `carregar_dados()` e `carregar_transacoes_pendentes()`
  - Chave composta: `['data', 'descricao', 'valor', 'fonte']`
  - Dashboard agora exibe cada transação apenas uma vez

- **Filtro de valor removido** - Eliminado `Valor < 0` das queries SQL
  - Valores já são normalizados como positivos (`valor_normalizado`)
  - Dados agora aparecem corretamente no dashboard

- **Filtro de mês aplicado na categorização** - Callback `atualizar_secao_pendentes()` recebe `mes_selecionado`
  - Função `carregar_transacoes_pendentes()` aceita parâmetro `mes_filtro`
  - Ao filtrar por "Dezembro 2025", tabela mostra apenas dezembro

- **Limpeza massiva do banco de dados** - Banco reduzido de 116.880 para 2.486 registros
  - Redução de 97,9% (114.394 registros duplicados removidos)
  - Backup automático criado: `lancamentos_archive_TIMESTAMP`

### ✨ Adicionado

#### **☑️ Categorização em Lote (dashboard_dash_excel.py)**

- **Checkbox "Selecionar Todos"** no cabeçalho da tabela
  - Marca/desmarca todos os checkboxes com um clique
  - Pattern-matching callback com `ALL`

- **Checkboxes individuais** por linha de transação
  - ID dinâmico: `{'type': 'checkbox-item', 'index': rowid}`
  - Estado persistente durante interações

- **Controles de categorização em lote**
  - Dropdown de categoria compartilhado
  - Botão "Aplicar aos Selecionados"
  - Feedback visual de sucesso/erro
  - Refresh automático da tabela após aplicação

- **Callback `aplicar_categoria_lote()`**
  - Aplica categoria a múltiplas transações simultaneamente
  - Loop de atualização com `atualizar_categoria_banco()`
  - Mensagem: "✅ Categoria 'X' aplicada a N transações!"

#### **🔄 Dictionary Updater Unificado (atualiza_dicionario_unificado.py)**

- **Script novo** com 3 fontes de atualização:
  1. `consolidado` - Excel consolidado_temp.xlsx
  2. `controle_pessoal` - Controle_pessoal.xlsm (aba Anual)
  3. `db` - Tabela lancamentos do banco (🆕 NOVO)

- **Função `atualizar_de_db()`**
  - Lê tabela lancamentos
  - Filtra apenas categorizados (exceto "A definir")
  - Exclui INVESTIMENTOS e SALÁRIO
  - Insere em `categorias_aprendidas` com `fonte_aprendizado='db'`

- **Uso via linha de comando:**
  ```bash
  python atualiza_dicionario_unificado.py consolidado
  python atualiza_dicionario_unificado.py controle_pessoal
  python atualiza_dicionario_unificado.py db
  ```

#### **🏛️ Integração no Menu Batch (agente_financeiro_completo.bat)**

- **Opção [5] adicionada** - "Atualizar Dicionário de Categorias do Banco de Dados"
  - Chama: `py atualiza_dicionario_unificado.py db`
  - Total de opções: 6 → 7

#### **🗑️ Scripts de Limpeza e Manutenção**

- **limpar_base_lancamentos.py** (162 linhas) - Limpeza completa do banco
  - Renomeia `lancamentos` → `lancamentos_archive_TIMESTAMP` (backup)
  - Cria nova tabela `lancamentos`
  - Importa do consolidado Excel
  - Complementa Out/Nov do `transacoes_openfinance`
  - Exibe estatísticas antes/depois com redução percentual

- **complementar_out_nov.py** (186 linhas) - Integração Open Finance
  - Importa apenas débitos (`tipo_transacao='DEBIT'`)
  - Filtra Out/Nov 2025
  - Exclui transferências internas (ITAU VISA/BLACK/MASTER, Pagamento recebido, Rendimentos)
  - Inseriu 128 registros na base limpa

- **agente_financeiro_mensal.py** (180 linhas) - Atualização mensal
  - Deleta registros do mês especificado
  - Importa do consolidado Excel apenas aquele mês
  - Exibe estatísticas antes/depois com destaque visual
  - Uso: `python agente_financeiro_mensal.py "Dezembro 2025"`

#### **📚 Documentação Completa**

- **010_SESSAO_CORRECOES_DASHBOARD_10DEZ.md** (1.200+ linhas)
  - 7 problemas identificados
  - 9 soluções implementadas com código completo
  - 6 arquivos criados/modificados
  - Estatísticas finais (116K → 2.5K registros)
  - 7 testes práticos de validação
  - Conhecimento técnico (pattern matching, archive pattern, filtros dinâmicos)
  - Roadmap de melhorias (curto/médio/longo prazo)

### 📊 Estatísticas

```
Banco de Dados:
  Antes da limpeza:   116.880 registros (duplicados)
  Depois da limpeza:    2.358 registros (consolidado)
  Complementação OF:      128 registros (Out/Nov)
  Total final:          2.486 registros
  Redução:             97,9% (114.394 registros removidos)

Dashboard:
  Transações válidas:     2.486
  Categorizadas:          2.234 (89,9%)
  Pendentes:                252 (10,1%)

Dictionary Updater:
  Fontes disponíveis: 3 (consolidado, controle_pessoal, db)
```

### 🔧 Modificado

- **dashboard_dash_excel.py**
  - Removido filtro `Valor < 0` (linhas ~69-96)
  - Adicionado `drop_duplicates()` em 2 funções (linhas ~98, ~123)
  - Parâmetro `mes_filtro` em `carregar_transacoes_pendentes()` (linha ~108)
  - UI de checkboxes e categorização em lote (linhas ~430-500)
  - Callbacks para "Selecionar Todos" (linha ~580)
  - Callbacks para "Aplicar em Lote" (linha ~595)
  - Callback `atualizar_secao_pendentes()` recebe `mes_selecionado` (linha ~388)

- **agente_financeiro_completo.bat**
  - Adicionada opção [5] - Atualizar dicionário do banco

### 🚀 Próximos Passos

- [ ] Layout responsivo do dashboard (1 gráfico por linha em 1920x1080) - **PRIORIDADE ALTA**
- [ ] Teste de performance com 10k+ registros
- [ ] Validação de integridade referencial no dictionary updater

---

## [2.3.0] - 2025-11-25 📊

### 🎯 Principais Mudanças

**DASHBOARD INTERATIVO COMPLETO!** Visualização em tempo real com análise gráfica, categorização inline e filtros dinâmicos otimizados para telas QHD.

### ✨ Adicionado

#### **📊 Dashboard Dash + Plotly**

- **Script `dashboard_dash.py`** - Dashboard interativo completo
  - 6 cards informativos compactos (Total, Média 12M, Categorizado, Pendentes, Transações, Meses)
  - Categorização inline de transações "A definir" direto no dashboard
  - 3 filtros dinâmicos (Mês, Categoria, Fonte) com refresh automático
  - 7 gráficos interativos: Real vs Ideal, Evolução Mensal, Fontes (pizza), Categorias (pizza), Distribuição, Acumulado
  - Pattern-matching callbacks para múltiplos botões de categorização
  - dcc.Store para gerenciamento de estado e refresh
  - Acesso via http://localhost:8050

#### **🎨 Otimizações UX para QHD (2560×1440)**

- **Layout compacto**: 6 cards ao invés de 4 (width=2 cada)
- **Fontes ajustadas**:
  - textfont: 10pt (valores nas barras)
  - legend: 14pt (legendas)
  - title: 24pt (títulos gráficos)
  - tickfont: 18pt (eixos)
  - uniformtext: minsize=10, mode='show' (força tamanho configurado)
- **Valores normalizados**: R$ 14.400 → 14.4k (formato k para milhares)
- **Cores inteligentes na 3ª barra**:
  - Verde: economizou (real < ideal)
  - Vermelho: excedeu (real > ideal)
  - Fonte 12pt em negrito, sem sinais +/-
- **Filtros compactos**: padding p-2, labels curtos

#### **🔧 Melhorias Técnicas**

- **Database filtering**: Exclusão automática de transferências internas (ITAU VISA/BLACK/MASTER/PGTO FATURA/PAGAMENTO CARTAO)
- **Callbacks otimizados**: 11 outputs no callback principal
- **Plotly config**: displayModeBar sempre visível com ferramentas (zoom, pan, download PNG, reset)
- **Pattern-matching**: Botões e dropdowns dinâmicos com IDs JSON-serializáveis
- **Média 12M fixa**: Sempre mostra média de 12 meses independente de filtros

### 🐛 Corrigido

- **titlefont inválido**: Mudado para `title={'font': {'size': 24}}` (sintaxe correta Plotly)
- **Fontes não aplicando**: Adicionado `uniformtext` para forçar Plotly a respeitar tamanhos
- **Transferências internas**: Filtradas 24 transações (R$ 237k) de pagamentos de cartão
- **Row ID inconsistente**: Usado alias `rowid as row_id` no SQLite para compatibilidade pandas

### 📈 Resultados Dashboard

- **2.096 transações** carregadas (após filtros)
- **97.2% categorizadas** (2.038/2.096)
- **0 pendentes** (100% categorizado)
- **R$ 328.943,96** total
- **12 meses** de dados (Jan-Dez 2025)

### 📚 Documentação

- Criado `docs/DASHBOARD_INTERATIVO.md` - Documentação completa do dashboard
  - Arquitetura técnica
  - Guia de uso
  - Configurações de fontes e cores
  - Estatísticas atuais
  - Limitações conhecidas
  - Roadmap de melhorias

---

## [2.2.0] - 2025-11-10 🎉

### 🎯 Principais Mudanças

**AVANÇO GIGANTE!** Geração completa de Excel consolidado a partir de dados reais do Open Finance com categorização inteligente, conversão de moeda e identificação de parcelas.

### ✨ Adicionado

#### **📊 Geração de Excel Open Finance**

- **Script `gerar_excel_pluggy.py`** - Geração completa de Excel consolidado
  - Fetches de 614 transações reais (3 contas Itaú: 2 cartões + 1 conta corrente)
  - Período: Ciclo 19-18 (19/10/2025 a 18/11/2025) = 141 transações
  - Compatibilidade total com formato `consolidado_temp.xlsx`
  - Categorização inteligente via `CategorizationService` (83% automático)
  - Conversão automática de moedas estrangeiras (USD, EUR, GBP → BRL)
  - Identificação de parcelas (1/3, 2/5, etc.) com metadata completa
  - Mapeamento de fontes usando `get_card_source()` (9 fontes: PIX, Master/Visa Físico/Virtual/Recorrente/Bia/Mae)
- **Colunas Excel**: Data, Descricao, Fonte, Valor, Categoria, MesComp, Origem_Banco, Tipo_Conta, Categoria_Banco, Tipo_Transacao, Parcela, Provider_ID
- **Ordenação correta**: MesComp (asc) → Fonte (desc) → Data (asc)
- **Output**: `dados/planilhas/consolidado_pluggy_nov2025.xlsx`

#### **🔧 Melhorias no Sistema**

- Adicionada categoria `VESTUARIO = "Vestuário"` ao enum `TransactionCategory`
- Scripts auxiliares:
  - `verificar_parcelas.py` - Análise de metadata de parcelas (121 transações encontradas)
  - `atualizar_categoria_vestuario.py` - Verificação de categorias no banco (30 categorias, 565 registros)
  - `buscar_itau_simples.py` - Fetch simplificado sem emojis (614 transações)
  - `listar_transacoes_3meses.py` - Demo com Mercado Pago (15 transações)

#### **📈 Resultados Conquistados**

- **141 transações** processadas para Novembro 2025
- **83% de categorização automática** (117/141 transações)
- **33 parcelas** identificadas com número/total
- **13 transações em moeda estrangeira** convertidas para BRL
- **23 transações** pendentes ("A definir" - 16.3%)
- **R$ -12.391,35** em débitos totais
- **Fontes mapeadas**: Visa Bia (28), PIX (28), Master Físico (22), Visa Recorrente (16), Visa Mae (12), Master Virtual (11), Visa Físico (11), Visa Virtual (7), Master Recorrente (6)

### 🔒 Segurança

- Confirmado acesso **somente leitura** via OAuth2 Open Finance
- Nenhuma operação de escrita possível (transferências, pagamentos, alterações)
- Dados sensíveis protegidos em `config.ini` (não versionado)

---

## [2.1.0] - 2025-11-10 🚀

### 🎉 Principais Mudanças

Esta versão representa um **avanço significativo** no projeto com integração Open Finance e reorganização profissional completa da documentação.

### ✨ Adicionado

#### **🔗 Integração Open Finance (Pluggy)**

- Integração completa com Open Finance Brasil via Pluggy
- Cliente REST API funcional (autenticação, contas, transações, identidade)
- Suporte a OAuth2 para conexão segura com bancos
- Mercado Pago conectado e validado com dados reais
- Sandbox de testes configurado e operacional
- Módulos `backend/src/integrations/`:
  - `pluggy_client.py` - Cliente API (REST, não SDK)
  - `pluggy_sync.py` - Serviço de sincronização de transações
- Scripts de teste e validação:
  - `teste_pluggy_rest.py` - Validação REST API ✅
  - `verificar_dados_completos.py` - Testes completos ✅

#### **📚 Documentação Profissional Reorganizada**

- Estrutura de documentação com padrão de mercado
- 3 categorias temáticas criadas:
  - `/docs/Desenvolvimento/` - Arquitetura, guias, planejamento
  - `/docs/Integracao/` - Open Finance, APIs externas
  - `/docs/Testing/` - Estratégia de testes, qualidade
- Numeração cronológica (XXX_NOME.md) em todos os documentos
- READMEs em cada categoria para navegação
- `/docs/README.md` - Índice visual completo
- `Integracao_PROXIMO_CHAT.md` - Contexto rápido para IA/novos membros
- Novos documentos técnicos:
  - `003_ARQUITETURA_PLUGGY.md` - Decisões técnicas (REST vs SDK)
  - `004_SEGURANCA_OPENFINANCE.md` - Compliance LGPD/BCB
  - `007_REORGANIZACAO_COMPLETA.md` - Histórico da reorganização

#### **⚙️ Configurações Centralizadas**

- Pasta `/config/` criada para arquivos de configuração
- `config/README.md` com guia completo de uso
- `config.ini` movido de `/backend/src/` para `/config/`
- Template `config.example.ini` atualizado com seção `[PLUGGY]`
- Proteção via `.gitignore` mantida

### 🔧 Melhorado

- **README.md** atualizado:
  - Badge Open Finance adicionado
  - Seção de integração Open Finance
  - Links para documentação reorganizada
  - Estrutura do projeto atualizada
  - Roadmap ajustado (v2.1 = Open Finance)
  - Informações de autor corretas
- **Badges** atualizadas com novos links (paths corretos)
- **Roadmap** reajustado para refletir avanço no cronograma

### 📖 Documentação

#### **Guias de Integração Open Finance**

- Decisões técnicas documentadas (por que REST API em vez de SDK)
- Diagramas de arquitetura (Mermaid) - componentes e fluxos
- Mapeamento completo Pluggy → Transaction model
- Segurança e compliance LGPD/BCB documentados
- Checklist de segurança e plano de resposta a incidentes
- Performance e otimizações implementadas

#### **Navegação Melhorada**

- Links cruzados entre documentos relacionados
- Índices em cada categoria
- Emojis padronizados para seções
- Estrutura hierárquica clara

### 🔐 Segurança

- Credenciais Pluggy protegidas em `config/config.ini` (`.gitignore`)
- OAuth2 implementado (não compartilha senha bancária)
- Read-only access (sem permissão de transferência)
- Compliance LGPD documentado
- Certificações Pluggy verificadas (ISO 27001, PCI DSS, SOC 2)
- Plano de resposta a incidentes documentado

### 🐛 Problemas Conhecidos

- **pluggy-sdk** tem bug de autenticação (não usar)
- Solução: REST API direta com biblioteca `requests`
- Trial Pluggy expirado, mas Sandbox funciona
- Items criados apenas via Dashboard (não programaticamente)
- Documentação completa em `docs/Integracao_PROXIMO_CHAT.md`

### 🎯 Próximos Passos

- [ ] Migrar credenciais para `.env` + `python-decouple`
- [ ] Refatorar `pluggy_client.py` para usar REST API definitivamente
- [ ] Conectar conta Itaú via Open Finance
- [ ] Implementar sincronização automática de transações
- [ ] Integrar Open Finance no fluxo principal do agente

### 📊 Estatísticas

- **9 novos arquivos** criados (docs + config)
- **14 arquivos** reorganizados com numeração
- **100% preservação** de conteúdo (nada perdido)
- **3 categorias** de documentação
- **4 READMEs** de navegação criados

---

## [2.0.2] - 2025-10-28 🐛

### 🐛 Corrigido

- **Lógica incorreta do ciclo mensal 19-18**
  - Sistema não buscava arquivos do mês correto após dia 19
  - Arquivos de novembro (202511) não eram processados
  - Lógica definia `mes_atual = hoje.month` independente do dia
  - Corrigido para avançar para o próximo mês quando `dia >= 19`

### 📊 Impacto

- **Antes:** 30 arquivos processados (202510 e anteriores)
- **Depois:** 33 arquivos processados (202511, 202510, ...)
- **Ganho:** +3 arquivos (novembro completo)
- **Transações:** 2184 (vs 2109 anterior, +75 transações)

### ✨ Adicionado

- **Script de validação do ciclo 19-18**

  - `backend/src/teste_ciclo_19_18.py`
  - Visualiza lógica do ciclo mensal
  - Lista arquivos que devem ser buscados
  - Compara com arquivos realmente encontrados

- **Novo teste unitário**
  - `test_find_recent_files_ciclo_19_18()`
  - Valida comportamento antes e depois do dia 19
  - Verifica arquivo correto sendo buscado

### 🔧 Melhorado

- **Documentação técnica atualizada**
  - Nova seção "Ciclo Mensal e Busca de Arquivos"
  - Tabela com exemplos práticos de datas
  - Explicação sobre não filtrar datas dentro dos arquivos
  - Motivos para preservar todas as transações

### 🧪 Testes

- **17/17 testes passando** em `test_file_processing_service.py`
- Teste de integração real executado com sucesso
- Processamento completo validado com 2184 transações

### 📝 Arquivos Modificados

```
M  backend/src/services/file_processing_service.py
M  tests/test_services/test_file_processing_service.py
M  docs/DOCUMENTACAO_TECNICA.md
A  backend/src/teste_ciclo_19_18.py
```

---

## [2.0.1] - 2025-10-28 🔧

### 🐛 Corrigido

- **Erro de PATH do Python ao executar arquivos .bat**
  - Scripts não executavam mesmo com Anaconda instalado
  - VS Code não detectava interpretador correto
  - Dependências não eram encontradas

### ✨ Adicionado

- **Ambiente Conda isolado para o projeto**

  - Criado ambiente `financeiro` com Python 3.11.14
  - Instaladas 19 dependências do requirements.txt
  - Ambiente separado do Anaconda base para evitar conflitos

- **Documentação de configuração**
  - `CONFIGURACAO_AMBIENTE.md`: Guia completo de setup do ambiente
  - Seção de troubleshooting em `DOCUMENTACAO_TECNICA.md`
  - Instruções de instalação atualizadas no `README.md`
  - Referências no `INDICE_DOCUMENTACAO.md`

### 🔧 Melhorado

- **Todos os arquivos .bat atualizados (5 arquivos)**

  - `agente_financeiro_completo.bat`
  - `agente_financeiro_simples.bat`
  - `agente_financeiro.bat`
  - `atualiza_dicionario.bat`
  - `atualiza_dicionario_controle.bat`
  - Agora executam via Conda: `conda run -n financeiro python script.py`
  - Validação de existência do Conda e ambiente
  - Mensagens de erro descritivas e informativas

- **Configuração do VS Code**
  - `.vscode/settings.json` atualizado para usar interpretador Conda
  - Path configurado: `C:\Users\<user>\.conda\envs\financeiro\python.exe`

### ✅ Validado

- **Testes de integração completos**
  - Ambiente Conda criado e funcional
  - Python 3.11.14 confirmado
  - Todas as 19 dependências instaladas corretamente
  - Sistema processou 2109 transações com 100% de sucesso
  - 30 arquivos processados em 16.97 segundos
  - 98.2% de precisão na categorização mantida
  - Zero erros de execução

### 📦 Dependências

**Instaladas no ambiente `financeiro`:**

- pandas 2.3.3
- openpyxl 3.1.5
- xlrd 2.0.2
- pytest 8.4.2
- pytest-cov 7.0.0
- pytest-mock 3.15.1
- black 25.9.0
- flake8 7.3.0
- isort 7.0.0
- tqdm 4.67.1
- colorama 0.4.6
- configparser 7.2.0
- E 7 dependências transitivas

### 📝 Documentação

- ✅ `CONFIGURACAO_AMBIENTE.md` - Novo guia completo
- ✅ `docs/DOCUMENTACAO_TECNICA.md` - Seção de troubleshooting
- ✅ `docs/INDICE_DOCUMENTACAO.md` - Referências atualizadas
- ✅ `README.md` - Instruções de instalação com Conda
- ✅ `COMMIT_MESSAGE.md` - Detalhamento completo da correção
- ✅ `CHANGELOG.md` - Este registro

### 🎯 Impacto

- ✅ Scripts .bat funcionam em qualquer máquina Windows com Anaconda
- ✅ Ambiente isolado evita conflitos entre projetos
- ✅ Configuração documentada e reproduzível
- ✅ Sistema 100% operacional e validado em produção

---

## [2.0.0] - 2025-09-30 🚀

### ✨ Adicionado

- **Sistema de automação completa via .bat files**

  - `agente_financeiro_completo.bat`: Interface completa com validações
  - `agente_financeiro_simples.bat`: Interface simplificada para compatibilidade
  - Menu interativo com 6 opções e emojis
  - Execução via duplo-clique no Windows Explorer
  - Tratamento robusto de erros com códigos de saída

- **Ordenação inteligente do Excel gerado**

  - Ordenação por MesComp → Fonte desc → Data
  - Limpeza automática de prefixes (Master/Visa sem "Itaú"/"Latam")
  - Formatação otimizada para análise

- **Sistema de limpeza de categorias duplicadas**

  - `limpar_categorias.py`: Remove duplicatas com sufixos de data
  - Consolidação inteligente de categorias similares
  - Proteção contra criação de novas duplicatas

- **Configuração automática do sistema**

  - `config.ini` criado automaticamente com paths absolutos
  - Configurações otimizadas para melhor performance
  - Detecção automática de estrutura de diretórios

- **Documentação completa**
  - README.md atualizado com métricas atuais
  - Documentação técnica detalhada
  - Guia do usuário com casos de uso
  - Changelog estruturado

### 🔧 Melhorado

- **Performance de categorização**: Saltou para **98.2% de precisão** (1759/1791 transações)
- **Base de conhecimento otimizada**: Reduzida de 772 para 584 categorias (24% menor)
- **Detecção de tipos de cartão**: Melhor identificação Master/Visa
- **Tratamento de erros**: Mais robusto em todos os scripts
- **Interface do usuário**: Menus com emojis e feedback visual

### 🐛 Corrigido

- **Duplicatas de categorias**: Sistema agora previne criação de categorias com sufixos de data
- **Navegação de diretórios**: .bat files agora funcionam de qualquer localização
- **Codificação de caracteres**: Melhor tratamento de caracteres especiais
- **Validação de arquivos**: Verificação mais robusta de formatos
- **Execução via Explorer**: Funciona perfeitamente via duplo-clique

### 🗄️ Dados

- **Transações processadas**: 1.791 total
- **Categorização automática**: 1.759 (98.2%)
- **Requer revisão manual**: 32 (1.8%)
- **Categorias únicas**: 584 (após otimização)

---

## [1.5.0] - 2025-09-29

### ✨ Adicionado

- **Scripts .bat individuais**
  - `agente_financeiro.bat`
  - `atualiza_dicionario.bat`
  - `atualiza_dicionario_controle.bat`
- **Configuração via config.ini**
- **Logs estruturados**

### 🔧 Melhorado

- **Categorização**: ~95% de precisão
- **Performance**: Processamento mais rápido
- **Estabilidade**: Menos erros durante execução

---

## [1.4.0] - 2025-09-28

### ✨ Adicionado

- **Suporte a múltiplos formatos**
  - CSV para PIX
  - XLSX para cartões
- **Normalização avançada de dados**
- **Detecção automática de moedas estrangeiras**

### 🔧 Melhorado

- **Algoritmo de categorização**: Melhor precisão em padrões
- **Tratamento de datas**: Suporte a formatos variados
- **Validação de dados**: Mais critérios de qualidade

---

## [1.3.0] - 2025-09-27

### ✨ Adicionado

- **Sistema de aprendizado com SQLite**
- **Categorização automática baseada em padrões**
- **Exportação estruturada para Excel**

### 🔧 Melhorado

- **Base de dados**: Migração de arquivos texto para SQLite
- **Performance**: Consultas mais rápidas
- **Escalabilidade**: Suporte a grandes volumes

---

## [1.2.0] - 2025-09-26

### ✨ Adicionado

- **Processamento de cartões Latam**
- **Detecção de tipos de cartão (Master/Visa)**
- **Consolidação por mês de competência**

### 🔧 Melhorado

- **Cobertura**: Mais fontes de dados
- **Análise temporal**: Agrupamento por períodos
- **Qualidade dos dados**: Validações adicionais

---

## [1.1.0] - 2025-09-25

### ✨ Adicionado

- **Suporte a cartões Itaú (XLS)**
- **Categorização manual básica**
- **Backup automático de dados**

### 🔧 Melhorado

- **Robustez**: Melhor tratamento de exceções
- **Usabilidade**: Interface mais clara
- **Documentação**: Exemplos práticos

---

## [1.0.0] - 2025-09-24

### ✨ Adicionado - Versão Inicial

- **Processamento de extratos PIX (TXT)**
- **Categorização manual via Excel**
- **Sistema básico de aprendizado**
- **Exportação para planilhas**

### 🏗️ Estrutura Inicial

- Script Python principal
- Leitura de arquivos TXT
- Base de conhecimento em arquivos
- Saída em formato Excel

---

## 🔮 **Roadmap Futuro**

### [2.1.0] - Planejado para Q4 2025

- [ ] **Dashboard web interativo** com Streamlit
- [ ] **API REST** para integração externa
- [ ] **Análise preditiva** com machine learning
- [ ] **Alertas automáticos** de orçamento

### [2.2.0] - Planejado para Q1 2026

- [ ] **Integração Open Banking**
- [ ] **Processamento em tempo real**
- [ ] **Mobile app** React Native
- [ ] **Sincronização na nuvem**

### [3.0.0] - Visão de Longo Prazo

- [ ] **IA generativa** para insights financeiros
- [ ] **Marketplace de extensões**
- [ ] **Suporte multi-idioma**
- [ ] **Versão enterprise**

---

## 📊 **Estatísticas de Evolução**

### **Performance de Categorização**

```
v1.0: ~70% precisão (categorização manual)
v1.1: ~75% precisão (primeiros padrões)
v1.2: ~80% precisão (mais fontes)
v1.3: ~85% precisão (SQLite + ML)
v1.4: ~90% precisão (normalização)
v1.5: ~95% precisão (otimizações)
v2.0: 98.2% precisão (sistema completo) ⭐
```

### **Base de Conhecimento**

```
v1.0: ~50 categorias manuais
v1.1: ~100 categorias
v1.2: ~200 categorias
v1.3: ~400 categorias
v1.4: ~600 categorias
v1.5: ~772 categorias
v2.0: 584 categorias otimizadas (limpeza de duplicatas)
```

### **Funcionalidades por Versão**

```
v1.0: 1 fonte (PIX TXT)
v1.1: 2 fontes (+ Itaú XLS)
v1.2: 3 fontes (+ Latam XLS)
v1.3: Múltiplos formatos (CSV, XLSX)
v1.4: Detecção automática
v1.5: Scripts .bat
v2.0: Automação completa 🚀
```

---

## 🏆 **Marcos Importantes**

- **🎯 98.2% de precisão** alcançada em v2.0
- **🚀 Automação completa** via interface .bat
- **🧹 Otimização da base** com 24% de redução
- **📱 Interface amigável** com menus e emojis
- **🔧 Zero configuração** manual necessária

---

## 📝 **Notas de Desenvolvimento**

### **Metodologia**

- Desenvolvimento iterativo com feedback contínuo
- Testes com dados reais para validação
- Foco na experiência do usuário
- Documentação como prioridade

### **Tecnologias Utilizadas**

- **Python 3.13**: Core do sistema
- **SQLite**: Base de dados
- **pandas/openpyxl**: Manipulação de Excel
- **Windows Batch**: Automação
- **Regex**: Processamento de texto

### **Princípios de Design**

- **Simplicidade**: Interface intuitiva
- **Robustez**: Tratamento de erros
- **Performance**: Processamento rápido
- **Escalabilidade**: Suporte a crescimento
- **Privacidade**: Dados locais apenas

---

_Changelog mantido em setembro de 2025_
_Agente Financeiro IA - Evolução contínua rumo à automação perfeita_ 🚀
