# ============================================================================
# MÓDULO DE LOGGING
# Sistema de log profissional com suporte a arquivo e console
# ============================================================================

import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(app):
    """
    Configura o sistema de logging da aplicação.
    
    Args:
        app (Flask): Instância da aplicação Flask
    """
    
    # Criar diretório de logs se não existir
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configurar logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Formato do log
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S'
    )
    
    # Handler para arquivo (Rotating)
    file_handler = RotatingFileHandler(
        'logs/sistema.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    logger.info('Sistema de logging inicializado')


def get_logger(name):
    """
    Obtém um logger para um módulo específico.
    
    Args:
        name (str): Nome do módulo
        
    Returns:
        logging.Logger: Logger configurado
    """
    return logging.getLogger(name)
