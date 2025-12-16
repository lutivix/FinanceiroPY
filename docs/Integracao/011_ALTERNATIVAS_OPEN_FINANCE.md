# 🔄 Alternativas ao Pluggy para Open Finance

**Data:** 16/12/2024  
**Status:** 📋 Pesquisa e Avaliação  
**Contexto:** Trial Pluggy expirado (R$ 2.500/mês)

---

## 🎯 Resumo Executivo

Após sucesso com Pluggy durante o trial, buscamos alternativas mais acessíveis ou gratuitas para continuar usando Open Finance no Brasil.

**⚠️ IMPORTANTE: Pessoa Física vs Empresa**

Como **pessoa física**, você **NÃO pode** acessar APIs dos bancos diretamente porque:
- ❌ Precisa ser TPP (Third Party Provider) registrado no Banco Central
- ❌ Requer certificado digital ICP-Brasil específico para Open Finance
- ❌ Processo de credenciamento complexo (somente para empresas)
- ❌ Infraestrutura de compliance e auditoria obrigatória

**Solução:** Use agregadores que já são TPP registrados (Pluggy, Belvo, etc)

**Resultado da pesquisa:**
- ✅ **4 alternativas viáveis** encontradas (agregadores)
- 💰 **1 opção mais barata** (Belvo = 5x menor custo)
- 🏆 **1 recomendação principal** para uso pessoal

---

## 📊 Comparativo Rápido

| Provedor | Preço | Trial | Limitação Free | Recomendação |
|----------|-------|-------|----------------|--------------|
| **Belvo** | Desde $99/mês | 30 dias | 25 links/mês | ⭐⭐⭐⭐⭐ **MELHOR OPÇÃO PF** |
| **Stark Bank** | R$ 0,50/transação | Sim | Sandbox apenas | ⭐⭐⭐ Boa para produção |
| **Quanto** | Freemium | Sim | 1 conta | ⭐⭐ Limitado |
| **Stone OpenBank** | Sob consulta | Sim | Sandbox | ⭐⭐⭐ Enterprise |
| ~~API BC Direto~~ | ~~GRÁTIS~~ | N/A | ❌ **Somente TPP** | ❌ Inviável para PF |

**Legenda:**
- **PF** = Pessoa Física
- **TPP** = Third Party Provider (empresa registrada no BC)

---

## 🏆 Opção Recomendada: Belvo (Melhor Custo-Benefício para PF)

### ✅ Vantagens
- ✅ **5x mais barato que Pluggy** ($99 vs $500+/mês)
- ✅ **Trial 30 dias completo** (sem cartão de crédito)
- ✅ **API similar ao Pluggy** (migração fácil)
- ✅ **TPP registrado** (legal e seguro)
- ✅ **SDK Python oficial** bem documentado
- ✅ **25 links/mês** suficiente para uso pessoal
- ✅ **Suporte em português**

### ⚠️ Limitações
- ⚠️ **Ainda é pago** após trial (mas viável: ~R$ 500/mês)
- ⚠️ **Empresa estrangeira** (México, mas atua no Brasil)

### 🔧 Como Funciona

1. **Você cria conta no Belvo** (empresa TPP registrada)
2. **Belvo conecta com bancos** via Open Finance oficial
3. **Você usa API do Belvo** para acessar seus dados
4. **Belvo te cobra mensalidade** (intermediário autorizado)

### 💻 Migração do Pluggy

```python
# Era assim com Pluggy:
from pluggy import PluggyClient
client = PluggyClient(client_id, client_secret)
items = client.get_items()
transactions = client.get_transactions(item_id)

# Fica assim com Belvo (muito similar!):
from belvo.client import Client
client = Client(secret_id, secret_password, "production")
links = client.Links.list()
transactions = client.Transactions.create(link=link_id)
```

**Tempo de migração:** 2-4 horas (APIs são muito parecidas!)

---

## ❌ ~~Opção API Banco Central Direto~~ (NÃO FUNCIONA PARA PF)

### Por que NÃO funciona?

