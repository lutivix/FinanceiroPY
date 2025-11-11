# 📜 Scripts - Agente Financeiro

> Pasta para scripts utilitários, testes de API e ferramentas auxiliares.

---

## 📂 Estrutura

```
scripts/
├── README.md                    # Este arquivo
│
└── testes/                      # Scripts de teste de API e validação
    ├── teste_pluggy_rest.py     # Teste REST API Pluggy
    ├── verificar_dados_completos.py  # Validação completa Open Finance
    ├── buscar_itau_simples.py   # Fetch Itaú sem emojis
    ├── listar_transacoes_3meses.py   # Demo Mercado Pago
    └── verificar_parcelas.py    # Análise de parcelas
```

---

## 🎯 Tipos de Scripts

### **1. Testes de API (`/testes/`)** 🔌

Scripts para testar integrações externas (Pluggy, Open Finance, etc).

- **Não são testes unitários** (esses ficam em `/tests/`)
- **São testes manuais** de API para validação
- **Usam dados reais** ou sandbox
- **Propósito:** Debugging, validação, exploração

**Exemplos:**

- `teste_pluggy_rest.py` - Valida REST API Pluggy
- `verificar_dados_completos.py` - Testa todos os endpoints

### **2. Scripts de Produção** 🚀

Scripts que fazem parte do fluxo de trabalho.

**Localização:** `backend/src/` (junto com código principal)

**Exemplos:**

- `gerar_excel_pluggy.py` - Geração de Excel Open Finance
- `atualizar_categoria_vestuario.py` - Manutenção de categorias
- `limpar_categorias.py` - Limpeza de duplicatas

### **3. Scripts de Automação (.bat)** ⚙️

Scripts batch para execução rápida no Windows.

**Localização:** `backend/src/` (perto dos .py correspondentes)

**Exemplos:**

- `agente_financeiro.bat`
- `atualiza_dicionario.bat`

---

## 🚫 Scripts Obsoletos

Scripts que não funcionam mais ou foram substituídos.

**Localização:** `backend/src/_deprecated/`

**Motivo comum:** Usam SDK com bug, substituídos por REST API

---

## 📋 Diferença: /scripts/ vs /tests/

| Aspecto       | `/scripts/`                        | `/tests/`                        |
| ------------- | ---------------------------------- | -------------------------------- |
| **Propósito** | Testes manuais de API, ferramentas | Testes automatizados (pytest)    |
| **Execução**  | Manual, ad-hoc                     | Automática (CI/CD, pytest)       |
| **Dados**     | Reais ou sandbox                   | Fixtures, mocks                  |
| **Objetivo**  | Validar integração externa         | Validar lógica interna           |
| **Exemplo**   | `teste_pluggy_rest.py`             | `test_transaction_repository.py` |

---

## 🎯 Como Usar

### **Executar teste de API:**

```bash
cd scripts/testes
python teste_pluggy_rest.py
```

### **Executar script de produção:**

```bash
cd backend/src
python gerar_excel_pluggy.py
```

### **Executar testes automatizados:**

```bash
pytest tests/
```

---

## 🔗 Links Relacionados

- [📚 docs/README.md](../docs/README.md) - Documentação completa
- [🧪 tests/](../tests/) - Testes automatizados (pytest)
- [🔧 backend/src/](../backend/src/) - Scripts de produção
- [🗄️ backend/src/\_deprecated/](../backend/src/_deprecated/) - Scripts obsoletos

---

**Criado em:** 11/11/2025  
**Última atualização:** 11/11/2025
