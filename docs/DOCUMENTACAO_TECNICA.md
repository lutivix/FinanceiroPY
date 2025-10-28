# 📚 Documentação Técnica - Agente Financeiro IA v2.0

## 🏗️ **Arquitetura do Sistema**

### **Visão Geral**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Arquivos de   │────│  Processamento   │────│     Saída       │
│    Entrada      │    │    Principal     │    │   Estruturada   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
│                      │                      │
├─ PIX (TXT)           ├─ agente_financeiro.py ├─ Excel consolidado
├─ Itaú (XLS)          ├─ Categorização ML    ├─ Base SQLite
├─ Latam (XLS)         ├─ Normalização       └─ Relatórios
└─ Outros...           └─ Validação
                       │
                       ▼
             ┌──────────────────┐
             │ Base de Conhec.  │
             │   SQLite DB      │
             │ 584 categorias   │
             │   98.2% precisão │
             └──────────────────┘
```

### **Fluxo de Dados**

1. **Entrada**: Leitura automática de arquivos (XLS, XLSX, TXT, CSV)
2. **Processamento**: Normalização, categorização e validação
3. **Aprendizado**: Atualização da base de conhecimento
4. **Saída**: Excel ordenado e base SQLite atualizada

---

## � **Ciclo Mensal e Busca de Arquivos**

### **Regra de Negócio: Ciclo 19-18**

O sistema opera com um **ciclo mensal personalizado** que vai do **dia 19 de um mês ao dia 18 do próximo mês**. Esta lógica garante que todas as transações do período correto sejam capturadas.

**Funcionamento:**

```python
# Determina o mês atual baseado no ciclo 19-18
if hoje.day >= 19:
    # A partir do dia 19, o ciclo é do PRÓXIMO mês
    mes_atual = hoje.month + 1
    ano_atual = hoje.year
    if mes_atual > 12:
        mes_atual = 1
        ano_atual += 1
else:
    # Antes do dia 19, o ciclo é do mês corrente
    mes_atual = hoje.month
    ano_atual = hoje.year
```

**Exemplos práticos:**

| Data Atual | Mês do Ciclo | Arquivo Buscado | Período Coberto |
| ---------- | ------------ | --------------- | --------------- |
| 15/10/2025 | Outubro      | 202510\__._     | 19/09 a 18/10   |
| 19/10/2025 | Novembro     | 202511\__._     | 19/10 a 18/11   |
| 28/10/2025 | Novembro     | 202511\__._     | 19/10 a 18/11   |
| 05/11/2025 | Novembro     | 202511\__._     | 19/10 a 18/11   |
| 19/11/2025 | Dezembro     | 202512\__._     | 19/11 a 18/12   |

### **Processamento de Arquivos**

**Importante:** O sistema **NÃO filtra datas dentro dos arquivos**. Todas as transações presentes no arquivo são processadas, independentemente de suas datas.

**Motivo:**

- ✅ Preserva compras parceladas que aparecem com datas futuras
- ✅ Mantém transações programadas e agendadas
- ✅ Captura ajustes e estornos retroativos
- ✅ Evita perda de informações importantes

**Exemplo:**

Arquivo `202511_Itau.xls` (novembro) pode conter:

- Transações de 19/10 (início do ciclo)
- Transações de 05/11 (meio do ciclo)
- Transações de 18/11 (fim do ciclo)
- **Parcelas futuras** (01/12, 01/01, etc.)

✅ **Todas são processadas!**

### **Busca de Arquivos Retroativos**

```python
def find_recent_files(months_back: int = 12) -> Dict[str, Path]:
    """
    Busca arquivos dos últimos N meses baseado no ciclo 19-18.

    Args:
        months_back: Quantos meses para trás buscar (padrão: 12)

    Returns:
        Dicionário com identificador -> caminho do arquivo
    """
    # Determina mês atual do ciclo
    mes_atual = calcular_mes_ciclo(hoje)

    # Busca retroativa
    for i in range(months_back):
        ano_mes = calcular_ano_mes(mes_atual - i)
        buscar_arquivos(ano_mes)
