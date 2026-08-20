# BLUEPRINT: OCORRÊNCIAS
# Rotas relacionadas ao CRUD de ocorrências

from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for, session, flash
from services.ocorrencias_service import ServicoOcorrencias
from utils.helpers import paginar_resultados, formatar_data_br
from utils.logger import get_logger

logger = get_logger(__name__)

ocorrencias_bp = Blueprint('ocorrencias', __name__, url_prefix='/ocorrencias')


@ocorrencias_bp.before_request
def verificar_autenticacao():
    """Garante que apenas usuários logados acessem as rotas de ocorrências."""
    if 'user' not in session:
        logger.warning(f"Acesso não autorizado (não logado) à área de ocorrências.")
        flash("Você precisa estar logado para acessar ocorrências.", "erro")
        return redirect(url_for('auth.login'))


def is_student_user():
    return session.get('user', {}).get('role') == 'aluno'


@ocorrencias_bp.route('/')
def listar():
    """
    Lista todas as ocorrências com opções de filtro e paginação.
    
    Returns:
        str: Template renderizado
    """
    try:
        servico = ServicoOcorrencias(current_app.config['DATA_PATH'])
        
        # Obter parâmetros de query
        pagina = request.args.get('pagina', 1, type=int)
        nome_filtro = request.args.get('nome', '')
        matricula_filtro = request.args.get('matricula', '')
        curso_filtro = request.args.get('curso', 'todos')
        ano_filtro = request.args.get('ano', 'todos')
        gravidade_filtro = request.args.get('gravidade', 'todos')
        
        # Preparar critérios de filtro
        criterios = {
            'nome': nome_filtro,
            'matricula': matricula_filtro,
            'curso': curso_filtro,
            'ano': ano_filtro,
            'gravidade': gravidade_filtro
        }
        
        # Filtrar ocorrências
        ocorrencias = servico.filtrar_ocorrencias(criterios)
        ocorrencias_agrupadas = servico.agrupar_ocorrencias_por_aluno(ocorrencias)
        
        # Paginar por aluno agrupado
        resultado_paginado = paginar_resultados(ocorrencias_agrupadas, pagina, itens_por_pagina=10)
        
        # Obter estatísticas para filtros
        stats = servico.obter_estatisticas()
        
        logger.info(f'Listagem de ocorrências agrupadas por aluno: {len(ocorrencias_agrupadas)} alunos encontrados')
        
        return render_template(
            'ocorrencias/listar.html',
            ocorrencias=resultado_paginado['itens'],
            pagina_atual=resultado_paginado['pagina_atual'],
            total_paginas=resultado_paginado['total_paginas'],
            total_itens=len(ocorrencias_agrupadas),
            criterios=criterios,
            stats=stats
        )
    
    except Exception as e:
        logger.error(f'Erro ao listar ocorrências: {str(e)}')
        return render_template('errors/500.html'), 500


@ocorrencias_bp.route('/criar', methods=['GET', 'POST'])
def criar():
    """
    Formulário para criar nova ocorrência.
    
    Returns:
        GET: str: Template renderizado
        POST: redirect: Redirecionado para listagem
    """
    try:
        if is_student_user():
            logger.warning(f"Aluno tentou acessar criação de ocorrência: {session['user'].get('email')}")
            flash("Acesso negado: alunos não podem cadastrar ocorrências.", "erro")
            return redirect(url_for('ocorrencias.listar'))

        if request.method == 'GET':
            return render_template('ocorrencias/criar.html')
        
        # POST - Processar formulário
        servico = ServicoOcorrencias(current_app.config['DATA_PATH'])
        
        resultado = servico.criar_ocorrencia(request.form)
        
        if resultado['sucesso']:
            logger.info('Ocorrência criada com sucesso via POST')
            return redirect(url_for('ocorrencias.detalhes', ocorrencia_id=resultado['dados']['id']))
        else:
            logger.warning(f'Falha ao criar ocorrência: {resultado["mensagem"]}')
            return render_template(
                'ocorrencias/criar.html',
                erro=resultado['mensagem']
            ), 400
    
    except Exception as e:
        logger.error(f'Erro ao criar ocorrência: {str(e)}')
        return render_template('errors/500.html'), 500


