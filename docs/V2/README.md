# 📊 Dashboard Financeiro V2 - Documentação

Bem-vindo à documentação completa do Dashboard Financeiro V2, uma aplicação moderna de gestão financeira pessoal com interface dark theme e análises avançadas.

## 📑 Índice de Documentação

### 🏗️ Arquitetura
- **[01_ARQUITETURA.md](01_ARQUITETURA.md)** - Estrutura MVC, diretórios, organização de código

### 🧩 Componentes
- **[02_COMPONENTES.md](02_COMPONENTES.md)** - Páginas, sidebar, cards, gráficos

### 💾 Database
- **[03_DATABASE.md](03_DATABASE.md)** - Queries, convenções de dados, exemplos

### 🎨 Estilização
- **[04_ESTILIZACAO.md](04_ESTILIZACAO.md)** - Dark theme, paleta de cores, fontes, CSS

### 🔧 Filtros e Callbacks
- **[05_FILTROS.md](05_FILTROS.md)** - Lógica de filtros, callbacks Dash

### 🐛 Troubleshooting
- **[06_TROUBLESHOOTING.md](06_TROUBLESHOOTING.md)** - Problemas comuns e soluções

## 🚀 Quick Start

### Instalação
```bash
cd backend/src/dashboard_v2
pip install -r requirements.txt
```

### Execução
```bash
# Windows
dashboard_v2.bat

# Linux/Mac
python main.py
```

### Acesso
- **URL**: http://localhost:8052
- **Porta**: 8052 (v1 usa 8051)

## 📊 Visão Geral

### Páginas

1. **Dashboard** (`/`)
   - 3 cards de métricas (Total, Cartões, Pix+Boletos)
   - Evolução últimos 12 meses
   - Top 5 Categorias e Fontes
   - Filtro por mês

2. **Analytics** (`/analytics`)
   - Real vs Ideal (comparativo mensal)
   - Distribuição Temporal (por dia da semana)
   - Evolução Acumulada (progressão mensal)

3. **Transações** (`/transacoes`)
   - 5 filtros simultâneos
   - Tabela com 100 transações
   - Subtotal dinâmico
   - Ordenação inteligente

### Tecnologias

- **Backend**: Python 3.13+
- **Framework**: Dash 3.2.0
- **UI**: Dash Bootstrap Components
- **Gráficos**: Plotly
- **Database**: SQLite3
- **Estilo**: CSS customizado (dark theme)

## 📈 Versões

- **v2.5.0** (16/12/2025) - Estrutura base, Dashboard principal
- **v2.6.0** (23/12/2025) - Analytics + Transações completas

## 🔗 Links Úteis

- [CHANGELOG.md](../../CHANGELOG.md) - Histórico de versões
- [COMMIT_MESSAGE.md](../../COMMIT_MESSAGE.md) - Mensagens de commit detalhadas
- [README.md do projeto](../../README.md) - Visão geral do projeto completo

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte [06_TROUBLESHOOTING.md](06_TROUBLESHOOTING.md)
2. Verifique issues conhecidos no CHANGELOG.md
3. Revise a arquitetura em [01_ARQUITETURA.md](01_ARQUITETURA.md)
