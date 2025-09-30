#!/usr/bin/env python3
"""
Script de teste para o Agente Financeiro IA
Execute este script para testar o sistema com dados de exemplo
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta

def criar_dados_exemplo():
    """Cria dados de exemplo para teste."""
    print("🧪 Criando dados de exemplo para teste...")
    
    # Obtém diretório do projeto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    dados_dir = os.path.join(project_root, "dados")
    
    # Cria estrutura se não existir
    os.makedirs(os.path.join(dados_dir, "db"), exist_ok=True)
    os.makedirs(os.path.join(dados_dir, "planilhas"), exist_ok=True)
    
    # Data atual para os exemplos
    hoje = datetime.now()
    mes_atual = hoje.strftime("%Y%m")
    mes_anterior = (hoje - timedelta(days=30)).strftime("%Y%m")
    
    # Cria extrato PIX de exemplo
    extrato_pix = [
        f"{hoje.strftime('%d/%m/%Y')};PIX TRANSF MERCADO LIVRE;-45,90",
        f"{(hoje - timedelta(days=1)).strftime('%d/%m/%Y')};PIX QRS UBER TRIP;-12,50",
        f"{(hoje - timedelta(days=2)).strftime('%d/%m/%Y')};PIX TRANSF IFOOD DELIVERY;-28,75",
        f"{(hoje - timedelta(days=3)).strftime('%d/%m/%Y')};REND PAGO APLIC AUT MAIS;15,30",
        f"{(hoje - timedelta(days=4)).strftime('%d/%m/%Y')};PIX TRANSF POSTO BR;-85,00",
    ]
    
    arquivo_pix = os.path.join(dados_dir, "planilhas", f"{mes_atual}_Extrato.txt")
    with open(arquivo_pix, 'w', encoding='utf-8') as f:
        f.write('\n'.join(extrato_pix))
    
    print(f"✅ Criado: {arquivo_pix}")
    
    # Cria extrato Itaú de exemplo
    dados_itau = [
        ["Data", "Descrição", "Valor", "Valor"],
        [hoje.strftime('%d/%m/%Y'), "COMPRA CARTAO FINAL 4059", "", -89.50],
        [(hoje - timedelta(days=1)).strftime('%d/%m/%Y'), "SUPERMERCADO SAO LUIZ", "", -156.78],
        [(hoje - timedelta(days=2)).strftime('%d/%m/%Y'), "POSTO IPIRANGA", "", -95.00],
        [(hoje - timedelta(days=3)).strftime('%d/%m/%Y'), "FARMACIA DROGA RAIA", "", -42.30],
        ["FINAL", "4059", "", ""],
    ]
    
    df_itau = pd.DataFrame(dados_itau[1:], columns=dados_itau[0])
    arquivo_itau = os.path.join(dados_dir, "planilhas", f"{mes_atual}_Itau.xls")
    df_itau.to_excel(arquivo_itau, index=False)
    
    print(f"✅ Criado: {arquivo_itau}")
    
    # Cria extrato Latam de exemplo
    dados_latam = [
        ["Data", "Descrição", "Valor", "Valor"],
        [hoje.strftime('%d/%m/%Y'), "COMPRA CARTAO FINAL 1152", "", -120.00],
        [(hoje - timedelta(days=1)).strftime('%d/%m/%Y'), "NETFLIX BRASIL", "", -39.90],
        [(hoje - timedelta(days=2)).strftime('%d/%m/%Y'), "SPOTIFY PREMIUM", "", -19.90],
        [(hoje - timedelta(days=3)).strftime('%d/%m/%Y'), "AMAZON PRIME", "", -14.90],
        ["FINAL", "1152", "", ""],
    ]
    
    df_latam = pd.DataFrame(dados_latam[1:], columns=dados_latam[0])
    arquivo_latam = os.path.join(dados_dir, "planilhas", f"{mes_atual}_Latam.xls")
    df_latam.to_excel(arquivo_latam, index=False)
    
    print(f"✅ Criado: {arquivo_latam}")
    
    print(f"\n📁 Dados de exemplo criados em: {dados_dir}")
    return dados_dir

def testar_sistema():
    """Testa o sistema com os dados de exemplo."""
    print("\n🧪 INICIANDO TESTE DO SISTEMA")
    print("=" * 40)
    
    try:
        # Importa o debug helper
        from debug_helper import debug_info, debug_processamento
        
        # Cria dados se necessário
        dados_dir = criar_dados_exemplo()
        
        # Executa debug
        debug_info(dados_dir)
        debug_processamento(dados_dir, limite_arquivos=3)
        
        print("\n✅ Teste concluído com sucesso!")
        print("💡 Agora você pode executar o agente principal:")
        print("   python agente_financeiro.py")
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("💡 Execute este script do diretório backend/src/")
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")

if __name__ == "__main__":
    print("🧪 TESTE DO AGENTE FINANCEIRO IA")
    print("=" * 40)
    
    resposta = input("Deseja criar dados de exemplo e testar? (s/n): ").lower().strip()
    
    if resposta in ['s', 'sim', 'y', 'yes']:
        testar_sistema()
    else:
        print("👋 Teste cancelado pelo usuário")