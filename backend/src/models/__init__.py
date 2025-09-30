"""
Modelos de dados para o Agente Financeiro IA
Classes que representam as entidades do sistema
"""

from dataclasses import dataclass, field
from datetime import date as Date, datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid


class TransactionSource(Enum):
    """Enum para fontes de transações."""
    PIX = "PIX"
    ITAU_MASTER_FISICO = "Master Físico"
    ITAU_MASTER_VIRTUAL = "Master Virtual"
    ITAU_MASTER_RECORRENTE = "Master Recorrente"
    LATAM_VISA_FISICO = "Visa Físico"
    LATAM_VISA_VIRTUAL = "Visa Virtual"
    LATAM_VISA_RECORRENTE = "Visa Recorrente"
    LATAM_VISA_BIA = "Visa Bia"
    LATAM_VISA_MAE = "Visa Mãe"


class TransactionCategory(Enum):
    """Enum para categorias de transações."""
    # Categorias originais do sistema
    SALARIO = "SALÁRIO"
    INVESTIMENTOS = "INVESTIMENTOS"
    A_DEFINIR = "A definir"
    
    # Categorias existentes no banco de dados
    BETINA = "Betina"
    CARRO = "Carro"
    CARTAO = "Cartão"
    CASA = "Casa"
    COMBUSTIVEL = "Combustível"
    COMPRAS = "Compras"
    DATAS = "Datas"
    ESPORTE = "Esporte"
    ESTETICA = "Estética"
    EVENTOS = "Eventos"
    FACULDADE = "Faculdade"
    FARMACIA = "Farmácia"
    FEIRA = "Feira"
    HOBBY = "Hobby"
    LF = "LF"
    LANCHE = "Lanche"
    LAZER = "Lazer"
    MERCADO = "Mercado"
    NITA = "Nita"
    PADARIA = "Padaria"
    PET = "Pet"
    ROUPA = "Roupa"
    SAUDE = "Saúde"
    SEGURO = "Seguro"
    STREAM = "Stream"
    TRANSPORTE = "Transporte"
    UTILIDADES = "Utilidades"
    VIAGEM = "Viagem"


@dataclass
class Transaction:
    """Modelo para uma transação financeira."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    date: Date = field(default_factory=Date.today)
    description: str = ""
    amount: float = 0.0
    source: TransactionSource = TransactionSource.PIX
    category: TransactionCategory = TransactionCategory.A_DEFINIR
    month_ref: str = ""
    raw_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validações após inicialização."""
        if not self.description.strip():
            raise ValueError("Descrição não pode estar vazia")
        
        # Normaliza descrição
        self.description = self.description.strip()
        
        # Gera mês de referência se não fornecido
        if not self.month_ref:
            meses_pt = {
                1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
                5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
                9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
            }
            self.month_ref = f"{meses_pt[self.date.month]} {self.date.year}"
    
    @property
    def is_income(self) -> bool:
        """Retorna True se é receita (valor positivo)."""
        return self.amount > 0
    
    @property
    def is_expense(self) -> bool:
        """Retorna True se é despesa (valor negativo)."""
        return self.amount < 0
    
    @property
    def amount_abs(self) -> float:
        """Retorna o valor absoluto da transação."""
        return abs(self.amount)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "description": self.description,
            "amount": self.amount,
            "source": self.source.value,
            "category": self.category.value,
            "month_ref": self.month_ref,
            "raw_data": self.raw_data,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Cria instância a partir de dicionário."""
        # Converte strings de volta para objetos
        data['date'] = datetime.fromisoformat(data['date']).date()
        data['source'] = TransactionSource(data['source'])
        data['category'] = TransactionCategory(data['category'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data['updated_at']:
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)


@dataclass
class LearnedCategory:
    """Modelo para categorias aprendidas pelo sistema."""
    description: str
    category: TransactionCategory
    confidence: float = 1.0
    learned_at: datetime = field(default_factory=datetime.now)
    usage_count: int = 1
    
    def __post_init__(self):
        """Validações após inicialização."""
        self.description = self.description.upper().strip()
        if not self.description:
            raise ValueError("Descrição não pode estar vazia")
        
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confiança deve estar entre 0 e 1")
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "description": self.description,
            "category": self.category.value,
            "confidence": self.confidence,
            "learned_at": self.learned_at.isoformat(),
            "usage_count": self.usage_count
        }


@dataclass
class ProcessingStats:
    """Estatísticas de processamento de arquivos."""
    files_processed: int = 0
    transactions_extracted: int = 0
    transactions_categorized: int = 0
    new_categories_learned: int = 0
    processing_time_seconds: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_error(self, error: str):
        """Adiciona um erro às estatísticas."""
        self.errors.append(error)
    
    def add_warning(self, warning: str):
        """Adiciona um aviso às estatísticas."""
        self.warnings.append(warning)
    
    @property
    def has_errors(self) -> bool:
        """Retorna True se houver erros."""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Retorna True se houver avisos."""
        return len(self.warnings) > 0
    
    def summary(self) -> str:
        """Retorna um resumo das estatísticas."""
        return (
            f"📊 Processamento concluído:\n"
            f"   📁 Arquivos: {self.files_processed}\n"
            f"   💰 Transações extraídas: {self.transactions_extracted}\n"
            f"   🏷️  Transações categorizadas: {self.transactions_categorized}\n"
            f"   🧠 Novas categorias aprendidas: {self.new_categories_learned}\n"
            f"   ⏱️  Tempo: {self.processing_time_seconds:.2f}s\n"
            f"   ❌ Erros: {len(self.errors)}\n"
            f"   ⚠️  Avisos: {len(self.warnings)}"
        )


