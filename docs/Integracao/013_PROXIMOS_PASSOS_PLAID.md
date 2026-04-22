# 🚀 Próximos Passos - Integração Plaid

**Data:** 21/04/2026  
**Status:** ✅ Testes bem-sucedidos - Pronto para implementação  
**Contexto:** Migração do Pluggy para Plaid (R$ 2.500/mês → R$ 5,40/mês)

---

## ✅ O Que Já Está Pronto

```
STATUS ATUAL:
├─ ✅ SDK instalado (plaid-python 39.1.0)
├─ ✅ Credenciais sandbox configuradas
├─ ✅ Conexão testada (sandbox.plaid.com)
├─ ✅ Link token ← Funciona
├─ ✅ Item creation ← Funciona  
├─ ✅ Access token ← Funciona
├─ ✅ Accounts API ← Funciona (12 contas)
├─ ⏳ Transactions API ← Aguardando prod (sandbox normal)
├─ ✅ Documentação completa criada
└─ ⏳ Aprovação produção - Status: Requested
```

---

## 📋 Próximas Tarefas (Priorizada)

### 🥇 FASE 1: Preparação (AGORA - Esta Semana)

**Enquanto aguarda aprovação de produção:**

#### 1.1 Criar Módulo de Sincronização Plaid

```bash
backend/src/services/
├─ __init__.py
├─ plaid_service.py          # ← CRIAR (similar ao pluggy)
└─ sync_plaid.py              # ← CRIAR (substitui sync_openfinance.py)
```

**Arquivo:** `backend/src/services/plaid_service.py`
```python
"""
Serviço de integração com Plaid API
Substitui Pluggy para redução de 99% nos custos
"""

class PlaidService:
    def __init__(self, client_id, secret, environment='sandbox'):
        """Inicializa cliente Plaid"""
        pass
    
    def create_link_token(self, user_id):
        """Cria token para Plaid Link UI"""
        pass
    
    def exchange_public_token(self, public_token):
        """Troca public_token por access_token permanente"""
        pass
    
    def get_accounts(self, access_token):
        """Busca contas conectadas"""
        pass
    
   def get_transactions(self, access_token, days=90):
        """Busca transações dos últimos N dias"""
        pass
    
    def sync_all_accounts(self):
        """Sincroniza todas as contas configuradas"""
        pass
```

#### 1.2 Mapear Campos Plaid → Database

| Plaid Field | Database Column | Transformação |
|-------------|----------------|---------------|
| `transaction_id` | `id` | Direto |
| `date` | `data` | Parse YYYY-MM-DD |
| `name` | `descricao` | Direto |
| `amount` | `valor` | **Inverter sinal!** |
| `category` | `categoria` | Usar primeiro elemento |
| `account_id` | `conta_id` | Mapear para fonte |

**⚠️ CRÍTICO:** Plaid usa `amount > 0 = débito`, seu sistema usa `valor < 0 debito`!

#### 1.3 Configurar Config.ini

**Arquivo:** `config/config.ini`
```ini
[PLAID]
habilitado = true
environment = sandbox  # Depois trocar para production
client_id = 69e7b1383357a7000e4e1ebb
secret = 9229419b2929fdb0b28082ed5a4592
access_tokens = 
sync_automatico = false
dias_retroativos = 90
products = transactions,investments
```

#### 1.4 Criar Script de Teste com Dados Reais

**Arquivo:** `backend/src/test_plaid_integration.py`
- Conectar conta sandbox
- Buscar transações
- Inserir no database (tabela temporária)
- Validar mapeamento de campos
- Comparar com estrutura Pluggy

---

### 🥈 FASE 2: Quando Produção Aprovar (Semana 2)

#### 2.1 Configurar Produção

```ini
[PLAID]
environment = production
secret = <NOVO_SECRET_PRODUCTION>  # Dashboard enviará
```

#### 2.2 Conectar Contas Reais

