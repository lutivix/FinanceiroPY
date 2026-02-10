# Dashboard Financeiro v2.8.0 - Estrutura

**Versão:** 2.8.0  
**Data:** Janeiro 2026  
**Status:** ✅ Produção

## 🎯 Correções Críticas v2.8.0

Esta versão corrige problemas importantes identificados:

✅ **Março 2025** - Corrigido encoding Windows (pd.to_datetime → mapeamento manual)  
✅ **Ideal Mensal** - Fixado em R$ 26.670 (não varia com filtros)  
✅ **Batch Categorization** - Import SPACING corrigido, controles visíveis  
✅ **Dezembro Master** - 57 transações preservadas (mes_comp na deduplicação)

```
dashboard_v2/
├── __init__.py                    # Pacote principal (v2.8.0)
├── main.py                        # App Dash (executa aqui)
├── config.py                      # Configurações (cores, fontes, orçamentos (IDEAL_MENSAL_TOTAL))
│
├── assets/                        # Arquivos estáticos
│   └── custom_styles.py          # CSS customizado
│
├── components/                    # Componentes reutilizáveis
│   └── sidebar.py                # Sidebar com navegação
│
├── pages/                         # Páginas do dashboard
│   ├── dashboard.py              # Página principal (overview + Ideal Mensal fixo)
│   ├── analytics.py              # Análises detalhadas
│   └── transacoes.py             # Lista/categorização (batch com SPACING)
│
└── utils/                         # Utilitários
    ├── database.py               # Funções de banco de dados
    └── graficos.py               # Geração de gráficos (converter_mes_para_data)
```

## � **IMPORTANTE: Use `py` no Windows**

**⚡ No Windows, sempre use o comando `py`:**

```bash
# ✅ CORRETO - Funciona sempre
py backend/src/dashboard_v2/main.py

# ❌ ERRADO - Pode falhar no Windows
python backend/src/dashboard_v2/main.py
```

**Por quê?** O Python Launcher (`py`) gerencia corretamente múltiplas versões do Python no Windows.

---

## 🚀 Como Executar

### Windows (Recomendado)
```bash
# Opção 1: Script interativo (recomendado)
./agente_financeiro_completo.sh
# Escolha opção [7] para iniciar o Dashboard

# Opção 2: Direto via comando
py backend/src/dashboard_v2/main.py

# Opção 3: Via batch (legado)
dashboard_v2.bat
```

### Linux/Mac
```bash
python backend/src/dashboard_v2/main.py
```

## 🌐 Acesso

- **URL:** http://localhost:8052
- **Porta:** 8052 (não conflita com v1 na 8051)

## 🎨 Design

- **Tema:** Dark Professional (baseado em Behance)
- **Paleta:** Azul escuro + Verde/Vermelho para valores
- **Tipografia:** Inter (system fonts fallback)
- **Layout:** Sidebar fixa + conteúdo responsivo

## 📊 Páginas

1. **Dashboard** (`/`)
   - 3 cards principais (Total, Média, Categorização)
   - Gráfico hero: Evolução 12 meses
   - Top 5 Categorias e Fontes

2. **Analytics** (`/analytics`)
   - Real vs Ideal (barras horizontais)
   - Distribuição temporal
   - Acumulado mensal

3. **Transações** (`/transacoes`)
   - Tabela interativa
   - Filtros por categoria, fonte, status
   - Categorização em lote

## ⚙️ Configuração

Todas as configurações centralizadas em `config.py`:
- Cores (COLORS)
- Fontes (FONTS)
- Espaçamentos (SPACING)
- Orçamentos (ORCAMENTO_IDEAL, ORCAMENTO_IDEAL_FONTE)

## � Documentação Completa

Para documentação detalhada, arquitetura, guias de desenvolvimento e exemplos:

👉 **[docs/V2/](../../../docs/V2/)** - Documentação completa do Dashboard V2

- [Arquitetura](../../../docs/V2/01_ARQUITETURA.md) - Estrutura MVC, diretórios, fluxo de dados
- [Componentes](../../../docs/V2/02_COMPONENTES.md) - Páginas, sidebar, gráficos
- [Database](../../../docs/V2/03_DATABASE.md) - Queries, convenções, exemplos
- [Estilização](../../../docs/V2/04_ESTILIZACAO.md) - Dark theme, cores, fontes
- [Filtros](../../../docs/V2/05_FILTROS.md) - Callbacks, lógica de filtros
- [Troubleshooting](../../../docs/V2/06_TROUBLESHOOTING.md) - Problemas comuns e soluções

## ✅ Status

- [x] Estrutura MVC organizada
- [x] Dashboard principal (3 gráficos + filtro mês)
- [x] Página Analytics (3 gráficos analíticos)
- [x] Página Transações (5 filtros + tabela + subtotal)
- [x] Dark theme completo
- [x] Callbacks interativos funcionando
- [ ] Paginação na tabela
- [ ] Categorização inline
- [ ] Testes unitários
- [ ] Export CSV
