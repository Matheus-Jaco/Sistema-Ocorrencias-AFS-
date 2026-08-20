# BLUEPRINT: DASHBOARD
# Rotas relacionadas ao dashboard inicial

from flask import Blueprint, render_template, current_app
from services.ocorrencias_service import ServicoOcorrencias
from utils.logger import get_logger

logger = get_logger(__name__)

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='')


@dashboard_bp.route('/')
def index():
    """
    Página inicial - Dashboard principal.
    
    Returns:
        str: Template renderizado
    """
    try:
        # Instanciar serviço
        servico = ServicoOcorrencias(current_app.config['DATA_PATH'])
        
        # Obter estatísticas
        stats = servico.obter_estatisticas()
        
        logger.info('Dashboard acessado com sucesso')
        
        return render_template(
            'dashboard/index.html',
            stats=stats
        )
    
    except Exception as e:
        logger.error(f'Erro ao carregar dashboard: {str(e)}')
        return render_template('errors/500.html'), 500