@dataclass
class CardMapping:
    """Mapeamento de finais de cartão para tipos."""
    final: str
    description: str
    source: TransactionSource
    
    def __post_init__(self):
        """Validações após inicialização."""
        if len(self.final) != 4:
            raise ValueError("Final do cartão deve ter 4 dígitos")
        
        if not self.final.isdigit():
            raise ValueError("Final do cartão deve conter apenas números")


# Mapeamentos de cartões pré-definidos
ITAU_CARD_MAPPINGS = [
    CardMapping("4059", "Master Físico", TransactionSource.ITAU_MASTER_FISICO),
    CardMapping("2800", "Master Recorrente", TransactionSource.ITAU_MASTER_RECORRENTE),
    CardMapping("2001", "Master Recorrente", TransactionSource.ITAU_MASTER_RECORRENTE),
]

LATAM_CARD_MAPPINGS = [
    CardMapping("1152", "Visa Recorrente", TransactionSource.LATAM_VISA_RECORRENTE),
    CardMapping("6259", "Visa Físico", TransactionSource.LATAM_VISA_FISICO),
    CardMapping("3666", "Visa Bia", TransactionSource.LATAM_VISA_BIA),
    CardMapping("8106", "Visa Mae", TransactionSource.LATAM_VISA_MAE),
]


def get_card_source(final_cartao: str, bank: str) -> TransactionSource:
    """
    Retorna a fonte da transação baseado no final do cartão e banco.
    
    Args:
        final_cartao: Final do cartão (4 dígitos)
        bank: Banco (Itau ou Latam)
        
    Returns:
        TransactionSource correspondente
    """
    if not final_cartao or len(final_cartao) != 4:
        # Retorna virtual como padrão
        return (TransactionSource.ITAU_MASTER_VIRTUAL 
                if bank.lower() == "itau" 
                else TransactionSource.LATAM_VISA_VIRTUAL)
    
    mappings = ITAU_CARD_MAPPINGS if bank.lower() == "itau" else LATAM_CARD_MAPPINGS
    
    for mapping in mappings:
        if mapping.final == final_cartao:
            return mapping.source
    
    # Retorna virtual como padrão se não encontrar
    return (TransactionSource.ITAU_MASTER_VIRTUAL 
            if bank.lower() == "itau" 
            else TransactionSource.LATAM_VISA_VIRTUAL)