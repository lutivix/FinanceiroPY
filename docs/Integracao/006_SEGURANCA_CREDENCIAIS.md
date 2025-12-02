# 🔒 Segurança de Credenciais - Integração Pluggy

> **Data:** 02/12/2025  
> **Status:** ⚠️ Ação Requerida  
> **Prioridade:** 🔴 Alta

---

## ⚠️ Situação Atual

### **Problema Identificado**

Credenciais Pluggy estão **hardcoded** em arquivos Python:

```python
# backend/src/gerar_excel_pluggy.py (linhas 17-19)
CLIENT_ID = '0774411c-feca-44dc-83df-b5ab7a1735a6'
CLIENT_SECRET = '3bd7389d-72d6-419a-804a-146e3e0eaacf'
ITEM_ID = '60cbf151-aaed-45c7-afac-f2aab15e6299'
```

```python
# backend/src/teste_pluggy_rest.py (linhas 9-11)
CLIENT_ID = '0774411c-feca-44dc-83df-b5ab7a1735a6'
CLIENT_SECRET = '3bd7389d-72d6-419a-804a-146e3e0eaacf'
ITEM_ID = '06f300c4-75e0-4a2f-bbea-e0fb1a1a13cf'
```

### **Riscos**

- 🔴 **Exposição acidental** em commits públicos
- 🔴 **Roubo de credenciais** se repositório vazar
- 🔴 **Acesso não autorizado** às contas bancárias via API
- 🟡 **Dificuldade de rotação** de credenciais (múltiplos arquivos)
- 🟡 **Violação de boas práticas** de segurança

---

## ✅ Solução Recomendada: Migrar para .env

### **Passo 1: Instalar python-decouple**

```bash
pip install python-decouple
```

### **Passo 2: Criar arquivo .env na raiz**

```bash
# .env (raiz do projeto)
# Open Finance - Pluggy API
PLUGGY_CLIENT_ID=0774411c-feca-44dc-83df-b5ab7a1735a6
PLUGGY_CLIENT_SECRET=3bd7389d-72d6-419a-804a-146e3e0eaacf
PLUGGY_ITEM_ID=60cbf151-aaed-45c7-afac-f2aab15e6299
PLUGGY_SANDBOX_ITEM_ID=06f300c4-75e0-4a2f-bbea-e0fb1a1a13cf
```

### **Passo 3: Adicionar .env ao .gitignore**

```bash
# .gitignore
.env
.env.local
.env.*.local
```

### **Passo 4: Criar .env.example (template)**

```bash
# .env.example (raiz do projeto)
# Open Finance - Pluggy API
# Obtenha suas credenciais em: https://dashboard.pluggy.ai/
PLUGGY_CLIENT_ID=seu-client-id-aqui
PLUGGY_CLIENT_SECRET=seu-client-secret-aqui
PLUGGY_ITEM_ID=seu-item-id-aqui
PLUGGY_SANDBOX_ITEM_ID=seu-sandbox-item-id-aqui
```

### **Passo 5: Atualizar código Python**

#### **gerar_excel_pluggy.py**

```python
from decouple import config

# ANTES (inseguro)
# CLIENT_ID = '0774411c-feca-44dc-83df-b5ab7a1735a6'
# CLIENT_SECRET = '3bd7389d-72d6-419a-804a-146e3e0eaacf'
# ITEM_ID = '60cbf151-aaed-45c7-afac-f2aab15e6299'

# DEPOIS (seguro)
CLIENT_ID = config('PLUGGY_CLIENT_ID')
CLIENT_SECRET = config('PLUGGY_CLIENT_SECRET')
ITEM_ID = config('PLUGGY_ITEM_ID')
```

#### **teste_pluggy_rest.py**

```python
from decouple import config

# ANTES (inseguro)
# CLIENT_ID = '0774411c-feca-44dc-83df-b5ab7a1735a6'
# CLIENT_SECRET = '3bd7389d-72d6-419a-804a-146e3e0eaacf'
# ITEM_ID = '06f300c4-75e0-4a2f-bbea-e0fb1a1a13cf'

# DEPOIS (seguro)
CLIENT_ID = config('PLUGGY_CLIENT_ID')
CLIENT_SECRET = config('PLUGGY_CLIENT_SECRET')
ITEM_ID = config('PLUGGY_SANDBOX_ITEM_ID')  # Usa sandbox para testes
```

