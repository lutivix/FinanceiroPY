# 🔗 Integração

Documentação sobre integrações externas: Open Finance (Pluggy), APIs bancárias e serviços de terceiros.

---

## 🎉 **CONQUISTAS v2.5.0** (25/11/2025)

### ✅ **FASE 2 CONCLUÍDA: DASHBOARD INTERATIVO PLOTLY DASH**

**🎯 Duas versões disponíveis:**

#### **1. Dashboard Excel/TXT (Recomendado)** ⭐
- **Script:** `backend/src/dashboard_dash_excel.py`
- **Porta:** 8051 (http://localhost:8051)
- **Dados:** Tabela `lancamentos` (extratos Excel/TXT processados)
- **Gratuito:** Funciona indefinidamente
- **Execução:** `dashboard_dash_excel.bat`

#### **2. Dashboard Open Finance (Futuro)**
- **Script:** `backend/src/dashboard_dash.py`
- **Porta:** 8050 (http://localhost:8050)
- **Dados:** Tabela `transacoes_openfinance` (API Pluggy)
- **Status:** ⚠️ Requer trial/plano ativo do Pluggy
- **Execução:** `dashboard_dash.bat`

**Recursos compartilhados:**
- **Framework:** Plotly Dash 3.2.0 + Bootstrap Components
- **Filtros interativos:** Mês, Categoria, Fonte (real-time)
- **6 gráficos dinâmicos** com sistema de 3 barras (Real/Ideal/Diferença)
- **Categorização inline** para transações pendentes
- **ORCAMENTO_IDEAL_FONTE:** R$ 26.670/mês mapeado por fonte
- **Acesso rede local:** host=0.0.0.0

### ✅ **FASE 1 CONCLUÍDA: IMPORTAÇÃO FLEXÍVEL**

- **2.131 transações** importadas para banco de dados (atualizado 25/11)
- **Correção mapeamento fontes:** PERSON=Master, LATAM=Visa
- **Ciclo 19-18** implementado e validado (MesComp correto)
- **Sync flexível:** prompt de meses retroativos (padrão: 1 mês)
- **Auto-sync:** Pluggy atualiza dados automaticamente a cada 24h
- **Script:** `backend/src/sync_openfinance.py` (com função refresh preparada)
- **Database:** `dados/db/financeiro.db` → tabela `transacoes_openfinance`

---

## 📂 Documentos

| Arquivo                                                      | Descrição                               | Status         |
| ------------------------------------------------------------ | --------------------------------------- | -------------- |
| [001_INTEGRACAO_PLUGGY.md](001_INTEGRACAO_PLUGGY.md)         | Integração Open Finance via Pluggy      | ✅ Completo    |
| [002_CHECKLIST_PLUGGY.md](002_CHECKLIST_PLUGGY.md)           | Checklist de implementação              | ✅ Concluído   |
| [003_ARQUITETURA_PLUGGY.md](003_ARQUITETURA_PLUGGY.md)       | Decisões técnicas REST vs SDK           | ✅ Documentado |
| [004_SEGURANCA_OPENFINANCE.md](004_SEGURANCA_OPENFINANCE.md) | Segurança e compliance                  | ✅ Documentado |
| [005_PROXIMOS_PASSOS.md](005_PROXIMOS_PASSOS.md)             | **Roadmap e próximas features**         | 🎯 **LEIA!**   |
| [006_SEGURANCA_CREDENCIAIS.md](006_SEGURANCA_CREDENCIAIS.md) | **🔒 Migração para .env (Urgente)**     | ⚠️ **AÇÃO!**   |
| [007_DASHBOARD_GUIA.md](007_DASHBOARD_GUIA.md)               | **📊 Guia completo do Dashboard**       | 🆕 **NOVO!**   |
| [008_RESUMO_CORRECOES.md](008_RESUMO_CORRECOES.md)           | **📋 Resumo de correções (02/12)**      | ✅ **INFO**    |
| [009_DASHBOARD_INTERATIVO.md](009_DASHBOARD_INTERATIVO.md)   | **📊 Dashboard Plotly (v2.3.0)**        | ✅ **PROD**    |
| [010_DASHBOARD_DUAL.md](010_DASHBOARD_DUAL.md)               | **📊 Dashboard Dual (Excel vs OF)**     | 🆕 **NOVO!**   |

---

## 📂 Documentos

### **1. Open Finance (Pluggy) - ✅ PRODUÇÃO**

- **Status:** ✅ Funcional e produzindo Excel
- **Contas conectadas:**
  - **Itaú (REAL):** 3 contas (2 cartões + 1 corrente) ✅
    - LATAM PASS VISA PLATINUM (6259) - R$ 15.159,75
    - PERSON MULTIPLO BLACK (4059) - R$ 18.272,58
    - Conta Corrente (00002663-4) - R$ 129,06
  - Mercado Pago (real, pouca atividade)
  - Sandbox (teste)
- **Dados acessados:**
  - ✅ Saldo da conta
  - ✅ Transações com categoria bancária
  - ✅ Dados de identidade
  - ✅ Metadata de parcelas (installments)
  - ✅ Conversão de moedas (amountInAccountCurrency)
  - ✅ Card numbers para mapeamento de fontes
- **Processamento:**
  - ✅ Dashboard interativo Plotly Dash (`dashboard_dash.py`)
  - ✅ Sincronização flexível banco de dados (`sync_openfinance.py`)
  - ✅ Script Excel mensal (`gerar_excel_pluggy.py`)
  - ✅ 2.318 transações em banco (11 meses)
  - ✅ Categorização automática 94,7%
  - ✅ Mapeamento de fontes (PIX, Visa, Master)
- **Ver:** [001_INTEGRACAO_PLUGGY.md](001_INTEGRACAO_PLUGGY.md)

### **2. Outras Instituições (Futuro)**

- **Status:** 📋 Disponível para conectar
- **Método:** Open Finance via Pluggy Dashboard
- **Próximos passos:**
  - Conectar outras contas bancárias se necessário
  - Cartões de outros bancos
  - Contas de investimento

---

## 🛠️ Stack Técnica

### **Open Finance**

- **Agregador:** Pluggy
- **Protocolo:** OAuth2
- **Implementação:** REST API (requests)
- **Autenticação:** X-API-KEY header
- **Base URL:** `https://api.pluggy.ai`

### **Limitações Plano Free/Trial**

⚠️ **Atualizações:**
- ❌ **Refresh via API bloqueado** (403 Forbidden)
  - Endpoint `POST /items/{id}/refresh` não disponível no plano Free
  - Necessário atualizar manualmente via Dashboard Pluggy
- ✅ **Auto-sync automático** pelo Pluggy
  - Dados atualizados automaticamente a cada 24h
  - Produção: 24h/12h/8h dependendo do plano contratado
- ✅ **Função refresh implementada** no código
  - Preparada para uso futuro em produção
  - Desabilitada por padrão (forcar_atualizacao=False)

💡 **Workflow recomendado:**
1. Clicar "Atualizar" no Dashboard Pluggy (quando necessário)
2. Aguardar 10-30s (sincronização com banco)
3. Rodar `sync_openfinance.py` para buscar novos dados
4. Alternativamente: aguardar auto-sync diário do Pluggy

### **Arquivos Relevantes**

```
backend/src/
├── [Scripts de Produção] ✅
│   ├── dashboard_dash.py              # ✅ Dashboard interativo Plotly Dash
│   ├── sync_openfinance.py            # ✅ Sincronização (prompt dias retroativos)
│   ├── gerar_excel_pluggy.py          # ✅ Geração Excel mensal
│   ├── agente_financeiro.py           # ✅ Agente principal
│   └── atualiza_dicionario.py         # ✅ Atualização dicionário
│
├── [Utilitários]
│   ├── abrir_firewall_dashboard.bat   # Script auxiliar firewall
│   └── config.ini                     # Credenciais (NÃO versionado)
│
└── [Legado/Teste]
    ├── gerar_dashboard.py             # Dashboard HTML estático (referência)
    └── integrations/                  # SDK antigo (não usar)
```

---

## 🔐 Segurança

### **Credenciais**

- **Localização:** `config/config.ini` (não versionado)
- **Seção:** `[PLUGGY]`
- **Campos:** `CLIENT_ID`, `CLIENT_SECRET`
- **Proteção:** `.gitignore` + `config.example.ini` template

### **Próximos Passos de Segurança**

- [ ] Migrar para `.env` na raiz
- [ ] Instalar `python-decouple`
- [ ] Atualizar scripts para usar env vars
- [ ] Documentar rotação de chaves

**Ver:** [004_SEGURANCA_OPENFINANCE.md](004_SEGURANCA_OPENFINANCE.md) (a criar)

---

## 📊 Performance

### **Open Finance (Pluggy)**

- ⚡ **Latência:** ~500ms por requisição
- 🔄 **Rate limit:** Não documentado oficialmente
- ⏱️ **Token expiry:** 2 horas (requer refresh)
- 📦 **Payload:** JSON completo (~2-10KB por transação)

---

## 🐛 Problemas Conhecidos

| Problema       | Descrição                           | Status           | Solução           |
| -------------- | ----------------------------------- | ---------------- | ----------------- |
| SDK Bug        | `pluggy-sdk` envia header errado    | ❌ Não corrigido | ✅ Usar REST API  |
| Trial Expirado | Não pode conectar contas via código | ⚠️ Limitação     | ✅ Usar Dashboard |
| Widget CDN     | PluggyConnect não carrega           | ❌ Abandonado    | ✅ Usar Dashboard |

**Ver detalhes:** [../Integracao_PROXIMO_CHAT.md](../Integracao_PROXIMO_CHAT.md)

---

## 🎯 Roadmap

### ✅ **Fase 1: Importação Flexível** (CONCLUÍDA - v2.4.0)

- ✅ Script `sync_openfinance.py` (com prompt de dias)
- ✅ Ciclo 19-18 implementado
- ✅ 2.318 transações importadas
- ✅ Categorização automática 94,7%
- ✅ Banco de dados `transacoes_openfinance`

### ✅ **Fase 2: Dashboard Interativo** (CONCLUÍDA - v2.4.0)

- ✅ Framework Plotly Dash + Bootstrap
- ✅ 6 gráficos dinâmicos
- ✅ Sistema 3 barras (Real/Ideal/Diferença)
- ✅ Design e organização visual
- ✅ Smart filtering (UX inteligente)
- ✅ Acesso rede local (host=0.0.0.0)

### 🔄 **Fase 3: Refinamentos** (PRÓXIMO)

- [ ] ORCAMENTO_IDEAL por fonte
- [ ] Export Excel do dashboard
- [ ] Botão atualizar dados (sem reiniciar)
- [ ] Gráficos adicionais (tendências)
- [ ] Modo escuro (dark theme)
- [ ] Autenticação básica

### 📋 **Fase 4: Integração com Fluxo Principal** (FUTURO)

- [ ] Integrar com `agente_financeiro.py`
- [ ] Merge inteligente (Open Finance + manual)
- [ ] Detecção de duplicatas
- [ ] Validação cruzada de valores

### 🤖 **Fase 5: Automação** (FUTURO)

- [ ] Sincronização automática mensal
- [ ] Notificações de novas transações
- [ ] Alertas de orçamento
- [ ] Machine Learning categorização

**Ver detalhes:** [005_PROXIMOS_PASSOS.md](005_PROXIMOS_PASSOS.md)

---

## 🔗 Links Úteis

### **Pluggy**

- [Dashboard](https://dashboard.pluggy.ai/)
- [API Docs](https://docs.pluggy.ai/)
- [Status Page](https://status.pluggy.ai/)

### **Open Finance Brasil**

- [Banco Central](https://www.bcb.gov.br/estabilidadefinanceira/openfinance)
- [Regulamentação](https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolu%C3%A7%C3%A3o%20BCB&numero=4)

### **OAuth2**

- [RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749)
- [OAuth2 Simplified](https://aaronparecki.com/oauth-2-simplified/)

---

## 📞 Links Relacionados

- [📋 ../README.md](../README.md) - Documentação principal
- [🔧 ../Desenvolvimento/](../Desenvolvimento/) - Arquitetura
- [🧪 ../Testing/](../Testing/) - Testes

---

**Criado em:** 10/11/2025  
**Última atualização:** 17/11/2025 (v2.4.0 - Dashboard Plotly Dash funcionando!)