@ocorrencias_bp.route('/api/criar', methods=['POST'])
def api_criar():
    """
    API para criar ocorrência via AJAX.
    
    Returns:
        json: Resultado da operação
    """
    try:
        if is_student_user():
            logger.warning(f"Aluno tentou chamar API de criação de ocorrência: {session['user'].get('email')}")
            return jsonify({
                'sucesso': False,
                'mensagem': 'Acesso negado: alunos não podem criar ocorrências.'
            }), 403

        servico = ServicoOcorrencias(current_app.config['DATA_PATH'])
        dados = request.get_json()
        
        resultado = servico.criar_ocorrencia(dados)
        
        status_code = 201 if resultado['sucesso'] else 400
        return jsonify(resultado), status_code
    
    except Exception as e:
        logger.error(f'Erro na API de criação: {str(e)}')
        return jsonify({
            'sucesso': False,
            'mensagem': 'Erro ao processar requisição'
        }), 500


@ocorrencias_bp.route('/<ocorrencia_id>')
def detalhes(ocorrencia_id):
    """
    Exibe detalhes de uma ocorrência.
    
    Args:
        ocorrencia_id (str): ID da ocorrência
        
    Returns:
        str: Template renderizado
    """
    try:
        if is_student_user():
            logger.warning(f"Aluno tentou acessar detalhes da ocorrência: {session['user'].get('email')}")
            flash("Acesso negado: alunos não podem visualizar detalhes de ocorrências.", "erro")
            return redirect(url_for('ocorrencias.listar'))

        servico = ServicoOcorrencias(current_app.config['DATA_PATH'])
        ocorrencia = servico.obter_ocorrencia_por_id(ocorrencia_id)
        
        if not ocorrencia:
            logger.warning(f'Ocorrência não encontrada: {ocorrencia_id}')
            return render_template('errors/404.html'), 404
        
        # Buscar histórico de ocorrências do mesmo aluno (excluindo a atual)
        historico = servico.obter_ocorrencias_por_aluno(ocorrencia['aluno_id'])
        historico = [o for o in historico if o['id'] != ocorrencia['id']]
        
        logger.info(f'Detalhes acessados: {ocorrencia_id}')
        
        return render_template('ocorrencias/detalhes.html', ocorrencia=ocorrencia, historico=historico)
    
    except Exception as e:
        logger.error(f'Erro ao carregar detalhes: {str(e)}')
        return render_template('errors/500.html'), 500


@ocorrencias_bp.route('/<ocorrencia_id>/editar', methods=['GET', 'POST'])
def editar(ocorrencia_id):
    """
    Edita uma ocorrência existente.
    
    Args:
        ocorrencia_id (str): ID da ocorrência
        
    Returns:
        GET: str: Template renderizado
        POST: redirect: Redirecionado para detalhes
    """
    try:
        if is_student_user():
            logger.warning(f"Aluno tentou acessar edição de ocorrência: {session['user'].get('email')}")
            flash("Acesso negado: alunos não podem editar ocorrências.", "erro")
            return redirect(url_for('ocorrencias.listar'))

        servico = ServicoOcorrencias(current_app.config['DATA_PATH'])
        ocorrencia = servico.obter_ocorrencia_por_id(ocorrencia_id)
        
        if not ocorrencia:
            logger.warning(f'Ocorrência não encontrada para edição: {ocorrencia_id}')
            return render_template('errors/404.html'), 404
        
        if request.method == 'GET':
            return render_template('ocorrencias/editar.html', ocorrencia=ocorrencia)
        
        # POST - Atualizar
        resultado = servico.atualizar_ocorrencia(ocorrencia_id, request.form)
        
        if resultado['sucesso']:
            logger.info(f'Ocorrência atualizada: {ocorrencia_id}')
            return redirect(url_for('ocorrencias.detalhes', ocorrencia_id=ocorrencia_id))
        else:
            logger.warning(f'Falha ao atualizar: {resultado["mensagem"]}')
            return render_template(
                'ocorrencias/editar.html',
                ocorrencia=ocorrencia,
                erro=resultado['mensagem']
            ), 400
    
    except Exception as e:
        logger.error(f'Erro ao editar ocorrência: {str(e)}')
        return render_template('errors/500.html'), 500


