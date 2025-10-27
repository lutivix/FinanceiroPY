# 🧪 Guia de Testes - Agente Financeiro IA

> **Documentação completa do sistema de testes automatizados**

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Instalação](#instalação)
- [Executando Testes](#executando-testes)
- [Estrutura de Testes](#estrutura-de-testes)
- [Escrevendo Novos Testes](#escrevendo-novos-testes)
- [Fixtures Disponíveis](#fixtures-disponíveis)
- [Cobertura de Código](#cobertura-de-código)

---

## 🎯 Visão Geral

O projeto utiliza **pytest** como framework de testes com as seguintes características:

- ✅ **Testes unitários** para processadores, serviços e repositórios
- ✅ **Fixtures reutilizáveis** para dados de teste
- ✅ **Dados anonimizados** para testes seguros
- ✅ **Cobertura de código** com relatórios detalhados
- ✅ **Testes parametrizados** para múltiplos cenários

**Meta de Cobertura:** 70%+ de cobertura de código

---

## 📦 Instalação

### 1. Instalar Dependências

```bash
# Windows (recomendado)
py -m pip install -r requirements.txt

# Linux/macOS
pip install -r requirements.txt
```

### 2. Verificar Instalação

```bash
# Windows
py -m pytest --version

# Linux/macOS
pytest --version

# Deve mostrar algo como: pytest 8.4.2
```

---

## ▶️ Executando Testes

### Comandos Básicos

```bash
# Windows - Rodar todos os testes
py -m pytest tests/ -v

# Linux/macOS - Rodar todos os testes
pytest tests/ -v

# Rodar testes de um arquivo específico
py -m pytest tests/test_processors/test_pix.py -v

# Rodar testes de uma classe específica
py -m pytest tests/test_processors/test_pix.py::TestPixProcessor -v

# Rodar um teste específico
py -m pytest tests/test_processors/test_pix.py::TestPixProcessor::test_can_process_valid_pix_file -v
```

### Testes com Cobertura

```bash
# Windows - Rodar testes com cobertura
py -m pytest tests/ --cov=backend/src --cov-report=html

# Linux/macOS
pytest tests/ --cov=backend/src --cov-report=html

# Visualizar relatório HTML
# Abra o arquivo: htmlcov/index.html no navegador
```

### Testes por Categoria

```bash
# Apenas testes unitários
py -m pytest -m unit

# Apenas testes de integração
py -m pytest -m integration

# Pular testes lentos
py -m pytest -m "not slow"
```

### Modo de Desenvolvimento

```bash
# Rodar testes e parar no primeiro erro
py -m pytest tests/ -x

# Rodar testes e mostrar variáveis locais em falhas
py -m pytest tests/ -l

# Rodar apenas testes que falharam na última execução
py -m pytest tests/ --lf

# Modo verboso com saída completa
py -m pytest tests/ -vv --tb=long
```

---

## 📁 Estrutura de Testes

```
tests/
├── __init__.py                       # Módulo de testes
├── conftest.py                       # Fixtures globais
│
├── fixtures/                         # Dados de teste
│   ├── sample_pix.txt               # Arquivo PIX de exemplo
│   └── expected_results.json        # Resultados esperados
│
├── test_processors/                  # Testes de processadores
│   ├── __init__.py
│   ├── test_base.py                 # Testes da classe base
│   ├── test_pix.py                  # Testes do processador PIX
│   └── test_cards.py                # Testes de cartões (TODO)
│
├── test_services/                    # Testes de serviços
│   ├── __init__.py
│   ├── test_categorization.py       # Testes de categorização
│   ├── test_file_processing.py      # Testes de processamento (TODO)
│   └── test_report.py               # Testes de relatórios (TODO)
│
└── test_database/                    # Testes de banco de dados
    ├── __init__.py
    ├── test_transaction_repository.py  # Testes de transações
    └── test_category_repository.py     # Testes de categorias (TODO)
```

---

## ✍️ Escrevendo Novos Testes

### Estrutura Básica

```python
"""
Descrição do módulo de teste
"""

import pytest
from pathlib import Path

# Imports condicionais para evitar erros antes da instalação
try:
    from processors.pix import PixProcessor
except ImportError:
    pytest.skip("Módulos ainda não disponíveis", allow_module_level=True)


class TestMinhaFuncionalidade:
    """Testes para minha funcionalidade."""

    @pytest.fixture
    def setup_dados(self):
        """Prepara dados para os testes."""
        return {"chave": "valor"}

    def test_comportamento_esperado(self, setup_dados):
        """Testa comportamento esperado."""
        resultado = minha_funcao(setup_dados)

        assert resultado is not None
        assert resultado == "esperado"

    @pytest.mark.parametrize("entrada,saida_esperada", [
        ("input1", "output1"),
        ("input2", "output2"),
    ])
    def test_multiplos_casos(self, entrada, saida_esperada):
        """Testa múltiplos casos."""
        assert minha_funcao(entrada) == saida_esperada
```

### Boas Práticas

1. **Nomes descritivos**: `test_should_categorize_food_transactions`
2. **Um assert por conceito**: Foque em testar uma coisa por teste
3. **AAA Pattern**: Arrange (preparar), Act (executar), Assert (verificar)
4. **Use fixtures**: Reutilize setup comum
5. **Docstrings**: Documente o que cada teste faz
6. **Parametrize**: Use `@pytest.mark.parametrize` para múltiplos casos

---

## 🎁 Fixtures Disponíveis

### Fixtures Globais (conftest.py)

```python
# Diretórios e arquivos temporários
temp_dir                  # Diretório temporário limpo
test_db_path             # Caminho para DB de teste

# Configuração
mock_config              # Configuração mock para testes

# Dados de teste
sample_transactions      # Lista de transações de exemplo
sample_categories        # Dicionário de categorias
sample_pix_content       # Conteúdo de arquivo PIX
sample_pix_file          # Arquivo PIX de teste completo

# Banco de dados
initialized_db           # DB inicializado com estrutura e dados

# Processadores
mock_pix_processor       # Processador PIX mock
mock_card_processor      # Processador de cartões mock
```

### Usando Fixtures

```python
def test_meu_teste(sample_transactions, test_db_path):
    """Usa fixtures no teste."""
    # Fixtures são injetadas automaticamente
    assert len(sample_transactions) > 0
    assert test_db_path.exists()
```

---

## 📊 Cobertura de Código

### Gerar Relatório

```bash
# Gerar relatório HTML
pytest --cov=backend/src --cov-report=html

# Gerar relatório no terminal
pytest --cov=backend/src --cov-report=term

# Gerar relatório XML (para CI/CD)
pytest --cov=backend/src --cov-report=xml
```

### Visualizar Cobertura

```bash
# Abrir relatório HTML no navegador
start htmlcov/index.html       # Windows
open htmlcov/index.html        # macOS
xdg-open htmlcov/index.html    # Linux
```

### Interpretar Resultados

- **Verde**: Linhas cobertas por testes
- **Vermelho**: Linhas não cobertas
- **Amarelo**: Parcialmente cobertas (branches)

**Meta:** Manter cobertura acima de 70%

---

### Workflow de Desenvolvimento

### 1. Antes de Desenvolver

```bash
# Garantir que testes existentes passam
py -m pytest tests/ -v
```

### 2. Durante o Desenvolvimento

```bash
# Rodar testes relacionados ao código alterado
py -m pytest tests/test_processors/test_pix.py -v
```

### 3. Após Implementar Funcionalidade

```bash
# Criar teste para nova funcionalidade
# Rodar todos os testes
py -m pytest tests/ --cov=backend/src

# Verificar cobertura
```

### 4. Antes de Commit

```bash
# Rodar todos os testes com cobertura
py -m pytest tests/ --cov=backend/src --cov-report=term

# Verificar se cobertura está acima de 70%
```

---

## 🐛 Debugging de Testes

### Ver Saída Completa

```bash
# Mostrar prints e logs
py -m pytest tests/ -s

# Mostrar variáveis em falhas
py -m pytest tests/ -l
```

### Debug Interativo

```python
def test_com_debug():
    """Teste com ponto de parada."""
    import pdb; pdb.set_trace()  # Ponto de parada

    resultado = funcao()
    assert resultado == esperado
```

### Ver Apenas Falhas

```bash
# Modo quiet - mostra apenas falhas
py -m pytest tests/ -q

# Mostrar apenas resumo
py -m pytest tests/ --tb=short
```

---

## 📝 Checklist de Qualidade

Antes de finalizar um Pull Request, certifique-se:

- [ ] ✅ Todos os testes passam: `py -m pytest tests/`
- [ ] ✅ Cobertura acima de 70%: `py -m pytest tests/ --cov`
- [ ] ✅ Código formatado: `py -m black backend/src/`
- [ ] ✅ Sem erros de lint: `py -m flake8 backend/src/`
- [ ] ✅ Testes documentados com docstrings
- [ ] ✅ Fixtures reutilizadas quando possível
- [ ] ✅ Dados sensíveis não incluídos nos testes

---

## 🆘 Problemas Comuns

### Pytest não encontrado

```bash
pip install pytest pytest-cov
```

### Imports não funcionam

```bash
# Certifique-se de estar no diretório raiz
cd /caminho/para/Financeiro

# Verifique PYTHONPATH no conftest.py
```

### Testes passam localmente mas falham no CI

- Verifique dependências no `requirements.txt`
- Confirme que dados de teste estão commitados
- Verifique caminhos absolutos vs relativos

---

## 📚 Recursos Adicionais

- [Documentação Pytest](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Guia de Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Parametrize](https://docs.pytest.org/en/stable/parametrize.html)

---

**✨ Mantenha os testes atualizados e a cobertura alta!**
