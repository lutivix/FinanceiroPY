# 📋 Changelog - Agente Financeiro IA

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [2.2.0] - 2025-11-10 🎉

### 🎯 Principais Mudanças

**AVANÇO GIGANTE!** Geração completa de Excel consolidado a partir de dados reais do Open Finance com categorização inteligente, conversão de moeda e identificação de parcelas.

### ✨ Adicionado

#### **📊 Geração de Excel Open Finance**

- **Script `gerar_excel_pluggy.py`** - Geração completa de Excel consolidado
  - Fetches de 614 transações reais (3 contas Itaú: 2 cartões + 1 conta corrente)
  - Período: Ciclo 19-18 (19/10/2025 a 18/11/2025) = 141 transações
  - Compatibilidade total com formato `consolidado_temp.xlsx`
  - Categorização inteligente via `CategorizationService` (83% automático)
  - Conversão automática de moedas estrangeiras (USD, EUR, GBP → BRL)
  - Identificação de parcelas (1/3, 2/5, etc.) com metadata completa
  - Mapeamento de fontes usando `get_card_source()` (9 fontes: PIX, Master/Visa Físico/Virtual/Recorrente/Bia/Mae)
- **Colunas Excel**: Data, Descricao, Fonte, Valor, Categoria, MesComp, Origem_Banco, Tipo_Conta, Categoria_Banco, Tipo_Transacao, Parcela, Provider_ID
- **Ordenação correta**: MesComp (asc) → Fonte (desc) → Data (asc)
- **Output**: `dados/planilhas/consolidado_pluggy_nov2025.xlsx`

#### **🔧 Melhorias no Sistema**

- Adicionada categoria `VESTUARIO = "Vestuário"` ao enum `TransactionCategory`
- Scripts auxiliares:
  - `verificar_parcelas.py` - Análise de metadata de parcelas (121 transações encontradas)
  - `atualizar_categoria_vestuario.py` - Verificação de categorias no banco (30 categorias, 565 registros)
  - `buscar_itau_simples.py` - Fetch simplificado sem emojis (614 transações)
  - `listar_transacoes_3meses.py` - Demo com Mercado Pago (15 transações)

#### **📈 Resultados Conquistados**

- **141 transações** processadas para Novembro 2025
- **83% de categorização automática** (117/141 transações)
- **33 parcelas** identificadas com número/total
- **13 transações em moeda estrangeira** convertidas para BRL
- **23 transações** pendentes ("A definir" - 16.3%)
- **R$ -12.391,35** em débitos totais
- **Fontes mapeadas**: Visa Bia (28), PIX (28), Master Físico (22), Visa Recorrente (16), Visa Mae (12), Master Virtual (11), Visa Físico (11), Visa Virtual (7), Master Recorrente (6)

### 🔒 Segurança

- Confirmado acesso **somente leitura** via OAuth2 Open Finance
- Nenhuma operação de escrita possível (transferências, pagamentos, alterações)
- Dados sensíveis protegidos em `config.ini` (não versionado)

---

## [2.1.0] - 2025-11-10 🚀

### 🎉 Principais Mudanças

Esta versão representa um **avanço significativo** no projeto com integração Open Finance e reorganização profissional completa da documentação.

### ✨ Adicionado

#### **🔗 Integração Open Finance (Pluggy)**

- Integração completa com Open Finance Brasil via Pluggy
- Cliente REST API funcional (autenticação, contas, transações, identidade)
- Suporte a OAuth2 para conexão segura com bancos
- Mercado Pago conectado e validado com dados reais
- Sandbox de testes configurado e operacional
- Módulos `backend/src/integrations/`:
  - `pluggy_client.py` - Cliente API (REST, não SDK)
  - `pluggy_sync.py` - Serviço de sincronização de transações
- Scripts de teste e validação:
  - `teste_pluggy_rest.py` - Validação REST API ✅
  - `verificar_dados_completos.py` - Testes completos ✅

#### **📚 Documentação Profissional Reorganizada**

