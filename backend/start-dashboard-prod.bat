@echo off
REM Script para iniciar Dashboard v2 em produção (Windows)

cd /d "%~dp0src\dashboard_v2"

echo 🚀 Iniciando Dashboard Financeiro v2 em modo produção...
echo 📍 Host: 0.0.0.0:8052
echo 🔒 Acesse: http://localhost:8052
echo.

REM Usando Waitress (recomendado para Windows)
waitress-serve --host=0.0.0.0 --port=8052 --threads=4 wsgi:server
