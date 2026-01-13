"""
Person Mapper - Mapeamento Pessoa-Cartão
========================================

Mapeia transações para pessoas baseado na fonte (cartão usado).
"""

from typing import Dict, List
from models import TransactionSource, Transaction
from .models import PersonCardMapping, DEFAULT_PERSON_MAPPINGS
import logging

logger = logging.getLogger(__name__)


class PersonMapper:
    """
    Mapeia transações para pessoas baseado no cartão usado.
    
    Usa configuração padrão mas permite customização.
    """
    
    def __init__(self, custom_mappings: List[PersonCardMapping] = None):
        """
        Inicializa o mapeador.
        
        Args:
            custom_mappings: Mapeamentos customizados (opcional)
        """
        self.mappings = custom_mappings or DEFAULT_PERSON_MAPPINGS
        self._build_lookup_table()
        logger.info(f"PersonMapper inicializado com {len(self.mappings)} pessoas")
    
    def _build_lookup_table(self):
        """Constrói tabela de lookup para busca rápida."""
        self.source_to_person: Dict[TransactionSource, str] = {}
        
        for mapping in self.mappings:
            for source in mapping.sources:
                if source in self.source_to_person:
                    logger.warning(
                        f"Fonte {source.value} já mapeada para "
                        f"{self.source_to_person[source]}, sobrescrevendo com {mapping.person}"
                    )
                self.source_to_person[source] = mapping.person
    
    def get_person(self, source: TransactionSource) -> str:
        """
        Retorna a pessoa associada a uma fonte.
        
        Args:
            source: Fonte da transação
            
        Returns:
            Nome da pessoa ou "Desconhecido"
        """
        return self.source_to_person.get(source, "Desconhecido")
    
    def get_sources_for_person(self, person: str) -> List[TransactionSource]:
        """
        Retorna as fontes (cartões) de uma pessoa.
        
        Args:
            person: Nome da pessoa
            
        Returns:
            Lista de fontes da pessoa
        """
        for mapping in self.mappings:
            if mapping.person == person:
                return mapping.sources
        return []
    
    def get_all_people(self) -> List[str]:
        """Retorna lista de todas as pessoas."""
        return [m.person for m in self.mappings]
    
    def add_transaction_person(self, transaction: Transaction) -> Transaction:
        """
        Adiciona informação de pessoa a uma transação.
        
        Args:
            transaction: Transação a ser enriquecida
            
        Returns:
            Transação com campo 'person' no raw_data
        """
        person = self.get_person(transaction.source)
        if 'person' not in transaction.raw_data:
            transaction.raw_data['person'] = person
        return transaction
    
    def get_mapping_summary(self) -> Dict:
        """Retorna resumo dos mapeamentos."""
        summary = {}
        for mapping in self.mappings:
            summary[mapping.person] = {
                "sources": [s.value for s in mapping.sources],
                "description": mapping.description
            }
        return summary
