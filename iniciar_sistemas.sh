#!/bin/bash

# Configuração
PATH_BCE="/c/Servidor/BelgoEstoqueFSTS"
PATH_FINANCEIRO="/c/Servidor/Financeiro"

# Arquivo para armazenar PIDs
PID_FILE="/tmp/sistemas_pids.txt"

# Variáveis de PIDs
PID_BCE_BACKEND=""
PID_BCE_FRONTEND=""
PID_FINANCEIRO=""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Função para limpar tela
clear_screen() {
    clear
}

# Função para carregar PIDs
load_pids() {
    if [ -f "$PID_FILE" ]; then
        source "$PID_FILE"
    fi
}

# Função para iniciar os sistemas
start_systems() {
    clear_screen
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}    INICIANDO SISTEMAS${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    
    # Limpar arquivo de PIDs anterior
    > "$PID_FILE"
    
    # Iniciar Backend BCE em nova janela bash
    echo -e "${YELLOW}[1/3]${NC} Iniciando Backend BCE..."
    mintty -t "BCE Backend" -s 120,30 /bin/bash -c "cd '$PATH_BCE/backend' && npm run start:dev; echo ''; echo 'Processo finalizado. Feche esta janela.'; exec bash" &
    PID_BCE_BACKEND=$!
    echo "PID_BCE_BACKEND=$PID_BCE_BACKEND" >> "$PID_FILE"
    sleep 2
    
    # Iniciar Frontend BCE em nova janela bash
    echo -e "${YELLOW}[2/3]${NC} Iniciando Frontend BCE..."
    mintty -t "BCE Frontend" -s 120,30 /bin/bash -c "cd '$PATH_BCE/frontend-vite' && npm run dev; echo ''; echo 'Processo finalizado. Feche esta janela.'; exec bash" &
    PID_BCE_FRONTEND=$!
    echo "PID_BCE_FRONTEND=$PID_BCE_FRONTEND" >> "$PID_FILE"
    sleep 2
    
    # Iniciar Backend Financeiro em nova janela bash
    echo -e "${YELLOW}[3/3]${NC} Iniciando Backend Financeiro..."
    mintty -t "Financeiro Backend" -s 120,30 /bin/bash -c "cd '$PATH_FINANCEIRO' && python backend/src/dashboard_v2/main.py; echo ''; echo 'Processo finalizado. Feche esta janela.'; exec bash" &
    PID_FINANCEIRO=$!
    echo "PID_FINANCEIRO=$PID_FINANCEIRO" >> "$PID_FILE"
    sleep 2
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}    TODOS OS SISTEMAS INICIADOS${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    sleep 3
}

# Função para verificar se um processo está rodando pelo PID
is_running() {
    local pid="$1"
    if [ -z "$pid" ]; then
        return 1
    fi
    ps -p "$pid" > /dev/null 2>&1
    return $?
}

# Função para fechar processo por PID e descendentes
close_process() {
    local pid="$1"
    local name="$2"
    echo ""
    echo -e "${YELLOW}Fechando $name...${NC}"
    
    if [ -z "$pid" ]; then
        echo -e "${RED}PID não encontrado.${NC}"
        sleep 2
        return
    fi
    
    if is_running "$pid"; then
        # Matar processo e todos os filhos
        pkill -P "$pid" 2>/dev/null
        kill "$pid" 2>/dev/null
        sleep 1
        # Força se ainda estiver vivo
        kill -9 "$pid" 2>/dev/null
        echo -e "${GREEN}$name fechado com sucesso!${NC}"
    else
        echo -e "${RED}$name já estava parado.${NC}"
    fi
    sleep 2
}

# Função para mostrar status dos sistemas
show_status() {
    load_pids
    echo -e "${CYAN}  SISTEMAS EM EXECUÇÃO:${NC}"
    
    if is_running "$PID_BCE_BACKEND"; then
        echo -e "  ${GREEN}●${NC} [1] BCE Backend      (npm run start:dev)"
    else
        echo -e "  ${RED}○${NC} [1] BCE Backend      (parado)"
    fi
    
    if is_running "$PID_BCE_FRONTEND"; then
        echo -e "  ${GREEN}●${NC} [2] BCE Frontend     (npm run dev)"
    else
        echo -e "  ${RED}○${NC} [2] BCE Frontend     (parado)"
    fi
    
    if is_running "$PID_FINANCEIRO"; then
        echo -e "  ${GREEN}●${NC} [3] Financeiro       (Python Dashboard)"
    else
        echo -e "  ${RED}○${NC} [3] Financeiro       (parado)"
    fi
}

# Função para mostrar menu
show_menu() {
    clear_screen
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}    GERENCIADOR DE SISTEMAS${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    show_status
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}    OPÇÕES${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    echo -e "  ${BLUE}[4]${NC} Fechar BCE Backend"
    echo -e "  ${BLUE}[5]${NC} Fechar BCE Frontend"
    echo -e "  ${BLUE}[6]${NC} Fechar Financeiro"
    echo -e "  ${RED}[7]${NC} Fechar TODOS os sistemas"
    echo -e "  ${BLUE}[8]${NC} Reiniciar todos os sistemas"
    echo -e "  ${YELLOW}[0]${NC} Sair (deixar sistemas rodando)"
    echo ""
    echo -e "${CYAN}========================================${NC}"
}

# Função para fechar todos os sistemas
close_all() {
    load_pids
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}    FECHANDO TODOS OS SISTEMAS${NC}"
    echo -e "${RED}========================================${NC}"
    
    close_process "$PID_BCE_BACKEND" "BCE Backend"
    close_process "$PID_BCE_FRONTEND" "BCE Frontend"
    close_process "$PID_FINANCEIRO" "Financeiro"
    
    echo ""
    echo -e "${GREEN}Todos os sistemas foram fechados!${NC}"
    
    # Limpar arquivo de PIDs
    rm -f "$PID_FILE"
    
    sleep 3
}

# Iniciar sistemas
start_systems

# Loop do menu
while true; do
    show_menu
    read -p "Escolha uma opção: " opcao
    
    load_pids
    
    case $opcao in
        4)
            close_process "$PID_BCE_BACKEND" "BCE Backend"
            ;;
        5)
            close_process "$PID_BCE_FRONTEND" "BCE Frontend"
            ;;
        6)
            close_process "$PID_FINANCEIRO" "Financeiro"
            ;;
        7)
            close_all
            ;;
        8)
            close_all
            start_systems
            ;;
        0)
            echo ""
            echo -e "${GREEN}Sistemas continuarão rodando em segundo plano...${NC}"
            echo -e "${YELLOW}Use este script novamente para gerenciar os sistemas.${NC}"
            sleep 2
            exit 0
            ;;
        *)
            echo -e "${RED}Opção inválida!${NC}"
            sleep 1
            ;;
    esac
done
