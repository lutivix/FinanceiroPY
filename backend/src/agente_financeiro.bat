@echo off
cd /d "D:\Professional\Projetos\Github\Financeiro\backend\src"
C:\ProgramData\anaconda3\Scripts\conda.exe run -n financeiro python agente_financeiro.py
echo.
echo ✅ Fim do processamento do agente financeiro. Pressione qualquer tecla para fechar...
pause >nul
