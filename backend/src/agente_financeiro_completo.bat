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

REM Define o caminho do Conda
set "CONDA_EXE=C:\ProgramData\anaconda3\Scripts\conda.exe"
set "CONDA_ENV=financeiro"

REM Verifica se o Conda está disponível
if not exist "%CONDA_EXE%" (
    echo ❌ ERRO: Anaconda nao encontrado em %CONDA_EXE%
    echo 💡 Verifique se o Anaconda esta instalado corretamente.
    echo.
    pause
    popd
    exit /b 1
)

REM Verifica se o ambiente existe
"%CONDA_EXE%" env list | findstr /C:"%CONDA_ENV%" >nul 2>&1
if errorlevel 1 (
    echo ❌ ERRO: Ambiente conda '%CONDA_ENV%' nao encontrado!
    echo 💡 Execute: conda create -n %CONDA_ENV% python=3.11
    echo.
    pause
    popd
    exit /b 1
)

echo ✅ Usando ambiente Conda: %CONDA_ENV%

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
echo [5] 💾 Atualizar Dicionario (do Banco de Dados)
echo [6] 🧹 Limpar Categorias Duplicadas (Manutencao)
echo [7] ❌ Sair
echo.
set /p opcao="Digite sua opcao (1-7): "

if "%opcao%"=="1" goto :completo
if "%opcao%"=="2" goto :agente
if "%opcao%"=="3" goto :dicionario
if "%opcao%"=="4" goto :controle
if "%opcao%"=="5" goto :dicionario_db
if "%opcao%"=="6" goto :limpeza
if "%opcao%"=="7" goto :sair

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
"%CONDA_EXE%" run -n %CONDA_ENV% python agente_financeiro.py
if errorlevel 1 (
    echo ❌ Erro no processamento principal!
    pause
    goto :inicio
)
echo.
echo ⏳ Atualizando dicionario do Excel...
"%CONDA_EXE%" run -n %CONDA_ENV% python atualiza_dicionario.py
if errorlevel 1 (
    echo ❌ Erro na atualização do dicionário Excel!
    pause
    goto :inicio
)
echo.
echo ⏳ Atualizando dicionario do Controle...  
"%CONDA_EXE%" run -n %CONDA_ENV% python atualiza_dicionario_controle.py
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
"%CONDA_EXE%" run -n %CONDA_ENV% python agente_financeiro.py
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
"%CONDA_EXE%" run -n %CONDA_ENV% python atualiza_dicionario.py
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
"%CONDA_EXE%" run -n %CONDA_ENV% python atualiza_dicionario_controle.py
if errorlevel 1 (
    echo ❌ Erro na atualização do dicionário!
    pause
    goto :inicio
)
goto :fim

:dicionario_db
cls
echo.
echo ========================================================
echo     💾 ATUALIZANDO DICIONARIO (BANCO DE DADOS)
echo ========================================================
echo.
echo 📊 Lendo categorizacoes da tabela lancamentos...
"%CONDA_EXE%" run -n %CONDA_ENV% python atualiza_dicionario_unificado.py db
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
"%CONDA_EXE%" run -n %CONDA_ENV% python limpar_categorias.py
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