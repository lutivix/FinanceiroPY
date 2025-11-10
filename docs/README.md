# 📚 Documentação - Agente Financeiro IA

> **Sistema inteligente de automação financeira com 98.2% de precisão**  
> **Versão:** 2.0.2  
> **Última atualização:** 10/11/2025

---

## 🎯 Início Rápido

| Documento                                                   | Descrição                                                       |
| ----------------------------------------------------------- | --------------------------------------------------------------- |
| [📖 README Principal](../README.md)                         | Visão geral do projeto, instalação e uso                        |
| [🚀 Integracao_PROXIMO_CHAT.md](Integracao_PROXIMO_CHAT.md) | **Contexto rápido para IA/próximas sessões sobre Open Finance** |
| [📋 CHANGELOG](../CHANGELOG.md)                             | Histórico de versões e mudanças                                 |
| [🤝 CONTRIBUTING](../CONTRIBUTING.md)                       | Guia de contribuição                                            |

---

## 📂 Estrutura da Documentação

### 🔧 [Desenvolvimento](Desenvolvimento/)

Documentação técnica, arquitetura e guias do sistema.

| Arquivo                                                                            | Descrição                                  |
| ---------------------------------------------------------------------------------- | ------------------------------------------ |
| [001_DOCUMENTACAO_TECNICA.md](Desenvolvimento/001_DOCUMENTACAO_TECNICA.md)         | Arquitetura, estrutura de dados, diagramas |
| [002_GUIA_USUARIO.md](Desenvolvimento/002_GUIA_USUARIO.md)                         | Manual de uso do sistema                   |
| [003_PLANEJAMENTO.md](Desenvolvimento/003_PLANEJAMENTO.md)                         | Roadmap e planejamento de features         |
| [004_RESUMO_RAPIDO.md](Desenvolvimento/004_RESUMO_RAPIDO.md)                       | Guia rápido de referência                  |
| [005_ATUALIZACAO_DOCUMENTACAO.md](Desenvolvimento/005_ATUALIZACAO_DOCUMENTACAO.md) | Log de atualizações da documentação        |
| [006_INDICE_DOCUMENTACAO.md](Desenvolvimento/006_INDICE_DOCUMENTACAO.md)           | Índice detalhado (legado)                  |

### 🔗 [Integração](Integracao/)

Documentação sobre integrações externas (Open Finance, APIs, etc).

| Arquivo                                                                 | Descrição                                 |
| ----------------------------------------------------------------------- | ----------------------------------------- |
| [001_INTEGRACAO_PLUGGY.md](Integracao/001_INTEGRACAO_PLUGGY.md)         | Integração Open Finance via Pluggy        |
| [002_CHECKLIST_PLUGGY.md](Integracao/002_CHECKLIST_PLUGGY.md)           | Checklist de implementação Pluggy         |
| [003_ARQUITETURA_PLUGGY.md](Integracao/003_ARQUITETURA_PLUGGY.md)       | Decisões técnicas e arquitetura (a criar) |
| [004_SEGURANCA_OPENFINANCE.md](Integracao/004_SEGURANCA_OPENFINANCE.md) | Segurança e compliance (a criar)          |

### 🧪 [Testing](Testing/)

Documentação sobre testes, qualidade e cobertura.

| Arquivo                                                                    | Descrição                                     |
| -------------------------------------------------------------------------- | --------------------------------------------- |
| [001_TESTING.md](Testing/001_TESTING.md)                                   | Estratégia de testes e configuração pytest    |
| [002_SEMANA1_CONCLUSAO.md](Testing/002_SEMANA1_CONCLUSAO.md)               | Relatório Semana 1 - Infraestrutura de testes |
| [003_SEMANA2_PRONTIDAO.md](Testing/003_SEMANA2_PRONTIDAO.md)               | Status de prontidão dos testes                |
| [004_SEMANA2_RESUMO_EXECUTIVO.md](Testing/004_SEMANA2_RESUMO_EXECUTIVO.md) | Resumo executivo Semana 2                     |

---

## 🔍 Navegação por Tópico

### 🏦 **Processamento de Extratos Bancários**

