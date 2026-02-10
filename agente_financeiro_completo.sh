#!/bin/bash

# Configuração
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

CONDA_EXE="/c/ProgramData/anaconda3/Scripts/conda.exe"
CONDA_ENV="financeiro"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Variável para controlar o dashboard
DASHBOARD_PID=""

# Função para limpar tela
clear_screen() {
    clear
}

# Função para obter ambiente conda ativo
get_active_conda_env() {
    if [ -n "$CONDA_DEFAULT_ENV" ]; then
        echo "$CONDA_DEFAULT_ENV"
    else
        echo "nenhum"
    fi
}

# Função para exibir banner
show_banner() {
    local active_env=$(get_active_conda_env)
    echo -e "${CYAN}========================================================${NC}"
    echo -e "${CYAN}          🚀 AGENTE FINANCEIRO IA v2.0 🚀${NC}"
    echo -e "${CYAN}========================================================${NC}"
    echo -e "${YELLOW}📁 Executando de: ${SCRIPT_DIR}${NC}"
    echo -e "${YELLOW}🐍 Ambiente configurado: ${GREEN}${CONDA_ENV}${NC}"
    if [ "$active_env" != "nenhum" ]; then
        echo -e "${YELLOW}✅ Ambiente ativo no terminal: ${GREEN}${active_env}${NC}"
    else
        echo -e "${YELLOW}⚠️  Ambiente ativo no terminal: ${RED}${active_env}${NC} ${BLUE}(ativando automaticamente)${NC}"
    fi
    echo ""
}

# Função para executar comando no ambiente conda
run_in_conda() {
    # Ativa o ambiente e executa o comando no shell atual (preserva TTY para UTF-8)
    bash -c "eval \"\$('$CONDA_EXE' shell.bash hook)\" && conda activate '$CONDA_ENV' && $*"
}

# Função para validar ambiente
validate_environment() {
    clear_screen
    show_banner
    
    # Verifica Conda
    if [ ! -f "$CONDA_EXE" ]; then
        echo -e "${RED}❌ ERRO: Anaconda não encontrado em $CONDA_EXE${NC}"
        echo -e "${YELLOW}💡 Verifique se o Anaconda está instalado corretamente.${NC}"
        echo ""
        read -p "Pressione ENTER para sair..."
        exit 1
    fi
    
    # Verifica se o ambiente existe
    "$CONDA_EXE" env list | grep -q "$CONDA_ENV"
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ ERRO: Ambiente conda '$CONDA_ENV' não encontrado!${NC}"
        echo -e "${YELLOW}💡 Execute: conda create -n $CONDA_ENV python=3.11${NC}"
        echo ""
        read -p "Pressione ENTER para sair..."
        exit 1
    fi
    
    echo -e "${GREEN}✅ Usando ambiente Conda: $CONDA_ENV${NC}"
    
    # Verifica arquivos principais
    if [ ! -f "backend/src/agente_financeiro.py" ]; then
        echo -e "${RED}❌ ERRO: agente_financeiro.py não encontrado!${NC}"
        echo -e "${YELLOW}📁 Diretório atual: $(pwd)${NC}"
        echo -e "${YELLOW}💡 Verifique se os arquivos estão no local correto.${NC}"
        echo ""
        read -p "Pressione ENTER para sair..."
        exit 1
    fi
    
    # Verifica configuração
    if [ -f "config/config.ini" ]; then
        echo -e "${GREEN}✅ Configuração encontrada: config/config.ini${NC}"
    elif [ -f "config/config.example.ini" ]; then
        echo -e "${YELLOW}⚠️  Usando configuração padrão: config/config.example.ini${NC}"
    else
        echo -e "${RED}❌ ERRO: Nenhum arquivo de configuração encontrado!${NC}"
        echo -e "${YELLOW}💡 Certifique-se que config.ini ou config.example.ini existe.${NC}"
        read -p "Pressione ENTER para sair..."
        exit 1
    fi
    
    echo -e "${GREEN}✅ Ambiente validado com sucesso!${NC}"
    echo ""
    sleep 2
}

# Função para verificar se dashboard está rodando
is_dashboard_running() {
    if [ -z "$DASHBOARD_PID" ]; then
        return 1
    fi
    ps -p "$DASHBOARD_PID" > /dev/null 2>&1
    return $?
}

