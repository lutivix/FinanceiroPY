@echo off
title Agente Financeiro IA - Sistema Completo
cd /d "%~dp0"
cls

:inicio
echo.
echo ========================================================
echo           🤖 AGENTE FINANCEIRO IA v2.0
echo ========================================================
echo 📂 Diretorio: %~dp0
echo.
echo 🎯 Selecione uma opcao:
echo.
echo [1] 🚀 Executar Processamento Completo (Recomendado)
echo [2] 📊 Apenas Processar Transacoes (Agente Principal)  
echo [3] 📚 Atualizar Dicionario (do Excel consolidado)
echo [4] 📋 Atualizar Dicionario (do Controle_pessoal.xlsm)
echo [5] 🧹 Limpar Categorias Duplicadas (Manutencao)
echo [6] 🚪 Sair
echo.
set /p opcao="Digite sua opcao (1-6): "

if "%opcao%"=="1" goto :completo
if "%opcao%"=="2" goto :agente
if "%opcao%"=="3" goto :dicionario
if "%opcao%"=="4" goto :controle
if "%opcao%"=="5" goto :limpeza
if "%opcao%"=="6" goto :sair

echo ❌ Opcao invalida! Tente novamente.
timeout /t 2 >nul
goto :inicio

:completo
cls
echo ========================================================
echo         🔄 PROCESSAMENTO COMPLETO INICIADO
echo ========================================================
echo.
python agente_financeiro.py
echo.
python atualiza_dicionario.py  
echo.
python atualiza_dicionario_controle.py
echo.
echo ✅ PROCESSAMENTO COMPLETO FINALIZADO!
goto :fim

:agente
cls
echo ========================================================
echo           📊 PROCESSANDO TRANSACOES
echo ========================================================
python agente_financeiro.py
goto :fim

:dicionario
cls
echo ========================================================
echo         📚 ATUALIZANDO DICIONARIO (EXCEL)
echo ========================================================
python atualiza_dicionario.py
goto :fim

:controle
cls
echo ========================================================
echo        📋 ATUALIZANDO DICIONARIO (CONTROLE)
echo ========================================================
python atualiza_dicionario_controle.py
goto :fim

:limpeza
cls
echo ========================================================
echo           🧹 LIMPANDO CATEGORIAS DUPLICADAS
echo ========================================================
python limpar_categorias.py
goto :fim

:sair
echo 👋 Ate logo!
timeout /t 2 >nul
exit

:fim
echo.
echo ========================================================
echo ✅ OPERACAO CONCLUIDA COM SUCESSO!
echo ========================================================
echo.
echo 💭 Deseja executar outra operacao?
set /p continuar="[S]im ou [N]ao: "
if /i "%continuar%"=="S" goto :inicio
echo 👋 Obrigado por usar o Agente Financeiro IA!
pause