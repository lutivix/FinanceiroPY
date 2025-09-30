# 👤 Guia do Usuário - Agente Financeiro IA v2.0

## 🚀 **Início Rápido (5 minutos)**

### **1. Preparação dos Arquivos**

Organize seus extratos na pasta `dados/planilhas/` seguindo o padrão:

```
dados/planilhas/
├── 202501_Extrato.txt     # PIX Janeiro 2025
├── 202501_Itau.xls        # Cartão Itaú Janeiro
├── 202501_Latam.xls       # Cartão Latam Janeiro
├── 202502_Extrato.txt     # PIX Fevereiro 2025
├── 202502_Itau.xls        # Cartão Itaú Fevereiro
└── ...                    # Outros meses
```

### **2. Execução Automática**

1. **Navegue** até a pasta `backend/src/`
2. **Duplo-clique** em `agente_financeiro_completo.bat`
3. **Escolha a opção 1** (Processamento Completo)
4. **Aguarde** o processamento (normalmente 30-60 segundos)

### **3. Resultado**

O arquivo `consolidado_categorizado.xlsx` será gerado com suas transações categorizadas automaticamente!

---

## 🎯 **Interface do Menu**

### **🚀 Opção 1: Processamento Completo (Recomendada)**

**O que faz:**

- Processa todos os extratos automaticamente
- Categoriza transações (98.2% de precisão)
- Gera Excel consolidado ordenado
- Atualiza base de conhecimento

**Quando usar:** Primeira execução ou processamento mensal completo

### **📊 Opção 2: Apenas Processar Transações**

**O que faz:**

- Executa apenas o processamento principal
- Não atualiza dicionários

**Quando usar:** Teste rápido ou quando a base já está atualizada

### **📚 Opção 3: Atualizar Dicionário (Excel)**

**O que faz:**

- Aprende com categorizações manuais do Excel
- Melhora precisão futura

**Quando usar:** Após categorizar manualmente no Excel consolidado

### **📋 Opção 4: Atualizar Dicionário (Controle)**

**O que faz:**

- Sincroniza com `Controle_pessoal.xlsm`
- Importa categorizações existentes

**Quando usar:** Primeira configuração ou sync com planilha de controle

### **🧹 Opção 5: Limpar Categorias Duplicadas**

**O que faz:**

- Remove categorias duplicadas da base
- Otimiza performance do sistema

**Quando usar:** Manutenção periódica (mensal/trimestral)

---

## 📋 **Formatos de Arquivo Suportados**

### **💳 PIX (Arquivos TXT/CSV)**

**Formato esperado:**

```
Data;Descrição;Valor
19/12/2024;PIX QRS PAGFACIL IP19/12;-2,00
20/12/2024;PIX TRANSF ROBERTA20/12;-600,00
21/12/2024;PIX RECEBIDO SALARIO;3500,00
```

**Regras:**

- ✅ Separador: ponto e vírgula (;)
- ✅ Data: DD/MM/AAAA
- ✅ Valor: formato brasileiro (-123,45)

### **🏦 Cartões Itaú/Latam (XLS/XLSX)**

**Estrutura esperada:**

```
Coluna A: Data (19/12/2024)
Coluna B: Descrição (UBER TRIP SAO PAULO)
Coluna D: Valor (-25,80)
```

**Regras:**

- ✅ Data na coluna A
- ✅ Descrição na coluna B
- ✅ Valor na coluna D
- ✅ Outras colunas são ignoradas

---

## 📊 **Entendendo o Excel Gerado**

### **Colunas do Arquivo Consolidado**

| Coluna        | Descrição             | Exemplo             |
| ------------- | --------------------- | ------------------- |
| **Data**      | Data da transação     | 19/12/2024          |
| **Descrição** | Descrição limpa       | UBER TRIP SAO PAULO |
| **Fonte**     | Origem (sem prefixos) | Master, Visa, PIX   |
| **Valor**     | Valor formatado       | -25,80              |
| **Categoria** | Categoria automática  | TRANSPORTE          |
| **MêsComp**   | Mês de competência    | 2024-12             |

