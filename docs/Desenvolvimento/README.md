# 🔧 Desenvolvimento

Documentação técnica, arquitetura, guias de usuário e planejamento do sistema.

---

## 📂 Documentos

| Arquivo                                                            | Descrição                                         | Última Atualização |
| ------------------------------------------------------------------ | ------------------------------------------------- | ------------------ |
| [001_DOCUMENTACAO_TECNICA.md](001_DOCUMENTACAO_TECNICA.md)         | Arquitetura completa, modelos de dados, diagramas | 28/10/2025         |
| [002_GUIA_USUARIO.md](002_GUIA_USUARIO.md)                         | Manual de uso do sistema                          | 24/10/2025         |
| [003_PLANEJAMENTO.md](003_PLANEJAMENTO.md)                         | Roadmap e planejamento de features                | 22/10/2025         |
| [004_RESUMO_RAPIDO.md](004_RESUMO_RAPIDO.md)                       | Guia rápido de referência                         | 24/10/2025         |
| [005_ATUALIZACAO_DOCUMENTACAO.md](005_ATUALIZACAO_DOCUMENTACAO.md) | Log de atualizações da documentação               | 28/10/2025         |
| [006_INDICE_DOCUMENTACAO.md](006_INDICE_DOCUMENTACAO.md)           | Índice detalhado (legado)                         | 24/10/2025         |

---

## 🎯 Tópicos Principais

### **Arquitetura do Sistema**

- **Models:** Transaction, Category, BankProcessor
- **Services:** CategorizationService, FileProcessingService, ReportService
- **Database:** SQLite com schema otimizado
- **Ver:** [001_DOCUMENTACAO_TECNICA.md](001_DOCUMENTACAO_TECNICA.md)

### **Fluxo de Processamento**

1. Detecção automática de arquivos (últimos 12 meses)
2. Processamento por tipo (Itaú, Latam, PIX)
3. Categorização automática (98.2% precisão)
4. Consolidação e exportação Excel

**Ver:** [002_GUIA_USUARIO.md](002_GUIA_USUARIO.md)

### **Sistema de Categorização**

- 584 categorias otimizadas
- Aprendizado contínuo via Excel
- Proteção contra duplicatas
- Base de conhecimento SQLite

**Ver:** [001_DOCUMENTACAO_TECNICA.md#sistema-de-aprendizado](001_DOCUMENTACAO_TECNICA.md)

---

## 🔗 Links Relacionados

- [📋 ../README.md](../README.md) - Documentação principal
- [🧪 ../Testing/](../Testing/) - Testes e qualidade
- [🔗 ../Integracao/](../Integracao/) - Integrações externas

---

**Criado em:** 10/11/2025
