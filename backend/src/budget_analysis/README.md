# 📊 Budget Analysis - Análise de Orçamento Semanal

Módulo para análise de padrões de gastos e geração de orçamento semanal por categoria, fonte e pessoa.

## 🎯 Objetivo

Identificar transações recorrentes e calcular meta semanal de gastos baseado em:
- **Transações recorrentes**: Contas fixas que aparecem todo mês
- **Médias semanais**: Categorias variáveis (mercado, combustível, etc.)
- **Distribuição por pessoa**: Master (Usuário), Visa (Bia/Mãe)

## 📁 Estrutura

```
budget_analysis/
├── __init__.py                    # Exports do módulo
├── models.py                      # Modelos de dados
├── person_mapper.py               # Mapeamento pessoa-cartão
├── recurring_analyzer.py          # Identificador de recorrências
├── weekly_budget_calculator.py    # Calculador de orçamento semanal
└── README.md                      # Esta documentação
```

## 🔧 Componentes

### 1. **Models** (`models.py`)

Define estruturas de dados:

- **`WeekOfMonth`**: Enum para semanas do mês (1-7, 8-14, 15-21, 22-28, 29-31)
- **`PersonCardMapping`**: Mapeamento pessoa → cartões
- **`RecurringTransaction`**: Transação recorrente identificada
- **`WeeklyBudget`**: Orçamento semanal por categoria/pessoa/fonte
- **`WeeklyBudgetSummary`**: Resumo consolidado por semana

### 2. **PersonMapper** (`person_mapper.py`)

Mapeia transações para pessoas baseado no cartão:

- **Usuário**: Master Físico, Master Virtual, Master Recorrente
- **Bia**: Visa Físico, Visa Virtual, Visa Bia (adicional)
- **Mãe**: Visa Mãe (adicional)

```python
from budget_analysis import PersonMapper

mapper = PersonMapper()
person = mapper.get_person(TransactionSource.ITAU_MASTER_FISICO)  # "Usuário"
```

### 3. **RecurringAnalyzer** (`recurring_analyzer.py`)

Identifica transações recorrentes através de análise histórica.

**Critérios:**
- Mesma categoria + descrição normalizada
- Mínimo de 6 meses de ocorrência (≥50% de confiança)
- Ignora valores (foca em padrão)

**Exemplo:**
```python
from budget_analysis import RecurringAnalyzer

analyzer = RecurringAnalyzer(min_months=3)
recurring = analyzer.analyze(transactions, months_to_analyze=12)

# Relatório
summary = analyzer.get_summary_report(recurring)
print(f"Total recorrentes: {summary['total']}")
```

### 4. **WeeklyBudgetCalculator** (`weekly_budget_calculator.py`)

Calcula orçamento semanal combinando:
- Transações recorrentes (contas fixas)
- Médias semanais (categorias variáveis)

**Categorias Variáveis:**
- Mercado, Combustível, Padaria, Lanche, Lazer, Compras

**Exemplo:**
```python
from budget_analysis import WeeklyBudgetCalculator

calculator = WeeklyBudgetCalculator()
budgets = calculator.calculate(recurring_transactions, historical_transactions)

# Exporta resumo
summary = calculator.export_to_dict(budgets)
```

## 🚀 Uso

### Script Principal

Execute a análise completa:

```bash
# Análise padrão (12 meses, min 6 recorrências)
python backend/src/analisar_padroes_semanais.py

# Customizado
python backend/src/analisar_padroes_semanais.py \
    --months-history 12 \
    --min-recurrence 6 \
    --output resultado.json
```

**Parâmetros:**
- `--months-history`: Meses de histórico (padrão: 12)
- `--min-recurrence`: Mínimo de meses para recorrência (padrão: 6)
- `--output`: Arquivo JSON de saída (padrão: weekly_budget.json, salvo em dados/)

### Output

O script gera:

1. **Console**: Resumo visual por semana
2. **JSON**: Arquivo completo com detalhes
3. **Log**: `budget_analysis.log` com diagnóstico

**Estrutura do JSON:**

