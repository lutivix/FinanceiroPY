# 📊 Dashboard Financeiro - Guia de Uso

> **Versão:** 2.5.0  
> **Script:** `backend/src/dashboard_dash.py`  
> **Framework:** Plotly Dash 3.2.0 + Bootstrap  
> **Última atualização:** 25/11/2025

---

## 🚀 Como Iniciar o Dashboard

### **1. Iniciar o servidor**

```bash
# Windows (PowerShell/CMD)
cd D:\Professional\Projetos\Github\Financeiro
py backend/src/dashboard_dash.py

# Linux/Mac
cd /caminho/para/Financeiro
python3 backend/src/dashboard_dash.py
```

### **2. Acessar o dashboard**

Após iniciar, você verá:
```
Dash está rodando em http://0.0.0.0:8050/

 * Serving Flask app 'dashboard_dash'
 * Debug mode: on
```

**Opções de acesso:**
- **Local:** http://localhost:8050
- **Rede local:** http://SEU_IP:8050 (ex: http://192.168.1.100:8050)
- **Outro dispositivo:** Qualquer aparelho na mesma rede Wi-Fi

### **3. Parar o servidor**

- Pressione `Ctrl+C` no terminal

---

## 📱 Interface do Dashboard

### **Cabeçalho - Resumo Geral**

```
┌─────────────────────────────────────────────────────────┐
│  💰 DASHBOARD FINANCEIRO                                │
│                                                         │
│  Total Real:     R$ 203.115,79                         │
│  Total Ideal:    R$ 293.370,00                         │
│  Diferença:      R$ 90.254,21 (30,8%)                  │
│  Período:        11 meses (Jan-Nov 2025)               │
└─────────────────────────────────────────────────────────┘
```

### **Filtros Interativos**

#### **🗓️ Filtro por Mês**
- **Dropdown** com todos os meses disponíveis
- **Padrão:** "Todos os meses"
- **Funcionalidade:** Filtra todas as visualizações simultaneamente

#### **🏷️ Filtro por Categoria**
- **Dropdown** com 33 categorias
- **Padrão:** "Todas as categorias"
- **Exemplos:** Mercado, Cartão, Casa, Stream, INVESTIMENTOS

#### **💳 Filtro por Fonte**
- **Dropdown** com 9 fontes de pagamento
- **Padrão:** "Todas as fontes"
- **Fontes disponíveis:**
  - PIX
  - Master Físico / Master Virtual / Master Recorrente
  - Visa Físico / Visa Virtual / Visa Recorrente / Visa Bia / Visa Mae

---

## 📊 Visualizações Disponíveis

### **1. Evolução Mensal (Real vs Ideal)**