**Via Plaid Link UI (interface web):**
1. Gerar `link_token` via API
2. Abrir Plaid Link no navegador
3. Usuário faz login no Itaú
4. Plaid retorna `public_token`
5. Backend troca por `access_token`
6. Salvar `access_token` no config.ini

**Contas a conectar:**
- 🏦 Itaú Conta Corrente (PF)
- 💳 Itaú Cartão 1
- 💳 Itaú Cartão 2
- 📈 Itaú Investimentos

#### 2.3 Primeira Sincronização

```bash
py backend/src/services/sync_plaid.py --initial
```

**Validações:**
- ✅ Transações importadas corretamente
- ✅ Valores com sinal correto
- ✅ Categorias mapeadas
- ✅ Sem duplicatas

#### 2.4 Comparar com Histórico Pluggy

```bash
py backend/src/compare_plaid_vs_pluggy.py
```

**Verificar:**
- Mesmo número de transações?
- Mesmos valores?
- Mesmas datas?
- Categorias compatíveis?

---

### 🥉 FASE 3: Migração Completa (Semana 3)

#### 3.1 Substituir Pluggy

**Arquivo:** `backend/src/agente_financeiro.py`
```python
# ANTES
from services import sync_openfinance

# DEPOIS
from services import sync_plaid

# MUDAR
if config.getboolean('PLUGGY', 'habilitado'):
    sync_openfinance.sync()

# PARA
if config.getboolean('PLAID', 'habilitado'):
    sync_plaid.sync()
```

#### 3.2 Atualizar Dashboard

**Fonte de dados:**
- Trocar "Pluggy" → "Plaid" nos labels
- Atualizar última sincronização
- Mostrar custo mensal (R$ 5,40)

#### 3.3 Desativar Pluggy

```ini
[PLUGGY]
habilitado = false
# Manter credenciais por segurança (30 dias backup)
```

#### 3.4 Documentar Migração

**Criar:** `docs/Integracao/014_MIGRACAO_PLUGGY_PLAID.md`
- Passos executados
- Problemas encontrados
- Soluções aplicadas
- Lições aprendidas

---

## 📊 Cronograma Estimado

```
┌─────────────────────────────────────────────────────┐
│ SEMANA 1 (ATUAL)                                    │
├─────────────────────────────────────────────────────┤
│ Segunda    │ Criar plaid_service.py                 │
│ Terça      │ Criar sync_plaid.py                    │
│ Quarta     │ Testar mapeamento campos               │
│ Quinta     │ Validar com sandbox                    │
│ Sexta      │ Aguardar aprovação produção            │
│ Fim de sem │ Ler sobre Plaid Link UI                │
├─────────────────────────────────────────────────────┤
│ SEMANA 2 (Após aprovação)                           │
├─────────────────────────────────────────────────────┤
│ Segunda    │ Configurar produção                    │
│ Terça      │ Conectar conta Itaú via Link           │
│ Quarta     │ Primeira sincronização real            │
│ Quinta     │ Comparar com histórico Pluggy          │
│ Sexta      │ Ajustes finais                         │
├─────────────────────────────────────────────────────┤
│ SEMANA 3 (Migração)                                 │
├─────────────────────────────────────────────────────┤
│ Segunda    │ Integrar com agente_financeiro.py      │
│ Terça      │ Atualizar dashboard                    │
│ Quarta     │ Testar fluxo completo                  │
│ Quinta     │ Desativar Pluggy                       │
│ Sexta      │ Documentar + celebrar 🎉               │
└─────────────────────────────────────────────────────┘
```

**Total:** ~15 dias (3 semanas)  
**Horas:** ~20-25h trabalho total  
**Economia:** R$ 2.495/mês a partir do dia 1!

---

## 🎯 Ações Imediatas (Esta Semana)

### Terça-feira (Amanhã):
- [ ] Criar `backend/src/services/plaid_service.py`
- [ ] Implementar métodos básicos
- [ ] Testar conexão sandbox

### Quarta-feira:
- [ ] Criar `backend/src/services/sync_plaid.py`
- [ ] Implementar lógica de sincronização
- [ ] Mapear campos Plaid → Database

