"""
Script para testar a lógica do ciclo 19-18
"""
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from services.file_processing_service import FileProcessingService

def testar_logica_ciclo():
    """Testa a lógica do ciclo 19-18"""
    
    print("=" * 70)
    print("TESTE DA LÓGICA DO CICLO 19-18")
    print("=" * 70)
    
    hoje = datetime.today()
    print(f"\n📅 Data de hoje: {hoje.strftime('%d/%m/%Y')}")
    print(f"   Dia do mês: {hoje.day}")
    
    # Lógica corrigida
    if hoje.day >= 19:
        mes_atual = hoje.month + 1
        ano_atual = hoje.year
        if mes_atual > 12:
            mes_atual = 1
            ano_atual += 1
        ciclo_info = f"A partir do dia 19, o ciclo atual é do PRÓXIMO mês"
    else:
        mes_atual = hoje.month
        ano_atual = hoje.year
        ciclo_info = f"Antes do dia 19, o ciclo atual é do mês CORRENTE"
    
    meses_pt = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    
    print(f"\n💡 {ciclo_info}")
    print(f"   Mês atual do ciclo: {meses_pt[mes_atual]} de {ano_atual}")
    print(f"   Arquivo esperado: {ano_atual}{mes_atual:02d}_Extrato.txt")
    
    # Lista arquivos que deveriam ser buscados
    print(f"\n📁 Arquivos dos últimos 3 meses que deveriam ser buscados:")
    for i in range(3):
        mes = mes_atual - i
        ano = ano_atual
        while mes <= 0:
            mes += 12
            ano -= 1
        print(f"   {i+1}. {ano}{mes:02d}_*.* ({meses_pt[mes]} {ano})")
    
    # Testa com o serviço real
    print(f"\n🔍 Testando busca de arquivos reais...")
    try:
        # Assume que o diretório de dados está em ../../dados
        data_dir = Path(__file__).parent.parent.parent / "dados"
        if not data_dir.exists():
            print(f"   ⚠️ Diretório de dados não encontrado: {data_dir}")
            return
        
        service = FileProcessingService(data_dir)
        arquivos = service.find_recent_files(months_back=3)
        
        if arquivos:
            print(f"   ✅ Encontrados {len(arquivos)} arquivo(s):")
            for chave, caminho in arquivos.items():
                print(f"      - {chave}: {caminho.name}")
        else:
            print(f"   ℹ️ Nenhum arquivo encontrado")
            
        # Lista o que existe no diretório
        planilhas_dir = data_dir / "planilhas"
        if planilhas_dir.exists():
            arquivos_disponiveis = list(planilhas_dir.glob("*.txt")) + list(planilhas_dir.glob("*.xls*"))
            if arquivos_disponiveis:
                print(f"\n📋 Arquivos disponíveis no diretório:")
                for arq in sorted(arquivos_disponiveis):
                    print(f"      - {arq.name}")
                    
    except Exception as e:
        print(f"   ❌ Erro ao testar serviço: {e}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    testar_logica_ciclo()
