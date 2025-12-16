# Commit v2.5.0

Luciano - feat(v2.5): Dashboard V2 dark theme + estrutura MVC + gráficos interativos

## Resumo

🎨 **NOVO DASHBOARD V2 (DARK THEME)!** Cria interface moderna inspirada em Behance com estrutura MVC organizada, tema escuro profissional, e gráficos interativos funcionais carregando dados reais do SQLite.

## Features

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
