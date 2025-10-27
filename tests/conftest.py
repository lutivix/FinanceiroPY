"""
Configurações e fixtures globais para testes pytest
===================================================

Este arquivo contém fixtures reutilizáveis em todos os testes.
"""

import os
import sys
import sqlite3
import pytest
import tempfile
from pathlib import Path
from datetime import datetime, date

# Adiciona o diretório backend/src ao PYTHONPATH para imports
backend_src = Path(__file__).parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))


@pytest.fixture
def temp_dir():
    """Diretório temporário para testes."""
    import gc
    import time
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir
        # Windows SQLite Cleanup Issue Workaround
        # Force garbage collection and wait briefly for file handles to close
        gc.collect()
        time.sleep(0.1)  # Give Windows time to release locks


@pytest.fixture
def test_db_path(temp_dir):
    """Cria banco de dados SQLite temporário para testes."""
    db_path = Path(temp_dir) / "test_financeiro.db"
    yield str(db_path)
    # Cleanup é automático com temp_dir


@pytest.fixture
def mock_config(temp_dir):
    """Retorna configuração mock para testes."""
    return {
        'PATHS': {
            'diretorio_arquivos': str(temp_dir),
            'arquivo_saida': 'test_consolidado.xlsx'
        },
        'DATABASE': {
            'arquivo_db': str(temp_dir / "test_financeiro.db")
        }
    }


@pytest.fixture
def sample_transactions():
    """Retorna lista de transações de exemplo para testes."""
    return [
        {
            'data': date(2025, 10, 15),
            'descricao': 'SUPERMERCADO ZONA SUL',
            'valor': -150.50,
            'fonte': 'Master',
            'categoria': 'Alimentação',
            'mes_comp': '202510'
        },
        {
            'data': date(2025, 10, 16),
            'descricao': 'PIX RECEBIDO JOAO SILVA',
            'valor': 500.00,
            'fonte': 'PIX',
            'categoria': 'Transferência',
            'mes_comp': '202510'
        },
        {
            'data': date(2025, 10, 17),
            'descricao': 'RESTAURANTE BOM SABOR',
            'valor': -85.00,
            'fonte': 'Visa',
            'categoria': 'Alimentação',
            'mes_comp': '202510'
        },
    ]


@pytest.fixture
def sample_pix_content():
    """Conteúdo de exemplo de arquivo PIX (TXT) - SEM cabeçalho."""
    return """15/10/2025;SUPERMERCADO ZONA SUL;-150,50
16/10/2025;PIX RECEBIDO JOAO SILVA;500,00
17/10/2025;FARMACIA DROGASIL;-45,80
18/10/2025;PAGAMENTO LUZ CEMIG;-250,00
19/10/2025;PIX ENVIADO MARIA SANTOS;-100,00"""


@pytest.fixture
def sample_pix_file(temp_dir, sample_pix_content):
    """Cria arquivo PIX de teste."""
    pix_file = Path(temp_dir) / "202510_Extrato.txt"
    pix_file.write_text(sample_pix_content, encoding='utf-8')
    return pix_file


@pytest.fixture
def sample_categories():
    """Retorna dicionário de categorias de exemplo."""
    return {
        'SUPERMERCADO': 'Alimentação',
        'RESTAURANTE': 'Alimentação',
        'FARMACIA': 'Saúde',
        'DROGARIA': 'Saúde',
        'LUZ': 'Contas',
        'AGUA': 'Contas',
        'INTERNET': 'Contas',
        'GASOLINA': 'Transporte',
        'UBER': 'Transporte',
        'NETFLIX': 'Lazer',
        'SPOTIFY': 'Lazer',
    }


@pytest.fixture
def initialized_db(test_db_path, sample_categories):
    """Cria banco de dados inicializado com estrutura e dados de teste."""
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    
    # Cria tabela de transações
    cursor.execute("""
        CREATE TABLE lancamentos (
            Data TEXT NOT NULL,
            Descricao TEXT NOT NULL,
            Valor REAL NOT NULL,
            Fonte TEXT NOT NULL,
            Categoria TEXT NOT NULL,
            MesComp TEXT NOT NULL,
            id TEXT,
            raw_data TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT
        )
    """)
    
    # Cria tabela de categorias
    cursor.execute("""
        CREATE TABLE categoria_dicionario (
            descricao_normalizada TEXT PRIMARY KEY,
            categoria TEXT NOT NULL,
            ultima_atualizacao TEXT DEFAULT CURRENT_TIMESTAMP,
            fonte_aprendizado TEXT,
            confianca REAL DEFAULT 1.0
        )
    """)
    
    # Insere categorias de exemplo
    for descricao, categoria in sample_categories.items():
        cursor.execute(
            "INSERT INTO categoria_dicionario (descricao_normalizada, categoria) VALUES (?, ?)",
            (descricao, categoria)
        )
    
    conn.commit()
    conn.close()
    
    # Força garbage collection para liberar handles do SQLite
    import gc
    gc.collect()
    
    return test_db_path


@pytest.fixture
def mock_excel_file(temp_dir):
    """Cria arquivo Excel de teste vazio."""
    import openpyxl
    
    excel_path = Path(temp_dir) / "test_consolidado.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    
    # Cria cabeçalho
    headers = ['Data', 'Descrição', 'Valor', 'Fonte', 'Categoria', 'MesComp']
    for col, header in enumerate(headers, start=1):
        ws.cell(row=1, column=col, value=header)
    
    wb.save(excel_path)
    return excel_path


# Fixtures para mocks de processadores
@pytest.fixture
def mock_pix_processor():
    """Mock do processador PIX."""
    from processors.pix import PixProcessor
    return PixProcessor()


@pytest.fixture
def mock_card_processor():
    """Mock do processador de cartões."""
    from processors.cards import CardProcessor
    return CardProcessor()


# Configurações de teste
def pytest_configure(config):
    """Configurações executadas antes dos testes."""
    config.addinivalue_line(
        "markers", "slow: marca testes que são lentos para executar"
    )
    config.addinivalue_line(
        "markers", "integration: marca testes de integração"
    )
    config.addinivalue_line(
        "markers", "unit: marca testes unitários"
    )
