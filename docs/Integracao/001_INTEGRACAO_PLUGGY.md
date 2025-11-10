# 🔌 Integração Open Finance - Pluggy

Guia completo para configurar e usar a integração com Open Finance através do Pluggy.

---

## 📋 **Pré-requisitos**

### **1. Criar Conta no Meu Pluggy**

1. Acesse: https://meu.pluggy.ai/
2. Crie sua conta (gratuita)
3. Conecte suas contas bancárias para teste

### **2. Obter Credenciais da API**

1. Acesse o **Dashboard Pluggy**: https://dashboard.pluggy.ai/
2. Faça login com sua conta
3. Navegue até **"API Keys"** ou **"Configurações"**
4. Copie suas credenciais:
   - `CLIENT_ID`
   - `CLIENT_SECRET`

### **3. Instalar Dependências**

```bash
pip install pluggy-sdk
```

---

## ⚙️ **Configuração**

### **1. Adicionar Credenciais**

Edite o arquivo `backend/src/config.ini`:

```ini
[PLUGGY]
# Habilita integração com Pluggy
habilitado = true

# Suas credenciais (obtidas no dashboard)
client_id = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
client_secret = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Sincronização automática
sync_automatico = true

# Dias retroativos (máximo: 365)
dias_retroativos = 30
```

---

## 🧪 **Testando a Integração**

### **Script de Teste**

Execute o script de teste para verificar se está tudo funcionando:

```bash
cd backend/src
python teste_pluggy.py
```

**O que o script faz:**

1. ✅ Solicita suas credenciais
2. ✅ Testa conexão com Pluggy
3. ✅ Lista contas conectadas
4. ✅ Busca transações dos últimos 30 dias
5. ✅ Exibe resumo dos dados

---

## 🚀 **Usando no Sistema**

### **Opção 1: Sincronização Automática**

Se `sync_automatico = true` no config.ini, o sistema **automaticamente** buscará dados do Pluggy ao executar:

```bash
python agente_financeiro.py
```

### **Opção 2: Sincronização Manual**

```python
from integrations import PluggyClient, PluggySyncService
from datetime import datetime, timedelta

# Inicializa cliente
client = PluggyClient(
    client_id="seu_client_id",
    client_secret="seu_client_secret"
)

# Cria serviço de sync
sync = PluggySyncService(client)

# Busca transações dos últimos 30 dias
from_date = datetime.now() - timedelta(days=30)
transactions = sync.sync_all_transactions(from_date=from_date)

print(f"✅ {len(transactions)} transações sincronizadas!")
```

---

## 💳 **Dados Disponíveis**

### **Contas (Accounts)**

- ✅ Tipo de conta (corrente, poupança, cartão)
- ✅ Saldo atual
- ✅ Limites de crédito (cartões)
- ✅ Data de vencimento (cartões)
- ✅ Bandeira (Mastercard, Visa, etc)

### **Transações (Transactions)**

- ✅ Data da transação
- ✅ Descrição completa
- ✅ Valor (positivo = despesa, negativo = receita em cartões)
- ✅ Categoria automática (plano Pro)
- ✅ Estabelecimento (CNPJ, razão social)
- ✅ Informações de parcelamento

### **Histórico**

- ✅ Até **12 meses** de transações
- ✅ Sincronização **automática diária**
- ✅ Webhooks para atualizações em tempo real

---

## 🔄 **Mapeamento de Dados**

### **Tipos de Conta → Fontes do Sistema**

| Pluggy Account Type        | Sistema (TransactionSource) |
| -------------------------- | --------------------------- |
| BANK (Corrente/Poupança)   | PIX                         |
| CREDIT - Mastercard (Itaú) | ITAU*MASTER*\*              |
| CREDIT - Visa (Latam)      | LATAM*VISA*\*               |

### **Categorias Pluggy → Categorias do Sistema**

| Pluggy Category            | Sistema             |
| -------------------------- | ------------------- |
| Food and Drink / Groceries | MERCADO             |
| Restaurants                | LANCHE              |
| Transportation / Gas       | CARRO / COMBUSTIVEL |
| Health                     | FARMACIA            |
| Shopping                   | COMPRAS             |
| Entertainment              | LAZER               |
| Travel                     | VIAGEM              |
| Bills                      | CASA                |
| Education                  | FACULDADE           |
| Income                     | SALARIO             |
| Investments                | INVESTIMENTOS       |

---

## ⚠️ **Limitações e Observações**

### **Limitações da API**

| Aspecto                    | Limite                   |
| -------------------------- | ------------------------ |
| **Histórico**              | Máximo 12 meses          |
| **Transações por request** | 500 (paginado)           |
| **Rate limiting**          | Varia por plano          |
| **Número do cartão**       | Apenas últimos 4 dígitos |

### **Planos do Pluggy**

| Recurso            | Gratuito | Pro    |
| ------------------ | -------- | ------ |
| Conexão de contas  | ✅ Sim   | ✅ Sim |
| Transações básicas | ✅ Sim   | ✅ Sim |
| Categorização IA   | ❌ Não   | ✅ Sim |
| Dados do merchant  | ❌ Não   | ✅ Sim |
| Suporte premium    | ❌ Não   | ✅ Sim |

---

## 🐛 **Solução de Problemas**

### **Erro: "Pluggy SDK não instalado"**

```bash
pip install pluggy-sdk
```

### **Erro: "Invalid credentials"**

1. Verifique se copiou corretamente o CLIENT_ID e CLIENT_SECRET
2. Certifique-se de estar usando credenciais do **Dashboard Pluggy**, não do Meu Pluggy
3. Verifique se não há espaços em branco nas credenciais

### **Erro: "No items found"**

1. Acesse https://meu.pluggy.ai/
2. Clique em **"Conectar Conta"**
3. Adicione ao menos uma conta bancária
4. Aguarde alguns minutos para sincronização

### **Nenhuma transação encontrada**

1. Verifique se a conta tem transações no período configurado
2. Aumente o `dias_retroativos` no config.ini
3. Verifique o status da conexão no Meu Pluggy

---

## 📚 **Recursos Adicionais**

- 📖 **Documentação oficial:** https://docs.pluggy.ai/
- 🔧 **Dashboard:** https://dashboard.pluggy.ai/
- 💬 **Discord (Suporte):** https://discord.gg/EanrwJADby
- 📊 **Status da API:** https://status.pluggy.ai/

---

## 🎯 **Próximos Passos**

Após configurar a integração:

1. ✅ Execute o script de teste
2. ✅ Configure suas credenciais no config.ini
3. ✅ Execute o agente_financeiro.py normalmente
4. ✅ Veja seus dados sendo sincronizados automaticamente!

---

**Atualizado em:** Novembro 2025  
**Versão:** 1.0