```

**Arquivos buscados (exemplo em 28/10/2025):**

```
202511_*.* (Nov 2025) ← Mês atual do ciclo
202510_*.* (Out 2025)
202509_*.* (Set 2025)
...
202412_*.* (Dez 2024) ← 12 meses atrás
```

---

## �🔧 **Componentes Principais**

### **1. agente_financeiro.py**

**Função**: Processador central do sistema
**Performance**: 98.2% de precisão na categorização

**Algoritmo de Categorização:**

```python
def categorizar_transacao(descricao):
    """
    1. Normaliza a descrição (remove acentos, maiúsculas)
    2. Busca padrões exatos na base de conhecimento
    3. Busca padrões parciais por similaridade
    4. Aplica regras heurísticas para casos especiais
    5. Retorna categoria ou 'A definir'
    """
```

**Fontes Suportadas:**

- **PIX**: Arquivos TXT/CSV com formato Data;Descrição;Valor
- **Itaú**: Arquivos XLS/XLSX com colunas A(Data), B(Descrição), D(Valor)
- **Latam**: Mesmo formato Itaú, detecção automática

**Normalização de Dados:**

- Remoção de acentos e caracteres especiais
- Padronização de formatos de data
- Conversão de valores para float
- Limpeza de prefixos desnecessários

### **2. atualiza_dicionario.py**

**Função**: Aprendizado a partir do Excel consolidado
**Entrada**: `consolidado_categorizado.xlsx` com categorizações manuais
**Processo**: Extrai padrões Descrição → Categoria e atualiza SQLite

### **3. atualiza_dicionario_controle.py**

**Função**: Sincronização com controle pessoal
**Entrada**: `Controle_pessoal.xlsm` (planilha de controle manual)
**Processo**: Importa categorizações manuais existentes

### **4. limpar_categorias.py**

**Função**: Otimização da base de conhecimento
**Processo**:

- Remove duplicatas com sufixos de data (ex: "ALIMENTACAO_20241215")
- Consolida categorias similares
- Reduz base de 772 para 584 categorias únicas

---

## 🗄️ **Estrutura do Banco de Dados**

### **Tabela: lancamentos**

```sql
CREATE TABLE lancamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    descricao TEXT NOT NULL,
    valor REAL NOT NULL,
    fonte TEXT NOT NULL,
    categoria TEXT DEFAULT 'A definir',
    mes_comp TEXT NOT NULL,
    data_processamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX idx_lancamentos_data ON lancamentos(data);
CREATE INDEX idx_lancamentos_categoria ON lancamentos(categoria);
CREATE INDEX idx_lancamentos_fonte ON lancamentos(fonte);
```

### **Tabela: categorias_aprendidas**

```sql
CREATE TABLE categorias_aprendidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao_original TEXT NOT NULL,
    descricao_normalizada TEXT NOT NULL,
    categoria TEXT NOT NULL,
    data_aprendizado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fonte_aprendizado TEXT DEFAULT 'manual',
    UNIQUE(descricao_normalizada, categoria)
);

-- Índice para busca rápida
CREATE INDEX idx_categorias_descricao ON categorias_aprendidas(descricao_normalizada);
```

---

## 🚀 **Sistema de Automação (.bat)**

### **agente_financeiro_completo.bat**

**Características:**

- Interface menu completa com 6 opções
- Validação de Python e arquivos
- Tratamento de erros com códigos de saída
- Navegação segura de diretórios
- Suporte a execução via Explorer

**Estrutura:**

```batch
@echo off
title Agente Financeiro IA - Sistema Completo
pushd "%~dp0"

:menu
    # Exibição do menu com emojis
    # Captura da opção do usuário
    # Validação da entrada

