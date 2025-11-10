"""
Atualiza categoria "Roupa" para "Vestuário" no banco de dados
"""
import sqlite3
from pathlib import Path

db_path = Path(__file__).parent.parent.parent / 'dados' / 'db' / 'financeiro.db'

print("🔄 Atualizando categorias no banco de dados...")
print(f"📁 Banco: {db_path}")

with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    
    # Verifica quantos registros têm "Roupa"
    cursor.execute("SELECT COUNT(*) FROM categorias_aprendidas WHERE categoria = 'Roupa'")
    count_roupa = cursor.fetchone()[0]
    print(f"\n📊 Registros com 'Roupa': {count_roupa}")
    
    # Atualiza "Roupa" para "Vestuário"
    if count_roupa > 0:
        cursor.execute("""
            UPDATE categorias_aprendidas 
            SET categoria = 'Vestuário' 
            WHERE categoria = 'Roupa'
        """)
        conn.commit()
        print(f"✅ {count_roupa} registro(s) atualizado(s) de 'Roupa' para 'Vestuário'")
    
    # Mostra todas as categorias únicas
    cursor.execute("SELECT DISTINCT categoria FROM categorias_aprendidas ORDER BY categoria")
    categorias = [row[0] for row in cursor.fetchall()]
    
    print(f"\n📋 Categorias no banco ({len(categorias)}):")
    for cat in categorias:
        cursor.execute("SELECT COUNT(*) FROM categorias_aprendidas WHERE categoria = ?", (cat,))
        count = cursor.fetchone()[0]
        print(f"   • {cat}: {count} registro(s)")

print("\n✅ Atualização concluída!")
