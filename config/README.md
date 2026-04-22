# ⚙️ Configurações

Arquivos de configuração centralizados do projeto.

---

## � **IMPORTANTE: Comando Python no Windows**

**⚡ Sempre use `py` ao invés de `python` no Windows:**

```bash
# ✅ CORRETO
py backend/src/agente_financeiro.py

# ❌ ERRADO
python backend/src/agente_financeiro.py  # Pode não funcionar
```

---

## 📂 Arquivos

| Arquivo                   | Descrição                                  | Versionado          |
| ------------------------- | ------------------------------------------ | ------------------- |
| `config.example.ini`      | Template de configuração (sem credenciais) | ✅ Sim              |
| `config.ini`              | Configuração real com credenciais          | ❌ Não (.gitignore) |
| `itau_api.example.ini`    | Template de configuração API Itaú          | ✅ Sim              |
| `itau_api.ini`            | Configuração real API Itaú                 | ❌ Não (.gitignore) |
| `certificates/`           | Certificados SSL/TLS da API Itaú           | ❌ Não (.gitignore) |

---

## 🔧 Uso

### **Primeira Configuração**

1. **Copie o template:**

   ```bash
   cp config/config.example.ini config/config.ini
   ```

2. **Edite com suas credenciais:**

   ```bash
   # Windows
   notepad config/config.ini

   # Linux/Mac
   nano config/config.ini
   ```

3. **Preencha as seções:**

   ```ini
   [DATABASE]
   path = dados/db/financeiro.db

   [PATHS]
   planilhas_dir = dados/planilhas

   [PLUGGY]
   CLIENT_ID = seu-client-id-aqui
   CLIENT_SECRET = seu-client-secret-aqui
   ```

---

## 🔐 Segurança

### **Proteção de Credenciais**

- ✅ `config.ini` está no `.gitignore` (não será versionado)
- ✅ `config.example.ini` é template público (sem credenciais)
- ⚠️ **NUNCA** commite `config.ini` com credenciais reais

### **Migração para .env (Planejado)**

```bash
# Formato futuro (mais seguro)
PLUGGY_CLIENT_ID=seu-client-id
PLUGGY_CLIENT_SECRET=seu-client-secret
DATABASE_PATH=dados/db/financeiro.db
```

**Status:** 📋 Planejado para próxima sprint

---

## 📋 Estrutura do config.ini

### **[DATABASE]**

```ini
[DATABASE]
path = dados/db/financeiro.db
```

- **path:** Caminho do banco SQLite

### **[PATHS]**

```ini
[PATHS]
planilhas_dir = dados/planilhas
backup_dir = dados/Backups
```

- **planilhas_dir:** Diretório de extratos bancários
- **backup_dir:** Diretório de backups

### **[PLUGGY]**

```ini
[PLUGGY]
CLIENT_ID = 0774411c-feca-44dc-83df-b5ab7a1735a6
CLIENT_SECRET = 3bd7389d-72d6-419a-804a-146e3e0eaacf
```

- **CLIENT_ID:** ID do cliente Pluggy
- **CLIENT_SECRET:** Secret do cliente Pluggy

⚠️ **Atenção:** Valores acima são exemplos. Use suas próprias credenciais.

---

## 🔄 Leitura no Código

### **Python (configparser)**

```python
import configparser
from pathlib import Path

# Carregar configuração
config = configparser.ConfigParser()
config_path = Path(__file__).parent.parent / 'config' / 'config.ini'
config.read(config_path, encoding='utf-8')

# Usar valores
db_path = config['DATABASE']['path']
client_id = config['PLUGGY']['CLIENT_ID']
client_secret = config['PLUGGY']['CLIENT_SECRET']
```

### **Exemplo Real (agente_financeiro.py)**

```python
from pathlib import Path
import configparser

def load_config():
    config = configparser.ConfigParser()
    config_file = Path(__file__).parent.parent / 'config' / 'config.ini'

    if not config_file.exists():
        raise FileNotFoundError(
            f"Arquivo de configuração não encontrado: {config_file}\n"
            f"Copie config.example.ini para config.ini e configure suas credenciais."
        )

    config.read(config_file, encoding='utf-8')
    return config
```

---

## ⚠️ Troubleshooting

### **Erro: config.ini não encontrado**

```
FileNotFoundError: Arquivo de configuração não encontrado
```

**Solução:**

```bash
cp config/config.example.ini config/config.ini
# Edite config.ini com suas credenciais
```