- Estrutura de documentação com padrão de mercado
- 3 categorias temáticas criadas:
  - `/docs/Desenvolvimento/` - Arquitetura, guias, planejamento
  - `/docs/Integracao/` - Open Finance, APIs externas
  - `/docs/Testing/` - Estratégia de testes, qualidade
- Numeração cronológica (XXX_NOME.md) em todos os documentos
- READMEs em cada categoria para navegação
- `/docs/README.md` - Índice visual completo
- `Integracao_PROXIMO_CHAT.md` - Contexto rápido para IA/novos membros
- Novos documentos técnicos:
  - `003_ARQUITETURA_PLUGGY.md` - Decisões técnicas (REST vs SDK)
  - `004_SEGURANCA_OPENFINANCE.md` - Compliance LGPD/BCB
  - `007_REORGANIZACAO_COMPLETA.md` - Histórico da reorganização

#### **⚙️ Configurações Centralizadas**

- Pasta `/config/` criada para arquivos de configuração
- `config/README.md` com guia completo de uso
- `config.ini` movido de `/backend/src/` para `/config/`
- Template `config.example.ini` atualizado com seção `[PLUGGY]`
- Proteção via `.gitignore` mantida

### 🔧 Melhorado

- **README.md** atualizado:
  - Badge Open Finance adicionado
  - Seção de integração Open Finance
  - Links para documentação reorganizada
  - Estrutura do projeto atualizada
  - Roadmap ajustado (v2.1 = Open Finance)
  - Informações de autor corretas
- **Badges** atualizadas com novos links (paths corretos)
- **Roadmap** reajustado para refletir avanço no cronograma

### 📖 Documentação

#### **Guias de Integração Open Finance**

- Decisões técnicas documentadas (por que REST API em vez de SDK)
- Diagramas de arquitetura (Mermaid) - componentes e fluxos
- Mapeamento completo Pluggy → Transaction model
- Segurança e compliance LGPD/BCB documentados
- Checklist de segurança e plano de resposta a incidentes
- Performance e otimizações implementadas

#### **Navegação Melhorada**

- Links cruzados entre documentos relacionados
- Índices em cada categoria
- Emojis padronizados para seções
- Estrutura hierárquica clara

### 🔐 Segurança

- Credenciais Pluggy protegidas em `config/config.ini` (`.gitignore`)
- OAuth2 implementado (não compartilha senha bancária)
- Read-only access (sem permissão de transferência)
- Compliance LGPD documentado
- Certificações Pluggy verificadas (ISO 27001, PCI DSS, SOC 2)
- Plano de resposta a incidentes documentado

### 🐛 Problemas Conhecidos

- **pluggy-sdk** tem bug de autenticação (não usar)
- Solução: REST API direta com biblioteca `requests`
- Trial Pluggy expirado, mas Sandbox funciona
- Items criados apenas via Dashboard (não programaticamente)
- Documentação completa em `docs/Integracao_PROXIMO_CHAT.md`

### 🎯 Próximos Passos

- [ ] Migrar credenciais para `.env` + `python-decouple`
- [ ] Refatorar `pluggy_client.py` para usar REST API definitivamente
- [ ] Conectar conta Itaú via Open Finance
- [ ] Implementar sincronização automática de transações
- [ ] Integrar Open Finance no fluxo principal do agente

### 📊 Estatísticas

- **9 novos arquivos** criados (docs + config)
- **14 arquivos** reorganizados com numeração
- **100% preservação** de conteúdo (nada perdido)
- **3 categorias** de documentação
- **4 READMEs** de navegação criados

---

## [2.0.2] - 2025-10-28 🐛

### 🐛 Corrigido

- **Lógica incorreta do ciclo mensal 19-18**
  - Sistema não buscava arquivos do mês correto após dia 19
  - Arquivos de novembro (202511) não eram processados
  - Lógica definia `mes_atual = hoje.month` independente do dia
  - Corrigido para avançar para o próximo mês quando `dia >= 19`

### 📊 Impacto

- **Antes:** 30 arquivos processados (202510 e anteriores)
- **Depois:** 33 arquivos processados (202511, 202510, ...)
- **Ganho:** +3 arquivos (novembro completo)
- **Transações:** 2184 (vs 2109 anterior, +75 transações)

