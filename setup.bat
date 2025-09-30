@echo off
REM Script de setup para Windows - Agente Financeiro IA

echo 🏦 Configurando Agente Financeiro IA...

REM Cria estrutura de diretórios
echo 📁 Criando estrutura de diretórios...
if not exist "dados\db" mkdir dados\db
if not exist "dados\planilhas" mkdir dados\planilhas
if not exist "dados\backup" mkdir dados\backup

REM Instala dependências
echo 📦 Instalando dependências Python...
pip install -r requirements.txt

REM Copia arquivo de configuração
echo ⚙️ Configurando projeto...
if not exist "backend\src\config.ini" (
    copy "backend\src\config.example.ini" "backend\src\config.ini"
    echo ✅ Arquivo config.ini criado!
    echo 💡 Edite backend\src\config.ini para ajustar seus caminhos
) else (
    echo ⚠️  config.ini já existe
)

echo.
echo 🎉 Setup concluído com sucesso!
echo.
echo 📋 Próximos passos:
echo 1. Edite backend\src\config.ini com seus caminhos
echo 2. Coloque seus extratos em dados\planilhas\
echo 3. Execute: cd backend\src ^&^& python agente_financeiro.py
echo.
echo 📖 Veja o README.md para mais informações

pause