# ============================================
# Financeiro Dashboard — Dockerfile
# ============================================
# Stack: Python 3.11 + Dash/Plotly + Gunicorn
# Porta: 8052
# DB: SQLite (volume externo em /app/dados/)
# ============================================

# --- Stage: production ---
FROM python:3.11-slim

LABEL maintainer="Luciano - LF Solutions"
LABEL description="Dashboard Financeiro v2 - Dash/Plotly"

WORKDIR /app

# Dependências de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências Python
COPY backend/requirements-dashboard.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY backend/src/ ./backend/src/
COPY config/ ./config/

# Criar usuário não-root
RUN adduser --disabled-password --gecos "" --uid 1001 appuser

# Criar diretório de dados (será montado como volume)
RUN mkdir -p /app/dados/db && chown -R appuser:appuser /app

USER appuser

EXPOSE 8052

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8052/ || exit 1

# Gunicorn em produção
CMD ["gunicorn", "wsgi:server", \
     "--bind", "0.0.0.0:8052", \
     "--workers", "2", \
     "--threads", "2", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "--chdir", "/app/backend/src/dashboard_v2"]