**Open Finance exige que você seja uma TPP (Third Party Provider):**

1. **Registro no Banco Central** como instituição participante
2. **Certificado digital ICP-Brasil** específico para Open Finance (~R$ 500/ano)
3. **CNPJ** (não aceita CPF)
4. **Infraestrutura de segurança:**
   - Servidor HTTPS com certificado válido
   - Política de privacidade e segurança
   - LGPD compliance documentado
   - Auditoria de segurança
5. **Processo burocrático:** 2-6 meses de aprovação

### Quem pode ser TPP?

- ✅ Instituições financeiras (bancos, fintechs)
- ✅ Empresas de tecnologia (com CNPJ e infraestrutura)
- ✅ Startups registradas como FIDC ou SCD
- ❌ **Pessoas físicas** (mesmo desenvolvedores)
- ❌ Aplicações pessoais sem CNPJ

### Alternativa "Gratuita" (com ressalvas)

Se você **realmente** quer grátis e **tem CNPJ**:

1. Abrir empresa (MEI, ME, etc)
2. Registrar no diretório Open Finance Brasil
3. Obter certificado digital empresarial
4. Implementar APIs seguindo padrão BC
5. Passar por auditoria de segurança

**Custo real:** R$ 3.000-10.000 (setup) + R$ 2.000/ano (manutenção)  
**Tempo:** 3-6 meses  
**Vale a pena?** ❌ Não para uso pessoal

---

## 💰 Opção 2: Belvo (Melhor Custo-Benefício)

### Sobre
Empresa latino-americana (México), especializada em Open Finance para América Latina, incluindo Brasil.

### Preços
```
Sandbox:   GRÁTIS (desenvolvimento)
Starter:   $99/mês USD (25 links)
Growth:    $299/mês USD (100 links)
Business:  $899/mês USD (500 links)
```

### ✅ Vantagens
- ✅ **Trial 30 dias completo**
- ✅ **Preço mais acessível** que Pluggy (4x menor)
- ✅ **SDK Python oficial** bem documentado
- ✅ **Dashboard intuitivo**
- ✅ **API similar ao Pluggy** (fácil migração)
- ✅ **Suporte em português**

### ⚠️ Limitações
- ⚠️ **Ainda é pago** após trial
- ⚠️ **Empresa estrangeira** (regulamentação)