### **Ordenação Automática**

O Excel é automaticamente ordenado por:

1. **MêsComp** (mês de competência)
2. **Fonte** (descendente: PIX → Visa → Master)
3. **Data** (cronológica crescente)

### **Categorias Automáticas Comuns**

| Categoria               | Exemplos de Transações           |
| ----------------------- | -------------------------------- |
| 💰 **SALÁRIO**          | SISPAG PIX, PAGTO REMUNERACAO    |
| 📈 **INVESTIMENTOS**    | REND PAGO APLIC, TED CORRETORA   |
| 🍕 **ALIMENTAÇÃO**      | IFOOD, RESTAURANTE, SUPERMERCADO |
| 🚗 **TRANSPORTE**       | UBER, 99, POSTO GASOLINA         |
| 🏠 **MORADIA**          | ALUGUEL, CONDOMINIO, ENERGIA     |
| 💊 **SAÚDE**            | FARMACIA, CONSULTA, PLANO SAUDE  |
| 🎮 **ENTRETENIMENTO**   | NETFLIX, SPOTIFY, CINEMA         |
| 👕 **VESTUÁRIO**        | LOJA ROUPAS, SAPATOS             |
| 📱 **TELECOMUNICAÇÕES** | VIVO, TIM, CLARO                 |
| 🔧 **A definir**        | Transações não categorizadas     |

---

## 🎓 **Como Melhorar a Precisão**

### **1. Categorização Manual (Recomendado)**

1. **Abra** o `consolidado_categorizado.xlsx`
2. **Filtre** pela categoria "A definir"
3. **Substitua** "A definir" pela categoria correta
4. **Salve** o arquivo
5. **Execute** opção 3 do menu (Atualizar Dicionário Excel)

**Resultado:** O sistema aprende e categoriza automaticamente transações similares no futuro!

### **2. Uso do Controle Pessoal**

Se você já tem um `Controle_pessoal.xlsm` com categorizações:

1. **Execute** opção 4 do menu (Atualizar Dicionário Controle)
2. O sistema importa suas categorizações existentes

### **3. Limpeza Periódica**

Execute opção 5 (Limpar Duplicatas) mensalmente para manter a base otimizada.

---

## 🔧 **Solução de Problemas**

### **❌ "Nenhum arquivo encontrado"**

**Causa:** Arquivos não estão na pasta correta ou formato incorreto

**Solução:**

- Verifique se os arquivos estão em `dados/planilhas/`
- Confirme o formato: `AAAAMM_Fonte.extensão`
- Exemplo: `202501_Extrato.txt`, `202501_Itau.xls`

### **❌ "Erro ao processar arquivo"**

**Causa:** Formato interno do arquivo não está correto

**Solução:**

- Abra o arquivo no Excel e verifique as colunas
- Para PIX: confirme formato Data;Descrição;Valor
- Para cartões: confirme colunas A(Data), B(Descrição), D(Valor)

### **❌ "Python não encontrado"**

**Causa:** Python não está instalado ou não está no PATH

**Solução:**

```cmd
# Teste se Python está disponível
python --version

# Se não funcionar, instale Python 3.13+
# ou adicione ao PATH do Windows
```

### **❌ "Caracteres estranhos no terminal"**

**Causa:** Limitação de codificação do terminal Windows

**Impacto:** Apenas visual - sistema funciona normalmente
**Solução:** Use PowerShell ou aceite os caracteres visuais

### **❌ "Erro de permissão no banco"**

**Causa:** Arquivo SQLite bloqueado ou sem permissão

**Solução:**

- Feche outros programas que possam estar usando o banco
- Execute como administrador se necessário
- Verifique permissões da pasta `dados/db/`

---

## 📈 **Dicas de Uso Avançado**

### **🗓️ Processamento Mensal**

**Rotina recomendada:**

1. No final do mês, baixe extratos dos bancos
2. Renomeie seguindo o padrão AAAAMM_Fonte
3. Execute processamento completo (Opção 1)
4. Revise transações "A definir" no Excel
5. Execute atualização do dicionário (Opção 3)