# Função para mostrar status do dashboard
show_dashboard_status() {
    if is_dashboard_running; then
        echo -e "  ${GREEN}●${NC} Dashboard v2 está ${GREEN}RODANDO${NC} (PID: $DASHBOARD_PID)"
    else
        echo -e "  ${RED}○${NC} Dashboard v2 está ${RED}PARADO${NC}"
    fi
}

# Função para exibir menu
show_menu() {
    clear_screen
    show_banner
    show_dashboard_status
    echo ""
    echo -e "${CYAN}Selecione uma opção:${NC}"
    echo ""
    echo -e "${GREEN}[1]${NC} 🔄 Executar Processamento Completo (Recomendado)"
    echo -e "${GREEN}[2]${NC} 📊 Apenas Processar Transações (Agente Principal)"
    echo -e "${GREEN}[3]${NC} 📚 Atualizar Dicionário (do Excel consolidado)"
    echo -e "${GREEN}[4]${NC} 📋 Atualizar Dicionário (do Controle_pessoal.xlsm)"
    echo -e "${GREEN}[5]${NC} 💾 Atualizar Dicionário (do Banco de Dados)"
    echo -e "${GREEN}[6]${NC} 🧹 Limpar Categorias Duplicadas (Manutenção)"
    echo ""
    if is_dashboard_running; then
        echo -e "${RED}[7]${NC} 🛑 Parar Dashboard v2"
    else
        echo -e "${BLUE}[7]${NC} 🚀 Iniciar Dashboard v2"
    fi
    echo -e "${MAGENTA}[8]${NC} 📦 Instalar Dependências do Dashboard"
    echo -e "${CYAN}[9]${NC} ℹ️  Informações do Ambiente"
    echo ""
    echo -e "${YELLOW}[0]${NC} ❌ Sair"
    echo ""
    echo -e "${CYAN}========================================================${NC}"
}

# Função para executar processamento completo
run_complete() {
    clear_screen
    show_banner
    echo -e "${CYAN}========================================================${NC}"
    echo -e "${CYAN}         🔄 PROCESSAMENTO COMPLETO INICIADO${NC}"
    echo -e "${CYAN}========================================================${NC}"
    echo ""
    
    echo -e "${YELLOW}⏳ Executando processamento principal...${NC}"
    run_in_conda py backend/src/agente_financeiro.py
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erro no processamento principal!${NC}"
        read -p "Pressione ENTER para continuar..."
        return 1
    fi
    
    echo ""
    echo -e "${YELLOW}⏳ Atualizando dicionário do Excel...${NC}"
    run_in_conda py backend/src/atualiza_dicionario.py
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erro na atualização do dicionário Excel!${NC}"
        read -p "Pressione ENTER para continuar..."
        return 1
    fi
    
    echo ""
    echo -e "${YELLOW}⏳ Atualizando dicionário do Controle...${NC}"
    run_in_conda py backend/src/atualiza_dicionario_controle.py
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erro na atualização do dicionário Controle!${NC}"
        read -p "Pressione ENTER para continuar..."
        return 1
    fi
    
    echo ""
    echo -e "${GREEN}✅ PROCESSAMENTO COMPLETO FINALIZADO!${NC}"
    return 0
}

# Função para executar apenas agente
run_agent() {
    clear_screen
    show_banner
    echo -e "${CYAN}========================================================${NC}"
    echo -e "${CYAN}           📊 PROCESSANDO TRANSAÇÕES${NC}"
    echo -e "${CYAN}========================================================${NC}"
    echo ""
    
    run_in_conda py backend/src/agente_financeiro.py
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erro no processamento!${NC}"
        read -p "Pressione ENTER para continuar..."
        return 1
    fi
    
    echo ""
    echo -e "${GREEN}✅ Processamento concluído!${NC}"
    return 0
}

# Função para atualizar dicionário Excel
update_dict_excel() {
    clear_screen
    show_banner
    echo -e "${CYAN}========================================================${NC}"
    echo -e "${CYAN}         📚 ATUALIZANDO DICIONÁRIO (EXCEL)${NC}"
    echo -e "${CYAN}========================================================${NC}"
    echo ""
    
    run_in_conda py backend/src/atualiza_dicionario.py
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erro na atualização do dicionário!${NC}"
        read -p "Pressione ENTER para continuar..."
        return 1
    fi
    
    echo ""
    echo -e "${GREEN}✅ Dicionário atualizado!${NC}"
    return 0
}

