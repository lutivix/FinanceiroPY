# 🏦 Agente Financeiro IA

> **Automação inteligente para controle financeiro pessoal com aprendizado de máquina**

Um sistema Python que automatiza a categorização e análise de extratos bancários, cartões de crédito e PIX, utilizando machine learning para aprender padrões de gastos e gerar relatórios consolidados.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![SQLite](https://img.shields.io/badge/Database-SQLite-green.svg)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 **Funcionalidades**

### 🤖 **Processamento Automático**

- ✅ **Múltiplas fontes**: Itaú, Latam, PIX (extensível)
- ✅ **Formatos diversos**: XLS, XLSX, TXT, CSV
- ✅ **Detecção inteligente** de tipos de cartão (físico/virtual/recorrente)
- ✅ **Busca automática** de arquivos dos últimos 12 meses

### 🧠 **Sistema de Aprendizado**

- ✅ **Categorização automática** baseada em ML
- ✅ **Mapeamento dinâmico** descrição → categoria
- ✅ **Aprendizado contínuo** com feedback do usuário
- ✅ **Base de conhecimento** persistente em SQLite

### 📊 **Análise e Relatórios**

- ✅ **Consolidação temporal** por mês/ano
- ✅ **Exportação Excel** com dados estruturados
- ✅ **Identificação de padrões** de gastos
- ✅ **Filtros inteligentes** (moedas estrangeiras, duplicatas)

### 🔧 **Tratamento de Dados**

- ✅ **Normalização automática** de descrições
- ✅ **Conversão de moedas** e formatos
- ✅ **Detecção de anomalias** (valores suspeitos)
- ✅ **Backup automático** em banco de dados

## 📁 **Estrutura do Projeto**

```
Financeiro/
├── backend/src/
│   ├── agente_financeiro.py           # 🤖 Script principal
│   ├── atualiza_dicionario.py         # 📚 Atualiza base de conhecimento
│   ├── atualiza_dicionario_controle.py # 📋 Sincroniza com controle manual
│   ├── *.bat                          # 🚀 Scripts de execução Windows
│   └── config.example.ini             # ⚙️ Configuração exemplo
├── dados/                             # 📊 Dados locais (não versionado)
│   ├── db/financeiro.db              # 🗄️ Base de dados principal
│   └── planilhas/                    # 📈 Extratos e relatórios
├── .gitignore                        # 🛡️ Proteção de dados sensíveis
└── README.md                         # 📖 Documentação
```

## ⚡ **Instalação Rápida**

### 1. **Clone o Repositório**

```bash
git clone https://github.com/seu-usuario/financeiro-ai-agent.git
cd financeiro-ai-agent
```

### 2. **Instale as Dependências**

```bash
pip install pandas sqlite3 openpyxl xlrd
```

### 3. **Configure o Ambiente**

```bash
# Copie o arquivo de configuração
cp backend/src/config.example.ini backend/src/config.ini

# Edite com seus caminhos
nano backend/src/config.ini
```

### 4. **Estruture seus Dados**

```bash
# Crie a estrutura de pastas para seus extratos
mkdir -p dados/db dados/planilhas

# Coloque seus arquivos no formato:
# - AAAAMM_Extrato.txt (PIX)
# - AAAAMM_Itau.xls (Cartão Itaú)
# - AAAAMM_Latam.xls (Cartão Latam)
```

## 🎯 **Como Usar**

### **Execução Principal**

```bash
cd backend/src
python agente_financeiro.py
```

### **Atualizar Base de Conhecimento**

```bash
# Após categorizar manualmente no Excel
python atualiza_dicionario.py

# Ou sincronizar com controle pessoal
python atualiza_dicionario_controle.py
```

### **Automatização (Windows)**

```cmd
:: Execute via batch para automação
agente_financeiro.bat
```

## 📋 **Formato dos Arquivos**

### **PIX (TXT/CSV)**

```csv
Data;Descrição;Valor
19/12/2024;PIX QRS PAGFACIL IP19/12;-2,00
20/12/2024;PIX TRANSF ROBERTA20/12;-600,00
```

### **Cartões (XLS/XLSX)**

```
Coluna A: Data (DD/MM/AAAA)
Coluna B: Descrição da transação
Coluna D: Valor (positivo/negativo)
```

## 🧠 **Sistema de Categorização**

### **Categorias Automáticas**

- 💰 **SALÁRIO**: `SISPAG PIX`, `PAGTO REMUNERACAO`
- 📈 **INVESTIMENTOS**: `REND PAGO APLIC`
- 🍕 **ALIMENTAÇÃO**: Restaurantes, delivery, supermercados
- 🚗 **TRANSPORTE**: Uber, combustível, estacionamento
- 🏠 **MORADIA**: Aluguel, condomínio, utilities

### **Aprendizado Contínuo**

```python
# O sistema aprende automaticamente:
"UBER TRIP" → "TRANSPORTE"
"IFOOD DELIVERY" → "ALIMENTAÇÃO"
"NETFLIX ASSINATURA" → "ENTRETENIMENTO"
```

## 🔧 **Configuração Avançada**

### **config.ini**

```ini
[PATHS]
diretorio_arquivos = /caminho/para/seus/dados
backup_path = /caminho/para/backup

[CATEGORIAS]
categoria_padrao = A definir
auto_categorize = true

[PROCESSAMENTO]
meses_retroativos = 12
filtrar_moedas_estrangeiras = true
```

## 📊 **Saídas Geradas**

### **Excel Consolidado**

- 📅 **Data**: Data da transação
- 📝 **Descrição**: Descrição normalizada
- 🏪 **Fonte**: Origem (Itaú Master, Latam Visa, PIX)
- 💵 **Valor**: Valor da transação
- 🏷️ **Categoria**: Categoria automaticamente atribuída
- 📆 **MêsComp**: Mês de competência

### **Base SQLite**

```sql
-- Transações processadas
SELECT * FROM lancamentos;

-- Base de aprendizado
SELECT * FROM categorias_aprendidas;
```

## 🛠️ **Próximas Funcionalidades**

- [ ] 🌐 **Dashboard Web** interativo
- [ ] 📱 **API REST** para integração
- [ ] 🔮 **Análise preditiva** de gastos
- [ ] 🚨 **Alertas de orçamento**
- [ ] 📧 **Relatórios por email**
- [ ] 🔄 **Sincronização com bancos** (Open Banking)

## 🤝 **Contribuindo**

1. **Fork** o projeto
2. **Clone** seu fork
3. **Crie** uma branch para sua feature
4. **Commit** suas mudanças
5. **Push** para a branch
6. **Abra** um Pull Request

```bash
git checkout -b feature/nova-funcionalidade
git commit -m "Adiciona nova funcionalidade"
git push origin feature/nova-funcionalidade
```

## 📈 **Roadmap**

- **v1.1**: Interface web com Streamlit
- **v1.2**: Análise preditiva com scikit-learn
- **v1.3**: Integração Open Banking
- **v2.0**: Aplicativo mobile React Native

## ⚠️ **Importante**

- 🛡️ **Dados sensíveis**: Mantenha seus extratos fora do Git
- 🔒 **Segurança**: Use sempre `.env` para credenciais
- 💾 **Backup**: Faça backup regular do `financeiro.db`
- 🧪 **Teste**: Sempre teste com dados de exemplo primeiro

## 📄 **Licença**

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 **Autor**

**Seu Nome**

- 🐙 GitHub: [@seu-usuario](https://github.com/seu-usuario)
- 💼 LinkedIn: [seu-perfil](https://linkedin.com/in/seu-perfil)
- 📧 Email: seu.email@exemplo.com

---

<div align="center">
  <p>⭐ <strong>Se este projeto te ajudou, considere dar uma estrela!</strong> ⭐</p>
  <p>💡 <strong>Sugestões e contribuições são sempre bem-vindas!</strong> 💡</p>
</div>