### **📊 Análise de Dados**

O Excel gerado pode ser usado para:

- **Tabelas dinâmicas** por categoria e mês
- **Gráficos** de evolução de gastos
- **Filtros** por período ou fonte
- **Importação** para outras ferramentas (Power BI, etc.)

### **🔄 Backup e Recuperação**

```cmd
# Backup manual da base de conhecimento
copy dados\db\financeiro.db dados\backup\financeiro_backup.db

# Em caso de problema, restaure o backup
copy dados\backup\financeiro_backup.db dados\db\financeiro.db
```

### **⚡ Performance**

Para melhor performance:

- Execute limpeza de duplicatas mensalmente
- Mantenha apenas extratos dos últimos 12-24 meses
- Use processamento completo apenas quando necessário

---

## 🎯 **Casos de Uso Comuns**

### **👤 Usuário Iniciante**

1. **Organize** extratos na pasta dados/planilhas/
2. **Execute** processamento completo
3. **Analise** o Excel gerado
4. **Categorize** transações "A definir" manualmente
5. **Execute** atualização do dicionário

### **👨‍💼 Usuário Experiente**

1. **Processe** novos extratos mensalmente
2. **Use** categorização automática (98.2% precisão)
3. **Revise** apenas transações específicas
4. **Mantenha** base de conhecimento atualizada
5. **Analise** tendências de gastos

### **🏢 Uso Profissional**

1. **Processe** extratos de múltiplas contas
2. **Personalize** categorias para necessidades específicas
3. **Exporte** dados para sistemas contábeis
4. **Automatize** via scripts .bat agendados
5. **Monitore** performance do sistema

---

## 📞 **Suporte e Comunidade**

### **🐛 Reportar Problemas**

Se encontrar problemas:

1. **Verifique** esta documentação primeiro
2. **Confira** logs em `agente_financeiro.log`
3. **Abra** uma issue no GitHub com detalhes
4. **Inclua** informações do sistema e erro

### **💡 Sugestões de Melhoria**

Ideias são bem-vindas:

- **Novas fontes** de dados (bancos, cartões)
- **Categorias especializadas**
- **Funcionalidades extras**
- **Melhorias de interface**

### **🤝 Contribuições**

Quer contribuir?

- **Código**: Fork + Pull Request
- **Documentação**: Melhorias e traduções
- **Testes**: Casos de uso diferentes
- **Divulgação**: Compartilhe com outros usuários

---

## 📊 **Métricas de Sucesso**

### **✅ Sistema Funcionando Bem**

- ✅ 95%+ transações categorizadas automaticamente
- ✅ Processamento em menos de 2 minutos
- ✅ Excel gerado sem erros
- ✅ Categorias consistentes mês a mês

### **⚠️ Sinais de Atenção**

- ⚠️ Muitas transações "A definir" (>10%)
- ⚠️ Categorias inconsistentes para mesma descrição
- ⚠️ Tempo de processamento muito longo (>5 min)
- ⚠️ Erros frequentes durante execução

### **🔧 Quando Fazer Manutenção**

- 🗓️ **Mensal**: Limpeza de duplicatas
- 🗓️ **Trimestral**: Backup da base de conhecimento
- 🗓️ **Semestral**: Revisão completa de categorias
- 🗓️ **Anual**: Atualização do sistema

---

## 🎉 **Conclusão**

O Agente Financeiro IA v2.0 foi projetado para ser:

- **🚀 Simples**: Interface intuitiva para todos os níveis
- **🎯 Eficiente**: 98.2% de precisão na categorização
- **⚡ Rápido**: Processamento completo em minutos
- **🧠 Inteligente**: Aprende com seu uso

**Aproveite a automatização e foque no que realmente importa: análise e planejamento financeiro!** 💰✨

---

_Guia do Usuário atualizado em September 30, 2025_
_Agente Financeiro IA v2.0 - Sua inteligência financeira automatizada_