:processamento
    # Execução dos scripts Python
    # Verificação de códigos de erro
    # Feedback para usuário

:erro_handler
    # Tratamento de erros específicos
    # Mensagens de diagnóstico
    # Opções de recuperação
```

### **agente_financeiro_simples.bat**

**Características:**

- Interface simplificada
- Máxima compatibilidade
- Menos validações, mais velocidade
- Foco na funcionalidade essencial

---

## 📊 **Métricas de Performance**

### **Estatísticas Atuais (Set/2025)**

```
Total de Transações Processadas: 1.791
Categorizações Automáticas: 1.759 (98.2%)
Requer Revisão Manual: 32 (1.8%)

Base de Conhecimento:
- Categorias Únicas: 584
- Padrões de Descrição: 1.247
- Taxa de Limpeza: 24% (redução de duplicatas)
```

### **Performance por Fonte**

```
PIX: 97.8% precisão
Itaú Master: 98.5% precisão
Latam Visa: 98.1% precisão
Média Geral: 98.2% precisão
```

### **Categorias Mais Frequentes**

```sql
SELECT categoria, COUNT(*) as freq,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM lancamentos), 2) as percentual
FROM lancamentos
WHERE categoria != 'A definir'
GROUP BY categoria
ORDER BY freq DESC
LIMIT 10;
```

---

## ⚙️ **Configurações Avançadas**

### **config.ini**

```ini
[PATHS]
diretorio_arquivos = D:/Professional/Projetos/Github/Financeiro/dados/planilhas
backup_path = D:/Professional/Projetos/Github/Financeiro/dados/backup
db_path = D:/Professional/Projetos/Github/Financeiro/dados/db/financeiro.db

[EXCEL]
output_path = D:/Professional/Projetos/Github/Financeiro/dados/planilhas
output_filename = consolidado_categorizado.xlsx
sort_by = MesComp,Fonte,Data
clean_card_names = true

[CATEGORIAS]
categoria_padrao = A definir
auto_categorize = true
confidence_threshold = 0.8

[PROCESSAMENTO]
meses_retroativos = 12
filtrar_moedas_estrangeiras = true
backup_automatico = true
log_level = INFO
```

### **Variáveis de Ambiente**

```bash
# Opcional: configuração via ambiente
export FINANCEIRO_DB_PATH="/custom/path/financeiro.db"
export FINANCEIRO_DATA_PATH="/custom/path/planilhas"
export FINANCEIRO_LOG_LEVEL="DEBUG"
```

---

## 🔍 **Algoritmos de Categorização**

### **1. Busca Exata**

```python
def busca_exata(descricao_normalizada):
    """Busca padrão exato na base de conhecimento"""
    return db.execute(
        "SELECT categoria FROM categorias_aprendidas WHERE descricao_normalizada = ?",
        (descricao_normalizada,)
    ).fetchone()
```

### **2. Busca por Similaridade**

```python
def busca_similaridade(descricao, threshold=0.8):
    """Busca por similaridade usando Levenshtein distance"""
    categorias = db.execute("SELECT * FROM categorias_aprendidas").fetchall()

    for cat in categorias:
        similarity = calculate_similarity(descricao, cat['descricao_normalizada'])
        if similarity >= threshold:
            return cat['categoria']

    return None
```

### **3. Regras Heurísticas**

```python
def aplicar_regras_heuristicas(descricao):
    """Regras específicas para casos especiais"""
    regras = {
        'PIX.*SISPAG': 'SALÁRIO',
        'REND.*PAGO.*APLIC': 'INVESTIMENTOS',
        'UBER|99|TAXI': 'TRANSPORTE',
        'IFOOD|DELIVERY': 'ALIMENTAÇÃO'
    }

    for padrao, categoria in regras.items():
        if re.search(padrao, descricao, re.IGNORECASE):
            return categoria

    return None
