#!/bin/bash
# Script de setup para o Agente Financeiro IA

echo "🏦 Configurando Agente Financeiro IA..."

# Cria estrutura de diretórios
echo "📁 Criando estrutura de diretórios..."
mkdir -p dados/db
mkdir -p dados/planilhas
mkdir -p dados/backup

# Instala dependências
echo "📦 Instalando dependências Python..."
pip install -r requirements.txt

# Copia arquivo de configuração
echo "⚙️ Configurando projeto..."
if [ ! -f "backend/src/config.ini" ]; then
    cp backend/src/config.example.ini backend/src/config.ini
    echo "✅ Arquivo config.ini criado!"
    echo "💡 Edite backend/src/config.ini para ajustar seus caminhos"
else
    echo "⚠️  config.ini já existe"
fi

# Verifica estrutura
echo "🔍 Verificando estrutura..."
if [ -d "dados/db" ] && [ -d "dados/planilhas" ]; then
    echo "✅ Estrutura de diretórios OK"
else
    echo "❌ Erro na criação de diretórios"
    exit 1
fi

echo ""
echo "🎉 Setup concluído com sucesso!"
echo ""
echo "📋 Próximos passos:"
echo "1. Edite backend/src/config.ini com seus caminhos"
echo "2. Coloque seus extratos em dados/planilhas/"
echo "3. Execute: cd backend/src && python agente_financeiro.py"
echo ""
echo "📖 Veja o README.md para mais informações"