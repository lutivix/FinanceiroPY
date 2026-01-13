"""
Helper para normalização e deduplicação de transações
======================================================

Fornece funções para normalizar descrições de transações,
removendo partes variáveis (datas, parcelas) para permitir
deduplicação efetiva.

Uso:
    from utils import DeduplicationHelper
    
    helper = DeduplicationHelper()
    desc_norm = helper.normalize_description_for_dedup("PIX ENVIADO 15/11")
    # Resultado: "PIX ENVIADO"
    
    key = helper.generate_dedup_key("2025-11-15", "PIX ENVIADO 15/11", -50.00, "ITAU")
    # Resultado: "2025-11-15|PIX ENVIADO|-50.00|ITAU"

Autor: Sistema
Data: 2026-01-13
Versão: 1.0
"""

import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class DeduplicationHelper:
    """
    Helper para normalização e deduplicação de transações.
    
    Fornece métodos para:
    - Normalizar descrições removendo datas e parcelas
    - Gerar chaves compostas para deduplicação
    - Converter formatos de data
    
    A normalização é essencial porque descrições podem variar ligeiramente
    mas representar a mesma transação:
    - "PIX ENVIADO MERCADO 15/11" vs "PIX ENVIADO MERCADO"
    - "COMPRA AMAZON 1/3" vs "COMPRA AMAZON 2/3"
    """
    
    @staticmethod
    def normalize_description_for_dedup(description: str) -> str:
        """
        Normaliza descrição removendo partes variáveis para deduplicação.
        
        Remove:
        - Datas no formato dd/mm (ex: "PIX RECEBIDO 25/12" -> "PIX RECEBIDO")
        - Parcelas no formato x/y (ex: "COMPRA 2/5" -> "COMPRA")
        - Espaços múltiplos e pontuação extra
        
        IMPORTANTE: Esta função NÃO deve ser usada para exibição ao usuário,
        apenas para comparação de duplicatas. A descrição original deve ser
        mantida no banco de dados.
        
        Args:
            description: Descrição original da transação
            
        Returns:
            Descrição normalizada para uso em chave de deduplicação
            
        Examples:
            >>> helper = DeduplicationHelper()
            >>> helper.normalize_description_for_dedup("PIX ENVIADO 15/11")
            'PIX ENVIADO'
            >>> helper.normalize_description_for_dedup("MERCADO LIVRE 2/12")
            'MERCADO LIVRE'
            >>> helper.normalize_description_for_dedup("SPOTIFY PREMIUM")
            'SPOTIFY PREMIUM'
        """
        if not description:
            return ""
        
        # Converte para uppercase e remove espaços extras
        desc = description.strip().upper()
        
        # Remove datas/números no final (vários formatos)
        # Formato 1: "PIX TRANSF Kamilla21/05" -> "PIX TRANSF KAMILLA"
        # Regex: \d{2}/\d{2}$ (2 dígitos + / + 2 dígitos no final, COM ou SEM espaço)
        desc = re.sub(r'\d{2}/\d{2}$', '', desc)
        
        # Formato 2: Parcelas "COMPRA 2/12" ou "COMPRA2/12"
        # Regex: \d{1,2}/\d{1,2}$ (1-2 dígitos + / + 1-2 dígitos no final)
        desc = re.sub(r'\d{1,2}/\d{1,2}$', '', desc)
        
        # Formato 3: Números grudados no final "TRANSF KENIA E28" -> "TRANSF KENIA E"
        # Regex: [A-Z]\d{1,2}$ (letra + 1-2 dígitos no final)
        desc = re.sub(r'([A-Z])\d{1,2}$', r'\1', desc)
        
        # Remove múltiplos espaços
        desc = re.sub(r'\s+', ' ', desc).strip()
        
        return desc
    
    @staticmethod
    def generate_dedup_key(data: str, descricao: str, valor: float, fonte: str) -> str:
        """
        Gera chave composta para deduplicação de transações.
        
        A chave é formada por: Data|Descrição_Normalizada|Valor|Fonte
        
        Esta chave permite identificar duplicatas mesmo quando:
        - A descrição tem datas ou parcelas variáveis
        - O formato da data é diferente (dd/mm/yyyy vs YYYY-MM-DD)
        - Há diferenças de casing ou espaços extras
        
        Args:
            data: Data da transação (aceita dd/mm/yyyy ou YYYY-MM-DD)
            descricao: Descrição da transação
            valor: Valor da transação (pode ser float ou string)
            fonte: Fonte da transação (ITAU, LATAM, etc)
            
        Returns:
            Chave composta no formato "YYYY-MM-DD|DESC_NORM|VALOR|FONTE"
            
        Examples:
            >>> helper = DeduplicationHelper()
            >>> helper.generate_dedup_key("15/11/2025", "PIX ENVIADO 15/11", -50.00, "ITAU")
            '2025-11-15|PIX ENVIADO|-50.00|ITAU'
            >>> helper.generate_dedup_key("2025-11-15", "PIX ENVIADO", -50.00, "itau")
            '2025-11-15|PIX ENVIADO|-50.00|ITAU'
        """
        # Normaliza data para YYYY-MM-DD
        if '/' in data:
            # Converte dd/mm/yyyy para YYYY-MM-DD
            parts = data.split('/')
            if len(parts) == 3:
                data_norm = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
            else:
                data_norm = data
        else:
            data_norm = data
        
        # Normaliza descrição
        desc_norm = DeduplicationHelper.normalize_description_for_dedup(descricao)
        
        # Normaliza valor (2 casas decimais)
        valor_norm = f"{float(valor):.2f}"
        
        # Fonte em uppercase
        fonte_norm = fonte.upper().strip()
        
        return f"{data_norm}|{desc_norm}|{valor_norm}|{fonte_norm}"
    
    @staticmethod
    def convert_date_to_iso(date_str: str) -> str:
        """
        Converte data de dd/mm/yyyy para YYYY-MM-DD.
        
        Se a data já estiver no formato ISO (YYYY-MM-DD), retorna sem modificar.
        
        Args:
            date_str: Data no formato dd/mm/yyyy ou YYYY-MM-DD
            
        Returns:
            Data no formato YYYY-MM-DD
            
        Examples:
            >>> helper = DeduplicationHelper()
            >>> helper.convert_date_to_iso("15/11/2025")
            '2025-11-15'
            >>> helper.convert_date_to_iso("2025-11-15")
            '2025-11-15'
        """
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) == 3:
                return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
        return date_str
    
    @staticmethod
    def parse_dedup_key(dedup_key: str) -> Tuple[str, str, float, str]:
        """
        Extrai componentes de uma chave de deduplicação.
        
        Args:
            dedup_key: Chave no formato "YYYY-MM-DD|DESC|VALOR|FONTE"
            
        Returns:
            Tupla (data, descricao, valor, fonte)
            
        Raises:
            ValueError: Se a chave não estiver no formato esperado
            
        Examples:
            >>> helper = DeduplicationHelper()
            >>> helper.parse_dedup_key("2025-11-15|PIX ENVIADO|-50.00|ITAU")
            ('2025-11-15', 'PIX ENVIADO', -50.0, 'ITAU')
        """
        parts = dedup_key.split('|')
        if len(parts) != 4:
            raise ValueError(f"Chave inválida: {dedup_key}. Esperado 4 partes separadas por '|'")
        
        data, descricao, valor_str, fonte = parts
        
        try:
            valor = float(valor_str)
        except ValueError:
            raise ValueError(f"Valor inválido na chave: {valor_str}")
        
        return data, descricao, valor, fonte
    
    @staticmethod
    def is_likely_duplicate(desc1: str, desc2: str, tolerance: float = 0.9) -> bool:
        """
        Verifica se duas descrições são provavelmente duplicatas usando similaridade.
        
        Esta é uma verificação adicional menos rigorosa que pode ser útil
        para detectar duplicatas com pequenas variações além de datas/parcelas.
        
        Args:
            desc1: Primeira descrição
            desc2: Segunda descrição
            tolerance: Nível de similaridade (0.0 a 1.0, padrão 0.9)
            
        Returns:
            True se as descrições normalizadas são idênticas
            
        Note:
            Por enquanto usa apenas comparação exata após normalização.
            Pode ser expandida para usar algoritmos de similaridade (Levenshtein, etc.)
        """
        norm1 = DeduplicationHelper.normalize_description_for_dedup(desc1)
        norm2 = DeduplicationHelper.normalize_description_for_dedup(desc2)
        
        return norm1 == norm2


