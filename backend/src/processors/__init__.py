"""
Módulo de processadores de extratos financeiros
"""

from .base import BaseProcessor
from .pix import PixProcessor
from .cards import ItauProcessor, LatamProcessor, CardProcessor
from .cards_v2 import CardStatementV2Processor

__all__ = [
    'BaseProcessor',
    'PixProcessor', 
    'ItauProcessor',
    'LatamProcessor',
    'CardProcessor',
    'CardStatementV2Processor'
]