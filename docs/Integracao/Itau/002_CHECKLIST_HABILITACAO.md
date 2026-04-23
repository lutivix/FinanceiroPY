# ✅ Checklist de Habilitação - API Itaú Account Statement

Use este checklist para acompanhar o progresso da habilitação da API do Itaú.

---

## 📋 Fase 1: Preparação e Habilitação

### Cadastro e Contrato

- [ ] **Criar conta no Developer Portal**
  - URL: https://devportal.itau.com.br
  - Fazer login e confirmar e-mail
  
- [ ] **Entrar em contato com time comercial**
  - E-mail: implantacaotecnica@itau-unibanco.com.br
  - Assunto: "Solicitação de acesso - API Account Statement"
  - Informar: CNPJ, razão social, objetivo da integração
  
- [ ] **Negociar termos contratuais**
  - SLA (Service Level Agreement)
  - TPS (Transactions Per Second)
  - Limites de uso
  
- [ ] **Assinar Termo de Adesão**
  - Aguardar contrato digital
  - Revisar termos
  - Assinar digitalmente

### Geração de Chaves

- [ ] **Verificar OpenSSL instalado**
  ```bash
  openssl version  # Deve ser 1.1.1 ou superior
  ```
  
- [ ] **Criar diretório de certificados**
  ```bash
  cd config/certificates
  ```
  
- [ ] **Gerar par de chaves (pública/privada)**
  ```bash
  openssl genpkey -out private.pem -algorithm RSA -pkeyopt rsa_keygen_bits:2048
  openssl rsa -in private.pem -pubout -out public.pem
  ```
  
- [ ] **Fazer backup seguro de private.pem**
  - Salvar em cofre digital
  - Nunca compartilhar ou versionar
  
- [ ] **Enviar public.pem ao ponto focal do Itaú**
  - Via e-mail institucional
  - Aguardar resposta (1 dia útil)

### Recebimento de Credenciais

- [ ] **Receber e-mail com credenciais criptografadas**
  - Remetente: `itau@itau.com.br`
  - Assunto: "Credenciais Itaú"
  - Contém: Client ID, Token Temporário, Chave de Sessão (todos criptografados)
  - ⚠️ Token válido por 7 dias!
  
- [ ] **Verificar conteúdo do e-mail**
  - [ ] Client ID criptografado
  - [ ] Token Temporário criptografado
  - [ ] Chave de Sessão criptografada
  - [ ] Razão social e CNPJ corretos
  
- [ ] **Salvar e-mail em local seguro**
  - Não deletar o e-mail original

### Descriptografia de Credenciais

- [ ] **Instalar Java 8+ ou Python 3.8+** (para script de descriptografia)
  
- [ ] **Criar script de descriptografia**
  - Usar código Java fornecido na documentação
  - Ou aguardar script Python (tools/decrypt_itau_credentials.py)
  
- [ ] **Executar descriptografia**
  - Inserir Client ID criptografado
  - Inserir Token Temporário criptografado
  - Inserir Chave de Sessão criptografada
  - Informar caminho de private.pem
  
- [ ] **Salvar credenciais descriptografadas**
  - [ ] Client ID descriptografado
  - [ ] Token Temporário descriptografado
  - Salvar em local seguro (NÃO no código!)

---

## 📋 Fase 2: Geração de Certificado Dinâmico

### Geração de CSR

- [ ] **Gerar Certificate Sign Request (CSR)**
  
  **Windows:**
  ```bash
  openssl req -new ^
    -subj "//CN={SEU_CLIENT_ID}\OU=SISTEMA_FINANCEIRO\L=SAO PAULO\ST=SP\C=BR" ^
    -out certificate_request.csr ^
    -nodes -sha512 -newkey rsa:2048 ^
    -keyout certificate_private.key
  ```
  
  **Linux/Mac:**
  ```bash
  openssl req -new \
    -subj "/CN={SEU_CLIENT_ID}/OU=SISTEMA_FINANCEIRO/L=SAO PAULO/ST=SP/C=BR" \
    -out certificate_request.csr \
    -nodes -sha512 -newkey rsa:2048 \
    -keyout certificate_private.key
  ```
  
  ⚠️ Substituir {SEU_CLIENT_ID} pelo client_id descriptografado!
  
