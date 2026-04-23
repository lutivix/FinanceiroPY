# Especificações da API Account Statement

Esta pasta contém as especificações técnicas da API Itaú Account Statement baixadas do Developer Portal.

## 📄 Arquivos Disponíveis

### Especificação OpenAPI 3.0
- **Arquivo:** `itau_x0_api_account_statement_v1_externo_3fc847dc52.json`
- **Versão:** 1.16.0
- **Formato:** OpenAPI 3.0.0
- **Descrição:** Especificação completa da API com endpoints, parâmetros, schemas e exemplos

### Collection Postman
- **Arquivo:** `itau_x0_api_account_statement_v1_externo_3fc847dc52-1_16.0-collection.json`
- **Versão:** 1.16.0
- **Formato:** Postman Collection v2.1
- **Descrição:** Collection pronta para importar no Postman com todos os endpoints configurados

## 🔧 Como Usar

### Importar Collection no Postman

1. Abra o Postman
2. Clique em **Import** (ou Ctrl+O)
3. Selecione o arquivo da collection JSON
4. Configure as variáveis de ambiente:
   - `base_url` - URL base da API (sandbox ou produção)
   - `client_id` - Seu Client ID
   - `access_token` - Token OAuth2 gerado
   - `statement_id` - ID da sua conta (Agência+Conta+DV)

### Visualizar Especificação OpenAPI

1. **Swagger Editor Online:**
   - Acesse: https://editor.swagger.io/
   - Cole o conteúdo do JSON
   - Visualize documentação interativa

2. **VS Code:**
   - Instale extensão: OpenAPI (Swagger) Editor
   - Abra o arquivo JSON
   - Clique em "Preview"

3. **Postman:**
   - Import → OpenAPI
   - Gera collection automaticamente

## 📋 Conteúdo da Especificação

### Endpoints Documentados

1. **GET /statements/{statementId}**
   - Consultar extrato bancário
   - Parâmetros: tipo, período, paginação, filtros
   - Response: transações, saldos, metadados de paginação

2. **GET /statements/{statementId}/interest-bearing-accounts**
   - Consultar rendimentos de aplicações automáticas
   - Parâmetros: período
   - Response: detalhes de rendimento (IOF, IR, valores)

### Schemas Principais

- `event` - Estrutura de uma transação/lançamento
- `balance` - Estrutura de saldo
- `statement` - Extrato completo com eventos e saldos
- `interestBearingAccount` - Dados de rendimento
- `pagination` - Informações de paginação
- `error` - Estrutura de erro padronizada

### Exemplos de Response

- ✅ Extrato completo com transações PIX, TED, etc.
- ✅ Estrutura de saldo disponível
- ✅ Dados de contrapartes (nome, CPF/CNPJ, instituição)
- ✅ Metadata de parcelas e origem da transação
- ✅ Códigos de erro (400, 401, 403, 404, 422, 500, 503)

## 🔄 Atualizações

Estes arquivos são referentes ao ambiente **Sandbox** inicial.

Quando migrar para **Produção**, os endpoints podem ser os mesmos, mas as URLs mudam:

- **Sandbox:** `https://account-statement.rdhi.com.br/`
- **Produção:** `https://account-statement.itau.com.br/`

## 🔗 Referências

- [Guia de Integração](../001_INTEGRACAO_API_ITAU.md)
- [Checklist de Habilitação](../002_CHECKLIST_HABILITACAO.md)
- [Developer Portal](https://devportal.itau.com.br)