```json
{
  "generated_at": "2026-01-13",
  "recurring_transactions": {
    "total": 45,
    "items": [
      {
        "description": "NETFLIX",
        "category": "Stream",
        "person": "Usuário",
        "source": "Master Virtual",
        "avg_amount": 55.00,
        "typical_day": 5,
        "week": 1,
        "occurrences": 12,
        "confidence": 1.0
      }
    ]
  },
  "weekly_budgets": {
    "total_budgets": 87,
    "monthly_total": 12450.50,
    "by_week": [
      {
        "week": 1,
        "week_days": "1-7",
        "total_expected": 2340.00,
        "by_person": {
          "Usuário": 1200.00,
          "Bia": 840.00,
          "Mãe": 300.00
        },
        "by_category": {
          "Stream": 77.00,
          "Casa": 450.00,
          "Mercado": 600.00
        }
      }
    ]
  }
}
```

## 📊 Exemplo de Saída

```
================================================================================
📅 ORÇAMENTO SEMANAL - RESUMO
================================================================================

🗓️  SEMANA 1 (Dias 1-7)
   Total Esperado: R$ 2,340.00

   Por Pessoa:
      Usuário: R$ 1,200.00
      Bia: R$ 840.00
      Mãe: R$ 300.00

   Por Categoria (Top 5):
      Mercado: R$ 600.00
      Casa: R$ 450.00
      Combustível: R$ 280.00
      Stream: R$ 77.00
      Farmácia: R$ 85.00

   Contas Fixas:
      Netflix, Spotify: R$ 77.00 (Usuário)
      Água: R$ 45.00 (Usuário)
      Remédios: R$ 85.00 (Mãe)

================================================================================
💵 TOTAL MENSAL ESTIMADO: R$ 12,450.50
================================================================================
```

## 🔬 Metodologia

### Identificação de Recorrências

1. **Normalização**: Remove números e caracteres especiais da descrição
2. **Agrupamento**: Agrupa por categoria + descrição normalizada + fonte
3. **Contagem**: Conta em quantos meses apareceu
4. **Confiança**: `(meses com ocorrência) / (meses analisados)`
5. **Filtro**: Apenas >= 3 meses

### Cálculo de Valores

- **Recorrentes**: Média arredondada para **menos** (evita surplus enganoso)
- **Variáveis**: Média semanal dos últimos 12 meses
- **Dia típico**: Mediana dos dias de ocorrência

### Semanas do Mês

```
Semana 1: Dias  1-7
Semana 2: Dias  8-14
Semana 3: Dias 15-21
Semana 4: Dias 22-28
Semana 5: Dias 29-31 (dias extras)
```

## 🎯 Próximos Passos

- [ ] Persistir budgets no banco de dados
- [ ] Integrar com Dashboard V2
- [ ] Alertas quando ultrapassar meta semanal
- [ ] Sazonalidade (ajustar para dezembro, etc.)
- [ ] Budgets adaptativos (ajustam com o tempo)

## 📝 Notas Técnicas

- **Arredondamento**: Sempre para menos para evitar surpresas
- **Tolerância**: ±2 dias para agrupar recorrências
- **Mínimo**: 6 meses (≥50% confiança) para focar em recorrências reais
- **Ignore**: Categoria "A definir" não entra na análise
- **Mapeamentos especiais**: Crossfit dividido entre Usuário e Bia

## 🐛 Troubleshooting

**Poucas recorrências identificadas?**
- Reduza `--min-recurrence` para 4 ou 5
- Verifique se as descrições estão normalizadas
- Confira se as categorias estão preenchidas

**Valores muito altos/baixos?**
- Verifique o período de análise (`--months-history`)
- Confirme se há outliers no histórico
- Ajuste manualmente no JSON se necessário

**Pessoa incorreta?**
- Revise `DEFAULT_PERSON_MAPPINGS` em `models.py`
- Adicione mapeamento customizado se necessário

## 📚 Referências

- [Código Principal](analisar_padroes_semanais.py)
- [Modelos de Dados](models.py)
- [Dashboard V2](../dashboard_v2/)
