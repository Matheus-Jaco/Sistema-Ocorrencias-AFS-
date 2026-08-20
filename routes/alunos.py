# BLUEPRINT: ALUNOS
# Rotas relacionadas ao gerenciamento de turmas e alunos (Apenas Admin)

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from services.alunos_service import ServicoAlunos
from services.ocorrencias_service import ServicoOcorrencias
from utils.logger import get_logger

logger = get_logger(__name__)

alunos_bp = Blueprint('alunos', __name__, url_prefix='/alunos')


@alunos_bp.before_request
def verificar_admin():
    """Garante que apenas administradores acessem as rotas de alunos."""
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    # Permitir rota de busca e detalhes para admin e professor
    if request.endpoint in ('alunos.detalhes_aluno', 'alunos.buscar'):
        if session['user'].get('role') == 'aluno':
            logger.warning(f"Acesso não autorizado de {session['user'].get('email')} à área de alunos.")
            flash("Acesso negado: apenas administradores e professores podem acessar esses dados.", "erro")
            return redirect(url_for('dashboard.index'))
        return None
    
    # Outras rotas (CRUD) - apenas admin
    if not session['user'].get('is_admin'):
        logger.warning(f"Acesso não autorizado de {session['user'].get('email')} à área de alunos.")
        flash("Acesso negado: apenas administradores podem gerenciar turmas e alunos.", "erro")
        return redirect(url_for('dashboard.index'))


@alunos_bp.route('/')
def index():
    """
    Página principal de gerenciamento de alunos e turmas.
    """
    try:
        servico = ServicoAlunos(current_app.config['DATA_PATH'])
        
        # Obter turmas com a contagem de alunos de forma relacional
        query = """
            SELECT t.*, COUNT(a.id) as total_alunos 
            FROM turmas t 
            LEFT JOIN alunos a ON t.id = a.turma_id 
            GROUP BY t.id 
            ORDER BY t.curso, t.ano
        """
        turmas = servico.db.fetchall_dict(query)
        
        # Opções válidas para cadastro
        cursos_validos = ['Administração', 'Logística', 'Enfermagem', 'Informática', 'Desenvolvimento de Sistemas']
        anos_validos = ['1º Ano', '2º Ano', '3º Ano']
        
        return render_template(
            'alunos/gerenciar.html',
            turmas=turmas,
            cursos_validos=cursos_validos,
            anos_validos=anos_validos,
            is_admin=session['user'].get('is_admin', False)
        )
    except Exception as e:
        logger.error(f"Erro ao carregar gerenciamento de alunos: {e}")
        return render_template('errors/500.html'), 500