# Função para atualizar dicionário Controle
update_dict_control() {
    clear_screen
    show_banner
    echo -e "${CYAN}========================================================${NC}"
    echo -e "${CYAN}        📋 ATUALIZANDO DICIONÁRIO (CONTROLE)${NC}"
    echo -e "${CYAN}========================================================${NC}"
    echo ""
    
    run_in_conda py backend/src/atualiza_dicionario_controle.py
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erro na atualização do dicionário!${NC}"
        read -p "Pressione ENTER para continuar..."
        return 1
    fi
    
    echo ""
    echo -e "${GREEN}✅ Dicionário atualizado!${NC}"
    return 0
}

# Função para atualizar dicionário DB
update_dict_db() {
    clear_screen
    show_banner
    echo -e "${CYAN}========================================================${NC}"
    echo -e "${CYAN}     💾 ATUALIZANDO DICIONÁRIO (BANCO DE DADOS)${NC}"
    echo -e "${CYAN}========================================================${NC}"
    echo ""
    echo -e "${BLUE}📊 Lendo categorizações da tabela lancamentos...${NC}"
    
    run_in_conda py backend/src/atualiza_dicionario_unificado.py db
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erro na atualização do dicionário!${NC}"
        read -p "Pressione ENTER para continuar..."
        return 1
    fi
    
    echo ""
    echo -e "${GREEN}✅ Dicionário atualizado!${NC}"
    return 0
}

# Função para limpar categorias
clean_categories() {
    clear_screen
    show_banner
    echo -e "${CYAN}========================================================${NC}"
    echo -e "${CYAN}           🧹 LIMPANDO CATEGORIAS DUPLICADAS${NC}"
    echo -e "${CYAN}========================================================${NC}"
    echo ""
    
    run_in_conda py backend/src/limpar_categorias.py
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erro na limpeza!${NC}"
        read -p "Pressione ENTER para continuar..."
        return 1
    fi
    
    echo ""
    echo -e "${GREEN}✅ Limpeza concluída!${NC}"
    return 0
}

# Função para verificar dependências do dashboard
check_dashboard_deps() {
    run_in_conda py -c 'import dash' 2>/dev/null
    return $?
}

# Função para instalar dependências do dashboard
install_dashboard_deps() {
    clear_screen
    show_banner
    echo -e "${CYAN}========================================================${NC}"
    echo -e "${CYAN}        📦 INSTALANDO DEPENDÊNCIAS DO DASHBOARD${NC}"
    echo -e "${CYAN}========================================================${NC}"
    echo ""
    
    if [ ! -f "backend/requirements-dashboard.txt" ]; then
        echo -e "${RED}❌ Arquivo requirements-dashboard.txt não encontrado!${NC}"
        read -p "Pressione ENTER para continuar..."
        return 1
    fi
    
    echo -e "${YELLOW}⏳ Instalando pacotes via pip...${NC}"
    echo ""
    
    run_in_conda pip install -r backend/requirements-dashboard.txt
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ Dependências instaladas com sucesso!${NC}"
    else
        echo ""
        echo -e "${RED}❌ Erro ao instalar dependências!${NC}"
    fi
    
    echo ""
    read -p "Pressione ENTER para continuar..."
}