- [ ] **Validar CSR gerado**
  ```bash
  openssl req -in certificate_request.csr -noout -text
  ```
  - Verificar se CN = client_id (exatamente igual!)
  
- [ ] **Fazer backup de certificate_private.key**
  - Salvar em cofre digital
  - Será usado em todas as requisições!

### Envio do CSR ao STS Itaú

- [ ] **Preparar requisição**
  - Endpoint: `https://sts.itau.com.br/seguranca/v1/certificado/solicitacao`
  - Header: `Authorization: Bearer {TOKEN_DESCRIPTOGRAFADO}`
  - Header: `Content-Type: text/plain`
  - Body: Conteúdo completo do arquivo .csr
  
- [ ] **Enviar CSR via curl, Postman ou Insomnia**
  
  **Exemplo curl:**
  ```bash
  curl -X POST "https://sts.itau.com.br/seguranca/v1/certificado/solicitacao" \
    -H "Authorization: Bearer {TOKEN_DESCRIPTOGRAFADO}" \
    -H "Content-Type: text/plain" \
    --data-binary "@certificate_request.csr"
  ```
  
- [ ] **Verificar resposta (Status 200)**
  - Linha 1: `client_secret: xxxxxxxxxx`
  - Demais linhas: Certificado (BEGIN CERTIFICATE ... END CERTIFICATE)
  
- [ ] **Salvar client_secret**
  - Copiar da primeira linha do response
  - Salvar em local seguro
  - Será usado na configuração!
  
- [ ] **Salvar certificado assinado**
  - Copiar de `-----BEGIN CERTIFICATE-----` até `-----END CERTIFICATE-----`
  - Salvar como `itau_certificate.crt` em `config/certificates/`

### Tratamento de Erros Comuns

Se receber erro, consultar tabela:

| Código | Significado | Ação |
|--------|-------------|------|
| C800 | CSR inválido | Verificar se CSR foi enviado corretamente |
| C800a | CN inválido | Regenerar CSR com CN = client_id exato |
| C600 | CN do certificado inválido | Confirmar client_id no subject do CSR |
| 401 | Não autorizado | Token expirado ou inválido - gerar novo |

---

## 📋 Fase 3: Configuração do Sistema

### Configuração Inicial

- [ ] **Copiar template de configuração**
  ```bash
  copy config\itau_api.example.ini config\itau_api.ini
  ```
  
- [ ] **Preencher credenciais em config/itau_api.ini**
  ```ini
  [credentials]
  client_id = {CLIENT_ID_DESCRIPTOGRAFADO}
  client_secret = {CLIENT_SECRET_RECEBIDO}
  ```
  
- [ ] **Configurar dados da conta**
  ```ini
  [account]
  statement_id = {AGENCIA}{CONTA}{DV}  # Exemplo: 150001234567
  account_type = current_account
  ```
  
- [ ] **Configurar caminhos dos certificados**
  ```ini
  [certificates]
  cert_file = config/certificates/itau_certificate.crt
  key_file = config/certificates/certificate_private.key
  ```
  
- [ ] **Escolher ambiente inicial**
  ```ini
  [api]
  environment = sandbox  # Começar com sandbox!
  ```

### Validação de Arquivos

- [ ] **Verificar estrutura de certificados:**
  ```
  config/certificates/
  ├── .gitignore ✓
  ├── README.md ✓
  ├── private.pem ✓
  ├── public.pem ✓
  ├── certificate_private.key ✓
  └── itau_certificate.crt ✓
  ```

- [ ] **Confirmar que certificados estão bloqueados no Git**
  ```bash
  git status
  # Não deve listar nenhum arquivo de config/certificates/
  ```

