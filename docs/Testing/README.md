# 🧪 Testing

Documentação sobre estratégia de testes, infraestrutura, cobertura e qualidade do código.

---

## 📂 Documentos

| Arquivo                                                            | Descrição                                  | Última Atualização |
| ------------------------------------------------------------------ | ------------------------------------------ | ------------------ |
| [001_TESTING.md](001_TESTING.md)                                   | Estratégia de testes e configuração pytest | 24/10/2025         |
| [002_SEMANA1_CONCLUSAO.md](002_SEMANA1_CONCLUSAO.md)               | Relatório Semana 1 - Setup infraestrutura  | 24/10/2025         |
| [003_SEMANA2_PRONTIDAO.md](003_SEMANA2_PRONTIDAO.md)               | Status de prontidão dos testes             | 28/10/2025         |
| [004_SEMANA2_RESUMO_EXECUTIVO.md](004_SEMANA2_RESUMO_EXECUTIVO.md) | Resumo executivo Semana 2                  | 28/10/2025         |

---

## 📊 Status Atual

### **Testes Implementados**

- ✅ **119 testes passing** (94% funcional)
- ⚠️ **8 testes to fix** (6% pendentes)
- 📊 **Cobertura:** 35.34% (meta: 70%)
- 🎯 **Performance:** 98.2% precisão em produção

### **Distribuição de Testes**

```
tests/
├── test_database/        # 15 testes - Database operations
├── test_models/          # 8 testes  - Models (Transaction, Category)
├── test_processors/      # 30 testes - File processors (Itaú, Latam, PIX)
├── test_services/        # 45 testes - Services (Categorization, Reports)
└── test_integration/     # 21 testes - Integration flows
```

---

## 🎯 Objetivos de Qualidade

### **Cobertura por Módulo**

| Módulo           | Cobertura Atual | Meta | Status     |
| ---------------- | --------------- | ---- | ---------- |
| **Models**       | 45%             | 90%  | 🔴 Crítico |
| **Database**     | 40%             | 80%  | 🔴 Crítico |
| **Processors**   | 55%             | 85%  | 🟡 Médio   |
| **Services**     | 30%             | 80%  | 🔴 Crítico |
| **Utils**        | 25%             | 70%  | 🔴 Crítico |
| **Integrations** | 0%              | 70%  | 🔴 Crítico |

**Ver detalhes:** [003_SEMANA2_PRONTIDAO.md](003_SEMANA2_PRONTIDAO.md)

---

## 🛠️ Infraestrutura

### **Framework**

- **pytest:** 8.3.3
- **pytest-cov:** 6.0.0
- **pytest-mock:** 3.14.0

### **Configuração**

- **Arquivo:** `pytest.ini` (raiz do projeto)
- **Fixtures:** `tests/conftest.py`
- **Test Data:** `tests/fixtures/`

### **Execução**

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=backend/src --cov-report=html

# Módulo específico
pytest tests/test_services/

# Teste específico
pytest tests/test_services/test_categorization_service.py::test_learn_from_excel
```

**Ver:** [001_TESTING.md](001_TESTING.md)

---

## 📈 Estratégia de Testes

### **Pirâmide de Testes**

```
        /\
       /E2E\          10% - Integration (21 testes)
      /------\
     /  API   \       30% - Services (45 testes)
    /----------\
   /   Unit     \     60% - Models + Utils (53 testes)
  /--------------\
