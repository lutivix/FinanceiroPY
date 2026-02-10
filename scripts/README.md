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

**Scripts Bash de Automação (na raiz do projeto):**
- `agente_financeiro_completo.sh` - Menu interativo com todas funcionalidades
- `iniciar_sistemas.sh` - Gerenciador de sistemas (Financeiro, BCE)
- `iniciar_sistemas.bat` - Versão Windows (fallback)

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

### **3. Scripts Bash de Automação** 🔧

Scripts shell para automação de tarefas e gerenciamento de sistemas.

**Localização:** Raiz do projeto

**Scripts principais:**

- **`agente_financeiro_completo.sh`** - Menu interativo com 9 opções:
  1. Processamento completo
  2. Processar apenas transações
  3-5. Atualizar dicionários (Excel, Controle, DB)
  6. Limpar categorias duplicadas
  7. Iniciar/Parar Dashboard
  8. Instalar dependências do dashboard
  9. Informações do ambiente

- **`iniciar_sistemas.sh`** - Gerenciador de sistemas múltiplos:
  - Financeiro backend
  - BCE backend
  - BCE frontend
  - Controle de PIDs e status

- **`iniciar_sistemas.bat`** - Versão Windows (plano B)

#### **⚡ Solução Técnica: UTF-8 no Git Bash**

**Problema:** `conda run` não preserva TTY, resultando em caracteres UTF-8 quebrados (emojis e acentos aparecem como `ðŸ"„`, `Ã§Ãµ`).

**Solução:** Usar `bash -c` com `conda activate` em vez de `conda run`:

```bash
# ❌ NÃO funciona (não preserva TTY)
run_in_conda() {
    "$CONDA_EXE" run -n "$CONDA_ENV" "$@"
}

# ✅ FUNCIONA (preserva TTY e UTF-8)
run_in_conda() {
    bash -c "eval \"\$('$CONDA_EXE' shell.bash hook)\" && conda activate '$CONDA_ENV' && $*"
}
```

**Motivo:** 
- `conda run` cria subprocesso sem detecção de TTY
- `bash -c + conda activate` mantém terminal interativo
- Python detecta TTY e habilita UTF-8 automaticamente
- Emojis e acentos aparecem corretamente: 🎉 ✅ 📊

**Aplicação:**
Todos os scripts que executam Python via conda devem usar este padrão para garantir saída formatada corretamente no Git Bash (Windows).

### **4. Scripts de Automação (.bat)** ⚙️

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
| **Propósito** | Testes manuais de API, ferramentas, automação | Testes automatizados (pytest)    |
| **Execução**  | Manual, ad-hoc, menu interativo    | Automática (CI/CD, pytest)       |
| **Dados**     | Reais ou sandbox                   | Fixtures, mocks                  |
| **Objetivo**  | Validar integração externa, gerenciar sistemas | Validar lógica interna           |
| **Exemplo**   | `teste_pluggy_rest.py`, `agente_financeiro_completo.sh` | `test_transaction_repository.py` |

---

## 🎯 Como Usar

### **Executar scripts bash de automação:**

```bash
# Menu interativo completo
./agente_financeiro_completo.sh

# Gerenciador de sistemas
./iniciar_sistemas.sh

# Windows (Git Bash ou CMD)
iniciar_sistemas.bat
```

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
**Última atualização:** 10/02/2026  
**Mudanças recentes:** Adicionada documentação sobre scripts bash de automação e solução UTF-8 para Git Bash
