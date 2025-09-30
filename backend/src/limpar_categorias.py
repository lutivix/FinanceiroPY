#!/usr/bin/env python3
"""
Script para limpar descrições que terminam com datas (dd/mm) no banco de dados.
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório src ao path
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

from database.category_repository import CategoryRepository
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Executa a limpeza de descrições."""
    try:
        # Caminho do banco de dados
        base_dir = Path(__file__).parent.parent.parent
        db_path = base_dir / "dados" / "db" / "financeiro.db"
        
        if not db_path.exists():
            logger.error(f"❌ Banco de dados não encontrado: {db_path}")
            sys.exit(1)
        
        # Inicializar repositório
        category_repo = CategoryRepository(db_path)
        
        logger.info("🧹 Iniciando limpeza de descrições com datas...")
        
        # Mostrar estatísticas antes
        stats_before = category_repo.get_stats()
        logger.info(f"📊 Antes da limpeza: {stats_before['total_categories']} categorias únicas")
        
        # Executar limpeza
        cleanup_stats = category_repo.clean_descriptions_with_dates()
        
        # Mostrar estatísticas depois
        stats_after = category_repo.get_stats()
        logger.info(f"📊 Após a limpeza: {stats_after['total_categories']} categorias únicas")
        
        # Resumo da limpeza
        logger.info("=" * 60)
        logger.info("📋 RESUMO DA LIMPEZA:")
        logger.info(f"   🔍 Descrições verificadas: {cleanup_stats['descriptions_checked']}")
        logger.info(f"   🧹 Descrições atualizadas: {cleanup_stats['descriptions_updated']}")
        logger.info(f"   🔗 Registros mesclados: {cleanup_stats['duplicates_merged']}")
        logger.info(f"   ⏭️ Descrições ignoradas: {cleanup_stats['descriptions_skipped']}")
        logger.info(f"   📝 Descrições com datas encontradas: {len(cleanup_stats['descriptions_with_dates'])}")
        
        if cleanup_stats['descriptions_with_dates']:
            logger.info("\n📝 Descrições limpas (primeiras 10):")
            for i, item in enumerate(cleanup_stats['descriptions_with_dates'][:10]):
                logger.info(f"   • '{item['original']}' → '{item['cleaned']}' ({item['records_updated']} registros)")
            
            if len(cleanup_stats['descriptions_with_dates']) > 10:
                logger.info(f"   ... e mais {len(cleanup_stats['descriptions_with_dates']) - 10} descrições")
        
        logger.info("=" * 60)
        logger.info("✅ Limpeza concluída com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro durante a limpeza: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()