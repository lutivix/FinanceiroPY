# ✅ CHECKLIST - INTEGRAÇÃO PLUGGY

## 🎯 **PASSO A PASSO COMPLETO**

### **□ ETAPA 1: CRIAR CONTA E CONECTAR BANCOS**

1. □ Acesse: https://meu.pluggy.ai/
2. □ Crie sua conta (gratuita)
3. □ Clique em **"Conectar Conta"**
4. □ Escolha um banco (Mercado Pago, Nubank, etc)
5. □ Faça login com suas credenciais bancárias
6. □ Aguarde sincronização (pode levar alguns minutos)
7. □ Veja suas transações na interface do Meu Pluggy

**✅ Status:** Conta conectada e dados visíveis no Meu Pluggy

---

### **□ ETAPA 2: OBTER CREDENCIAIS DA API**

⚠️ **ATENÇÃO:** Não é o Meu Pluggy, é o **Dashboard Pluggy**!

1. □ Acesse: https://dashboard.pluggy.ai/
2. □ Faça login (mesma conta do Meu Pluggy)
3. □ Navegue até **"API Keys"** ou **"Configurações"**
4. □ Copie o **CLIENT_ID** (formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
5. □ Copie o **CLIENT_SECRET** (string longa)
6. □ Guarde em local seguro (não compartilhe!)

**✅ Status:** Credenciais copiadas

---

### **□ ETAPA 3: INSTALAR DEPENDÊNCIAS**

```bash
pip install pluggy-sdk
```

**Como verificar se instalou:**

```bash
python -c "import pluggy_sdk; print('OK')"
```

**✅ Status:** SDK instalado

---

### **□ ETAPA 4: EXECUTAR TESTE**

**Opção A - Arquivo Batch (Windows):**

```bash
cd backend/src
teste_pluggy.bat
```

**Opção B - Python direto:**

```bash
cd backend/src
python teste_pluggy.py
```

**O que vai acontecer:**

1. Script pedirá CLIENT_ID
2. Script pedirá CLIENT_SECRET
3. Testará conexão
4. Mostrará suas contas
5. Buscará transações dos últimos 30 dias

**✅ Status:** Teste executado com sucesso

---

### **□ ETAPA 5: CONFIGURAR NO SISTEMA**

Edite: `backend/src/config.ini`

```ini
[PLUGGY]
habilitado = true
client_id = cole_seu_client_id_aqui
client_secret = cole_seu_client_secret_aqui
sync_automatico = true
dias_retroativos = 30
```

**✅ Status:** Configurado

---

### **□ ETAPA 6: USAR NO SISTEMA**

Execute o agente normalmente:

```bash
cd backend/src
python agente_financeiro.py
```

Ou use o batch:

```bash
cd backend/src
agente_financeiro.bat
```

**O sistema irá:**

1. ✅ Processar arquivos locais (como antes)
2. ✅ **NOVO:** Buscar dados do Pluggy automaticamente
3. ✅ Consolidar tudo em um único relatório

**✅ Status:** Sistema rodando com Open Finance!

---

## 🆘 **PROBLEMAS COMUNS**

### **❌ "Pluggy SDK não instalado"**

**Solução:**

```bash
pip install pluggy-sdk
```

---

### **❌ "Invalid credentials"**

**Causas possíveis:**

1. Credenciais erradas (copie novamente)
2. Espaços em branco (remova espaços)
3. Usando credenciais do Meu Pluggy (use Dashboard!)

**Solução:**

1. Acesse: https://dashboard.pluggy.ai/
2. Copie as credenciais novamente
3. Cole sem espaços extras

---

### **❌ "No items found"**

**Causa:** Nenhuma conta conectada no Meu Pluggy

**Solução:**

1. Acesse: https://meu.pluggy.ai/
2. Clique em "Conectar Conta"
3. Adicione ao menos um banco
4. Aguarde alguns minutos
5. Execute o teste novamente

---

### **❌ "No transactions found"**

**Causas possíveis:**

1. Conta sem transações no período
2. Período muito curto

**Solução:**

1. Aumente `dias_retroativos` no config.ini
2. Use uma conta com movimentação recente
3. Verifique se a conta está ativa no Meu Pluggy

---

## 📊 **VALIDAÇÃO FINAL**

Marque ✅ quando concluir cada item:

- □ Conta criada no Meu Pluggy
- □ Banco conectado e sincronizado
- □ Credenciais obtidas no Dashboard
- □ SDK instalado (pluggy-sdk)
- □ Teste executado com sucesso
- □ Config.ini atualizado
- □ Sistema rodando com dados do Pluggy

**🎉 SE TODOS MARCADOS = INTEGRAÇÃO COMPLETA!**

---

## 💡 **DICAS**

### **Bancos Recomendados para Teste:**

- ✅ **Mercado Pago** (você já usou!)
- ✅ Nubank
- ✅ Inter
- ✅ C6 Bank
- ✅ PicPay

### **Melhor Banco para Testar:**

Use um banco que você **realmente usa** para ver dados reais, mas que não seja sua conta principal (por segurança).

---

## 🔗 **LINKS ÚTEIS**

| Recurso                      | Link                          |
| ---------------------------- | ----------------------------- |
| Meu Pluggy (Conectar contas) | https://meu.pluggy.ai/        |
| Dashboard (API Keys)         | https://dashboard.pluggy.ai/  |
| Documentação                 | https://docs.pluggy.ai/       |
| Status da API                | https://status.pluggy.ai/     |
| Suporte (Discord)            | https://discord.gg/EanrwJADby |

---

**Criado em:** Novembro 2025  
**Última atualização:** Hoje 🚀
