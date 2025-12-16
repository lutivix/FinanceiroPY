# 🎨 Dashboard Financeiro v2.0 - Guia Visual

## 📁 Estrutura de Arquivos Criada

```
Financeiro/
├── dashboard_v2.bat                         # ⭐ Execute este arquivo!
│
└── backend/src/dashboard_v2/
    ├── __init__.py                          # Pacote Python
    ├── main.py                              # ⭐ App principal (porta 8052)
    ├── config.py                            # Configurações globais
    ├── README.md                            # Documentação técnica
    │
    ├── assets/
    │   └── custom_styles.py                 # CSS customizado (dark theme)
    │
    ├── components/
    │   └── sidebar.py                       # Sidebar com navegação
    │
    ├── pages/
    │   ├── dashboard.py                     # Página principal
    │   ├── analytics.py                     # Análises detalhadas
    │   └── transacoes.py                    # Lista de transações
    │
    └── utils/
        └── database.py                      # Funções de banco de dados
```

---

## 🎨 Paleta de Cores (Design Behance)

### **Backgrounds**
- `#0F0F23` - Fundo principal (azul escuro profundo)
- `#1A1A2E` - Fundo secundário (cards, sidebar)
- `#16213E` - Fundo dos cards individuais
- `#1F2A44` - Hover states

### **Textos**
- `#FFFFFF` - Texto principal (branco)
- `#A0AEC0` - Texto secundário (cinza claro)
- `#718096` - Texto terciário (cinza médio)

### **Valores Financeiros**
- `#06A77D` - Verde (economia/positivo) ✅
- `#D62246` - Vermelho (excesso/negativo) ❌
- `#FFD369` - Amarelo (alerta) ⚠️
- `#4ECDC4` - Turquesa (informação) ℹ️
- `#2E86AB` - Azul (destaque principal) ⭐

### **Gráficos**
Paleta harmoniosa de 6 cores:
1. `#4ECDC4` - Turquesa
2. `#95E1D3` - Verde água
3. `#FFD369` - Amarelo suave
4. `#F38181` - Rosa suave
5. `#AA96DA` - Roxo suave
6. `#2E86AB` - Azul corporativo

---

## 📐 Layout Visual

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  SIDEBAR (280px)                                               │
│  ┌────────────┐                                                │
│  │ 💰         │                                                │
│  │ FinancePro │                                                │
│  ├────────────┤                                                │
│  │ ▶ Dashboard│  ← Ativo (bordas azul)                       │
│  │   Analytics│                                                │
│  │   Transações│                                               │
│  │            │                                                │
│  │            │                                                │
│  │  [Filtro:  │                                                │
│  │   Mês ▼]   │                                                │
│  │            │                                                │
│  ├────────────┤                                                │
│  │ v2.0       │                                                │
│  └────────────┘                                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### **Página Dashboard** (`/`)
```
┌──────────────────────────────────────────────────────────────┐
│  Dashboard Financeiro                                        │
│  Visão geral das suas finanças                               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│  │ 💰       │    │ 📈       │    │ 🏷️       │             │
│  │ TOTAL    │    │ MÉDIA    │    │ CATEG.   │             │
│  │ GASTO    │    │ MENSAL   │    │          │             │
│  │          │    │          │    │          │             │
│  │ R$ 14.5k │    │ R$ 26k   │    │  89.9%   │             │
│  │ 2.486 tx │    │ 11 meses │    │ 251 pend │             │
│  └──────────┘    └──────────┘    └──────────┘             │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Evolução dos Últimos 12 Meses                         │ │
│  │                                                        │ │
│  │  [Gráfico de LINHA com área preenchida - 400px]       │ │
│  │                                                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─────────────────────┐  ┌─────────────────────┐          │
│  │ Top 5 Categorias    │  │ Top 5 Fontes        │          │
│  │                     │  │                     │          │
│  │ [Barras horizontais]│  │ [Barras horizontais]│          │
│  │                     │  │                     │          │
│  └─────────────────────┘  └─────────────────────┘          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### **Página Analytics** (`/analytics`)
```
┌──────────────────────────────────────────────────────────────┐
│  Analytics                                                   │
│  Análises detalhadas e comparações                           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Real vs Ideal por Categoria                           │ │
│  │                                                        │ │
│  │  [Barras horizontais - 2 cores: Real + Ideal]         │ │
│  │  [Diferença como texto no final]                      │ │
│  │                                                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─────────────────────┐  ┌─────────────────────┐          │
│  │ Distribuição        │  │ Acumulado Mensal    │          │
│  │ Temporal            │  │                     │          │
│  │                     │  │ [Linha acumulada]   │          │
│  │ [Heatmap ou barras] │  │                     │          │
│  └─────────────────────┘  └─────────────────────┘          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### **Página Transações** (`/transacoes`)
```
┌──────────────────────────────────────────────────────────────┐
│  Transações                                                  │
│  Gerencie e categorize suas transações                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  [Categoria ▼]  [Fonte ▼]  [Status ▼]                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Data       │ Descrição       │ Valor    │ Categoria   │ │
│  ├────────────┼─────────────────┼──────────┼─────────────┤ │
│  │ 15/12/2025 │ Mercado XYZ     │ R$ 250   │ Mercado     │ │
│  │ 14/12/2025 │ Posto ABC       │ R$ 180   │ Combustível │ │
│  │ ...        │ ...             │ ...      │ ...         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## ✨ Funcionalidades Implementadas

### **✅ Estrutura Base**
- [x] Organização em pastas (MVC style)
- [x] Configuração centralizada
- [x] CSS customizado (dark theme)
- [x] Sidebar com navegação

### **✅ Componentes**
- [x] 3 cards principais (grandes, com ícones)
- [x] Sidebar fixa (280px)
- [x] Filtro de mês global
- [x] Navegação entre páginas

### **✅ Páginas**
- [x] Dashboard (estrutura + placeholders)
- [x] Analytics (estrutura + placeholders)
- [x] Transações (estrutura + placeholders)

### **⏳ Pendente (Próxima Sessão)**
- [ ] Implementar gráficos (Plotly)
- [ ] Tabela de transações
- [ ] Categorização inline
- [ ] Callbacks interativos

---

## 🚀 Como Testar

### **1. Execute o dashboard**
```bash
# Windows
dashboard_v2.bat