```

### **Tipos de Teste**

#### **1. Testes Unitários (53 testes)**

- Models (Transaction, Category)
- Database repositories
- Utility functions
- Processors individuais

#### **2. Testes de Serviço (45 testes)**

- CategorizationService
- FileProcessingService
- ReportService
- FinancialAgentService

#### **3. Testes de Integração (21 testes)**

- Fluxo completo de processamento
- Integração entre serviços
- Persistência de dados
- Geração de relatórios

**Ver:** [001_TESTING.md#estratégia](001_TESTING.md)

---

## 🐛 Testes Pendentes (To Fix)

| Teste                                   | Módulo                | Motivo          | Prioridade |
| --------------------------------------- | --------------------- | --------------- | ---------- |
| `test_learn_from_excel_with_duplicates` | CategorizationService | Mock incorreto  | 🔴 Alta    |
| `test_find_recent_files_empty`          | FileProcessingService | Edge case       | 🟡 Média   |
| `test_process_invalid_format`           | Processors            | Error handling  | 🟡 Média   |
| `test_database_connection_error`        | Database              | Mock de exceção | 🟡 Média   |
| `test_concurrent_categorization`        | Integration           | Threading       | 🔵 Baixa   |
| `test_large_file_processing`            | Integration           | Performance     | 🔵 Baixa   |
| `test_memory_leak_detection`            | Integration           | Profiling       | 🔵 Baixa   |
| `test_unicode_handling`                 | Processors            | Encoding        | 🟡 Média   |

**Ver:** [003_SEMANA2_PRONTIDAO.md#testes-pendentes](003_SEMANA2_PRONTIDAO.md)

---

## 📊 Relatórios de Cobertura

### **HTML Report**

- **Localização:** `htmlcov/index.html`
- **Geração:** `pytest --cov=backend/src --cov-report=html`
- **Navegação:** Abrir `htmlcov/index.html` no browser

### **Console Report**

```bash
pytest --cov=backend/src --cov-report=term-missing
```

### **CI/CD Integration**

```bash
# Para CI (sem HTML)
pytest --cov=backend/src --cov-report=xml
```

**Ver:** [001_TESTING.md#relatórios](001_TESTING.md)

---

## 🎯 Roadmap de Testes

### **Semana 3: Correção dos Pendentes**

- [ ] Corrigir 8 testes pendentes
- [ ] Aumentar cobertura para 50%
- [ ] Adicionar testes de integração Pluggy
- [ ] Implementar testes de performance

### **Semana 4: Expansão**

- [ ] Cobertura de 70% em Models
- [ ] Cobertura de 60% em Services
- [ ] Testes E2E completos
- [ ] Benchmark de performance

### **Semana 5: CI/CD**

- [ ] Configurar GitHub Actions
- [ ] Testes automáticos em PRs
- [ ] Quality gates (cobertura mínima)
- [ ] Relatórios automatizados

**Ver:** [004_SEMANA2_RESUMO_EXECUTIVO.md#próximos-passos](004_SEMANA2_RESUMO_EXECUTIVO.md)

---

## 🔧 Boas Práticas

### **Nomenclatura**

```python
# Padrão: test_<função>_<cenário>_<resultado_esperado>
def test_categorize_transaction_with_known_description_returns_category():
    pass

def test_process_file_with_invalid_format_raises_exception():
    pass
```

### **Fixtures**

```python
# Reutilizar fixtures de conftest.py
@pytest.fixture
def sample_transaction():
    return Transaction(
        description="COMPRA MERCADO",
        amount=-100.50,
        date=datetime.now()
    )
```

### **Mocking**

```python
# Usar mocker (pytest-mock)
def test_api_call(mocker):
    mock_response = mocker.patch('requests.get')
    mock_response.return_value.json.return_value = {'status': 'ok'}
    # Test code
```

**Ver:** [001_TESTING.md#boas-práticas](001_TESTING.md)

---

## 📚 Recursos

### **Documentação**

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [pytest-mock](https://pytest-mock.readthedocs.io/)

### **Tutoriais**

- [Real Python - pytest](https://realpython.com/pytest-python-testing/)
- [Test-Driven Development with Python](https://www.obeythetestinggoat.com/)

---

## 🔗 Links Relacionados

- [📋 ../README.md](../README.md) - Documentação principal
- [🔧 ../Desenvolvimento/](../Desenvolvimento/) - Arquitetura
- [🔗 ../Integracao/](../Integracao/) - Integrações

---

**Criado em:** 10/11/2025  
**Status:** 119/127 testes passing (94% funcional)  
**Meta:** 70% de cobertura
