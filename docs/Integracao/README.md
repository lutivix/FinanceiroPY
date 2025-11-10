# 🔗 Integração

Documentação sobre integrações externas: Open Finance (Pluggy), APIs bancárias e serviços de terceiros.

---

## 📂 Documentos

| Arquivo                                                      | Descrição                          | Status          |
| ------------------------------------------------------------ | ---------------------------------- | --------------- |
| [001_INTEGRACAO_PLUGGY.md](001_INTEGRACAO_PLUGGY.md)         | Integração Open Finance via Pluggy | ✅ Em uso       |
| [002_CHECKLIST_PLUGGY.md](002_CHECKLIST_PLUGGY.md)           | Checklist de implementação         | 🔄 Em progresso |
| [003_ARQUITETURA_PLUGGY.md](003_ARQUITETURA_PLUGGY.md)       | Decisões técnicas REST vs SDK      | 📋 Planejado    |
| [004_SEGURANCA_OPENFINANCE.md](004_SEGURANCA_OPENFINANCE.md) | Segurança e compliance             | 📋 Planejado    |

---

## 🚀 **LEIA PRIMEIRO!**

### [📌 Integracao_PROXIMO_CHAT.md](../Integracao_PROXIMO_CHAT.md)

**Contexto rápido essencial para IA e próximas sessões:**

- ✅ O que já funciona (REST API working)
- 🔑 Credenciais e segurança
- ❌ O que NÃO usar (SDK com bug)
- 🎯 Próximos passos (roadmap)
- 📊 Dados reais obtidos
- 💡 Decisões técnicas

---

## 🎯 Integrações Ativas

### **1. Open Finance (Pluggy)**

- **Status:** ✅ Funcional (REST API)
- **Contas conectadas:**
  - Mercado Pago (real)
  - Sandbox (teste)
- **Dados acessados:**
  - ✅ Saldo da conta
  - ✅ Transações com categoria
  - ✅ Dados de identidade
  - ✅ Investimentos
- **Ver:** [001_INTEGRACAO_PLUGGY.md](001_INTEGRACAO_PLUGGY.md)

### **2. Itaú (Planejado)**

- **Status:** 📋 Planejado
- **Método:** Open Finance via Pluggy
- **Próximos passos:**
  - Conectar via Dashboard
  - Testar recuperação de dados
  - Comparar com arquivos XLS manuais
  - Implementar sincronização automática

---

## 🛠️ Stack Técnica

### **Open Finance**

- **Agregador:** Pluggy
- **Protocolo:** OAuth2
- **Implementação:** REST API (requests)
- **Autenticação:** X-API-KEY header
- **Base URL:** `https://api.pluggy.ai`

### **Arquivos Relevantes**

```
backend/src/
├── integrations/
│   ├── pluggy_client.py      # ⚠️ Precisa refatorar (ainda usa SDK)
│   └── pluggy_sync.py         # Serviço de sincronização (não testado)
│
└── [Scripts de teste]
    ├── teste_pluggy_rest.py           # ✅ WORKING - REST API
    ├── verificar_dados_completos.py   # ✅ WORKING - Dados completos
    ├── teste_pluggy.py                # ❌ Obsoleto (SDK)
    ├── teste_pluggy_rapido.py         # ❌ Obsoleto (SDK)
    ├── testar_item_pluggy.py          # ❌ Obsoleto (SDK)
    └── criar_item_pluggy.py           # ❌ Obsoleto (SDK)
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

### **Fase 1: Segurança** 🔐

- [ ] Migrar credenciais para `.env`
- [ ] Implementar rotação de API keys
- [ ] Documentar compliance LGPD

### **Fase 2: Refatoração** 🔧

- [ ] Refatorar `pluggy_client.py` para REST API
- [ ] Remover dependência do `pluggy-sdk`
- [ ] Implementar error handling robusto
- [ ] Adicionar logging estruturado

### **Fase 3: Sincronização** 🔄

- [ ] Atualizar `pluggy_sync.py` para REST
- [ ] Mapear Pluggy → Transaction model
- [ ] Implementar sync incremental
- [ ] Detectar e prevenir duplicatas

### **Fase 4: Expansão** 🏦

- [ ] Conectar Itaú via Pluggy
- [ ] Testar com múltiplas contas
- [ ] Validar categorização automática
- [ ] Comparar manual vs Open Finance

### **Fase 5: Automação** 🤖

- [ ] Integrar com `agente_financeiro.py`
- [ ] Script de sincronização automática
- [ ] Adicionar ao fluxo mensal
- [ ] Relatórios consolidados

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
**Última atualização:** 10/11/2025