# Ou manualmente
python backend/src/dashboard_v2/main.py
```

### **2. Acesse no navegador**
```
http://localhost:8052
```

### **3. Navegue pelas páginas**
- Clique em "Dashboard" → Página principal
- Clique em "Analytics" → Análises detalhadas
- Clique em "Transações" → Lista de transações

### **4. Teste o filtro de mês**
- Altere o dropdown na sidebar
- Todas as páginas devem reagir ao filtro

---

## 🎯 Próximos Passos Sugeridos

### **Prioridade Alta**
1. **Implementar gráficos** (usar funções do dashboard antigo como base)
2. **Testar navegação** e garantir que tudo carrega
3. **Ajustar tamanhos** de fontes para sua tela QHD

### **Prioridade Média**
4. **Tabela interativa** na página Transações
5. **Categorização em lote**
6. **Animações suaves** (já tem CSS base)

### **Prioridade Baixa**
7. **Export para Excel** dos filtros
8. **Dark/Light mode toggle**
9. **Notificações** (toasts)

---

## 📊 Comparação: v1 vs v2

| Aspecto | v1 (dashboard_dash_excel.py) | v2 (dashboard_v2/) |
|---------|------------------------------|-------------------|
| **Estrutura** | 1 arquivo monolítico (1105 linhas) | Múltiplos arquivos organizados |
| **Tema** | Bootstrap default | Dark theme profissional |
| **Navegação** | Rolagem vertical | Sidebar + páginas |
| **Cards** | 6 pequenos (2 cols) | 3 grandes (4 cols) |
| **Fontes** | 0.85-1.3rem | 0.75-2.5rem (maior) |
| **Gráficos** | 7 gráficos empilhados | 3-4 por página (organizados) |
| **Manutenção** | Difícil (tudo junto) | Fácil (modular) |
| **Porta** | 8051 | 8052 |

---

## 💡 Dicas de Uso

### **Para desenvolver novos gráficos:**
```python
# Edite: pages/dashboard.py ou pages/analytics.py
# Use: config.COLORS para cores consistentes
# Template base em: config.PLOTLY_TEMPLATE
```

### **Para adicionar nova página:**
```python
# 1. Crie: pages/nova_pagina.py
# 2. Import em: main.py
# 3. Adicione item na sidebar: components/sidebar.py
# 4. Adicione rota no callback: main.py (display_page)
```

### **Para ajustar cores:**
```python
# Edite: config.py → COLORS
# Todas as páginas/componentes usam essa configuração
```

---

**Criado em:** 16/12/2025  
**Versão:** 2.0.0  
**Status:** ✅ Estrutura base completa | ⏳ Gráficos pendentes