# Função para iniciar dashboard
start_dashboard() {
    if is_dashboard_running; then
        echo ""
        echo -e "${YELLOW}⚠️  Dashboard já está rodando!${NC}"
        sleep 2
        return 0
    fi
    
    # Verificar se dependências estão instaladas
    if ! check_dashboard_deps; then
        clear_screen
        show_banner
        echo -e "${RED}❌ ERRO: Dependências do Dashboard não estão instaladas!${NC}"
        echo ""
        echo -e "${YELLOW}O módulo 'dash' não foi encontrado no ambiente conda.${NC}"
        echo ""
        read -p "Deseja instalar as dependências agora? (S/N): " install_deps
        
        if [[ "$install_deps" =~ ^[Ss]$ ]]; then
            install_dashboard_deps
            if ! check_dashboard_deps; then
                echo ""
                echo -e "${RED}❌ Não foi possível iniciar o Dashboard.${NC}"
                read -p "Pressione ENTER para voltar ao menu..."
                return 1
            fi
        else
            echo ""
            echo -e "${YELLOW}💡 Execute a opção [8] para instalar as dependências.${NC}"
            sleep 3
            return 1
        fi
    fi
    
    clear_screen
    show_banner
    echo -e "${CYAN}========================================================${NC}"
    echo -e "${CYAN}           🚀 INICIANDO DASHBOARD V2${NC}"
    echo -e "${CYAN}========================================================${NC}"
    echo ""
    
    clear_screen
    show_banner
    echo -e "${CYAN}========================================================${NC}"
    echo -e "${CYAN}           🚀 INICIANDO DASHBOARD V2${NC}"
    echo -e "${CYAN}========================================================${NC}"
    echo ""
    
    echo -e "${YELLOW}⏳ Abrindo Dashboard em nova janela...${NC}"
    mintty -t "Dashboard Financeiro v2" -s 120,30 /bin/bash -c "cd '$SCRIPT_DIR' && echo 'Iniciando Dashboard...' && '/c/ProgramData/anaconda3/Scripts/conda.exe' run -n financeiro py backend/src/dashboard_v2/main.py 2>&1; echo ''; echo 'Dashboard encerrado. Pressione ENTER para fechar.'; read" &
    DASHBOARD_PID=$!
    
    echo -e "${YELLOW}⏳ Aguardando servidor inicializar...${NC}"
    sleep 5
    
    echo ""
    echo -e "${GREEN}✅ Dashboard iniciado com sucesso! (PID: $DASHBOARD_PID)${NC}"
    echo -e "${BLUE}🌐 URL: http://localhost:8052${NC}"
    echo ""
    echo -e "${YELLOW}🌍 Abrindo navegador...${NC}"
    
    # Tentar abrir no navegador
    if command -v start &> /dev/null; then
        start "http://localhost:8052" 2>/dev/null
    elif command -v xdg-open &> /dev/null; then
        xdg-open "http://localhost:8052" 2>/dev/null
    else
        echo -e "${YELLOW}⚠️  Não foi possível abrir automaticamente. Acesse manualmente:${NC}"
        echo -e "${CYAN}   http://localhost:8052${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}✅ Navegador aberto!${NC}"
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}📋 IMPORTANTE:${NC}"
    echo -e "${BLUE}   • A janela preta = Servidor rodando (não feche!)${NC}"
    echo -e "${BLUE}   • Se aparecer erro na janela preta, leia a mensagem${NC}"
    echo -e "${BLUE}   • Se o navegador mostrar 'Não foi possível conectar':${NC}"
    echo -e "${BLUE}     → O servidor teve um erro, verifique a janela preta${NC}"
    echo -e "${BLUE}   • Se funcionar: use normalmente o Dashboard!${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    read -p "Pressione ENTER para voltar ao menu..."
}

# Função para parar dashboard
stop_dashboard() {
    if ! is_dashboard_running; then
        echo ""
        echo -e "${YELLOW}⚠️  Dashboard não está rodando!${NC}"
        sleep 2
        return 0
    fi
    
    echo ""
    echo -e "${YELLOW}⏳ Parando Dashboard...${NC}"
    
    # Matar processo e filhos
    pkill -P "$DASHBOARD_PID" 2>/dev/null
    kill "$DASHBOARD_PID" 2>/dev/null
    sleep 1
    kill -9 "$DASHBOARD_PID" 2>/dev/null
    
    DASHBOARD_PID=""
    
    echo -e "${GREEN}✅ Dashboard parado!${NC}"
    sleep 2
}