### 🔗 Links
- [Site oficial](https://belvo.com/)
- [Documentação](https://developers.belvo.com/)
- [Preços](https://belvo.com/pricing/)
- [Python SDK](https://github.com/belvo-finance/belvo-python)

### 💻 Exemplo de Código
```python
from belvo.client import Client

# Criar cliente
client = Client("secret_id", "secret_password", "sandbox")

# Criar link (conexão com banco)
link = client.Links.create(
    institution='itau_br',
    username='seu_usuario',
    password='sua_senha'
)

# Buscar transações
transactions = client.Transactions.create(
    link=link['id'],
    date_from='2024-01-01',
    date_to='2024-12-31'
)
```

---

## 🏦 Opção 3: Stark Bank

### Sobre
Fintech brasileira, oferece banking as a service + Open Finance.

### Preços
```
Sandbox:      GRÁTIS
Produção:     R$ 0,50 por transação consultada
              R$ 10/mês por conta conectada
```

### ✅ Vantagens
- ✅ **Empresa brasileira** (regulada pelo BC)
- ✅ **Pay-as-you-go** (paga só o que usar)
- ✅ **SDK Python oficial**
- ✅ **APIs bancárias completas** (PIX, boletos, etc)

### ⚠️ Limitações
- ⚠️ **Custo variável** pode ficar caro
- ⚠️ **Foco em empresas**, não pessoas físicas

### 🔗 Links
- [Site oficial](https://starkbank.com/)
- [Documentação Open Finance](https://starkbank.com/docs/api/open-finance)
- [Python SDK](https://github.com/starkbank/sdk-python)

---

## 📱 Opção 4: Quanto

### Sobre
Agregador financeiro brasileiro, com app mobile e API.

### Preços
```
Freemium:   GRÁTIS (1 conta)
Premium:    R$ 14,90/mês (ilimitado)
API:        Sob consulta
```

### ✅ Vantagens
- ✅ **App brasileiro popular**
- ✅ **Freemium generoso** para uso pessoal
- ✅ **Interface web + mobile**

### ⚠️ Limitações
- ⚠️ **API não pública** (precisa contato comercial)
- ⚠️ **Foco em B2C**, não B2D (Business to Developer)

### 🔗 Links
- [Site oficial](https://www.quantoapp.com.br/)
- [App iOS](https://apps.apple.com/br/app/quanto/id1459816080)
- [App Android](https://play.google.com/store/apps/details?id=br.com.quanto)

---

## 🏢 Opção 5: Stone OpenBank

### Sobre
Solução empresarial da Stone (Ton/PagSeguro) para Open Finance.

### Preços
```
Sob consulta (foco enterprise)
```

### ✅ Vantagens
- ✅ **Empresa grande e confiável**
- ✅ **Infraestrutura robusta**
- ✅ **Compliance garantido**

### ⚠️ Limitações
- ⚠️ **Preço alto** (enterprise)
- ⚠️ **Processo comercial demorado**

### 🔗 Links
- [Stone OpenBank](https://www.stone.com.br/openbanking/)

---

## 🛠️ Implementação Recomendada

### ✅ Migração para Belvo (Recomendado)

**Passo 1: Criar conta (hoje - 30min)**
```bash
# 1. Acesse https://belvo.com
# 2. Clique "Start for Free"
# 3. Preencha dados (30 dias grátis, sem cartão)
# 4. Confirme email
```

**Passo 2: Instalar SDK (hoje - 5min)**
```bash
pip install belvo-python
```

**Passo 3: Testar em Sandbox (amanhã - 1h)**
```python
from belvo.client import Client

# Credenciais do dashboard (sandbox)
client = Client("seu_secret_id", "seu_secret_password", "sandbox")

# Conectar banco de teste
link = client.Links.create(
    institution='erebor_br_retail',  # Banco fictício do sandbox
    username='test',
    password='test'
)

# Buscar transações
transactions = client.Transactions.create(
    link=link['id'],
    date_from='2024-01-01',
    date_to='2024-12-31'
)

print(f"✅ Encontradas {len(transactions)} transações!")
```

**Passo 4: Migrar código do Pluggy (semana 1 - 4h)**
```python
# Adaptar sync_openfinance.py

# ANTES (Pluggy):
from pluggy import PluggyClient
client = PluggyClient(
    client_id=config['PLUGGY']['CLIENT_ID'],
    client_secret=config['PLUGGY']['CLIENT_SECRET']
)
items = client.get_items()
for item in items:
    transactions = client.get_transactions(item.id)
    
# DEPOIS (Belvo):
from belvo.client import Client
client = Client(
    config['BELVO']['SECRET_ID'],
    config['BELVO']['SECRET_PASSWORD'],
    'production'  # ou 'sandbox'
)
links = client.Links.list()
for link in links:
    transactions = client.Transactions.create(
        link=link['id'],
        date_from='2024-01-01',
        date_to='2024-12-31'
    )
```

**Passo 5: Conectar bancos reais (semana 2)**
```python
# Mudar para produção
client = Client(secret_id, secret_password, "production")

# Conectar Itaú (via código ou dashboard)
link_itau = client.Links.create(
    institution='itau_br_retail',
    username='seu_usuario',
    password='sua_senha',
    # Ou usar external_id se já conectou via dashboard
)
```

---

### ⚠️ Opções NÃO Recomendadas

#### ❌ API BC Direta (Impossível para PF)
Requer CNPJ + TPP + certificado + compliance = R$ 10.000+

#### ❌ Web Scraping (Ilegal/Arriscado)
```python
# NÃO FAÇA ISSO!
from selenium import webdriver
# Automatizar login no internet banking
# ⚠️ Viola termos de uso
# ⚠️ Pode bloquear sua conta
# ⚠️ Problemas de segurança
```

#### ❌ Planilhas Manuais (Inviável)
Você já automatizou com Pluggy, voltar atrás não faz sentido!

---

## 📋 Checklist de Migração

### ✅ Migração para Belvo (Viável para PF)

**Preparação (hoje)**
- [ ] Criar conta em [belvo.com](https://belvo.com) (trial 30 dias)
- [ ] Verificar [bancos suportados](https://developers.belvo.com/docs/institutions)
- [ ] Ler [quick start](https://developers.belvo.com/docs/quickstart-python)

**Setup técnico (hoje/amanhã)**
- [ ] Instalar SDK: `pip install belvo-python`
- [ ] Obter credenciais sandbox no dashboard
- [ ] Testar conexão com banco fictício
- [ ] Validar estrutura de dados retornados

**Migração código (semana 1)**
- [ ] Criar seção `[BELVO]` no `config.ini`
- [ ] Adaptar `sync_openfinance.py` para Belvo
- [ ] Testar em sandbox (dados fictícios)
- [ ] Comparar estrutura Belvo vs Pluggy
- [ ] Ajustar mapeamentos (categorias, fontes)

**Produção (semana 2)**
- [ ] Trocar credenciais para produção
- [ ] Conectar Itaú (via dashboard ou código)
- [ ] Buscar transações reais
- [ ] Validar vs histórico Pluggy
- [ ] Testar dashboard com dados Belvo

**Decisão (dia 30 do trial)**
- [ ] Avaliar custos ($99/mês = ~R$ 500)
- [ ] Verificar se atende necessidades
- [ ] Assinar plano ou buscar alternativa

---

### ❌ ~~Opção API BC~~ (NÃO aplicável para PF)

~~Esse checklist foi removido pois não é viável para pessoa física.~~

**Por quê?** Requer CNPJ, registro TPP, certificado empresarial, etc.

---

## 🔍 Análise Detalhada: API Banco Central

### Endpoints Principais

```python
# Base URL (exemplo Itaú)
BASE_URL = "https://openbanking.api.itau.com.br"

# 1. Autenticação OAuth2
POST /auth/oauth/v2/token
Headers:
  Authorization: Basic <client_credentials>
Body:
  grant_type=authorization_code
  code=<authorization_code>
  redirect_uri=<callback_url>

# 2. Listar Contas
GET /open-banking/accounts/v1/accounts
Headers:
  Authorization: Bearer <access_token>

# 3. Buscar Transações
GET /open-banking/accounts/v1/accounts/{accountId}/transactions
Params:
  fromBookingDate=2024-01-01
  toBookingDate=2024-12-31
Headers:
  Authorization: Bearer <access_token>
```

### Exemplo de Resposta (Transações)

```json
{
  "data": [
    {
      "transactionId": "TXN-123456",
      "type": "DEBIT",
      "amount": {
        "amount": "150.00",
        "currency": "BRL"
      },
      "transactionDate": "2024-12-15",
      "partiesCreditDebit": {
        "personType": "NATURAL",
        "name": "ESTABELECIMENTO XYZ"
      },
      "creditDebitType": "CREDITO"
    }
  ],
  "meta": {
    "totalRecords": 1,
    "totalPages": 1
  }
}
```

### Fluxo de Autorização

```
┌─────────┐                    ┌──────────┐                ┌─────────┐
│ Usuário │                    │ Sua App  │                │  Banco  │
└────┬────┘                    └────┬─────┘                └────┬────┘
     │                              │                           │
     │  1. Clica "Conectar Banco"   │                           │
     ├─────────────────────────────>│                           │
     │                              │                           │
     │                              │ 2. Redireciona p/ OAuth   │
     │                              ├──────────────────────────>│
     │                              │                           │
     │  3. Faz login no banco       │                           │
     ├──────────────────────────────────────────────────────────>│
     │                              │                           │
     │  4. Autoriza acesso          │                           │
     ├──────────────────────────────────────────────────────────>│
     │                              │                           │
     │                              │  5. Retorna código        │
     │                              │<──────────────────────────┤
     │                              │                           │
     │                              │  6. Troca código por token│
     │                              ├──────────────────────────>│
     │                              │                           │
     │                              │  7. Retorna access_token  │
     │                              │<──────────────────────────┤
     │                              │                           │
     │                              │  8. Busca transações      │
     │                              ├──────────────────────────>│
     │                              │                           │
     │                              │  9. Retorna JSON          │
     │                              │<──────────────────────────┤
     │                              │                           │
     │  10. Mostra dados            │                           │
     │<─────────────────────────────┤                           │
     │                              │                           │
```

### Implementação Básica (Conceito)

```python
import requests
from urllib.parse import urlencode

class OpenFinanceBrasilAPI:
    """Cliente para APIs Open Finance padrão Banco Central"""
    
    def __init__(self, banco: str):
        # URLs por banco (exemplo Itaú)
        self.banks = {
            'itau': {
                'base_url': 'https://openbanking.api.itau.com.br',
                'client_id': 'SEU_CLIENT_ID',
                'client_secret': 'SEU_CLIENT_SECRET',
                'redirect_uri': 'http://localhost:8080/callback'
            }
        }
        self.config = self.banks[banco]
        self.access_token = None
    
    def get_authorization_url(self) -> str:
        """Gera URL para autorização do usuário"""
        params = {
            'response_type': 'code',
            'client_id': self.config['client_id'],
            'redirect_uri': self.config['redirect_uri'],
            'scope': 'accounts transactions',
            'state': 'random_state_123'
        }
        return f"{self.config['base_url']}/auth/oauth/v2/authorize?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str) -> dict:
        """Troca código de autorização por access token"""
        url = f"{self.config['base_url']}/auth/oauth/v2/token"
        
        response = requests.post(
            url,
            auth=(self.config['client_id'], self.config['client_secret']),
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': self.config['redirect_uri']
            }
        )
        
        data = response.json()
        self.access_token = data['access_token']
        return data
    
    def get_accounts(self) -> list:
        """Lista contas do usuário"""
        url = f"{self.config['base_url']}/open-banking/accounts/v1/accounts"
        
        response = requests.get(
            url,
            headers={'Authorization': f'Bearer {self.access_token}'}
        )
        
        return response.json()['data']
    
    def get_transactions(self, account_id: str, date_from: str, date_to: str) -> list:
        """Busca transações de uma conta"""
        url = f"{self.config['base_url']}/open-banking/accounts/v1/accounts/{account_id}/transactions"
        
        response = requests.get(
            url,
            headers={'Authorization': f'Bearer {self.access_token}'},
            params={
                'fromBookingDate': date_from,
                'toBookingDate': date_to
            }
        )
        
        return response.json()['data']

# Uso
api = OpenFinanceBrasilAPI('itau')

# 1. Usuário acessa URL e autoriza
print("Acesse:", api.get_authorization_url())

# 2. Após autorização, você recebe código
code = input("Cole o código de autorização: ")

# 3. Troca código por token
api.exchange_code_for_token(code)

# 4. Busca dados
contas = api.get_accounts()
transacoes = api.get_transactions(
    account_id=contas[0]['accountId'],
    date_from='2024-01-01',
    date_to='2024-12-31'
)

print(f"Encontradas {len(transacoes)} transações")
```

---

## 💡 Decisão Recomendada

### Para seu caso (pessoa física, uso pessoal):

**🏆 OPÇÃO ÚNICA VIÁVEL: Belvo**

**Por quê?**
1. ✅ **Custo acessível:** $99/mês (~R$ 500) vs R$ 2.500 do Pluggy
2. ✅ **Você já tem experiência** com APIs (Pluggy funcionou)
3. ✅ **Migração rápida:** 2-4 horas de trabalho
4. ✅ **Legal e seguro:** TPP registrado no BC
5. ✅ **Trial 30 dias:** testa antes de pagar
6. ✅ **25 links/mês:** suficiente (você usa ~3-5)

**Custo-benefício:**
```
Pluggy:  R$ 2.500/mês = R$ 30.000/ano
Belvo:   R$ 500/mês   = R$ 6.000/ano
Economia: R$ 24.000/ano (80% de desconto!)
```

**Cronograma sugerido:**
```
Hoje:     Criar conta Belvo (30min)
Amanhã:   Conectar Itaú no sandbox (1h)
Semana 1: Migrar código do Pluggy (4h total)
Semana 2: Testar em produção
Semana 3: Validar dados vs histórico Pluggy
Dia 30:   Decidir se assina ($99/mês)
```

### ❌ Por que NÃO usar API BC direta?

**Simplesmente porque você não pode como pessoa física!**

Open Finance exige:
- ❌ CNPJ (empresa)
- ❌ Registro como TPP no BC
- ❌ Certificado digital empresarial
- ❌ Infraestrutura de compliance
- ❌ Auditoria de segurança

**Custo real se abrir empresa:** R$ 10.000+ (setup + manutenção)  
**Não vale a pena** vs pagar R$ 500/mês para Belvo!

---

## 📚 Recursos de Aprendizado

### OAuth2
- [OAuth2 Simplified](https://aaronparecki.com/oauth-2-simplified/)
- [OAuth2 Flow Diagrams](https://developers.google.com/identity/protocols/oauth2)

### Open Finance Brasil
- [Portal Oficial](https://openbankingbrasil.org.br/)
- [Atlassian Wiki](https://openfinancebrasil.atlassian.net/wiki/spaces/OF/overview)
- [Diretório Participantes](https://web.directory.openbankingbrasil.org.br/)

### APIs por Banco
- [Itaú Open Finance](https://developer.itau.com.br/)
- [Bradesco Open Banking](https://developers.bradesco.com.br/)
- [Santander Open Banking](https://developer.santander.com.br/)

---

## 🎯 Próximos Passos

### Imediato (esta semana)
1. [ ] Decidir entre API BC vs Belvo trial
2. [ ] Criar conta no provedor escolhido
3. [ ] Fazer POC (Proof of Concept) básico

### Curto prazo (próximo mês)
1. [ ] Implementar autenticação OAuth2
2. [ ] Conectar primeira conta (Itaú)
3. [ ] Buscar transações de teste
4. [ ] Comparar dados com Pluggy (se ainda tiver histórico)

### Médio prazo (próximos 3 meses)
1. [ ] Migrar todo código do Pluggy
2. [ ] Conectar demais bancos/cartões
3. [ ] Documentar processo
4. [ ] Criar guia para outros desenvolvedores

---

## 📞 Suporte

### Comunidades
- [Open Banking Brasil - Slack](https://openbankingbr.slack.com/)
- [Reddit r/brasil](https://reddit.com/r/brasil)
- [Stack Overflow [open-banking]](https://stackoverflow.com/questions/tagged/open-banking)

### Contatos Comerciais
- **Belvo:** sales@belvo.com
- **Stark Bank:** api@starkbank.com
- **Quanto:** contato@quantoapp.com.br

---

## ⚠️ Avisos Importantes

### Regulamentação
- ⚠️ **LGPD:** Você é responsável pelos dados dos usuários
- ⚠️ **Banco Central:** Siga as normas de Open Finance
- ⚠️ **Consentimento:** Precisa autorização explícita do usuário

### Segurança
- 🔒 **Nunca armazene senhas** de banco
- 🔒 **Use HTTPS** sempre
- 🔒 **Criptografe tokens** em repouso
- 🔒 **Implemente refresh token** (tokens expiram)

### Performance
- ⏱️ **Rate limiting:** APIs têm limites de requisições
- ⏱️ **Cache:** Evite buscar mesmos dados repetidamente
- ⏱️ **Timeout:** Implemente retry logic

---

**Criado em:** 16/12/2024  
**Autor:** Sistema Financeiro  
**Status:** ✅ Pronto para uso
