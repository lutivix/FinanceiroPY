# 📊 Dashboard Dual: Excel/TXT vs Open Finance

**Data:** 09/12/2025  
**Versão:** 2.5.1

---

## 🎯 **Objetivo**

Criar duas versões do dashboard para suportar:
1. **Extratos Excel/TXT** (uso diário, gratuito)
2. **Open Finance** (uso futuro, quando/se contratar agregador)

---

## 📁 **Estrutura de Arquivos**

```
backend/src/
├── dashboard_dash.py           # Dashboard Open Finance (Pluggy)
├── dashboard_dash.bat          # Launcher Open Finance
├── dashboard_dash_excel.py     # Dashboard Excel/TXT (NOVO) ⭐
└── dashboard_dash_excel.bat    # Launcher Excel/TXT (NOVO) ⭐
```

---

## 🔄 **Diferenças Principais**

| Aspecto | Dashboard Excel/TXT | Dashboard Open Finance |
|---------|---------------------|------------------------|
| **Tabela** | `lancamentos` | `transacoes_openfinance` |
| **Porta** | 8051 | 8050 |
| **Colunas** | Data, Descricao, Valor, Categoria, Fonte, MesComp | data, descricao, valor, categoria, fonte, mes_comp + metadados |
| **Origem** | Extratos processados (Excel/TXT) | API Pluggy |
| **Custo** | R$ 0 (gratuito) | R$ 100-500/mês (após trial) |
| **Status** | ✅ Operacional | ⚠️ Requer trial ativo |

---

## 🗂️ **Mapeamento de Colunas**

### **Tabela `lancamentos` (Excel/TXT)**
```sql
CREATE TABLE lancamentos (
    Data DATE,              -- Data da transação
    Descricao TEXT,         -- Descrição
    Fonte TEXT,             -- Fonte (Visa Físico, PIX, etc)
    Valor REAL,             -- Valor (negativo = despesa)
    Categoria TEXT,         -- Categoria
    MesComp TEXT,           -- Mês de Competência
    id TEXT,                -- ID único
    raw_data TEXT,          -- Dados brutos
    created_at TEXT,        -- Data criação
    updated_at TEXT         -- Data atualização
)
```

### **Tabela `transacoes_openfinance` (Pluggy)**
```sql
CREATE TABLE transacoes_openfinance (
    id INTEGER PRIMARY KEY,
    provider_id TEXT UNIQUE,
    account_id TEXT,
    data DATE,              -- Data da transação
    descricao TEXT,         -- Descrição
    valor REAL,             -- Valor (negativo = despesa)
    categoria TEXT,         -- Categoria
    categoria_banco TEXT,   -- Categoria do banco
    fonte TEXT,             -- Fonte
    mes_comp TEXT,          -- Mês de Competência
    tipo_transacao TEXT,    -- DEBIT/CREDIT
    origem_banco TEXT,      -- Itaú/Mercado Pago
    parcela_numero INT,     -- Número da parcela
    parcela_total INT,      -- Total de parcelas
    cartao_final TEXT,      -- Final do cartão (4 dígitos)
    ... (+ outros metadados)
)
```

---

## 🚀 **Como Usar**

### **1. Dashboard Excel/TXT (Recomendado)**

```bash
# Opção 1: Arquivo .bat
cd backend/src
dashboard_dash_excel.bat

# Opção 2: Python direto
python dashboard_dash_excel.py
```

**Acesso:** http://localhost:8051

### **2. Dashboard Open Finance (Futuro)**

```bash
# Opção 1: Arquivo .bat
cd backend/src
dashboard_dash.bat

# Opção 2: Python direto
python dashboard_dash.py
```

**Acesso:** http://localhost:8050

---

## 🔧 **Adaptações Realizadas**

### **1. Queries SQL**
```python
# ANTES (Open Finance)
SELECT data, descricao, valor, categoria, fonte, mes_comp
FROM transacoes_openfinance
WHERE categoria NOT IN ('INVESTIMENTOS', 'SALÁRIO')
  AND tipo_transacao = 'DEBIT'

# DEPOIS (Excel/TXT)
SELECT 
    Data as data,
    Descricao as descricao,
    Valor as valor,
    Categoria as categoria,
    Fonte as fonte,
    MesComp as mes_comp
FROM lancamentos
WHERE Categoria NOT IN ('INVESTIMENTOS', 'SALÁRIO')
  AND Valor < 0
```

### **2. Função de Atualização**
```python
# ANTES
UPDATE transacoes_openfinance 
SET categoria = ? 
WHERE rowid = ?

# DEPOIS
UPDATE lancamentos 
SET Categoria = ? 
WHERE rowid = ?
```

