"""
Repositório para gerenciamento de categorias aprendidas
"""

import sqlite3
import logging
from typing import List, Dict, Optional
from pathlib import Path

from models import LearnedCategory, TransactionCategory

logger = logging.getLogger(__name__)


class CategoryRepository:
    """Repositório para gerenciar categorias aprendidas no banco de dados."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Garante que a tabela de categorias existe."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS categorias_aprendidas (
                        descricao TEXT PRIMARY KEY,
                        categoria TEXT NOT NULL,
                        confidence REAL DEFAULT 1.0,
                        learned_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        usage_count INTEGER DEFAULT 1
                    )
                """)
                conn.commit()
                logger.debug("✅ Tabela categorias_aprendidas verificada/criada")
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabela categorias_aprendidas: {e}")
            raise
    
    def save_category(self, learned_category: LearnedCategory) -> bool:
        """
        Salva uma categoria aprendida no banco.
        
        Args:
            learned_category: Categoria a ser salva
            
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO categorias_aprendidas 
                    (descricao, categoria, confidence, learned_at, usage_count)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    learned_category.description,
                    learned_category.category.value,
                    learned_category.confidence,
                    learned_category.learned_at.isoformat(),
                    learned_category.usage_count
                ))
                conn.commit()
                logger.debug(f"✅ Categoria salva: {learned_category.description} -> {learned_category.category.value}")
                return True
        except Exception as e:
            logger.error(f"❌ Erro ao salvar categoria: {e}")
            return False
    
    def get_category_mapping(self) -> Dict[str, TransactionCategory]:
        """
        Retorna mapeamento de descrições para categorias.
        
        Returns:
            Dicionário com descrições (maiúsculas) -> categorias
        """
        mapping = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT descricao, categoria FROM categorias_aprendidas
                """)
                
                for row in cursor.fetchall():
                    description, category = row
                    try:
                        mapping[description.upper().strip()] = TransactionCategory(category)
                    except ValueError:
                        logger.warning(f"⚠️ Categoria inválida no banco: {category}")
                
                logger.debug(f"📚 {len(mapping)} categorias carregadas do banco")
        except Exception as e:
            logger.error(f"❌ Erro ao carregar categorias: {e}")
        
        return mapping
    
    def find_category(self, description: str) -> Optional[TransactionCategory]:
        """
        Busca categoria para uma descrição específica.
        
        Args:
            description: Descrição a ser pesquisada
            
        Returns:
            Categoria encontrada ou None
        """
        normalized_desc = description.upper().strip()
        mapping = self.get_category_mapping()
        
        # Busca exata
        if normalized_desc in mapping:
            return mapping[normalized_desc]
        
        # Busca por substring (contém)
        for desc_key, category in mapping.items():
            if desc_key in normalized_desc or normalized_desc in desc_key:
                return category
        
        return None
    
    def get_all_categories(self) -> List[LearnedCategory]:
        """
        Retorna todas as categorias aprendidas.
        
        Returns:
            Lista de categorias aprendidas
        """
        categories = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT descricao, categoria, confidence, learned_at, usage_count
                    FROM categorias_aprendidas
                    ORDER BY usage_count DESC, learned_at DESC
                """)
                
                for row in cursor.fetchall():
                    description, category, confidence, learned_at, usage_count = row
                    try:
                        categories.append(LearnedCategory(
                            description=description,
                            category=TransactionCategory(category),
                            confidence=confidence,
                            learned_at=learned_at,
                            usage_count=usage_count
                        ))
                    except ValueError as e:
                        logger.warning(f"⚠️ Erro ao carregar categoria: {e}")
        except Exception as e:
            logger.error(f"❌ Erro ao buscar categorias: {e}")
        
        return categories
    
    def update_usage_count(self, description: str) -> bool:
        """
        Incrementa contador de uso de uma categoria.
        
        Args:
            description: Descrição da categoria
            
        Returns:
            True se atualizou com sucesso
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE categorias_aprendidas 
                    SET usage_count = usage_count + 1
                    WHERE descricao = ?
                """, (description.upper().strip(),))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar contador: {e}")
            return False
    
    def delete_category(self, description: str) -> bool:
        """
        Remove uma categoria aprendida.
        
        Args:
            description: Descrição da categoria a remover
            
        Returns:
            True se removeu com sucesso
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM categorias_aprendidas WHERE descricao = ?
                """, (description.upper().strip(),))
                conn.commit()
                removed = cursor.rowcount > 0
                if removed:
                    logger.info(f"🗑️ Categoria removida: {description}")
                return removed
        except Exception as e:
            logger.error(f"❌ Erro ao remover categoria: {e}")
            return False
    
    def get_stats(self) -> Dict[str, int]:
        """
        Retorna estatísticas das categorias.
        
        Returns:
            Dicionário com estatísticas
        """
        stats = {
            "total_categories": 0,
            "categories_by_type": {},
            "total_usage": 0
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total de categorias
                cursor.execute("SELECT COUNT(*) FROM categorias_aprendidas")
                stats["total_categories"] = cursor.fetchone()[0]
                
                # Por tipo de categoria
                cursor.execute("""
                    SELECT categoria, COUNT(*) 
                    FROM categorias_aprendidas 
                    GROUP BY categoria
                """)
                stats["categories_by_type"] = dict(cursor.fetchall())
                
                # Total de usos
                cursor.execute("SELECT SUM(usage_count) FROM categorias_aprendidas")
                result = cursor.fetchone()[0]
                stats["total_usage"] = result if result else 0
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar estatísticas: {e}")
        
        return stats
    
    def clean_descriptions_with_dates(self) -> Dict[str, int]:
        """
        Limpa descrições que terminam com formato de data (dd/mm) no banco de dados.
        Remove apenas os últimos 5 caracteres se terminarem com padrão dd/mm.
        
        Returns:
            Dicionário com estatísticas da limpeza
        """
        stats = {
            "descriptions_checked": 0,
            "descriptions_updated": 0,
            "descriptions_with_dates": [],
            "duplicates_merged": 0,
            "descriptions_skipped": 0
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Busca todas as descrições únicas que terminam com padrão dd/mm
                cursor.execute("""
                    SELECT DISTINCT descricao 
                    FROM categorias_aprendidas 
                    WHERE SUBSTRING(descricao, LENGTH(descricao) - 2, 1) = '/'
                    AND LENGTH(descricao) >= 5
                    ORDER BY descricao
                """)
                descriptions = cursor.fetchall()
                
                for (description,) in descriptions:
                    stats["descriptions_checked"] += 1
                    
                    # Verifica se termina com padrão dd/mm (últimos 5 caracteres)
                    if (len(description) >= 5 and 
                        description[-3] == '/' and 
                        description[-5:-3].isdigit() and 
                        description[-2:].isdigit()):
                        
                        # Remove os últimos 5 caracteres (dd/mm)
                        cleaned_description = description[:-5].strip()
                        
                        if cleaned_description:  # Só atualiza se não ficar vazio
                            # Verifica se a descrição limpa já existe
                            cursor.execute("""
                                SELECT descricao, categoria, usage_count 
                                FROM categorias_aprendidas 
                                WHERE descricao = ?
                            """, (cleaned_description,))
                            existing = cursor.fetchone()
                            
                            if existing:
                                # Se já existe, mescla os registros
                                # Busca os dados do registro original
                                cursor.execute("""
                                    SELECT categoria, usage_count 
                                    FROM categorias_aprendidas 
                                    WHERE descricao = ?
                                """, (description,))
                                original_data = cursor.fetchone()
                                
                                if original_data:
                                    original_category, original_usage = original_data
                                    existing_desc, existing_category, existing_usage = existing
                                    
                                    # Atualiza o usage_count do registro existente
                                    new_usage_count = existing_usage + original_usage
                                    cursor.execute("""
                                        UPDATE categorias_aprendidas 
                                        SET usage_count = ?
                                        WHERE descricao = ?
                                    """, (new_usage_count, cleaned_description))
                                    
                                    # Remove o registro original
                                    cursor.execute("""
                                        DELETE FROM categorias_aprendidas 
                                        WHERE descricao = ?
                                    """, (description,))
                                    
                                    stats["duplicates_merged"] += 1
                                    logger.info(f"🔗 Registros mesclados: '{description}' → '{cleaned_description}' (usage: {original_usage} + {existing_usage} = {new_usage_count})")
                            else:
                                # Se não existe, faz o UPDATE normal
                                cursor.execute("""
                                    UPDATE categorias_aprendidas 
                                    SET descricao = ? 
                                    WHERE descricao = ?
                                """, (cleaned_description, description))
                                
                                if cursor.rowcount > 0:
                                    stats["descriptions_updated"] += cursor.rowcount
                                    stats["descriptions_with_dates"].append({
                                        "original": description,
                                        "cleaned": cleaned_description,
                                        "records_updated": cursor.rowcount
                                    })
                                    logger.info(f"🧹 Descrição limpa: '{description}' → '{cleaned_description}' ({cursor.rowcount} registros)")
                        else:
                            stats["descriptions_skipped"] += 1
                            logger.warning(f"⚠️ Descrição ignorada (ficaria vazia): '{description}'")
                
                total_changes = stats["descriptions_updated"] + stats["duplicates_merged"]
                logger.info(f"🧹 Limpeza concluída: {stats['descriptions_checked']} verificadas, {total_changes} alterações feitas")
                
        except Exception as e:
            logger.error(f"❌ Erro ao limpar descrições: {e}")
        
        return stats