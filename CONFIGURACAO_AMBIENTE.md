# 🐍 Configuração do Ambiente Python - Projeto Financeiro

## ✅ Status Atual (28/10/2025)

### Ambientes Python Disponíveis:

1. **Anaconda Base (Python 3.13.5)**
   - Localização: `C:\ProgramData\anaconda3\python.exe`
   - Uso: Gerenciamento geral do Conda
2. **Ambiente Financeiro (Python 3.11.14)** ⭐ **USAR ESTE**

   - Localização: `C:\Users\luti_\.conda\envs\financeiro\python.exe`
   - Uso: **Projeto Financeiro atual**
   - Dependências instaladas: ✅ pandas, openpyxl, pytest, etc.

3. **Python Global (3.13.2)**
   - Localização: `C:\Python313\python.exe`
   - Uso: Instalação separada (pode ignorar)

---

## 🎯 Configuração Recomendada para VS Code

### No VS Code, selecione:

```
Python 3.11.14 (financeiro)
~\.conda\envs\financeiro\python.exe
```

### Comando para ativar manualmente no terminal:

```bash
conda activate financeiro
```

### PATH do Windows:

O PATH atual está CORRETO. Mantém:

- ✅ `C:\ProgramData\anaconda3`
- ✅ `C:\ProgramData\anaconda3\Scripts`
- ✅ `C:\ProgramData\anaconda3\condabin`

---

## 📦 Dependências Instaladas no Ambiente 'financeiro':

- ✅ pandas (2.3.3)
- ✅ openpyxl (3.1.5)
- ✅ xlrd (2.0.2)
- ✅ pytest (8.4.2)
- ✅ pytest-cov (7.0.0)
- ✅ pytest-mock (3.15.1)
- ✅ black (25.9.0)
- ✅ flake8 (7.3.0)
- ✅ isort (7.0.0)
- ✅ tqdm (4.67.1)
- ✅ colorama (0.4.6)
- ✅ configparser (7.2.0)

---

## 🚀 Como Executar os Scripts

### Opção 1: Usando os arquivos .bat (RECOMENDADO)

Todos os `.bat` foram atualizados para usar o ambiente `financeiro` automaticamente:

```batch
agente_financeiro_completo.bat
agente_financeiro_simples.bat
agente_financeiro.bat
atualiza_dicionario.bat
atualiza_dicionario_controle.bat
```

### Opção 2: Via terminal do VS Code

```bash
conda activate financeiro
python backend/src/agente_financeiro.py
```

### Opção 3: Comando direto

```bash
C:/ProgramData/anaconda3/Scripts/conda.exe run -n financeiro python backend/src/agente_financeiro.py
```

---

## 🔧 Comandos Úteis

### Verificar ambiente ativo:

```bash
conda env list
```

### Verificar Python do ambiente:

```bash
conda activate financeiro
python --version
```

### Listar pacotes instalados:

```bash
conda activate financeiro
pip list
```

### Instalar novo pacote:

```bash
conda activate financeiro
pip install <nome_pacote>
```

### Recriar ambiente (se necessário):

```bash
conda env remove -n financeiro
conda create -n financeiro python=3.11 -y
conda activate financeiro
pip install -r requirements.txt
```

---

## ⚠️ Observações Importantes

1. **NÃO remova o Anaconda base** - ele gerencia os ambientes
2. **USE sempre o ambiente 'financeiro'** para este projeto
3. **Os arquivos .bat já estão configurados** - apenas execute-os
4. **No VS Code, sempre selecione** o interpretador `financeiro`
5. **Python 3.13.2 global** pode ficar, mas não interfere se usar conda

---

## 📞 Troubleshooting

### Problema: "Python não encontrado"

**Solução:** Selecione o interpretador correto no VS Code (Ctrl+Shift+P → "Python: Select Interpreter")

### Problema: "ModuleNotFoundError"

**Solução:** Certifique-se que está usando o ambiente correto:

```bash
conda activate financeiro
pip install -r requirements.txt
```

### Problema: ".bat não funciona"

**Solução:** Execute diretamente do Explorer (duplo clique) ou pelo terminal do projeto

---

## ✅ Checklist de Configuração

- [x] Ambiente Conda 'financeiro' criado
- [x] Python 3.11.14 instalado no ambiente
- [x] Todas dependências do requirements.txt instaladas
- [x] Arquivos .bat atualizados para usar Conda
- [x] VS Code configurado (.vscode/settings.json)
- [ ] **Selecionar interpretador 'financeiro' no VS Code** ⬅️ **FAÇA ISSO AGORA!**

---

## 🎉 Pronto para Usar!

Após selecionar o interpretador correto no VS Code, você pode:

1. Executar qualquer `.bat` do projeto
2. Rodar scripts Python diretamente no VS Code
3. Usar o terminal integrado com `conda activate financeiro`

**Qualquer dúvida, consulte este guia!** 📚
