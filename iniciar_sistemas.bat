@echo off
chcp 65001 >nul
title Gerenciador de Sistemas
color 0A

:: Variáveis de controle de processos
set "PID_BCE_BACKEND="
set "PID_BCE_FRONTEND="
set "PID_FINANCEIRO="

:: Caminhos dos sistemas
set "PATH_BCE=C:\Servidor\BelgoEstoqueFSTS"
set "PATH_FINANCEIRO=C:\Servidor\Financeiro"

echo ========================================
echo    INICIANDO SISTEMAS
echo ========================================
echo.

:: Iniciar Backend BCE
echo [1/3] Iniciando Backend BCE...
start "BCE Backend" /D "%PATH_BCE%\backend" cmd /k "npm run start:dev"
timeout /t 2 >nul

:: Iniciar Frontend BCE
echo [2/3] Iniciando Frontend BCE...
start "BCE Frontend" /D "%PATH_BCE%\frontend-vite" cmd /k "npm run dev"
timeout /t 2 >nul

:: Iniciar Backend Financeiro
echo [3/3] Iniciando Backend Financeiro...
start "Financeiro Backend" /D "%PATH_FINANCEIRO%" cmd /k "py backend/src/dashboard_v2/main.py"
timeout /t 2 >nul

echo.
echo ========================================
echo    TODOS OS SISTEMAS INICIADOS
echo ========================================
echo.

:MENU
cls
echo ========================================
echo    GERENCIADOR DE SISTEMAS
echo ========================================
echo.
echo  SISTEMAS EM EXECUCAO:
echo  [1] BCE Backend      (npm run start:dev)
echo  [2] BCE Frontend     (npm run dev)
echo  [3] Financeiro       (Python Dashboard)
echo.
echo ========================================
echo    OPCOES
echo ========================================
echo.
echo  [4] Fechar BCE Backend
echo  [5] Fechar BCE Frontend
echo  [6] Fechar Financeiro
echo  [7] Fechar TODOS os sistemas
echo  [0] Sair (deixar sistemas rodando)
echo.
echo ========================================
set /p opcao="Escolha uma opcao: "

if "%opcao%"=="4" goto FECHAR_BCE_BACKEND
if "%opcao%"=="5" goto FECHAR_BCE_FRONTEND
if "%opcao%"=="6" goto FECHAR_FINANCEIRO
if "%opcao%"=="7" goto FECHAR_TODOS
if "%opcao%"=="0" goto SAIR
goto MENU

:FECHAR_BCE_BACKEND
echo.
echo Fechando BCE Backend...
taskkill /FI "WINDOWTITLE eq BCE Backend*" /T /F >nul 2>&1
echo BCE Backend fechado!
timeout /t 2 >nul
goto MENU

:FECHAR_BCE_FRONTEND
echo.
echo Fechando BCE Frontend...
taskkill /FI "WINDOWTITLE eq BCE Frontend*" /T /F >nul 2>&1
echo BCE Frontend fechado!
timeout /t 2 >nul
goto MENU

:FECHAR_FINANCEIRO
echo.
echo Fechando Financeiro...
taskkill /FI "WINDOWTITLE eq Financeiro Backend*" /T /F >nul 2>&1
echo Financeiro fechado!
timeout /t 2 >nul
goto MENU

:FECHAR_TODOS
echo.
echo ========================================
echo    FECHANDO TODOS OS SISTEMAS
echo ========================================
echo.
echo Fechando BCE Backend...
taskkill /FI "WINDOWTITLE eq BCE Backend*" /T /F >nul 2>&1
echo Fechando BCE Frontend...
taskkill /FI "WINDOWTITLE eq BCE Frontend*" /T /F >nul 2>&1
echo Fechando Financeiro...
taskkill /FI "WINDOWTITLE eq Financeiro Backend*" /T /F >nul 2>&1
echo.
echo Todos os sistemas foram fechados!
timeout /t 3 >nul
exit

:SAIR
echo.
echo Sistemas continuarao rodando em segundo plano...
echo Use o menu novamente para gerenciar os sistemas.
timeout /t 2 >nul
exit
