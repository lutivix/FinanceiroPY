import pandas as pd
import locale
from datetime import datetime

# Testar locale
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
    except:
        pass

print(f"Locale atual: {locale.getlocale(locale.LC_TIME)}")

# Testar conversões
teste1 = pd.to_datetime('março 2025', format='%B %Y', errors='coerce')
teste2 = pd.to_datetime('Março 2025', format='%B %Y', errors='coerce')
teste3 = pd.to_datetime('marco 2025', format='%B %Y', errors='coerce')

print(f"\nmarço (minúscula): {teste1}")
print(f"Março (maiúscula): {teste2}")
print(f"marco (sem acento): {teste3}")

# Testar o que o locale espera
meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho']
print("\n--- Testando todos os meses ---")
for mes in meses:
    resultado = pd.to_datetime(f'{mes} 2025', format='%B %Y', errors='coerce')
    print(f"{mes}: {resultado}")
