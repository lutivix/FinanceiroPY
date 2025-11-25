"""
Script para corrigir mapeamento de fontes de cartões no banco de dados.

Problema identificado:
- Cartões PERSON (Master) estavam sendo classificados como Visa Virtual
- Origem: sync_openfinance_anual.py não diferenciava LATAM vs PERSON

Correções:
- origem_banco = LATAM → Cartões Visa
- origem_banco = PERSON → Cartões Master
- origem_banco = itau → PIX
"""

import sqlite3
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / 'dados' / 'db' / 'financeiro.db'

# Mapeamentos de cartões Master (PERSON)
MASTER_MAPPINGS = {
    '4059': 'Master Físico',
    '2800': 'Master Recorrente',
    '2001': 'Master Recorrente'
}

# Mapeamentos de cartões Visa (LATAM) - já corretos, mas garantir
VISA_MAPPINGS = {
    '6259': 'Visa Físico',
    '3666': 'Visa Bia',
    '8106': 'Visa Mae',
    '1152': 'Visa Recorrente'
}

def corrigir_fontes():
    """Corrige fontes de cartões baseado em origem_banco e cartao_final."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("🔧 CORREÇÃO DE FONTES DE CARTÕES")
    print("="*70)
    
    # 1. Corrigir cartões Master (PERSON) - finais mapeados
    print("\n📋 Corrigindo cartões Master mapeados (origem_banco = PERSON)...")
    for final, fonte_correta in MASTER_MAPPINGS.items():
        cursor.execute("""
            UPDATE transacoes_openfinance 
            SET fonte = ?
            WHERE origem_banco = 'PERSON' 
              AND cartao_final = ?
              AND fonte != ?
        """, (fonte_correta, final, fonte_correta))
        
        if cursor.rowcount > 0:
            print(f"  ✅ Cartão final {final}: {cursor.rowcount} transações → {fonte_correta}")
    
    # 2. Corrigir cartões Master Virtual (PERSON) - finais NÃO mapeados
    print("\n📋 Corrigindo cartões Master Virtual (origem_banco = PERSON, não mapeados)...")
    finais_mapeados = "', '".join(MASTER_MAPPINGS.keys())
    cursor.execute(f"""
        UPDATE transacoes_openfinance 
        SET fonte = 'Master Virtual'
        WHERE origem_banco = 'PERSON' 
          AND cartao_final NOT IN ('{finais_mapeados}')
          AND fonte != 'Master Virtual'
    """)
    if cursor.rowcount > 0:
        print(f"  ✅ {cursor.rowcount} transações → Master Virtual")
    
    # 3. Garantir cartões Visa (LATAM) - finais mapeados
    print("\n📋 Validando cartões Visa mapeados (origem_banco = LATAM)...")
    for final, fonte_correta in VISA_MAPPINGS.items():
        cursor.execute("""
            UPDATE transacoes_openfinance 
            SET fonte = ?
            WHERE origem_banco = 'LATAM' 
              AND cartao_final = ?
              AND fonte != ?
        """, (fonte_correta, final, fonte_correta))
        
        if cursor.rowcount > 0:
            print(f"  ✅ Cartão final {final}: {cursor.rowcount} transações → {fonte_correta}")
    
    # 4. Garantir cartões Visa Virtual (LATAM) - finais NÃO mapeados
    print("\n📋 Validando cartões Visa Virtual (origem_banco = LATAM, não mapeados)...")
    finais_visa_mapeados = "', '".join(VISA_MAPPINGS.keys())
    cursor.execute(f"""
        UPDATE transacoes_openfinance 
        SET fonte = 'Visa Virtual'
        WHERE origem_banco = 'LATAM' 
          AND cartao_final NOT IN ('{finais_visa_mapeados}')
          AND cartao_final IS NOT NULL
          AND fonte != 'Visa Virtual'
    """)
    if cursor.rowcount > 0:
        print(f"  ✅ {cursor.rowcount} transações → Visa Virtual")
    
    # 5. PIX já deve estar correto (origem_banco = itau, sem cartao_final)
    print("\n📋 Validando PIX...")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM transacoes_openfinance 
        WHERE origem_banco = 'itau' 
          AND cartao_final IS NULL 
          AND fonte = 'PIX'
    """)
    pix_count = cursor.fetchone()[0]
    print(f"  ✅ PIX: {pix_count} transações corretas")
    
    # 4. Relatório final
    print("\n" + "="*70)
    print("📊 RELATÓRIO FINAL - Distribuição por Fonte")
    print("="*70)
    
    cursor.execute("""
        SELECT fonte, COUNT(*) as qtd, SUM(ABS(valor)) as total
        FROM transacoes_openfinance
        WHERE tipo_transacao = 'DEBIT'
        GROUP BY fonte
        ORDER BY qtd DESC
    """)
    
    for fonte, qtd, total in cursor.fetchall():
        print(f"  {fonte:20s}: {qtd:4d} transações | R$ {total:12,.2f}")
    
    # 5. Cartões não mapeados (Virtual)
    print("\n" + "="*70)
    print("📋 Cartões Virtuais (não mapeados)")
    print("="*70)
    
    cursor.execute("""
        SELECT DISTINCT origem_banco, cartao_final, COUNT(*) as qtd
        FROM transacoes_openfinance
        WHERE fonte IN ('Visa Virtual', 'Master Virtual')
          AND cartao_final IS NOT NULL
        GROUP BY origem_banco, cartao_final
        ORDER BY qtd DESC
        LIMIT 10
    """)
    
    print(f"  {'Banco':<10} {'Final':<8} {'Qtd':<6}")
    print("  " + "-"*30)
    for banco, final, qtd in cursor.fetchall():
        print(f"  {banco:<10} {final:<8} {qtd:<6}")
    
    # Commit
    conn.commit()
    conn.close()
    
    print("\n" + "="*70)
    print("✅ CORREÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*70 + "\n")


if __name__ == '__main__':
    corrigir_fontes()