# Funções de conveniência para uso direto
def normalize_description(description: str) -> str:
    """Atalho para DeduplicationHelper.normalize_description_for_dedup"""
    return DeduplicationHelper.normalize_description_for_dedup(description)


def generate_dedup_key(data: str, descricao: str, valor: float, fonte: str) -> str:
    """Atalho para DeduplicationHelper.generate_dedup_key"""
    return DeduplicationHelper.generate_dedup_key(data, descricao, valor, fonte)


# Testes unitários internos
if __name__ == "__main__":
    print("=" * 60)
    print("TESTES DO DEDUPLICATION HELPER")
    print("=" * 60)
    
    helper = DeduplicationHelper()
    
    # Teste 1: Normalização de descrição com data
    print("\n1. Teste: Descrição com data")
    desc1 = "PIX ENVIADO MERCADO 15/11"
    norm1 = helper.normalize_description_for_dedup(desc1)
    print(f"   Original: '{desc1}'")
    print(f"   Normalizada: '{norm1}'")
    assert norm1 == "PIX ENVIADO MERCADO", "Falha: data não removida"
    print("   ✅ OK")
    
    # Teste 2: Normalização de descrição com parcela
    print("\n2. Teste: Descrição com parcela")
    desc2 = "COMPRA AMAZON 2/12"
    norm2 = helper.normalize_description_for_dedup(desc2)
    print(f"   Original: '{desc2}'")
    print(f"   Normalizada: '{norm2}'")
    assert norm2 == "COMPRA AMAZON", "Falha: parcela não removida"
    print("   ✅ OK")
    
    # Teste 3: Geração de chave
    print("\n3. Teste: Geração de chave composta")
    key = helper.generate_dedup_key("15/11/2025", "PIX ENVIADO 15/11", -50.00, "ITAU")
    print(f"   Chave: '{key}'")
    assert key == "2025-11-15|PIX ENVIADO|-50.00|ITAU", "Falha: chave incorreta"
    print("   ✅ OK")
    
    # Teste 4: Conversão de data
    print("\n4. Teste: Conversão de data")
    data_br = "15/11/2025"
    data_iso = helper.convert_date_to_iso(data_br)
    print(f"   BR: '{data_br}' -> ISO: '{data_iso}'")
    assert data_iso == "2025-11-15", "Falha: conversão incorreta"
    print("   ✅ OK")
    
    # Teste 5: Parse de chave
    print("\n5. Teste: Parse de chave")
    key = "2025-11-15|PIX ENVIADO|-50.00|ITAU"
    data, desc, valor, fonte = helper.parse_dedup_key(key)
    print(f"   Chave: '{key}'")
    print(f"   Componentes: data={data}, desc={desc}, valor={valor}, fonte={fonte}")
    assert data == "2025-11-15", "Falha: data incorreta"
    assert desc == "PIX ENVIADO", "Falha: descrição incorreta"
    assert valor == -50.00, "Falha: valor incorreto"
    assert fonte == "ITAU", "Falha: fonte incorreta"
    print("   ✅ OK")
    
    print("\n" + "=" * 60)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("=" * 60)