# Função para mostrar informações do ambiente
show_environment_info() {
    clear_screen
    show_banner
    echo -e "${CYAN}========================================================${NC}"
    echo -e "${CYAN}           ℹ️  INFORMAÇÕES DO AMBIENTE${NC}"
    echo -e "${CYAN}========================================================${NC}"
    echo ""
    
    local active_env=$(get_active_conda_env)
    
    echo -e "${BLUE}📦 Ambiente Configurado:${NC}"
    echo -e "   Nome: ${GREEN}${CONDA_ENV}${NC}"
    echo -e "   Conda: ${CONDA_EXE}"
    echo ""
    
    echo -e "${BLUE}🔍 Status do Ambiente:${NC}"
    if [ "$active_env" != "nenhum" ]; then
        echo -e "   Terminal: ${GREEN}✅ Ativado ($active_env)${NC}"
        echo -e "   Modo: ${GREEN}Execução direta (python)${NC}"
    else
        echo -e "   Terminal: ${YELLOW}⚠️  Não ativado${NC}"
        echo -e "   Modo: ${BLUE}Ativação automática via source${NC}"
    fi
    echo ""
    
    echo -e "${BLUE}🐍 Versão do Python no ambiente:${NC}"
    run_in_conda py --version 2>&1 | sed 's/^/   /'
    echo ""
    
    echo -e "${BLUE}📚 Pacotes Principais Instalados:${NC}"
    
    # Verificar pacotes principais
    if check_dashboard_deps; then
        echo -e "   ${GREEN}✅${NC} dash (Dashboard)"
    else
        echo -e "   ${RED}❌${NC} dash (Dashboard) - ${YELLOW}Use opção [8] para instalar${NC}"
    fi
    
    PANDAS_VER=$(run_in_conda py -c "import pandas; print(pandas.__version__)" 2>/dev/null)
    if [ -n "$PANDAS_VER" ]; then
        echo -e "   ${GREEN}✅${NC} pandas $PANDAS_VER"
    else
        echo -e "   ${RED}❌${NC} pandas"
    fi
    
    PLOTLY_VER=$(run_in_conda py -c "import plotly; print(plotly.__version__)" 2>/dev/null)
    if [ -n "$PLOTLY_VER" ]; then
        echo -e "   ${GREEN}✅${NC} plotly $PLOTLY_VER"
    else
        echo -e "   ${RED}❌${NC} plotly"
    fi
    
    OPENPYXL_VER=$(run_in_conda py -c "import openpyxl; print(openpyxl.__version__)" 2>/dev/null)
    if [ -n "$OPENPYXL_VER" ]; then
        echo -e "   ${GREEN}✅${NC} openpyxl $OPENPYXL_VER"
    else
        echo -e "   ${RED}❌${NC} openpyxl"
    fi
    
    echo ""
    echo -e "${BLUE}📂 Arquivos de Configuração:${NC}"
    if [ -f "config/config.ini" ]; then
        echo -e "   ${GREEN}✅${NC} config/config.ini"
    else
        echo -e "   ${RED}❌${NC} config/config.ini"
    fi
    if [ -f "config/config.example.ini" ]; then
        echo -e "   ${GREEN}✅${NC} config/config.example.ini"
    fi
    if [ -f "backend/requirements-dashboard.txt" ]; then
        echo -e "   ${GREEN}✅${NC} backend/requirements-dashboard.txt"
    fi
    
    echo ""
    echo -e "${BLUE}💡 Dica:${NC}"
    echo -e "   Para ativar o ambiente manualmente:"
    echo -e "   ${CYAN}conda activate ${CONDA_ENV}${NC}"
    echo ""
    echo -e "${CYAN}========================================================${NC}"
    echo ""
    read -p "Pressione ENTER para voltar ao menu..."
}

# Função para mostrar resultado final
show_result() {
    echo ""
    echo -e "${CYAN}========================================================${NC}"
    echo -e "${GREEN}✅ OPERAÇÃO CONCLUÍDA COM SUCESSO!${NC}"
    echo -e "${CYAN}========================================================${NC}"
    echo ""
    read -p "Pressione ENTER para voltar ao menu..."
}

# Validar ambiente no início
validate_environment

# Loop principal
while true; do
    show_menu
    read -p "Digite sua opção (0-9): " opcao
    
    case $opcao in
        1)
            run_complete && show_result
            ;;
        2)
            run_agent && show_result
            ;;
        3)
            update_dict_excel && show_result
            ;;
        4)
            update_dict_control && show_result
            ;;
        5)
            update_dict_db && show_result
            ;;
        6)
            clean_categories && show_result
            ;;
        7)
            if is_dashboard_running; then
                stop_dashboard
            else
                start_dashboard
            fi
            ;;
        8)
            install_dashboard_deps
            ;;
        9)
            show_environment_info
            ;;
        0)
            echo ""
            if is_dashboard_running; then
                echo -e "${YELLOW}⚠️  Dashboard ainda está rodando!${NC}"
                echo ""
                read -p "Deseja parar o Dashboard antes de sair? (S/N): " stop_dash
                if [[ "$stop_dash" =~ ^[Ss]$ ]]; then
                    stop_dashboard
                fi
            fi
            echo -e "${GREEN}👋 Obrigado por usar o Agente Financeiro IA!${NC}"
            sleep 2
            exit 0
            ;;
        *)
            echo ""
            echo -e "${RED}❌ Opção inválida! Tente novamente.${NC}"
            sleep 2
            ;;
    esac
done