**Tipo:** Gráfico de barras agrupadas  
**Eixo X:** Meses (Jan-Nov 2025)  
**Eixo Y:** Valor em R$  
**Cores:**
- 🔵 **Real:** Azul (#4472C4)
- 🟢 **Ideal:** Verde (#70AD47)
- 🔴 **Diferença:** Vermelho (#FF6B6B)

**Interpretação:**
- Barra azul > verde: Gastou mais que o ideal
- Barra azul < verde: Gastou menos que o ideal
- Barra vermelha: Magnitude da diferença

### **2. Real vs Ideal por Categoria**

**Tipo:** Gráfico de barras horizontal agrupadas (Top 15)  
**Ordenação:** Por valor real (maior → menor)  
**Sistema 3 barras:**
- Real (azul)
- Ideal (verde)
- Diferença (vermelho)

**Uso:**
- Identificar categorias com maior desvio
- Ver onde economizar
- Priorizar ajustes

### **3. Real vs Ideal por Fonte**

**Tipo:** Gráfico de barras horizontal agrupadas (9 fontes)  
**Orçamento mapeado:** R$ 26.670/mês por fonte  
**Sistema 3 barras:** Real / Ideal / Diferença

**Fontes com orçamento específico:**
- PIX: R$ 8.900
- Visa Bia: R$ 4.100
- Master Físico: R$ 3.850
- Visa Recorrente: R$ 3.114
- Visa Físico: R$ 2.050
- Master Recorrente: R$ 1.886
- Visa Mae: R$ 1.390
- Visa Virtual: R$ 880
- Master Virtual: R$ 500

### **4. Distribuição por Categoria**

**Tipo:** Gráfico de pizza  
**Top 10 categorias** (por valor)  
**Porcentagens:** Calculadas automaticamente  
**Hover:** Mostra valor e percentual

**Uso:**
- Ver proporção de gastos
- Identificar maiores categorias
- Visão rápida do orçamento

### **5. Distribuição por Fonte**

**Tipo:** Gráfico de pizza (9 fatias)  
**Todas as fontes** mostradas  
**Hover:** Valor e percentual

**Uso:**
- Ver qual cartão/fonte mais usa
- Balancear uso entre cartões
- Identificar dependência de fonte específica

### **6. Timeline de Transações**

**Tipo:** Scatter plot com linha  
**Eixo X:** Data da transação  
**Eixo Y:** Valor acumulado em R$  
**Linha:** Tendência cumulativa

**Uso:**
- Ver padrão de gastos ao longo do tempo
- Identificar picos de consumo
- Analisar sazonalidade

---

## 🎯 Casos de Uso Práticos

### **Caso 1: Analisar gastos de um mês específico**

1. Selecionar mês no dropdown "Mês"
2. Observar resumo atualizado no topo
3. Ver distribuição por categoria (gráfico pizza)
4. Identificar maiores gastos (barras horizontais)

**Exemplo:** "Novembro 2025"
- Total Real atualiza para o mês
- Gráficos mostram apenas dados de novembro
- Timeline mostra evolução dentro do mês

### **Caso 2: Entender onde está gastando em "Mercado"**

1. Filtrar por categoria "Mercado"
2. Ver evolução mensal (gráfico 1)
3. Verificar fontes usadas (gráfico pizza fonte)
4. Analisar timeline para ver frequência

**Descobertas possíveis:**
- Quanto gasta por mês em mercado
- Qual cartão mais usa para mercado
- Dias do mês com mais compras

### **Caso 3: Verificar uso de um cartão específico**

1. Filtrar por fonte (ex: "Master Físico")
2. Ver total gasto com esse cartão
3. Categorias principais desse cartão
4. Comparar com orçamento ideal (R$ 3.850)

**Ações possíveis:**
- Redistribuir gastos entre cartões
- Identificar se está próximo do limite
- Ver evolução de uso ao longo dos meses

### **Caso 4: Planejamento mensal**

1. Ver "Todos os meses"
2. Gráfico 1: Identificar meses com maior desvio
3. Gráfico 2: Categorias que mais estouram orçamento
4. Gráfico 3: Fontes mais utilizadas vs ideal

**Resultado:**
- Lista de categorias para economizar
- Meses com padrões anormais
- Ajuste de orçamentos realistas

---

## 🔄 Atualizar Dados do Dashboard

### **Opção 1: Reiniciar servidor** (recarrega dados)

```bash
# Parar: Ctrl+C
# Iniciar novamente
py backend/src/dashboard_dash.py
```

### **Opção 2: Sincronizar novas transações**

```bash
# 1. Atualizar no Dashboard Pluggy (manual)
#    - Acessar https://dashboard.pluggy.ai/
#    - Clicar em "Atualizar" nos items
#    - Aguardar 10-30s

# 2. Rodar sync para buscar novos dados
py backend/src/sync_openfinance.py
# Quando perguntar meses: 1 (para último mês)

# 3. Reiniciar dashboard para ver novos dados
py backend/src/dashboard_dash.py
```

### **Opção 3: Aguardar auto-sync** (Pluggy atualiza 1x/dia)

O Pluggy sincroniza automaticamente com os bancos a cada 24h. Basta rodar o sync para buscar os dados já atualizados.

---

## ⚙️ Configurações Técnicas

### **Porta e acesso rede**

**Arquivo:** `backend/src/dashboard_dash.py` (linha ~577)

```python
if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',  # ← Permite acesso rede local
        port=8050        # ← Porta padrão
    )
```

**Mudar porta:**
```python
port=8080  # ou qualquer porta livre
```

**Desabilitar acesso rede:**
```python
host='127.0.0.1'  # Apenas localhost
```

### **Firewall (Windows)**

Para acesso de outros dispositivos, libere a porta:

```bash
# Executar como Administrador
backend\src\abrir_firewall_dashboard.bat
```

Ou manualmente:
1. Painel de Controle → Firewall
2. Configurações Avançadas → Regras de Entrada
3. Nova Regra → Porta TCP 8050
4. Permitir conexão

### **Dados carregados**

**Origem:** `dados/db/financeiro.db`  
**Tabela:** `transacoes_openfinance`  
**Filtro aplicado:** Apenas transações DEBIT  
**Carregamento:** Na inicialização do servidor

---

## 🎨 Próximos Refinamentos Planejados

### **Curto Prazo**

1. ✅ ~~ORCAMENTO_IDEAL_FONTE~~ (Concluído v2.5.0)
2. **Botão "Atualizar Dados"**
   - Recarregar sem reiniciar servidor
   - Callback no Dash
3. **Export para Excel**
   - Botão para baixar dados filtrados
   - Formato: consolidado_pluggy_YYYYMM.xlsx

### **Médio Prazo**

4. **Modo escuro (dark theme)**
   - Toggle claro/escuro
   - Salvar preferência
5. **Autenticação básica**
   - Login/senha simples
   - dash-auth
6. **Gráficos adicionais**
   - Previsão de gastos
   - Comparativo ano anterior
   - Heatmap de consumo

### **Longo Prazo**

7. **Drill-down interativo**
   - Clicar em categoria → ver transações
   - Tabela com detalhes
8. **Alertas e notificações**
   - Orçamento estourado
   - Gastos incomuns
9. **Exportar relatório PDF**
   - Snapshot do dashboard
   - Análises automáticas

---

## 🐛 Troubleshooting

### **Problema: "Address already in use"**

**Causa:** Porta 8050 ocupada  
**Solução:**
```bash
# Windows
netstat -ano | findstr :8050
taskkill /PID <número> /F

# Linux/Mac
lsof -i :8050
kill -9 <PID>
```

### **Problema: Não carrega dados**

**Causa:** Banco de dados vazio ou caminho incorreto  
**Solução:**
1. Verificar se `dados/db/financeiro.db` existe
2. Rodar `sync_openfinance.py` para popular
3. Verificar logs no terminal

### **Problema: Gráficos não atualizam com filtros**

**Causa:** Cache do navegador  
**Solução:**
1. Ctrl+F5 (hard refresh)
2. Limpar cache do navegador
3. Tentar em janela anônima

### **Problema: Acesso negado na rede**

**Causa:** Firewall bloqueando  
**Solução:**
1. Executar `abrir_firewall_dashboard.bat` como Admin
2. Ou adicionar exceção manualmente
3. Verificar se host='0.0.0.0' no código

---

## 📚 Recursos Adicionais

**Documentação relacionada:**
- [README.md](README.md) - Visão geral integração
- [005_PROXIMOS_PASSOS.md](005_PROXIMOS_PASSOS.md) - Roadmap
- [GUIA_USUARIO.md](../GUIA_USUARIO.md) - Guia geral sistema

**Links externos:**
- [Plotly Dash](https://dash.plotly.com/)
- [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/)
- [Plotly Python](https://plotly.com/python/)

---

**Última atualização:** 25/11/2025 (v2.5.0)  
**Mantido por:** Luciano  
**Feedback:** Abrir issue no repositório
