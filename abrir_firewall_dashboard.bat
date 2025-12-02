@echo off
echo ========================================
echo Abrindo porta 8050 no Firewall
echo ========================================
echo.

netsh advfirewall firewall delete rule name="Dashboard Financeiro - Dash" >nul 2>&1
netsh advfirewall firewall add rule name="Dashboard Financeiro - Dash" dir=in action=allow protocol=TCP localport=8050

echo.
if %ERRORLEVEL% EQU 0 (
    echo [OK] Porta 8050 liberada no firewall!
    echo.
    echo Agora outras maquinas podem acessar:
    echo http://192.168.7.216:8050
) else (
    echo [ERRO] Nao foi possivel adicionar regra.
    echo Execute este arquivo como Administrador.
)
echo.
echo ========================================
pause