#### **pluggy_client.py** (se necessário)

```python
from decouple import config

def create_pluggy_client():
    """Factory para criar cliente Pluggy com credenciais seguras"""
    return PluggyClient(
        client_id=config('PLUGGY_CLIENT_ID'),
        client_secret=config('PLUGGY_CLIENT_SECRET')
    )
```

---

## 🔐 Melhores Práticas

### **1. Nunca comitar credenciais**

```bash
# ❌ NUNCA FAÇA ISSO
git add .env
git commit -m "Adiciona credenciais"

# ✅ SEMPRE FAÇA ISSO
echo ".env" >> .gitignore
git add .gitignore
```

### **2. Rotação periódica**

- 🔄 Trocar credenciais a cada **3-6 meses**
- 🔄 Trocar **imediatamente** se houver suspeita de exposição
- 🔄 Usar credenciais **diferentes** para dev/staging/prod

### **3. Níveis de acesso**

```python
# Desenvolvimento/Testes
PLUGGY_ITEM_ID=06f300c4-75e0-4a2f-bbea-e0fb1a1a13cf  # Sandbox

# Produção
PLUGGY_ITEM_ID=60cbf151-aaed-45c7-afac-f2aab15e6299  # Dados reais
```

### **4. Documentar sem expor**

```markdown
# ✅ BOM - Documentação sem credenciais
Para obter suas credenciais:
1. Acesse: https://dashboard.pluggy.ai/
2. Copie CLIENT_ID e CLIENT_SECRET
3. Adicione ao arquivo .env

# ❌ RUIM - Credenciais expostas
CLIENT_ID = 0774411c-feca-44dc-83df-b5ab7a1735a6
```

---

## 📋 Checklist de Implementação

### **Fase 1: Preparação**

- [ ] Instalar `python-decouple`
- [ ] Criar `.env` na raiz
- [ ] Adicionar `.env` ao `.gitignore`
- [ ] Criar `.env.example` template

### **Fase 2: Migração de Código**

- [ ] Atualizar `gerar_excel_pluggy.py`
- [ ] Atualizar `teste_pluggy_rest.py`
- [ ] Atualizar `buscar_itau_simples.py` (se usar Pluggy)
- [ ] Atualizar qualquer outro script com credenciais

### **Fase 3: Teste**

- [ ] Testar `gerar_excel_pluggy.py` com .env
- [ ] Testar `teste_pluggy_rest.py` com .env
- [ ] Verificar que credenciais não estão mais hardcoded

### **Fase 4: Limpeza**

- [ ] Remover credenciais hardcoded de todos os arquivos
- [ ] Commit das mudanças
- [ ] Verificar histórico do Git (se público)
- [ ] Considerar rotação de credenciais expostas

---

## 🆘 E se já commitei credenciais?

### **Repositório Privado (caso atual)**

✅ **Risco Baixo** - Mas ainda assim deve corrigir:

1. Implementar .env imediatamente
2. Remover credenciais hardcoded
3. Commit da correção

### **Repositório Público** ⚠️

🔴 **AÇÃO URGENTE:**

1. **Revogar credenciais** no Dashboard Pluggy
2. **Gerar novas credenciais**
3. **Limpar histórico Git:**

```bash
# Use BFG Repo-Cleaner ou git-filter-repo
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch backend/src/gerar_excel_pluggy.py" \
  --prune-empty --tag-name-filter cat -- --all
```

4. **Force push** (cuidado!)
5. **Notificar colaboradores**

---

## 📚 Referências

- [python-decouple Documentation](https://github.com/henriquebastos/python-decouple)
- [12 Factor App - Config](https://12factor.net/config)
- [OWASP - Credential Storage](https://cheatsheetseries.owasp.org/cheatsheets/Credential_Storage_Cheat_Sheet.html)
- [GitHub - Removing Sensitive Data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)

---

## ✅ Próximos Passos

1. Revisar este documento
2. Executar Checklist de Implementação
3. Testar nova configuração
4. Atualizar documentação (README, etc)
5. Considerar rotação de credenciais (opcional, mas recomendado)

---

**Data de revisão:** 02/12/2025  
**Status:** Pendente de implementação
