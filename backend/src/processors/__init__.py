"""
Módulo de processadores de extratos financeiros
"""

from .base import BaseProcessor
from .pix import PixProcessor
from .cards import ItauProcessor, LatamProcessor, CardProcessor

__all__ = [
    'BaseProcessor',
    'PixProcessor', 
    'ItauProcessor',
    'LatamProcessor',
    'CardProcessor'
]