@alunos_bp.route('/buscar')
def buscar():
    """Busca alunos usando filtros e paginação."""
    try:
        nome = request.args.get('nome', '').strip()
        matricula = request.args.get('matricula', '').strip()
        curso = request.args.get('curso', '').strip()
        ano = request.args.get('ano', '').strip()
        page = request.args.get('page', '1')
        try:
            page = int(page)
        except ValueError:
            page = 1
        if page < 1:
            page = 1

        servico = ServicoAlunos(current_app.config['DATA_PATH'])
        resultado = servico.buscar_alunos(nome=nome, matricula=matricula, curso=curso, ano=ano, page=page)
        alunos = resultado['alunos']
        total = resultado['total']
        page_size = resultado.get('page_size', 10)
        total_pages = max(1, (total + page_size - 1) // page_size)
        if page > total_pages:
            page = total_pages

        cursos_validos = ['Administração', 'Logística', 'Enfermagem', 'Informática', 'Desenvolvimento de Sistemas']
        anos_validos = ['1º Ano', '2º Ano', '3º Ano']

        filtros = {
            'nome': nome,
            'matricula': matricula,
            'curso': curso,
            'ano': ano
        }

        return render_template(
            'alunos/buscar.html',
            alunos=alunos,
            total=total,
            page=page,
            total_pages=total_pages,
            page_size=page_size,
            cursos_validos=cursos_validos,
            anos_validos=anos_validos,
            filtros=filtros
        )
    except Exception as e:
        logger.error(f"Erro ao carregar busca de alunos: {e}")
        return render_template('errors/500.html'), 500


@alunos_bp.route('/turma/criar', methods=['POST'])
def criar_turma():
    """
    Cria uma nova turma.
    """
    try:
        servico = ServicoAlunos(current_app.config['DATA_PATH'])
        resultado = servico.criar_turma(request.form)
        
        if resultado['sucesso']:
            flash(resultado['mensagem'], 'sucesso')
        else:
            flash(resultado['mensagem'], 'erro')
            
        return redirect(url_for('alunos.index'))
    except Exception as e:
        logger.error(f"Erro ao criar turma: {e}")
        flash(f"Erro ao cadastrar turma: {e}", 'erro')
        return redirect(url_for('alunos.index'))


@alunos_bp.route('/aluno/criar', methods=['POST'])
def criar_aluno():
    """
    Cadastra um novo aluno em uma turma específica.
    """
    try:
        servico = ServicoAlunos(current_app.config['DATA_PATH'])
        resultado = servico.criar_aluno(request.form)
        
        if resultado['sucesso']:
            flash(resultado['mensagem'], 'sucesso')
        else:
            flash(resultado['mensagem'], 'erro')
            
        return redirect(url_for('alunos.index'))
    except Exception as e:
        logger.error(f"Erro ao cadastrar aluno: {e}")
        flash(f"Erro ao cadastrar aluno: {e}", 'erro')
        return redirect(url_for('alunos.index'))


@alunos_bp.route('/detalhes/<aluno_id>')
def detalhes_aluno(aluno_id):
    """Exibe detalhes de um aluno e seu histórico de ocorrências."""
    try:
        servico_alunos = ServicoAlunos(current_app.config['DATA_PATH'])
        servico_ocorrencias = ServicoOcorrencias(current_app.config['DATA_PATH'])

        aluno = servico_alunos.obter_aluno_por_id(aluno_id)
        if not aluno:
            logger.warning(f"Aluno não encontrado: {aluno_id}")
            return render_template('errors/404.html'), 404

        ocorrencias = servico_ocorrencias.obter_ocorrencias_por_aluno(aluno_id)
        responsaveis = servico_alunos.obter_responsaveis_por_aluno(aluno_id)

        return render_template(
            'alunos/detalhes.html',
            aluno=aluno,
            ocorrencias=ocorrencias,
            responsaveis=responsaveis
        )
    except Exception as e:
        logger.error(f"Erro ao carregar detalhes do aluno: {e}")
        return render_template('errors/500.html'), 500


@alunos_bp.route('/editar/<aluno_id>', methods=['GET', 'POST'])
def editar_aluno(aluno_id):
    """Exibe e processa o formulário de edição de um aluno."""
    servico = ServicoAlunos(current_app.config['DATA_PATH'])
    try:
        aluno = servico.obter_aluno_por_id(aluno_id)
        if not aluno:
            logger.warning(f"Aluno não encontrado para edição: {aluno_id}")
            return render_template('errors/404.html'), 404

        if request.method == 'POST':
            resultado = servico.atualizar_aluno(aluno_id, request.form, editor_email=session['user'].get('email'))
            if resultado['sucesso']:
                flash(resultado['mensagem'], 'sucesso')
                return redirect(url_for('alunos.editar_aluno', aluno_id=aluno_id))
            flash(resultado['mensagem'], 'erro')

        responsaveis = servico.obter_responsaveis_por_aluno(aluno_id)
        cursos_validos = ['Administração', 'Logística', 'Enfermagem', 'Informática', 'Desenvolvimento de Sistemas']
        anos_validos = ['1º Ano', '2º Ano', '3º Ano']

        return render_template(
            'alunos/editar.html',
            aluno=aluno,
            responsaveis=responsaveis,
            cursos_validos=cursos_validos,
            anos_validos=anos_validos
        )
    except Exception as e:
        logger.error(f"Erro ao carregar/editar aluno: {e}")
        return render_template('errors/500.html'), 500


# --- ENDPOINTS DE API REST (AJAX) ---

@alunos_bp.route('/api/turma/<turma_id>/alunos', methods=['GET'])
def api_obter_alunos(turma_id):
    """
    Obtém alunos de uma turma via JSON.
    """
    try:
        servico = ServicoAlunos(current_app.config['DATA_PATH'])
        alunos = servico.obter_alunos_por_turma(turma_id)
        return jsonify({
            'sucesso': True,
            'alunos': alunos
        }), 200
    except Exception as e:
        logger.error(f"Erro na API de obter alunos: {e}")
        return jsonify({
            'sucesso': False,
            'mensagem': "Erro ao buscar alunos da turma."
        }), 500


@alunos_bp.route('/api/aluno/<aluno_id>/deletar', methods=['DELETE'])
def api_deletar_aluno(aluno_id):
    """
    Deleta um aluno via requisição AJAX.
    """
    try:
        servico = ServicoAlunos(current_app.config['DATA_PATH'])
        resultado = servico.deletar_aluno(aluno_id)
        status_code = 200 if resultado['sucesso'] else 400
        return jsonify(resultado), status_code
    except Exception as e:
        logger.error(f"Erro na API de deletar aluno: {e}")
        return jsonify({
            'sucesso': False,
            'mensagem': "Erro interno ao remover aluno."
        }), 500


@alunos_bp.route('/api/turma/<turma_id>/deletar', methods=['DELETE'])
def api_deletar_turma(turma_id):
    """
    Deleta uma turma via requisição AJAX (e cascade).
    """
    try:
        servico = ServicoAlunos(current_app.config['DATA_PATH'])
        resultado = servico.deletar_turma(turma_id)
        status_code = 200 if resultado['sucesso'] else 400
        return jsonify(resultado), status_code
    except Exception as e:
        logger.error(f"Erro na API de deletar turma: {e}")
        return jsonify({
            'sucesso': False,
            'mensagem': "Erro interno ao remover turma."
        }), 500