---

## 📋 Fase 4: Testes (Quando implementação estiver pronta)

### Testes em Sandbox

- [ ] **Configurar ambiente = sandbox**
- [ ] **Testar autenticação OAuth2**
  - Obter access_token via STS
  - Validar validade do token (5 minutos)
  
- [ ] **Testar consulta de extrato**
  - Consultar últimos 7 dias
  - Validar estrutura do JSON retornado
  
- [ ] **Testar paginação**
  - Consultar período com muitas transações
  - Navegar entre páginas
  
- [ ] **Testar filtros**
  - Filtrar apenas PIX
  - Filtrar por valor mínimo
  - Filtrar apenas créditos/débitos

### Testes em Produção

- [ ] **Alterar environment = production**
- [ ] **Fazer backup do banco de dados**
- [ ] **Testar consulta com dados reais**
- [ ] **Validar categorização automática**
- [ ] **Verificar deduplação de transações**
- [ ] **Monitorar logs de erro**

---

## 📋 Fase 5: Deploy e Produção

### Configuração Final

- [ ] **Configurar sincronização automática**
  ```ini
  [sync]
  auto_sync_enabled = true
  sync_interval_hours = 6
  ```
  
- [ ] **Configurar logs**
  ```ini
  [logging]
  log_level = INFO
  log_file = logs/itau_api.log
  ```
  
- [ ] **Criar diretório de logs**
  ```bash
  mkdir logs
  ```

### Monitoramento

- [ ] **Verificar primeira sincronização completa**
- [ ] **Validar dados no banco de dados**
- [ ] **Conferir categorias atribuídas**
- [ ] **Revisar logs de erro**
- [ ] **Testar dashboard atualizado**

### Desativação Gradual de Importação Manual

- [ ] **Validar 1 semana de sincronização automática**
- [ ] **Comparar com extratos manuais (garantir 100% de precisão)**
- [ ] **Documentar casos de erro encontrados**
- [ ] **Desativar importação manual de Excel/PDF**

---

## 🎯 Status Atual

**Última atualização:** _________

| Fase | Status | Data Conclusão |
|------|--------|----------------|
| Fase 1: Preparação e Habilitação | ⏳ Em andamento | ___/___/___ |
| Fase 2: Geração de Certificado | ⏳ Aguardando | ___/___/___ |
| Fase 3: Configuração do Sistema | ⏳ Aguardando | ___/___/___ |
| Fase 4: Testes | ⏳ Aguardando | ___/___/___ |
| Fase 5: Deploy e Produção | ⏳ Aguardando | ___/___/___ |

---

## 📞 Contatos Importantes

| Contato | Informação | Uso |
|---------|------------|-----|
| **Implantação Técnica** | implantacaotecnica@itau-unibanco.com.br | Dúvidas técnicas e habilitação |
| **Developer Portal** | https://devportal.itau.com.br | Login e documentação |
| **Suporte** | Via portal após habilitação | Problemas com APIs |

---

## 📚 Documentação Relacionada

- [Documentação Completa da Integração](001_INTEGRACAO_API_ITAU.md)
- [Visão Geral da Integração Itaú](README.md)
- [Configuração no README](../../../config/README.md#-configuração-da-api-itaú-novo)
- [Especificação OpenAPI](specs/api_account_statement.json) (a adicionar)

---

## 💡 Dicas e Lembretes

- ⏰ **Token temporário vale 7 dias** - Não deixe passar!
- 📅 **Certificado dinâmico vale 365 dias** - Renovar antes de expirar
- 🔒 **Nunca commite certificados** - Sempre bloqueados no .gitignore
- 💾 **Faça backup dos certificados** - Armazene em cofre digital
- 📧 **E-mails do Itaú vêm de** `itau@itau.com.br` - Não aceite outros
- 🔄 **Renove certificado 60 dias antes** - Use endpoint de renovação

---

**Criado em:** 21/04/2026  
**Checklist versão:** 1.0.0
