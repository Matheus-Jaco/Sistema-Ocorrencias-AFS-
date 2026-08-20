# SISTEMA DE OCORRÊNCIAS ESCOLARES AFS
# Desenvolvido com: Python + Flask | HTML5 + CSS3 + JavaScript
# Arquitetura: MVC com Blueprints | Persistência: BANCO DE DADOS SQLITE3

from flask import Flask, render_template
from datetime import datetime
import logging
import os
from logging.handlers import RotatingFileHandler

# Importação de Blueprints
from routes.ocorrencias import ocorrencias_bp
from routes.dashboard import dashboard_bp
from routes.auth import auth_bp
from routes.alunos import alunos_bp

# Importação de Utilities
from utils.logger import setup_logger
from flask import request, redirect, url_for, session


def create_app():
    """
    Factory pattern para criar e configurar a aplicação Flask.
    
    Returns:
        Flask: Aplicação Flask configurada
    """
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # CONFIGURAÇÕES
    app.config['JSON_AS_ASCII'] = False
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'sua-chave-secreta-aqui')
    
    # Caminho do banco de dados SQLite
    app.config['DATA_PATH'] = os.path.join(os.path.dirname(__file__), 'data', 'ocorrencias.db')
    
    # LOGGING 
    setup_logger(app)
    logger = logging.getLogger(__name__)
    
    # REGISTRO DE BLUEPRINTS 
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(ocorrencias_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(alunos_bp)
    
    # MIDDLEWARE DE AUTENTICAÇÃO
    @app.before_request
    def verificar_autenticacao():
        # Permitir acesso a rotas de login/logout e estáticos sem autenticação
        if request.endpoint:
            if request.endpoint.startswith('auth.') or request.endpoint == 'static':
                return
        
        # Se não estiver logado, redireciona para login
        if 'user' not in session:
            return redirect(url_for('auth.login'))
            
    # CONTEXT PROCESSORS 
    @app.context_processor
    def inject_globals():
        """Injeta variáveis globais nos templates."""
        from routes.auth import AuthUser
        current_user = None
        if 'user' in session:
            current_user = AuthUser(session['user'])
        return {
            'ano_atual': datetime.now().year,
            'app_name': 'Sistema de Ocorrências Escolares AFS',
            'versao': '1.0.0',
            'current_user': current_user
        }
    
    # ERROR HANDLERS 
    @app.errorhandler(404)
    def page_not_found(e):
        """Manipulador para erro 404."""
        logger.warning(f'Página não encontrada: {e}')
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        """Manipulador para erro 500."""
        logger.error(f'Erro interno do servidor: {e}')
        return render_template('errors/500.html'), 500
    
    # INICIALIZAÇÃO 
    logger.info('Aplicação Flask inicializada com sucesso')
    
    return app

# PONTO DE ENTRADA DA APLICAÇÃO
if __name__ == '__main__':
    app = create_app()
    
    # Desenvolvimento
    app.run(
        debug=True,
        host='127.0.0.1',
        port=5000,
        use_reloader=True
    )
