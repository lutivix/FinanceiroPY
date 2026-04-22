# 🏦 Integração API Itaú Account Statement

Documentação completa da integração com a API de Extrato de Contas do Itaú Developer Portal.

---

## ⚠️ REQUISITO IMPORTANTE - ESCLARECER COM ITAÚ

**A documentação não deixa claro se a API funciona para contas PF ou apenas PJ.**

### O que sabemos:
- ✅ **Developer (cadastro)**: Precisa ser correntista **PJ** para se cadastrar no portal
- ❓ **Contas consultadas**: Pode consultar PF, PJ, ou só PJ? **NÃO ESPECIFICADO**
- ✅ **Transações**: Podem envolver contrapartes PF ou PJ

### Perguntas para fazer ao Itaú:

Ao solicitar acesso, **pergunte explicitamente**:
> "Com credenciais de developer PJ, posso consultar extratos de contas PF autorizadas, ou apenas contas PJ?"

**Ver detalhes completos:** [Seção de Requisitos PJ/PF](001_INTEGRACAO_API_ITAU.md#️-requisitos-importantes)

**Alternativa garantida para PF:** Use agregadores Open Finance como Pluggy - [ver aqui](../README.md)

---

## 📊 Status da Integração

| Status Atual | Fase | Data |
|--------------|------|------|
| ⏳ **Em Habilitação** | Aguardando credenciais | 21/04/2026 |

**Próximo passo:** Cadastro no Developer Portal e contato com time comercial

---

## 📂 Documentos

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| [001_INTEGRACAO_API_ITAU.md](001_INTEGRACAO_API_ITAU.md) | Guia completo de integração e arquitetura | ✅ Completo |
| [002_CHECKLIST_HABILITACAO.md](002_CHECKLIST_HABILITACAO.md) | Checklist passo a passo de habilitação | ✅ Completo |
| `003_IMPLEMENTACAO.md` | Implementação dos módulos Python | ⏳ Aguardando habilitação |
| `004_TESTES.md` | Documentação de testes | ⏳ Futuro |

### 📁 Especificações

| Arquivo | Descrição |
|---------|-----------|
| `specs/api_account_statement.json` | Especificação OpenAPI 3.0 da API | ⏳ Adicionar |

---

## 🎯 Sobre a API

### Endpoints Disponíveis

1. **GET /statements/{statementId}** - Consultar extrato bancário
   - Parâmetros: período, paginação, filtros
   - Retorna: transações, saldo, paginação

2. **GET /statements/{statementId}/interest-bearing-accounts** - Rendimentos de aplicações
   - Parâmetros: período
   - Retorna: detalhes de rendimento

### Autenticação

- **OAuth2** + **mTLS** (Mutual TLS)
- **Certificado Dinâmico** gerado via STS Itaú
- **Token de acesso** válido por 5 minutos

### Ambientes

- **Sandbox:** `https://account-statement.rdhi.com.br`
- **Produção:** `https://account-statement.itau.com.br`

---

## 🔧 Arquivos de Configuração

Localizados em: `config/`

- `itau_api.example.ini` - Template de configuração
- `itau_api.ini` - Configuração real (não versionado)
- `certificates/` - Certificados SSL/TLS (não versionado)

**Ver:** [config/README.md](../../../config/README.md#-configuração-da-api-itaú-novo)

---

## 🚀 Roadmap de Implementação

### ✅ Fase 1: Documentação (Concluída - 21/04/2026)

- [x] Documentação completa de integração
- [x] Checklist de habilitação
- [x] Templates de configuração
- [x] Estrutura de pastas
- [x] Segurança (.gitignore)

### ⏳ Fase 2: Habilitação (Em Andamento)

- [ ] Cadastro no Developer Portal
- [ ] Contato com time comercial/técnico
- [ ] Assinatura de termo de adesão
- [ ] Geração de par de chaves
- [ ] Recebimento de credenciais
- [ ] Geração de certificado dinâmico

### ⏳ Fase 3: Implementação (Aguardando Habilitação)

- [ ] Módulo `itau_oauth_handler.py`
- [ ] Módulo `itau_api_client.py`
- [ ] Módulo `itau_statement_processor.py`
- [ ] Módulo `itau_sync_service.py`
- [ ] Script de descriptografia
- [ ] Script de geração de certificados

### ⏳ Fase 4: Testes

- [ ] Testes em Sandbox
- [ ] Validação de autenticação
- [ ] Validação de endpoints
- [ ] Testes de paginação e filtros

### ⏳ Fase 5: Produção

- [ ] Deploy em produção
- [ ] Sincronização automática
- [ ] Integração com sistema atual
- [ ] Monitoramento

---

## 🔗 Links Importantes

### Portais e Documentação

- **Developer Portal:** https://devportal.itau.com.br
- **Certificado Dinâmico:** https://devportal.itau.com.br/certificado-dinamico
- **Como Começar:** https://devportal.itau.com.br/como-comecar
- **FAQ:** https://devportal.itau.com.br/suportefaq

### Contatos

- **Implantação Técnica:** implantacaotecnica@itau-unibanco.com.br
- **Suporte:** Via portal após habilitação

### Documentação do Projeto

- [📖 Documentação Principal](../../README.md)
- [⚙️ Configuração](../../../config/README.md)
- [🔗 Outras Integrações](../README.md)

---

## 🔐 Segurança

**⚠️ NUNCA commite:**

- Certificados (`.pem`, `.key`, `.crt`, `.csr`)
- Arquivo `itau_api.ini` com credenciais
- `client_id` e `client_secret` em código
- Tokens de acesso

**Proteções configuradas:**

- ✅ `.gitignore` global
- ✅ `.gitignore` em `config/certificates/`
- ✅ Templates `.example.ini` versionados
- ✅ Arquivos reais bloqueados

---

## 💡 Vantagens da Integração

### vs. Importação Manual (Excel/PDF)

| Antes (Manual) | Depois (API) |
|----------------|--------------|
| 📄 Download manual | 🤖 Automático |
| ⏰ 1x por semana | ⚡ A cada 6h |
| 🖱️ Categorização manual | 🎯 Automática |
| ❌ Erros possíveis | ✅ Dados oficiais |
| 📊 Dados básicos | 📈 Dados completos |
| 🕒 ~30 min/semana | ⚙️ 0 minutos |

### Benefícios Técnicos

- ✅ **Tempo real** - Dados sempre atualizados
- ✅ **Rastreabilidade** - ID único por transação
- ✅ **Detalhamento** - Nome, CPF/CNPJ da contraparte
- ✅ **Performance** - Até 1000 transações/requisição
- ✅ **Confiabilidade** - Dados diretos do banco

---

## 📞 Suporte

**Dúvidas sobre a integração?**

1. Consulte: [001_INTEGRACAO_API_ITAU.md](001_INTEGRACAO_API_ITAU.md)
2. Use: [002_CHECKLIST_HABILITACAO.md](002_CHECKLIST_HABILITACAO.md)
3. Contate: implantacaotecnica@itau-unibanco.com.br

---

**Criado em:** 21/04/2026  
**Última atualização:** 21/04/2026  
**Responsável:** Equipe de Desenvolvimento  
**Status:** 📋 Documentação completa, aguardando habilitação
