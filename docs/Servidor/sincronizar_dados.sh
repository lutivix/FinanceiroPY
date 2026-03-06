#!/bin/bash
# =============================================================================
# sincronizar_dados.sh — Sync do banco SQLite Financeiro → LFADM
# =============================================================================
# Execução: rode este script no Nitro5, APÓS rodar o processamento completo
#   com agente_financeiro_completo.sh (opção 1).
#
# O que faz:
#   1. Valida que o financeiro.db existe e foi modificado recentemente
#   2. Copia dados/db/financeiro.db para LFADM via SSH/rsync
#   3. Reinicia o container financeiro-dashboard no LFADM
#   4. Verifica se o dashboard respondeu (health check)
#
# Uso:
#   bash docs/Servidor/sincronizar_dados.sh              # sync real
#   bash docs/Servidor/sincronizar_dados.sh --dry-run    # simulação
#   bash docs/Servidor/sincronizar_dados.sh --status     # apenas status
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Origem (Nitro5)
DB_LOCAL="$REPO_ROOT/dados/db/financeiro.db"
DB_LOCAL_DIR="$REPO_ROOT/dados/db"

# Destino (LFADM)
LFADM_HOST="lfadm"                                         # alias em ~/.ssh/config
LFADM_DADOS_DIR="C:/Servidor/Financeiro/dados/db"
LFADM_CONTAINER="financeiro-dashboard"
LFADM_DASHBOARD_URL="http://192.168.7.106:8052/"

# Tempo máximo (em horas) que o DB pode ter sem ser considerado "desatualizado"
DB_MAX_AGE_HOURS=24

# Flags
DRY_RUN=false
STATUS_ONLY=false

# ---------------------------------------------------------------------------
# Cores
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ---------------------------------------------------------------------------
# Argumentos
# ---------------------------------------------------------------------------
for arg in "$@"; do
    case $arg in
        --dry-run)  DRY_RUN=true ;;
        --status)   STATUS_ONLY=true ;;
        --help|-h)
            sed -n '/^# Uso:/,/^# ====/p' "$0" | grep -v "^# ===="
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Argumento desconhecido: $arg${NC}"
            echo "   Use --dry-run, --status ou --help"
            exit 1
            ;;
    esac
done

# ---------------------------------------------------------------------------
# Funções utilitárias
# ---------------------------------------------------------------------------

log_info()    { echo -e "${CYAN}[INFO]${NC}  $*"; }
log_ok()      { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error()   { echo -e "${RED}[ERRO]${NC}  $*"; }
log_step()    { echo -e "\n${BLUE}▶ $*${NC}"; }
log_dry()     { echo -e "${YELLOW}[DRY-RUN]${NC} $*"; }

banner() {
    echo ""
    echo -e "${CYAN}============================================================${NC}"
    echo -e "${CYAN}  💰 Financeiro — Sync de Dados para LFADM${NC}"
    if $DRY_RUN;    then echo -e "${YELLOW}  ⚠️  MODO DRY-RUN — nenhuma alteração será feita${NC}"; fi
    if $STATUS_ONLY;then echo -e "${BLUE}  ℹ️  MODO STATUS${NC}"; fi
    echo -e "${CYAN}  $(date '+%d/%m/%Y %H:%M:%S')${NC}"
    echo -e "${CYAN}============================================================${NC}"
    echo ""
}

# Tamanho legível
human_size() {
    local file="$1"
    local bytes
    bytes=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo 0)
    awk -v b="$bytes" 'BEGIN {
        if      (b >= 1073741824) printf "%.1f GB", b/1073741824
        else if (b >= 1048576)    printf "%.1f MB", b/1048576
        else if (b >= 1024)       printf "%.1f KB", b/1024
        else                      printf "%d B",    b
    }'
}

# Retorna idade do arquivo em horas (inteiro)
file_age_hours() {
    local file="$1"
    local now mod_time diff
    now=$(date +%s)
    if mod_time=$(date -r "$file" +%s 2>/dev/null); then
        diff=$(( (now - mod_time) / 3600 ))
        echo $diff
    else
        echo 9999
    fi
}

# ---------------------------------------------------------------------------
# STATUS ONLY
# ---------------------------------------------------------------------------

