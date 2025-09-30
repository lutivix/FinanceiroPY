
"""
Agente Financeiro - Sistema de Processamento de Extratos Bancários
================================================================

Sistema modular para processamento e categorização automática de extratos
bancários de PIX, Itaú e Latam com geração de relatórios em Excel.

Versão: 2.0 - Arquitetura Modular Refatorada
"""

import os
import sys
import logging
import configparser
from pathlib import Path

# Imports da nova arquitetura modular
from services import FinancialAgentService


def configurar_logging():
    """Configura o sistema de logging do aplicativo."""
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            # logging.FileHandler('agente_financeiro.log', encoding='utf-8')  # Descomente para salvar em arquivo
        ]
    )
    return logging.getLogger(__name__)


def carregar_configuracao():
    """Carrega configurações do arquivo ini."""
    config = configparser.ConfigParser()
    config_file = 'config.ini'
    
    # Se não existe config.ini, usa o exemplo
    if not os.path.exists(config_file):
        config_file = 'config.example.ini'
        logger.warning("⚠️  config.ini não encontrado. Usando config.example.ini")
        logger.info("💡 Copie config.example.ini para config.ini e ajuste seus caminhos")
    
    try:
        config.read(config_file, encoding='utf-8')
        logger.info(f"✅ Configuração carregada de: {config_file}")
        return config
    except Exception as e:
        logger.error(f"❌ Erro ao carregar configuração: {e}")
        sys.exit(1)


def validar_estrutura_diretorios(diretorio_base):
    """Valida se a estrutura de diretórios necessária existe."""
    diretorios_necessarios = ['planilhas', 'db']
    
    for diretorio in diretorios_necessarios:
        caminho = Path(diretorio_base) / diretorio
        if not caminho.exists():
            logger.error(f"❌ Diretório não encontrado: {caminho}")
            logger.info("💡 Execute o script setup.bat para criar a estrutura necessária")
            return False
    
    return True


def main():
    """Função principal do agente financeiro."""
    logger.info("� Iniciando Agente Financeiro v2.0")
    logger.info("=" * 60)
    
    try:
        # Carrega configuração
        config = carregar_configuracao()
        
        # Determina diretório de dados
        diretorio_base = config.get('PATHS', 'diretorio_arquivos', fallback='dados')
        
        # Se é caminho relativo, usa relativo ao script atual
        if not os.path.isabs(diretorio_base):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(script_dir))  # Volta 2 níveis
            diretorio_dados = os.path.join(project_root, diretorio_base)
        else:
            diretorio_dados = diretorio_base
        
        logger.info(f"� Diretório de dados: {diretorio_dados}")
        
        # Valida estrutura de diretórios
        if not os.path.exists(diretorio_dados):
            logger.error(f"❌ Diretório base não encontrado: {diretorio_dados}")
            sys.exit(1)
        
        if not validar_estrutura_diretorios(diretorio_dados):
            sys.exit(1)
        
        # Inicializa serviço principal
        financial_service = FinancialAgentService(
            data_directory=Path(diretorio_dados),
            config={
                'excel_filename': config.get('EXCEL', 'arquivo_saida', fallback='consolidado_temp.xlsx'),
                'months_back': config.getint('PROCESSAMENTO', 'meses_retroativos', fallback=12),
                'default_category': config.get('PROCESSAMENTO', 'categoria_padrao', fallback='A definir')
            }
        )
        
        # Executa processamento completo
        logger.info("🔄 Iniciando processamento completo...")
        resultado = financial_service.run_complete_processing(
            months_back=config.getint('PROCESSAMENTO', 'meses_retroativos', fallback=12),
            save_to_database=True,
            generate_excel=True
        )
        
        # Verifica se o processamento foi bem-sucedido
        if not resultado.get('success', False):
            logger.error(f"❌ Falha no processamento: {resultado.get('error', 'Erro desconhecido')}")
            sys.exit(1)
        
        # Exibe resultado
        logger.info("=" * 60)
        logger.info("✅ PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
        logger.info("=" * 60)
        
        summary = resultado.get('summary', {})
        stats = resultado.get('stats')
        
        if resultado.get('excel_path'):
            logger.info(f"📄 Arquivo Excel gerado: {resultado['excel_path']}")
        
        # Calcula caminho do banco
        banco_path = Path(diretorio_dados) / 'db' / 'financeiro.db'
        logger.info(f"🗄️  Dados salvos no banco: {banco_path}")
        
        # Estatísticas do processamento
        total_transacoes = resultado.get('transactions_count', 0)
        logger.info(f"📊 Total de transações processadas: {total_transacoes}")
        
        if stats:
            logger.info(f"📂 Transações extraídas: {stats.transactions_extracted}")
            logger.info(f"🎯 Transações categorizadas automaticamente: {stats.transactions_categorized}")
            
            transacoes_nao_categorizadas = stats.transactions_extracted - stats.transactions_categorized
            if transacoes_nao_categorizadas > 0:
                logger.warning(f"⚠️  Transações para revisar: {transacoes_nao_categorizadas}")
                logger.info("💡 Revise as transações 'A definir' no Excel e execute novamente para aprender")
            
            if stats.processing_time_seconds:
                logger.info(f"⏱️  Tempo de processamento: {stats.processing_time_seconds:.2f}s")
        
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        logger.warning("⚠️  Operação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro durante processamento: {e}")
        logger.exception("Detalhes do erro:")
        sys.exit(1)


if __name__ == "__main__":
    logger = configurar_logging()
    main()