### **Erro: Credenciais inválidas Pluggy**

```
403 Forbidden - Invalid credentials
```

**Solução:**

1. Verifique CLIENT_ID e CLIENT_SECRET em `config.ini`
2. Obtenha novas credenciais em [Pluggy Dashboard](https://dashboard.pluggy.ai/)
3. Certifique-se de usar credenciais corretas (não do config.example.ini)

### **Paths relativos não funcionam**

```python
# ❌ Errado (depende de onde o script é executado)
config.read('config/config.ini')

# ✅ Correto (usa Path relativo ao arquivo)
from pathlib import Path
config_path = Path(__file__).parent.parent / 'config' / 'config.ini'
config.read(config_path)
```

---

## 🎯 Próximos Passos

### **Migração para .env**

- [ ] Instalar `python-decouple`
- [ ] Criar `.env` na raiz
- [ ] Atualizar `.gitignore` para incluir `.env`
- [ ] Criar `.env.example` template
- [ ] Refatorar código para usar `decouple.config()`
- [ ] Depreciar `config.ini` (manter por compatibilidade)

### **Validação de Configuração**

- [ ] Adicionar validação de campos obrigatórios
- [ ] Verificar formato de credenciais
- [ ] Testar conectividade com APIs
- [ ] Alertas claros para erros de config

---

## 🔗 Links Relacionados

- [📖 Documentação de Integração](../docs/Integracao/)
- [🔐 Segurança Open Finance](../docs/Integracao/004_SEGURANCA_OPENFINANCE.md)
- [🚀 Integracao_PROXIMO_CHAT.md](../docs/Integracao_PROXIMO_CHAT.md)
- [🏦 API Itaú Account Statement](../docs/Integracao/Itau/README.md)

---

## 🏦 Configuração da API Itaú (Novo)

### **Configuração da API Account Statement**

A integração com a API do Itaú permite sincronização automática de extratos bancários.

### **Setup Inicial**

1. **Copie o template de configuração:**

   ```bash
   # Windows
   copy config\itau_api.example.ini config\itau_api.ini
   
   # Linux/Mac
   cp config/itau_api.example.ini config/itau_api.ini
   ```

2. **Preencha as credenciais** (após receber do Itaú):

   ```ini
   [credentials]
   client_id = e26f2f89-0ead-4ca6-8bc3-dd44b4ab3cc7
   client_secret = seu_client_secret_aqui
   
   [account]
   statement_id = 150001234567  # Agência + Conta + DV (12 dígitos)
   account_type = current_account
   ```

### **Certificados SSL/TLS**

Os certificados devem ser armazenados em `config/certificates/`:

```
config/
└── certificates/
    ├── private.pem              # Chave privada (gerada localmente)
    ├── public.pem               # Chave pública (enviar ao Itaú)
    ├── certificate_private.key  # Chave privada do certificado
    └── itau_certificate.crt     # Certificado assinado pelo Itaú
```

⚠️ **IMPORTANTE:** Este diretório está no `.gitignore` - nunca será commitado!

### **Ambientes Disponíveis**

```ini
[api]
environment = sandbox  # ou production
```

- **Sandbox**: Ambiente de testes (dados fictícios)
- **Production**: Ambiente real (dados bancários reais)

### **Processo Completo de Habilitação**

Documentação completa: [Visão Geral](../docs/Integracao/Itau/README.md) | [Guia Completo](../docs/Integracao/Itau/001_INTEGRACAO_API_ITAU.md)

**Resumo dos passos:**
1. ✅ Cadastro no Developer Portal do Itaú
2. ⏳ Contato com time comercial/técnico
3. ⏳ Assinatura de contrato e termo de adesão
4. ⏳ Geração de par de chaves (pública/privada)
5. ⏳ Recebimento de credenciais criptografadas
6. ⏳ Descriptografia de credenciais
7. ⏳ Geração e envio de CSR (Certificate Sign Request)
8. ⏳ Recebimento de certificado assinado
9. ⏳ Configuração final no sistema

### **Status Atual**

| Item | Status |
|------|--------|
| Documentação | ✅ Completa |
| Configuração template | ✅ Criada |
| Cadastro Developer Portal | ⏳ Pendente |
| Credenciais | ⏳ Aguardando |
| Certificados | ⏳ Aguardando |
| Implementação código | ⏳ Aguardando habilitação |

---

**Criado em:** 10/11/2025  
**Última atualização:** 21/04/2026
