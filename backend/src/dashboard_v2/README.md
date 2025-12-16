# Dashboard Financeiro v2.0 - Estrutura

```
dashboard_v2/
├── __init__.py                    # Pacote principal
├── main.py                        # App Dash (executa aqui)
├── config.py                      # Configurações (cores, fontes, orçamentos)
│
├── assets/                        # Arquivos estáticos
│   └── custom_styles.py          # CSS customizado
│
├── components/                    # Componentes reutilizáveis
│   └── sidebar.py                # Sidebar com navegação
│
├── pages/                         # Páginas do dashboard
│   ├── dashboard.py              # Página principal (overview)
│   ├── analytics.py              # Análises detalhadas
│   └── transacoes.py             # Lista/categorização
│
└── utils/                         # Utilitários
    └── database.py               # Funções de banco de dados
```

## 🚀 Como Executar

### Windows
```bash
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

## 🔄 Próximos Passos

- [ ] Implementar callbacks dos gráficos (dashboard.py)
- [ ] Implementar callbacks dos gráficos (analytics.py)
- [ ] Implementar tabela de transações (transacoes.py)
- [ ] Adicionar testes unitários
- [ ] Documentar componentes individuais
