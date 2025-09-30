"""
Serviço de categorização automática de transações
"""

import logging
from typing import List, Dict, Optional
from pathlib import Path

from models import Transaction, TransactionCategory, LearnedCategory
from database import CategoryRepository

logger = logging.getLogger(__name__)


class CategorizationService:
    """Serviço responsável pela categorização automática de transações."""
    
    def __init__(self, category_repository: CategoryRepository):
        self.category_repo = category_repository
        self._category_cache = None
        self._load_categories()
    
    def _load_categories(self):
        """Carrega categorias do banco para cache."""
        self._category_cache = self.category_repo.get_category_mapping()
        logger.info(f"📚 {len(self._category_cache)} categorias carregadas para cache")
    
    def categorize_transaction(self, transaction: Transaction) -> TransactionCategory:
        """
        Categoriza uma transação específica usando lógica original.
        
        Args:
            transaction: Transação a ser categorizada
            
        Returns:
            Categoria determinada para a transação
        """
        # Limpa descrição removendo data PIX se presente
        desc = self._clean_pix_description(transaction.description)
        
        # Aplica regras básicas originais
        category = self._categorize_by_original_rules(desc)
        if category != TransactionCategory.A_DEFINIR:
            return category
        
        # Busca no aprendizado (banco)
        learned_category = self._categorize_by_learning(desc)
        if learned_category:
            # Atualiza contador de uso
            self.category_repo.update_usage_count(desc.upper().strip())
            return learned_category
        
        # Se não encontrou, retorna categoria padrão
        return TransactionCategory.A_DEFINIR
    
    def _clean_pix_description(self, description: str) -> str:
        """
        Remove últimos 5 dígitos de data das descrições PIX (XX/YY).
        
        Args:
            description: Descrição original
            
        Returns:
            Descrição limpa
        """
        desc = description.upper().strip()
        
        # Se contém PIX e tem pelo menos 5 caracteres
        if "PIX" in desc and len(desc) >= 5:
            possivel_data = desc[-5:]
            # Se os últimos 5 caracteres são data (XX/YY)
            if "/" in possivel_data and possivel_data.replace("/", "").isdigit():
                desc = desc[:-5].strip()
        
        return desc
    
    def _categorize_by_original_rules(self, description: str) -> TransactionCategory:
        """
        Categorização baseada nas 4 regras originais apenas.
        
        Args:
            description: Descrição da transação (já limpa)
            
        Returns:
            Categoria baseada em regras originais ou A_DEFINIR
        """
        desc_upper = description.upper().strip()
        
        # Mapeamento original das 4 regras
        contains_map = {
            "SISPAG PIX": TransactionCategory.SALARIO,
            "REND PAGO APLIC": TransactionCategory.INVESTIMENTOS,
            "PAGTO REMUNERACAO": TransactionCategory.SALARIO,
            "PAGTO SALARIO": TransactionCategory.SALARIO
        }
        
        # Verifica se alguma regra se aplica
        for trecho, categoria in contains_map.items():
            if trecho in desc_upper:
                return categoria
        
        return TransactionCategory.A_DEFINIR
    
    def categorize_transactions(self, transactions: List[Transaction]) -> List[Transaction]:
        """
        Categoriza uma lista de transações.
        
        Args:
            transactions: Lista de transações
            
        Returns:
            Lista de transações com categorias atualizadas
        """
        categorized_count = 0
        
        for transaction in transactions:
            original_category = transaction.category
            new_category = self.categorize_transaction(transaction)
            
            if new_category != TransactionCategory.A_DEFINIR:
                transaction.category = new_category
                
                if original_category == TransactionCategory.A_DEFINIR:
                    categorized_count += 1
        
        logger.info(f"🏷️ {categorized_count}/{len(transactions)} transações categorizadas automaticamente")
        return transactions
    
    def _categorize_by_learning(self, description: str) -> Optional[TransactionCategory]:
        """
        Categorização baseada em aprendizado de máquina.
        
        Args:
            description: Descrição da transação
            
        Returns:
            Categoria aprendida ou None
        """
        if not self._category_cache:
            return None
        
        desc_normalized = description.upper().strip()
        
        # Busca exata
        if desc_normalized in self._category_cache:
            return self._category_cache[desc_normalized]
        
        # Busca por substring (mais flexível)
        for learned_desc, category in self._category_cache.items():
            # Verifica se a descrição aprendida está contida na atual
            if learned_desc in desc_normalized:
                return category
            
            # Verifica se a descrição atual está contida na aprendida
            if desc_normalized in learned_desc:
                return category
        
        return None
    
    def learn_category(self, description: str, category: TransactionCategory, 
                      confidence: float = 1.0) -> bool:
        """
        Aprende uma nova associação descrição -> categoria.
        
        Args:
            description: Descrição da transação
            category: Categoria correta
            confidence: Nível de confiança (0-1)
            
        Returns:
            True se aprendeu com sucesso
        """
        if category == TransactionCategory.A_DEFINIR:
            logger.warning("⚠️ Tentativa de aprender categoria 'A definir' ignorada")
            return False
        
        learned_category = LearnedCategory(
            description=description,
            category=category,
            confidence=confidence
        )
        
        success = self.category_repo.save_category(learned_category)
        
        if success:
            # Atualiza cache
            if self._category_cache is None:
                self._category_cache = {}
            self._category_cache[description.upper().strip()] = category
            logger.info(f"🧠 Nova categoria aprendida: {description} -> {category.value}")
        
        return success
    
    def learn_from_transactions(self, transactions: List[Transaction]) -> int:
        """
        Aprende categorias a partir de transações já categorizadas.
        
        Args:
            transactions: Lista de transações categorizadas
            
        Returns:
            Número de categorias aprendidas
        """
        learned_count = 0
        
        for transaction in transactions:
            if transaction.category != TransactionCategory.A_DEFINIR:
                if self.learn_category(transaction.description, transaction.category):
                    learned_count += 1
        
        logger.info(f"🧠 {learned_count} novas categorias aprendidas")
        return learned_count
    
    def get_categorization_suggestions(self, description: str, limit: int = 5) -> List[Dict]:
        """
        Retorna sugestões de categorização para uma descrição.
        
        Args:
            description: Descrição da transação
            limit: Número máximo de sugestões
            
        Returns:
            Lista de sugestões com categoria e confiança
        """
        suggestions = []
        desc_normalized = description.upper().strip()
        
        # Primeiro tenta regras
        rule_category = self._categorize_by_original_rules(description)
        if rule_category != TransactionCategory.A_DEFINIR:
            suggestions.append({
                "category": rule_category,
                "confidence": 0.9,
                "reason": "Regra automática"
            })
        
        # Depois busca similares no aprendizado
        if self._category_cache:
            for learned_desc, category in self._category_cache.items():
                # Calcula similaridade simples
                similarity = self._calculate_similarity(desc_normalized, learned_desc)
                
                if similarity > 0.3:  # Threshold mínimo
                    suggestions.append({
                        "category": category,
                        "confidence": similarity,
                        "reason": f"Similar a: {learned_desc}"
                    })
        
        # Ordena por confiança e limita
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        return suggestions[:limit]
    
    def _calculate_similarity(self, desc1: str, desc2: str) -> float:
        """
        Calcula similaridade simples entre duas descrições.
        
        Args:
            desc1: Primeira descrição
            desc2: Segunda descrição
            
        Returns:
            Valor de similaridade (0-1)
        """
        # Implementação simples baseada em palavras comuns
        words1 = set(desc1.split())
        words2 = set(desc2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def refresh_cache(self):
        """Recarrega cache de categorias do banco."""
        self._load_categories()
    
    def get_stats(self) -> Dict:
        """
        Retorna estatísticas do serviço de categorização.
        
        Returns:
            Dicionário com estatísticas
        """
        repo_stats = self.category_repo.get_stats()
        
        return {
            "cached_categories": len(self._category_cache) if self._category_cache else 0,
            "database_stats": repo_stats
        }