### ✨ Adicionado

- **Script de validação do ciclo 19-18**

  - `backend/src/teste_ciclo_19_18.py`
  - Visualiza lógica do ciclo mensal
  - Lista arquivos que devem ser buscados
  - Compara com arquivos realmente encontrados

- **Novo teste unitário**
  - `test_find_recent_files_ciclo_19_18()`
  - Valida comportamento antes e depois do dia 19
  - Verifica arquivo correto sendo buscado

### 🔧 Melhorado

- **Documentação técnica atualizada**
  - Nova seção "Ciclo Mensal e Busca de Arquivos"
  - Tabela com exemplos práticos de datas
  - Explicação sobre não filtrar datas dentro dos arquivos
  - Motivos para preservar todas as transações

### 🧪 Testes

- **17/17 testes passando** em `test_file_processing_service.py`
- Teste de integração real executado com sucesso
- Processamento completo validado com 2184 transações

### 📝 Arquivos Modificados

```
M  backend/src/services/file_processing_service.py
M  tests/test_services/test_file_processing_service.py
M  docs/DOCUMENTACAO_TECNICA.md
A  backend/src/teste_ciclo_19_18.py
```

---

## [2.0.1] - 2025-10-28 🔧

### 🐛 Corrigido

- **Erro de PATH do Python ao executar arquivos .bat**
  - Scripts não executavam mesmo com Anaconda instalado
  - VS Code não detectava interpretador correto
  - Dependências não eram encontradas

### ✨ Adicionado

- **Ambiente Conda isolado para o projeto**

  - Criado ambiente `financeiro` com Python 3.11.14
  - Instaladas 19 dependências do requirements.txt
  - Ambiente separado do Anaconda base para evitar conflitos

- **Documentação de configuração**
  - `CONFIGURACAO_AMBIENTE.md`: Guia completo de setup do ambiente
  - Seção de troubleshooting em `DOCUMENTACAO_TECNICA.md`
  - Instruções de instalação atualizadas no `README.md`
  - Referências no `INDICE_DOCUMENTACAO.md`

### 🔧 Melhorado

- **Todos os arquivos .bat atualizados (5 arquivos)**

  - `agente_financeiro_completo.bat`
  - `agente_financeiro_simples.bat`
  - `agente_financeiro.bat`
  - `atualiza_dicionario.bat`
  - `atualiza_dicionario_controle.bat`
  - Agora executam via Conda: `conda run -n financeiro python script.py`
  - Validação de existência do Conda e ambiente
  - Mensagens de erro descritivas e informativas

- **Configuração do VS Code**
  - `.vscode/settings.json` atualizado para usar interpretador Conda
  - Path configurado: `C:\Users\<user>\.conda\envs\financeiro\python.exe`

### ✅ Validado

- **Testes de integração completos**
  - Ambiente Conda criado e funcional
  - Python 3.11.14 confirmado
  - Todas as 19 dependências instaladas corretamente
  - Sistema processou 2109 transações com 100% de sucesso
  - 30 arquivos processados em 16.97 segundos
  - 98.2% de precisão na categorização mantida
  - Zero erros de execução

### 📦 Dependências

**Instaladas no ambiente `financeiro`:**

- pandas 2.3.3
- openpyxl 3.1.5
- xlrd 2.0.2
- pytest 8.4.2
- pytest-cov 7.0.0
- pytest-mock 3.15.1
- black 25.9.0
- flake8 7.3.0
- isort 7.0.0
- tqdm 4.67.1
- colorama 0.4.6
- configparser 7.2.0
- E 7 dependências transitivas

### 📝 Documentação

- ✅ `CONFIGURACAO_AMBIENTE.md` - Novo guia completo
- ✅ `docs/DOCUMENTACAO_TECNICA.md` - Seção de troubleshooting
- ✅ `docs/INDICE_DOCUMENTACAO.md` - Referências atualizadas
- ✅ `README.md` - Instruções de instalação com Conda
- ✅ `COMMIT_MESSAGE.md` - Detalhamento completo da correção
- ✅ `CHANGELOG.md` - Este registro