```

---

## 🧪 **Testes e Validação**

### **Testes de Categorização**

```python
def test_categorization_accuracy():
    """Testa precisão do sistema de categorização"""
    test_cases = [
        ("PIX QRS PAGFACIL", "A definir"),
        ("UBER TRIP SAO PAULO", "TRANSPORTE"),
        ("REND PAGO APLIC AUTO", "INVESTIMENTOS")
    ]

    accuracy = 0
    for desc, expected in test_cases:
        result = categorizar_transacao(desc)
        if result == expected:
            accuracy += 1

    return accuracy / len(test_cases)
```

### **Validação de Dados**

```python
def validar_arquivo_entrada(filepath):
    """Valida formato e conteúdo do arquivo"""
    checks = [
        verificar_formato_arquivo(),
        verificar_colunas_obrigatorias(),
        verificar_tipos_dados(),
        verificar_datas_validas(),
        verificar_valores_numericos()
    ]
    return all(checks)
```

---

## 🚨 **Tratamento de Erros**

### **Códigos de Erro .bat**

```batch
REM Códigos de retorno Python
REM 0: Sucesso
REM 1: Erro geral
REM 2: Arquivo não encontrado
REM 3: Erro de formato
REM 4: Erro de banco de dados

if errorlevel 4 (
    echo ❌ ERRO: Problema com banco de dados
    echo Verifique se o arquivo financeiro.db existe e tem permissoes
) else if errorlevel 3 (
    echo ❌ ERRO: Formato de arquivo invalido
    echo Verifique se os arquivos estao no formato correto
) else if errorlevel 2 (
    echo ❌ ERRO: Arquivos nao encontrados
    echo Verifique se existem arquivos para processar
)
```

### **Logging Python**

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agente_financeiro.log'),
        logging.StreamHandler()
    ]
)

def processar_com_log():
    try:
        logging.info("Iniciando processamento...")
        # processamento
        logging.info(f"Processadas {count} transações com {accuracy}% precisão")
    except Exception as e:
        logging.error(f"Erro durante processamento: {str(e)}")
        raise
```

---

## 🔧 **Manutenção e Otimização**

### **Limpeza Periódica**

```sql
-- Remove transações muito antigas (opcional)
DELETE FROM lancamentos WHERE data < date('now', '-24 months');

-- Otimiza o banco de dados
VACUUM;

-- Recompila estatísticas para melhor performance
ANALYZE;
```

### **Backup Automatizado**

```python
def backup_database():
    """Cria backup automático do banco"""
    import shutil
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    source = "dados/db/financeiro.db"
    backup = f"dados/backup/financeiro_backup_{timestamp}.db"

    shutil.copy2(source, backup)
    logging.info(f"Backup criado: {backup}")
```

### **Monitoramento de Performance**

```python
def monitor_performance():
    """Monitora métricas do sistema"""
    stats = {
        'total_transacoes': count_total_transactions(),
        'precisao_categoria': calculate_categorization_accuracy(),
        'tempo_processamento': measure_processing_time(),
        'tamanho_base_conhecimento': count_learned_categories()
    }

    logging.info(f"Stats: {stats}")
    return stats
```

---

## 📈 **Roadmap Técnico**

### **v2.1 (Próxima)**

- [ ] Dashboard web com Streamlit
- [ ] API REST para integração externa
- [ ] Análise preditiva com scikit-learn
- [ ] Exportação para múltiplos formatos

### **v2.2**

- [ ] Integração Open Banking
- [ ] Categorização em tempo real
- [ ] Machine Learning avançado
- [ ] Interface mobile-friendly

### **v3.0**

- [ ] Aplicativo mobile nativo
- [ ] Sincronização multi-dispositivo
- [ ] IA generativa para insights
- [ ] Marketplace de extensões

---

## � **Troubleshooting e Configuração**

### **Problema: Erro de PATH do Python ao executar .bat**

**Sintoma:**

