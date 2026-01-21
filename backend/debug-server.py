"""
Script de debug para identificar problemas no servidor
Execute ANTES de rodar o dashboard em produção
"""

import sys
from pathlib import Path

print("\n" + "=" * 60)
print("🔍 DEBUG - Dashboard Financeiro v2")
print("=" * 60 + "\n")

# 1. Python Version
print(f"🐍 Python: {sys.version}")
print(f"   Executable: {sys.executable}\n")

# 2. Pasta atual
print(f"📁 Current Dir: {Path.cwd()}")
print(f"   Script Dir: {Path(__file__).resolve().parent}\n")

# 3. Estrutura de pastas esperada
script_dir = Path(__file__).resolve().parent
expected_db = script_dir.parent / 'dados' / 'db' / 'financeiro.db'
print(f"💾 DB Esperado: {expected_db}")
print(f"   Existe? {'✅ SIM' if expected_db.exists() else '❌ NÃO'}\n")

# 4. Testar imports
print("📦 Testando imports:")
try:
    import pandas as pd
    print(f"   ✅ pandas {pd.__version__}")
except ImportError as e:
    print(f"   ❌ pandas: {e}")

try:
    import dash
    print(f"   ✅ dash {dash.__version__}")
except ImportError as e:
    print(f"   ❌ dash: {e}")

try:
    import dash_bootstrap_components as dbc
    print(f"   ✅ dash-bootstrap-components {dbc.__version__}")
except ImportError as e:
    print(f"   ❌ dash-bootstrap-components: {e}")

try:
    import plotly
    print(f"   ✅ plotly {plotly.__version__}")
except ImportError as e:
    print(f"   ❌ plotly: {e}")

print()

# 5. Testar conexão com banco
if expected_db.exists():
    print("🔗 Testando conexão com banco:")
    try:
        import sqlite3
        conn = sqlite3.connect(expected_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM lancamentos")
        count = cursor.fetchone()[0]
        print(f"   ✅ Conexão OK - {count} lançamentos encontrados")
        
        # Testar query de meses
        cursor.execute("SELECT DISTINCT MesComp FROM lancamentos ORDER BY MesComp DESC LIMIT 5")
        meses = cursor.fetchall()
        print(f"   ✅ Últimos meses: {[m[0] for m in meses]}")
        
        conn.close()
    except Exception as e:
        print(f"   ❌ Erro: {e}")
else:
    print(f"❌ Banco não encontrado: {expected_db}")
    print("\n🔧 SOLUÇÃO:")
    print(f"   1. Verifique se o banco existe em: {expected_db}")
    print(f"   2. Ou configure variável de ambiente:")
    print(f"      export DB_PATH='/caminho/completo/para/financeiro.db'")

print()

# 6. Testar imports do dashboard
print("🎨 Testando imports do dashboard:")
sys.path.insert(0, str(script_dir / 'src'))

try:
    from dashboard_v2.config import COLORS
    print(f"   ✅ dashboard_v2.config")
except Exception as e:
    print(f"   ❌ dashboard_v2.config: {e}")

try:
    from dashboard_v2.utils.database import carregar_transacoes, obter_meses_disponiveis
    print(f"   ✅ dashboard_v2.utils.database")
    
    # Testar carregamento real
    meses = obter_meses_disponiveis()
    print(f"   ✅ Meses disponíveis: {len(meses)}")
    
except Exception as e:
    print(f"   ❌ dashboard_v2.utils.database: {e}")

try:
    from dashboard_v2.components.sidebar import create_sidebar
    print(f"   ✅ dashboard_v2.components.sidebar")
except Exception as e:
    print(f"   ❌ dashboard_v2.components.sidebar: {e}")

try:
    from dashboard_v2.pages.dashboard import create_dashboard_page
    print(f"   ✅ dashboard_v2.pages.dashboard")
except Exception as e:
    print(f"   ❌ dashboard_v2.pages.dashboard: {e}")

print("\n" + "=" * 60)
print("✅ Debug concluído!")
print("=" * 60 + "\n")

print("📝 Se todos os testes passaram, execute:")
print(f"   cd {script_dir / 'src' / 'dashboard_v2'}")
print("   python main.py")
print()