### 🎯 Impacto

- ✅ Scripts .bat funcionam em qualquer máquina Windows com Anaconda
- ✅ Ambiente isolado evita conflitos entre projetos
- ✅ Configuração documentada e reproduzível
- ✅ Sistema 100% operacional e validado em produção

---

## [2.0.0] - 2025-09-30 🚀

### ✨ Adicionado

- **Sistema de automação completa via .bat files**

  - `agente_financeiro_completo.bat`: Interface completa com validações
  - `agente_financeiro_simples.bat`: Interface simplificada para compatibilidade
  - Menu interativo com 6 opções e emojis
  - Execução via duplo-clique no Windows Explorer
  - Tratamento robusto de erros com códigos de saída

- **Ordenação inteligente do Excel gerado**

  - Ordenação por MesComp → Fonte desc → Data
  - Limpeza automática de prefixes (Master/Visa sem "Itaú"/"Latam")
  - Formatação otimizada para análise

- **Sistema de limpeza de categorias duplicadas**

  - `limpar_categorias.py`: Remove duplicatas com sufixos de data
  - Consolidação inteligente de categorias similares
  - Proteção contra criação de novas duplicatas

- **Configuração automática do sistema**

  - `config.ini` criado automaticamente com paths absolutos
  - Configurações otimizadas para melhor performance
  - Detecção automática de estrutura de diretórios

- **Documentação completa**
  - README.md atualizado com métricas atuais
  - Documentação técnica detalhada
  - Guia do usuário com casos de uso
  - Changelog estruturado

### 🔧 Melhorado

- **Performance de categorização**: Saltou para **98.2% de precisão** (1759/1791 transações)
- **Base de conhecimento otimizada**: Reduzida de 772 para 584 categorias (24% menor)
- **Detecção de tipos de cartão**: Melhor identificação Master/Visa
- **Tratamento de erros**: Mais robusto em todos os scripts
- **Interface do usuário**: Menus com emojis e feedback visual

### 🐛 Corrigido

- **Duplicatas de categorias**: Sistema agora previne criação de categorias com sufixos de data
- **Navegação de diretórios**: .bat files agora funcionam de qualquer localização
- **Codificação de caracteres**: Melhor tratamento de caracteres especiais
- **Validação de arquivos**: Verificação mais robusta de formatos
- **Execução via Explorer**: Funciona perfeitamente via duplo-clique

### 🗄️ Dados

- **Transações processadas**: 1.791 total
- **Categorização automática**: 1.759 (98.2%)
- **Requer revisão manual**: 32 (1.8%)
- **Categorias únicas**: 584 (após otimização)

---

## [1.5.0] - 2025-09-29

### ✨ Adicionado

- **Scripts .bat individuais**
  - `agente_financeiro.bat`
  - `atualiza_dicionario.bat`
  - `atualiza_dicionario_controle.bat`
- **Configuração via config.ini**
- **Logs estruturados**

### 🔧 Melhorado

- **Categorização**: ~95% de precisão
- **Performance**: Processamento mais rápido
- **Estabilidade**: Menos erros durante execução

---

## [1.4.0] - 2025-09-28

### ✨ Adicionado

- **Suporte a múltiplos formatos**
  - CSV para PIX
  - XLSX para cartões
- **Normalização avançada de dados**
- **Detecção automática de moedas estrangeiras**

### 🔧 Melhorado

- **Algoritmo de categorização**: Melhor precisão em padrões
- **Tratamento de datas**: Suporte a formatos variados
- **Validação de dados**: Mais critérios de qualidade

---

## [1.3.0] - 2025-09-27

### ✨ Adicionado

- **Sistema de aprendizado com SQLite**
- **Categorização automática baseada em padrões**
- **Exportação estruturada para Excel**

### 🔧 Melhorado

- **Base de dados**: Migração de arquivos texto para SQLite
- **Performance**: Consultas mais rápidas
- **Escalabilidade**: Suporte a grandes volumes

---

## [1.2.0] - 2025-09-26

### ✨ Adicionado

- **Processamento de cartões Latam**
- **Detecção de tipos de cartão (Master/Visa)**
- **Consolidação por mês de competência**