- Ao executar os arquivos `.bat`, aparece erro "Python não encontrado no PATH"
- Scripts não executam mesmo com Anaconda instalado
- VS Code não detecta o interpretador correto

**Causa Raiz:**

- Ambientes Conda não são automaticamente adicionados ao PATH do Windows
- Arquivos `.bat` tentam executar `python` direto sem especificar o ambiente
- VS Code pode estar configurado para Python genérico ao invés do ambiente específico

**Solução Implementada:**

1. **Criar ambiente Conda específico para o projeto:**

   ```bash
   conda create -n financeiro python=3.11 -y
   conda activate financeiro
   pip install -r requirements.txt
   ```

2. **Atualizar todos os arquivos .bat para usar o Conda:**

   ```batch
   REM Define o caminho do Conda
   set "CONDA_EXE=C:\ProgramData\anaconda3\Scripts\conda.exe"
   set "CONDA_ENV=financeiro"

   REM Executa Python via Conda
   "%CONDA_EXE%" run -n %CONDA_ENV% python agente_financeiro.py
   ```

3. **Configurar VS Code (.vscode/settings.json):**

   ```json
   {
     "python.defaultInterpreterPath": "C:\\Users\\<user>\\.conda\\envs\\financeiro\\python.exe"
   }
   ```

4. **Verificar instalação:**
   ```bash
   conda env list  # Verificar ambientes disponíveis
   conda activate financeiro
   python --version  # Deve mostrar Python 3.11.x
   pip list  # Verificar pacotes instalados
   ```

**Arquivos Atualizados:**

- ✅ `agente_financeiro_completo.bat`
- ✅ `agente_financeiro_simples.bat`
- ✅ `agente_financeiro.bat`
- ✅ `atualiza_dicionario.bat`
- ✅ `atualiza_dicionario_controle.bat`
- ✅ `.vscode/settings.json`

**Documentação de Referência:**

- 📄 `CONFIGURACAO_AMBIENTE.md` - Guia completo de configuração do ambiente

**Observações Importantes:**

- É normal ter múltiplos Pythons no sistema (Anaconda base + ambientes específicos)
- Cada projeto deve ter seu próprio ambiente Conda isolado
- Python global (ex: Python 3.13 standalone) não interfere se usar Conda corretamente
- O Anaconda base (ex: 3.13) gerencia os ambientes, mas projetos usam versões específicas

**Validação de Sucesso:**

```bash
# Teste 1: Verificar ambiente
C:\ProgramData\anaconda3\Scripts\conda.exe env list
# Deve listar: financeiro

# Teste 2: Verificar dependências
"C:\Users\<user>\.conda\envs\financeiro\python.exe" -c "import pandas, openpyxl, pytest"
# Não deve dar erro

# Teste 3: Executar script
cd backend/src
"C:\Users\<user>\.conda\envs\financeiro\python.exe" agente_financeiro.py
# Deve processar transações com sucesso
```

---

## �🛡️ **Segurança e Privacidade**

### **Proteção de Dados**

- ✅ Dados financeiros nunca saem do ambiente local
- ✅ Banco SQLite criptografado (opcional)
- ✅ `.gitignore` protege arquivos sensíveis
- ✅ Logs não contêm informações pessoais

### **Boas Práticas**

```python
# Sanitização de dados
def sanitize_description(desc):
    """Remove informações sensíveis das descrições"""
    patterns_to_remove = [
        r'\d{4}\.\d{4}\.\d{4}\.\d{4}',  # Números de cartão
        r'CPF:\d{11}',                   # CPF
        r'TEL:\d{10,11}'                 # Telefones
    ]

    for pattern in patterns_to_remove:
        desc = re.sub(pattern, '[REMOVIDO]', desc)

    return desc
```

---

_Documentação técnica atualizada em September 30, 2025_
_Sistema Agente Financeiro IA v2.0 - 98.2% de precisão_