### **3. Exclusão de Transferências Internas**
Ambos filtram pagamentos de faturas:
```sql
AND Descricao NOT LIKE '%ITAU VISA%'
AND Descricao NOT LIKE '%PGTO FATURA%'
AND Descricao NOT LIKE '%PAGAMENTO CARTAO%'
AND Descricao NOT LIKE '%PAGAMENTO EFETUADO%'
```

---

## ⚙️ **Funcionalidades Idênticas**

Ambos dashboards possuem:

✅ **Filtros Interativos**
- Mês (individual ou todos)
- Categoria (específica ou todas)
- Fonte (específica ou todas)

✅ **6 Cards Principais**
- 💰 Total
- 📅 Média 12M
- ✅ Categorizado %
- ⚠️ Pendentes
- 📊 Transações
- 📆 Meses

✅ **Cards Condicionais** (quando filtrar mês)
- 🎯 Ideal do Mês
- 🔴/🟢 Diferença (Excedeu/Economizou)

✅ **6 Gráficos Interativos**
1. 💰 Real vs Ideal por Categoria (3 barras)
2. 📊 Evolução Mensal / Real vs Ideal por Fonte
3. 💳 Gastos por Fonte (Pizza)
4. 🏷️ Gastos por Categoria (Pizza)
5. 📅 Distribuição de Transações
6. 📈 Acumulado Anual

✅ **Categorização Inline**
- Tabela de pendentes
- Dropdown de categorias
- Botão salvar
- Atualização real-time

---

## 📊 **Orçamentos Configurados**

Ambos usam os mesmos orçamentos ideais:

### **Por Categoria**
```python
ORCAMENTO_IDEAL = {
    'Mercado': 4200.00,
    'Casa': 3400.00,
    'LF': 2400.00,
    'Nita': 2100.00,
    # ... total: ~R$ 26.670
}
```

### **Por Fonte**
```python
ORCAMENTO_IDEAL_FONTE = {
    'PIX': 8900.00,
    'Visa Bia': 4100.00,
    'Master Físico': 3850.00,
    # ... total: R$ 26.670
}
```

---

## 🎨 **Design e Layout**

Ambos compartilham:
- **Framework:** Plotly Dash 3.2.0
- **Tema:** Bootstrap (dbc.themes.BOOTSTRAP)
- **Layout:** 70/30 (gráfico principal vs secundário)
- **Cores:** Padronizadas (Laranja=Real, Azul=Ideal, Verde/Vermelho=Diferença)
- **Responsivo:** Sim
- **Altura gráficos:** 450-500px

---

## 🔄 **Workflow Recomendado**

```
1. Baixar extratos (Excel/TXT) ─────┐
2. Rodar agente_financeiro.py       │
3. Dados salvos em lancamentos      │  GRÁTIS ✅
4. Abrir dashboard_dash_excel.py ───┘
   → http://localhost:8051

                vs

1. Conectar Pluggy (trial ativo) ───┐
2. Rodar sync_openfinance.py        │
3. Dados em transacoes_openfinance  │  PAGO 💰
4. Abrir dashboard_dash.py ─────────┘
   → http://localhost:8050
```

---

## 📝 **Notas Importantes**

1. **Porta diferente:** Evita conflitos (8051 vs 8050)
2. **Dados independentes:** Cada dashboard lê sua própria tabela
3. **Compatível:** Mesma lógica, apenas fontes de dados diferentes
4. **Manutenção:** Alterações futuras devem ser replicadas em ambos

---

## 🚦 **Status Atual**

- ✅ **dashboard_dash_excel.py** → Criado e funcional
- ✅ **dashboard_dash.py** → Mantido para uso futuro
- ✅ **Documentação** → Atualizada
- ⚠️ **Teste** → Pendente (executar dashboard_dash_excel.bat)

---

## 🔮 **Próximos Passos**

1. **Testar dashboard Excel/TXT:**
   ```bash
   cd backend/src
   dashboard_dash_excel.bat
   ```

2. **Verificar dados carregados:**
   - Deve mostrar transações da tabela `lancamentos`
   - Verificar se filtros funcionam
   - Testar categorização inline

3. **Ajustes finos (se necessário):**
   - Mapeamento de fontes
   - Formato de datas
   - Exclusões adicionais

---

## 📞 **Suporte**

- **Dashboard não carrega?** → Verifique se tem dados em `lancamentos`
- **Erro de porta?** → Porta 8051 já em uso (mude no código)
- **Gráficos vazios?** → Execute `agente_financeiro.py` primeiro
- **Categorização não salva?** → Verifique permissões do banco de dados

---

**✅ Dashboard dual pronto para uso!**
