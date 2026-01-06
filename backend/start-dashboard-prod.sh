#!/bin/bash
# Script para iniciar Dashboard v2 em produção (Linux/Mac)

cd "$(dirname "$0")/src/dashboard_v2"

echo "🚀 Iniciando Dashboard Financeiro v2 em modo produção..."
echo "📍 Host: 0.0.0.0:8052"
echo "🔒 Acesse: http://localhost:8052"
echo ""

# Usando Gunicorn (recomendado para Linux)
gunicorn wsgi:server \
    --bind 0.0.0.0:8052 \
    --workers 4 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
