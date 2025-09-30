@echo off
setlocal enabledelayedexpansion
title Agente Financeiro IA - Sistema Completo
color 0A

REM Obtém o diretório onde o .bat está localizado
set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%"

echo.
echo ========================================================
echo          🚀 AGENTE FINANCEIRO IA v2.0 🚀
echo ========================================================
echo 📁 Executando de: %SCRIPT_DIR%
echo.

REM Verifica se o Python está disponível
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERRO: Python nao encontrado no PATH!
    echo 💡 Tente executar pelo VS Code ou configure o PATH do Python.
    echo.
    pause
    popd
    exit /b 1
)

REM Verifica se os arquivos principais existem
if not exist "agente_financeiro.py" (
    echo ❌ ERRO: agente_financeiro.py nao encontrado!
    echo 📁 Diretorio atual: %CD%
    echo 💡 Verifique se os arquivos estao no local correto.
    echo.
    pause
    popd
    exit /b 1
)

REM Verifica configuração
if exist "config.ini" (
    echo ✅ Configuracao encontrada: config.ini
) else if exist "config.example.ini" (
    echo ⚠️  Usando configuracao padrao: config.example.ini
) else (
    echo ❌ ERRO: Nenhum arquivo de configuracao encontrado!
    echo 💡 Certifique-se que config.ini ou config.example.ini existe.
    pause
    popd
    exit /b 1
)

echo ✅ Ambiente validado com sucesso!
echo.

:inicio
cls
echo.
echo ========================================================
echo          🚀 AGENTE FINANCEIRO IA v2.0 🚀
echo ========================================================
echo.
echo Selecione uma opcao:
echo.
echo [1] 🔄 Executar Processamento Completo (Recomendado)
echo [2] 📊 Apenas Processar Transacoes (Agente Principal)  
echo [3] 📚 Atualizar Dicionario (do Excel consolidado)
echo [4] 📋 Atualizar Dicionario (do Controle_pessoal.xlsm)
echo [5] 🧹 Limpar Categorias Duplicadas (Manutencao)
echo [6] ❌ Sair
echo.
set /p opcao="Digite sua opcao (1-6): "

if "%opcao%"=="1" goto :completo
if "%opcao%"=="2" goto :agente
if "%opcao%"=="3" goto :dicionario
if "%opcao%"=="4" goto :controle
if "%opcao%"=="5" goto :limpeza
if "%opcao%"=="6" goto :sair

echo.
echo ❌ Opcao invalida! Tente novamente.
timeout /t 2 >nul
goto :inicio

:completo
cls
echo.
echo ========================================================
echo         🔄 PROCESSAMENTO COMPLETO INICIADO
echo ========================================================
echo.
echo ⏳ Executando processamento principal...
python agente_financeiro.py
if errorlevel 1 (
    echo ❌ Erro no processamento principal!
    pause
    goto :inicio
)
echo.
echo ⏳ Atualizando dicionario do Excel...
python atualiza_dicionario.py
if errorlevel 1 (
    echo ❌ Erro na atualização do dicionário Excel!
    pause
    goto :inicio
)
echo.
echo ⏳ Atualizando dicionario do Controle...  
python atualiza_dicionario_controle.py
if errorlevel 1 (
    echo ❌ Erro na atualização do dicionário Controle!
    pause
    goto :inicio
)
echo.
echo ✅ PROCESSAMENTO COMPLETO FINALIZADO!
goto :fim

:agente
cls
echo.
echo ========================================================
echo           📊 PROCESSANDO TRANSACOES
echo ========================================================
echo.
python agente_financeiro.py
if errorlevel 1 (
    echo ❌ Erro no processamento!
    pause
    goto :inicio
)
goto :fim

:dicionario
cls
echo.
echo ========================================================
echo         📚 ATUALIZANDO DICIONARIO (EXCEL)
echo ========================================================
echo.
python atualiza_dicionario.py
if errorlevel 1 (
    echo ❌ Erro na atualização do dicionário!
    pause
    goto :inicio
)
goto :fim

:controle
cls
echo.
echo ========================================================
echo        📋 ATUALIZANDO DICIONARIO (CONTROLE)
echo ========================================================
echo.
python atualiza_dicionario_controle.py
if errorlevel 1 (
    echo ❌ Erro na atualização do dicionário!
    pause
    goto :inicio
)
goto :fim

:limpeza
cls
echo.
echo ========================================================
echo           🧹 LIMPANDO CATEGORIAS DUPLICADAS
echo ========================================================
echo.
python limpar_categorias.py
if errorlevel 1 (
    echo ❌ Erro na limpeza!
    pause
    goto :inicio
)
goto :fim

:sair
echo.
echo 👋 Ate logo!
timeout /t 2 >nul
popd
exit /b 0

:fim
echo.
echo ========================================================
echo ✅ OPERACAO CONCLUIDA COM SUCESSO!
echo ========================================================
echo.
echo Deseja executar outra operacao?
echo.
echo [S] Sim - Voltar ao menu
echo [N] Nao - Sair
echo.
set /p continuar="Digite sua opcao (S/N): "
if /i "%continuar%"=="S" goto :inicio
if /i "%continuar%"=="s" goto :inicio

echo.
echo 👋 Obrigado por usar o Agente Financeiro IA!
echo 💡 Pressione qualquer tecla para fechar...
pause >nul
popd
exit /b 0