@ocorrencias_bp.route('/api/<ocorrencia_id>/atualizar', methods=['PUT'])
def api_atualizar(ocorrencia_id):
    """
    API para atualizar ocorrência via AJAX.
    
    Args:
        ocorrencia_id (str): ID da ocorrência
        
    Returns:
        json: Resultado da operação
    """
    try:
        if is_student_user():
            logger.warning(f"Aluno tentou chamar API de atualização de ocorrência: {session['user'].get('email')}")
            return jsonify({
                'sucesso': False,
                'mensagem': 'Acesso negado: alunos não podem editar ocorrências.'
            }), 403

        servico = ServicoOcorrencias(current_app.config['DATA_PATH'])
        dados = request.get_json()
        
        resultado = servico.atualizar_ocorrencia(ocorrencia_id, dados)
        
        status_code = 200 if resultado['sucesso'] else 400
        return jsonify(resultado), status_code
    
    except Exception as e:
        logger.error(f'Erro na API de atualização: {str(e)}')
        return jsonify({
            'sucesso': False,
            'mensagem': 'Erro ao processar requisição'
        }), 500


@ocorrencias_bp.route('/api/<ocorrencia_id>/deletar', methods=['DELETE'])
def api_deletar(ocorrencia_id):
    """
    API para deletar ocorrência via AJAX.
    
    Args:
        ocorrencia_id (str): ID da ocorrência
        
    Returns:
        json: Resultado da operação
    """
    try:
        if is_student_user():
            logger.warning(f"Aluno tentou chamar API de exclusão de ocorrência: {session['user'].get('email')}")
            return jsonify({
                'sucesso': False,
                'mensagem': 'Acesso negado: alunos não podem excluir ocorrências.'
            }), 403

        servico = ServicoOcorrencias(current_app.config['DATA_PATH'])
        resultado = servico.deletar_ocorrencia(ocorrencia_id)
        
        status_code = 200 if resultado['sucesso'] else 400
        return jsonify(resultado), status_code
    
    except Exception as e:
        logger.error(f'Erro na API de exclusão: {str(e)}')
        return jsonify({
            'sucesso': False,
            'mensagem': 'Erro ao processar requisição'
        }), 500


@ocorrencias_bp.route('/api/filtrar', methods=['GET'])
def api_filtrar():
    """
    API para filtrar ocorrências em tempo real.
    
    Returns:
        json: Lista de ocorrências filtradas
    """
    try:
        servico = ServicoOcorrencias(current_app.config['DATA_PATH'])
        
        criterios = {
            'nome': request.args.get('nome', ''),
            'matricula': request.args.get('matricula', ''),
            'curso': request.args.get('curso', 'todos'),
            'ano': request.args.get('ano', 'todos'),
            'gravidade': request.args.get('gravidade', 'todos')
        }
        
        ocorrencias = servico.filtrar_ocorrencias(criterios)
        
        return jsonify({
            'sucesso': True,
            'total': len(ocorrencias),
            'ocorrencias': ocorrencias
        }), 200
    
    except Exception as e:
        logger.error(f'Erro na API de filtro: {str(e)}')
        return jsonify({
            'sucesso': False,
            'mensagem': 'Erro ao processar filtro'
        }), 500


@ocorrencias_bp.route('/api/alunos_por_turma', methods=['GET'])
def api_alunos_por_turma():
    """
    Retorna a lista de alunos de uma turma específica com base em curso e ano.
    """
    try:
        curso = request.args.get('curso', '').strip()
        ano = request.args.get('ano', '').strip()
        
        if not curso or not ano:
            return jsonify({'sucesso': False, 'mensagem': 'Curso e Ano são obrigatórios.'}), 400
        
        # Normalizar ano
        if not ano.endswith('Ano') and ano in ['1º', '2º', '3º']:
            ano = f"{ano} Ano"
            
        from services.alunos_service import ServicoAlunos
        servico_alunos = ServicoAlunos(current_app.config['DATA_PATH'])
        
        turma = servico_alunos.obter_turma_por_curso_e_ano(curso, ano)
        if not turma:
            return jsonify({'sucesso': True, 'alunos': []}), 200
            
        alunos = servico_alunos.obter_alunos_por_turma(turma['id'])
        return jsonify({'sucesso': True, 'alunos': alunos}), 200
    except Exception as e:
        logger.error(f"Erro na API de alunos por turma: {str(e)}")
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao processar requisição.'}), 500

