@echo off
REM Script para executar Dashboard v2.0
REM Porta: 8052 (para nao conflitar com dashboard antigo na 8051)

echo.
echo ========================================
echo   Dashboard Financeiro v2.0
echo   Dark Theme Professional
echo ========================================
echo.
echo Iniciando servidor...
echo Acesse: http://localhost:8052
echo.
echo Pressione Ctrl+C para parar
echo.

cd /d "%~dp0"
py backend\src\dashboard_v2\main.py

pause