- [Documentação Técnica - Processadores](Desenvolvimento/001_DOCUMENTACAO_TECNICA.md#processadores)
- [Guia do Usuário - Fluxo de Processamento](Desenvolvimento/002_GUIA_USUARIO.md)

### 🤖 **Categorização com IA**

- [Documentação Técnica - Sistema de Aprendizado](Desenvolvimento/001_DOCUMENTACAO_TECNICA.md#sistema-de-aprendizado)
- [Resultados de Performance](../README.md#-performance-atual)

### 🔗 **Open Finance (Pluggy)**

- [🚀 Integracao_PROXIMO_CHAT.md](Integracao_PROXIMO_CHAT.md) - **LEIA PRIMEIRO!**
- [Integração Completa](Integracao/001_INTEGRACAO_PLUGGY.md)
- [Checklist de Implementação](Integracao/002_CHECKLIST_PLUGGY.md)

### 🧪 **Testes e Qualidade**

- [Estratégia de Testes](Testing/001_TESTING.md)
- [Cobertura: 35.34%](../htmlcov/index.html)
- [Status: 119/127 testes passing](Testing/003_SEMANA2_PRONTIDAO.md)

### 📊 **Relatórios e Análises**

- [Guia do Usuário - Relatórios](Desenvolvimento/002_GUIA_USUARIO.md#relatórios)
- [Exemplos de Saída](Desenvolvimento/001_DOCUMENTACAO_TECNICA.md#exemplos)

---

## 📊 Status do Projeto

### ✅ **Produção**

- **Versão:** 2.0.2
- **Precisão:** 98.2% (1759/1791 transações)
- **Categorias:** 584 otimizadas
- **Status:** ✅ Estável

### 🧪 **Qualidade**

- **Testes:** 119/127 passing (94% funcional)
- **Cobertura:** 35.34%
- **Meta:** 70% de cobertura

### 🚧 **Em Desenvolvimento**

- 🔄 Integração Open Finance (Pluggy)
- 🔄 Migração para .env (segurança)
- 🔄 Automação completa de sincronização
- 🔄 Expansão para múltiplos bancos

---

## 🛠️ Convenções de Documentação

### **Nomenclatura de Arquivos**

- Formato: `XXX_NOME_DESCRITIVO.md`
- `XXX` = Número cronológico (001, 002, 003...)
- `NOME_DESCRITIVO` = Título em SNAKE_CASE
- Exceções: `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`

### **Estrutura de Pastas**

```
/docs/
├── README.md                    # Este arquivo (índice)
├── Integracao_PROXIMO_CHAT.md  # Contexto rápido Open Finance
│
├── /Desenvolvimento/            # Arquitetura e guias
│   ├── README.md
│   └── XXX_NOME.md
│
├── /Integracao/                 # Integrações externas
│   ├── README.md
│   └── XXX_NOME.md
│
└── /Testing/                    # Testes e qualidade
    ├── README.md
    └── XXX_NOME.md
```

### **Emojis de Seção**

- 🎯 Objetivo
- 📋 Contexto
- 🔧 Implementação
- ✅ Resultados
- 📚 Referências
- ⚠️ Atenção
- 💡 Dica
- 📌 Nota

---

## 🔗 Links Úteis

### **Projeto**

- [Repositório GitHub](https://github.com/lutivix/FinanceiroPY)
- [Issues](https://github.com/lutivix/FinanceiroPY/issues)
- [Releases](https://github.com/lutivix/FinanceiroPY/releases)

### **Tecnologias**

- [Python 3.13+](https://python.org)
- [SQLite](https://sqlite.org)
- [pytest](https://pytest.org)
- [OpenPyXL](https://openpyxl.readthedocs.io/)

### **Open Finance**

- [Pluggy Dashboard](https://dashboard.pluggy.ai/)
- [Pluggy API Docs](https://docs.pluggy.ai/)
- [Banco Central - Open Finance](https://www.bcb.gov.br/estabilidadefinanceira/openfinance)

---

## 📞 Suporte

**Desenvolvedor:** Luciano Costa Fernandes  
**Email:** luti_vix@hotmail.com  
**Projeto:** Agente Financeiro IA v2.0

---

**Última atualização:** 10/11/2025  
**Criado em:** 10/11/2025
