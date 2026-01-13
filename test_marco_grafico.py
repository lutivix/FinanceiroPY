"""Teste rápido para verificar se março está sendo reconhecido"""
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / 'backend' / 'src'))

from dashboard_v2.utils.graficos import criar_grafico_evolucao

print("Testando gráfico de evolução...")
fig = criar_grafico_evolucao('TODOS')

if fig.data:
    x_values = fig.data[0].x
    y_values = fig.data[0].y
    text_values = fig.data[0].text  # Labels reais
    
    print(f"\nTotal de meses no gráfico: {len(x_values)}")
    print("\nMeses e valores:")
    for idx, (mes, valor) in enumerate(zip(text_values, y_values)):
        print(f"  {idx}: {mes} - R$ {valor:,.2f}")
    
    # Verificar se março está presente
    marco_presente = any('março' in str(mes).lower() for mes in text_values)
    print(f"\nMarço presente: {'✓ SIM' if marco_presente else '✗ NÃO'}")
else:
    print("Nenhum dado encontrado")
