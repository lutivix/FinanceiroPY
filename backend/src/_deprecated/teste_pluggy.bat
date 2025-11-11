@echo off
REM ========================================================
REM         🔌 TESTE DE INTEGRAÇÃO PLUGGY
REM ========================================================

cd /d "%~dp0"

echo.
echo ========================================================
echo          TESTE DE INTEGRACAO COM PLUGGY
echo ========================================================
echo.
echo 📋 PRE-REQUISITOS:
echo    1. Conta criada em https://meu.pluggy.ai/
echo    2. Credenciais obtidas em https://dashboard.pluggy.ai/
echo    3. Pluggy SDK instalado (pip install pluggy-sdk)
echo.
echo ========================================================
echo.

REM Verifica se o SDK está instalado
python -c "import pluggy_sdk" 2>nul
if errorlevel 1 (
    echo ❌ ERRO: Pluggy SDK não está instalado!
    echo.
    echo 📦 Instalando automaticamente...
    pip install pluggy-sdk
    echo.
)

echo 🚀 Executando teste...
echo.

python teste_pluggy.py

echo.
echo ========================================================
echo ✅ TESTE CONCLUIDO!
echo ========================================================
echo.
echo 💡 Se funcionou, adicione as credenciais em config.ini
echo.
pause