### 🔧 Melhorado

- **Cobertura**: Mais fontes de dados
- **Análise temporal**: Agrupamento por períodos
- **Qualidade dos dados**: Validações adicionais

---

## [1.1.0] - 2025-09-25

### ✨ Adicionado

- **Suporte a cartões Itaú (XLS)**
- **Categorização manual básica**
- **Backup automático de dados**

### 🔧 Melhorado

- **Robustez**: Melhor tratamento de exceções
- **Usabilidade**: Interface mais clara
- **Documentação**: Exemplos práticos

---

## [1.0.0] - 2025-09-24

### ✨ Adicionado - Versão Inicial

- **Processamento de extratos PIX (TXT)**
- **Categorização manual via Excel**
- **Sistema básico de aprendizado**
- **Exportação para planilhas**

### 🏗️ Estrutura Inicial

- Script Python principal
- Leitura de arquivos TXT
- Base de conhecimento em arquivos
- Saída em formato Excel

---

## 🔮 **Roadmap Futuro**

### [2.1.0] - Planejado para Q4 2025

- [ ] **Dashboard web interativo** com Streamlit
- [ ] **API REST** para integração externa
- [ ] **Análise preditiva** com machine learning
- [ ] **Alertas automáticos** de orçamento

### [2.2.0] - Planejado para Q1 2026

- [ ] **Integração Open Banking**
- [ ] **Processamento em tempo real**
- [ ] **Mobile app** React Native
- [ ] **Sincronização na nuvem**

### [3.0.0] - Visão de Longo Prazo

- [ ] **IA generativa** para insights financeiros
- [ ] **Marketplace de extensões**
- [ ] **Suporte multi-idioma**
- [ ] **Versão enterprise**

---

## 📊 **Estatísticas de Evolução**

### **Performance de Categorização**

```
v1.0: ~70% precisão (categorização manual)
v1.1: ~75% precisão (primeiros padrões)
v1.2: ~80% precisão (mais fontes)
v1.3: ~85% precisão (SQLite + ML)
v1.4: ~90% precisão (normalização)
v1.5: ~95% precisão (otimizações)
v2.0: 98.2% precisão (sistema completo) ⭐
```

### **Base de Conhecimento**

```
v1.0: ~50 categorias manuais
v1.1: ~100 categorias
v1.2: ~200 categorias
v1.3: ~400 categorias
v1.4: ~600 categorias
v1.5: ~772 categorias
v2.0: 584 categorias otimizadas (limpeza de duplicatas)
```

### **Funcionalidades por Versão**

```
v1.0: 1 fonte (PIX TXT)
v1.1: 2 fontes (+ Itaú XLS)
v1.2: 3 fontes (+ Latam XLS)
v1.3: Múltiplos formatos (CSV, XLSX)
v1.4: Detecção automática
v1.5: Scripts .bat
v2.0: Automação completa 🚀
```

---

## 🏆 **Marcos Importantes**

- **🎯 98.2% de precisão** alcançada em v2.0
- **🚀 Automação completa** via interface .bat
- **🧹 Otimização da base** com 24% de redução
- **📱 Interface amigável** com menus e emojis
- **🔧 Zero configuração** manual necessária

---

## 📝 **Notas de Desenvolvimento**

### **Metodologia**

- Desenvolvimento iterativo com feedback contínuo
- Testes com dados reais para validação
- Foco na experiência do usuário
- Documentação como prioridade

### **Tecnologias Utilizadas**

- **Python 3.13**: Core do sistema
- **SQLite**: Base de dados
- **pandas/openpyxl**: Manipulação de Excel
- **Windows Batch**: Automação
- **Regex**: Processamento de texto

### **Princípios de Design**

- **Simplicidade**: Interface intuitiva
- **Robustez**: Tratamento de erros
- **Performance**: Processamento rápido
- **Escalabilidade**: Suporte a crescimento
- **Privacidade**: Dados locais apenas

---

_Changelog mantido em setembro de 2025_
_Agente Financeiro IA - Evolução contínua rumo à automação perfeita_ 🚀