### Quinta-feira:
- [ ] Criar script de teste com dados sandbox
- [ ] Validar mapeamento de categorias
- [ ] Documentar descobertas

### Sexta-feira:
- [ ] Revisar código
- [ ] Preparar para produção
- [ ] Aguardar aprovação (verificar dashboard)

---

## 📝 Checklist de Implementação

### Setup Inicial
- [x] Instalar plaid-python
- [x] Testar conexão sandbox
- [x] Obter credenciais
- [ ] Criar estrutura de arquivos
- [ ] Configurar config.ini

### Desenvolvimento
- [ ] Implementar PlaidService
- [ ] Implementar sync_plaid
- [ ] Mapear campos
- [ ] Tratamento de erros
- [ ] Logging

### Testes
- [ ] Teste unitário PlaidService
- [ ] Teste integração sync
- [ ] Teste mapeamento campos
- [ ] Teste com dados sandbox
- [ ] Validação duplicatas

### Produção (Quando aprovar)
- [ ] Receber credenciais production
- [ ] Configurar environment=production
- [ ] Conectar contas reais
- [ ] Testar sincronização
- [ ] Comparar com Pluggy
- [ ] Migrar agente_financeiro
- [ ] Desativar Pluggy

### Documentação
- [ ] README do módulo
- [ ] Guia de troubleshooting
- [ ] Documento de migração
- [ ] Atualizar README principal

---

## ⚠️ Pontos de Atenção

### 1. **Inversão de Sinal**
⚠️ **CRÍTICO:** Plaid usa convenção oposta!
- Plaid: `amount > 0` = débito (saída de dinheiro)
- Seu DB: `valor < 0` = débito

**Solução:**
```python
valor_db = -plaid_amount  # Inverter sinal!
```

### 2. **Categorização**
Plaid retorna categorias diferentes do Pluggy:
- Plaid: `['Food and Drink', 'Restaurants']`
- Pluggy: `'Alimentação'`

**Solução:** Criar tabela de mapeamento

### 3. **IDs de Transação**
- Plaid IDs são strings longas
- Verificar tamanho coluna `id` no banco
- Pode precisar aumentar VARCHAR

### 4. **Webhooks**
Plaid envia webhooks quando há novas transações:
- Configurar URL no dashboard
- Implementar endpoint /webhooks/plaid
- Sincronizar automaticamente

### 5. **Rate Limits**
Plaid tem limites de requisições:
- Sandbox: 100 req/min
- Production: Depende do plano
- Implementar retry com backoff

---

## 💰 ROI - Retorno do Investimento

**Investimento:**
- Tempo desenvolvimento: ~25 horas
- Valor/hora: R$ 0 (você mesmo)
- Custo Plaid: R$ 5,40/mês

**Economia:**
- Mês 1: R$ 2.495
- Ano 1: R$ 29.940
- 5 anos: R$ 149.700

**Payback:** Imediato! (economia de R$ 2.495 no primeiro mês)

---

## 🔗 Recursos Úteis

### Plaid Docs
- [Quickstart](https://plaid.com/docs/quickstart/)
- [Transactions](https://plaid.com/docs/transactions/)
- [Investments](https://plaid.com/docs/investments/)
- [Error Handling](https://plaid.com/docs/errors/)

### Seu Projeto
- [Guia Sandbox](012_PLAID_SANDBOX_GUIA.md)
- [Alternativas](011_ALTERNATIVAS_OPEN_FINANCE.md)
- [Test Script](../../test_plaid_sandbox.py)

### Suporte
- [Dashboard](https://dashboard.plaid.com)
- [Discord](https://discord.gg/sf57M8DW3y)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/plaid)

---

**Criado em:** 21/04/2026  
**Autor:** Sistema Financeiro  
**Status:** ✅ Roadmap confirmado - Pronto para começar!

**🎯 PRÓXIMO PASSO:** Começar Fase 1.1 - Criar `plaid_service.py`