show_status() {
    log_step "Status local (Nitro5)"
    if [ -f "$DB_LOCAL" ]; then
        local age size mdate
        age=$(file_age_hours "$DB_LOCAL")
        size=$(human_size "$DB_LOCAL")
        mdate=$(date -r "$DB_LOCAL" '+%d/%m/%Y %H:%M' 2>/dev/null || echo "?")
        log_ok "financeiro.db encontrado"
        log_info "  Tamanho : $size"
        log_info "  Modificado: $mdate (${age}h atrás)"
        if (( age > DB_MAX_AGE_HOURS )); then
            log_warn "  ⚠️  Banco tem mais de ${DB_MAX_AGE_HOURS}h — rode o processamento antes de sincronizar"
        else
            log_ok "  Banco atualizado (< ${DB_MAX_AGE_HOURS}h)"
        fi
    else
        log_error "financeiro.db NÃO encontrado em: $DB_LOCAL"
    fi

    echo ""
    log_step "Status remoto (LFADM)"
    if ssh -o ConnectTimeout=5 "$LFADM_HOST" "exit" 2>/dev/null; then
        log_ok "SSH OK"

        # DB no LFADM
        local remote_info
        remote_info=$(ssh "$LFADM_HOST" "
            if [ -f '$LFADM_DADOS_DIR/financeiro.db' ]; then
                date -r '$LFADM_DADOS_DIR/financeiro.db' '+%d/%m/%Y %H:%M' 2>/dev/null || echo '?'
            else
                echo 'AUSENTE'
            fi
        " 2>/dev/null) || remote_info="erro"
        log_info "  DB no LFADM: $remote_info"

        # Container
        local container_status
        container_status=$(ssh "$LFADM_HOST" "docker inspect --format='{{.State.Status}} | {{.State.Health.Status}}' $LFADM_CONTAINER 2>/dev/null" 2>/dev/null) || container_status="não encontrado"
        log_info "  Container : $container_status"
    else
        log_error "SSH para LFADM falhou — verifique conexão e chave id_lfadm"
    fi

    echo ""
    log_step "Health check do Dashboard"
    local http_code
    http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$LFADM_DASHBOARD_URL" 2>/dev/null) || http_code="timeout"
    if [ "$http_code" = "200" ]; then
        log_ok "Dashboard respondendo (HTTP $http_code)"
    else
        log_warn "Dashboard: HTTP $http_code (pode estar reiniciando ou fora do ar)"
    fi
}

# ---------------------------------------------------------------------------
# SYNC PRINCIPAL
# ---------------------------------------------------------------------------

check_prerequisites() {
    log_step "Verificando pré-requisitos"

    # SSH / SCP disponível?
    if ! command -v ssh &>/dev/null; then
        log_error "ssh não encontrado"
        exit 1
    fi
    log_ok "ssh disponível"

    if ! command -v scp &>/dev/null; then
        log_error "scp não encontrado"
        exit 1
    fi
    log_ok "scp disponível"
}

check_db_local() {
    log_step "Validando banco de dados local"

    if [ ! -f "$DB_LOCAL" ]; then
        log_error "financeiro.db não encontrado em: $DB_LOCAL"
        log_error "Execute o processamento completo primeiro:"
        log_error "  bash agente_financeiro_completo.sh  →  opção [1]"
        exit 1
    fi
    log_ok "financeiro.db encontrado"

    local age size mdate
    age=$(file_age_hours "$DB_LOCAL")
    size=$(human_size "$DB_LOCAL")
    mdate=$(date -r "$DB_LOCAL" '+%d/%m/%Y %H:%M' 2>/dev/null || echo "?")

    log_info "  Caminho  : $DB_LOCAL"
    log_info "  Tamanho  : $size"
    log_info "  Modificado: $mdate (${age}h atrás)"

    if (( age > DB_MAX_AGE_HOURS )); then
        log_warn "⚠️  O banco tem mais de ${DB_MAX_AGE_HOURS}h sem modificação."
        log_warn "   Considere rodar o processamento antes de sincronizar."
        echo ""
        read -rp "   Continuar mesmo assim? [s/N] " confirm
        if [[ ! "$confirm" =~ ^[Ss]$ ]]; then
            log_info "Sync cancelado pelo usuário."
            exit 0
        fi
    else
        log_ok "Banco atualizado (< ${DB_MAX_AGE_HOURS}h)"
    fi
}

check_ssh() {
    log_step "Verificando conexão SSH com LFADM"
    if ! ssh -o ConnectTimeout=10 "$LFADM_HOST" "exit" 2>/dev/null; then
        log_error "Não foi possível conectar ao LFADM via SSH"
        log_error "Verifique:"
        log_error "  1. LFADM está ligado e acessível (192.168.7.106)"
        log_error "  2. ~/.ssh/config tem entrada para 'lfadm'"
        log_error "  3. Chave id_lfadm está configurada"
        exit 1
    fi
    log_ok "SSH OK → $LFADM_HOST"
}

sync_database() {
    log_step "Sincronizando banco de dados"
    log_info "  Origem : $DB_LOCAL"
    log_info "  Destino: $LFADM_HOST:$LFADM_DADOS_DIR/financeiro.db"
    echo ""

    if $DRY_RUN; then
        log_dry "scp dados/db/financeiro.db → $LFADM_HOST:$LFADM_DADOS_DIR/financeiro.db (simulado)"
        log_dry "Arquivo local : $(human_size "$DB_LOCAL")"
        local remote_size
        remote_size=$(ssh "$LFADM_HOST" "
            if [ -f '$LFADM_DADOS_DIR/financeiro.db' ]; then
                stat -c%s '$LFADM_DADOS_DIR/financeiro.db' 2>/dev/null || echo 0
            else
                echo 0
            fi
        " 2>/dev/null) || remote_size=0
        local local_size
        local_size=$(stat -c%s "$DB_LOCAL" 2>/dev/null || echo 0)
        if [ "$local_size" = "$remote_size" ]; then
            log_dry "Arquivos idênticos (mesmo tamanho) — nada seria transferido"
        else
            log_dry "Diferença detectada → arquivo seria transferido"
        fi
        return 0
    fi

    # Garante que o diretório existe no LFADM
    ssh "$LFADM_HOST" "mkdir -p '$LFADM_DADOS_DIR'" 2>/dev/null || true

    # Cópia via scp
    scp "$DB_LOCAL" "${LFADM_HOST}:${LFADM_DADOS_DIR}/financeiro.db"

    log_ok "Banco sincronizado com sucesso"
}

restart_container() {
    log_step "Reiniciando container $LFADM_CONTAINER"

    if $DRY_RUN; then
        log_dry "docker restart $LFADM_CONTAINER (simulado)"
        return 0
    fi

    local restart_output
    restart_output=$(ssh "$LFADM_HOST" "docker restart $LFADM_CONTAINER 2>&1") || {
        log_error "Falha ao reiniciar container: $restart_output"
        exit 1
    }
    log_ok "Container reiniciado"

    log_info "Aguardando container inicializar..."
    sleep 5
}

health_check() {
    log_step "Health check do Dashboard"

    if $DRY_RUN; then
        log_dry "curl $LFADM_DASHBOARD_URL (simulado)"
        return 0
    fi

    local attempts=0
    local max_attempts=10
    local http_code

    while (( attempts < max_attempts )); do
        (( attempts++ ))
        http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$LFADM_DASHBOARD_URL" 2>/dev/null) || http_code="0"

        if [ "$http_code" = "200" ]; then
            log_ok "Dashboard respondendo (HTTP 200) ✅"
            return 0
        fi

        log_info "  Tentativa $attempts/$max_attempts — HTTP $http_code — aguardando..."
        sleep 3
    done

    # Não falha o script — sync já foi feito, dashboard pode demorar mais pra subir
    log_warn "Dashboard ainda não respondeu HTTP 200 (pode levar mais alguns segundos)"
    log_warn "Acesse manualmente: $LFADM_DASHBOARD_URL"
    log_warn "Ou verifique: ssh lfadm \"docker logs $LFADM_CONTAINER --tail 30\""
    return 0
}

print_summary() {
    local db_mdate
    db_mdate=$(date -r "$DB_LOCAL" '+%d/%m/%Y %H:%M' 2>/dev/null || echo "?")

    echo ""
    echo -e "${CYAN}============================================================${NC}"
    echo -e "${GREEN}  ✅ SYNC CONCLUÍDO COM SUCESSO${NC}"
    echo -e "${CYAN}============================================================${NC}"
    echo ""
    echo -e "  📦 Banco sincronizado  : $db_mdate"
    echo -e "  🖥️  Servidor            : LFADM (192.168.7.106)"
    echo -e "  🐳 Container           : $LFADM_CONTAINER (reiniciado)"
    echo -e "  🌐 Dashboard           : $LFADM_DASHBOARD_URL"
    echo ""
}

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
banner

if $STATUS_ONLY; then
    show_status
    exit 0
fi

check_prerequisites
check_db_local
check_ssh
sync_database
restart_container
health_check

if ! $DRY_RUN; then
    print_summary
else
    echo ""
    log_dry "Dry-run concluído. Nenhuma alteração foi feita."
    echo -e "  Para executar de verdade: ${GREEN}bash docs/Servidor/sincronizar_dados.sh${NC}"
fi
