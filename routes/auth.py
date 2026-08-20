# BLUEPRINT: AUTENTICAÇÃO
# Rotas relacionadas ao login, logout e perfil de usuários

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from utils.logger import get_logger

logger = get_logger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

CREDENCIAIS = {
    'admin@afs.com': {
        'senha_hash': generate_password_hash('Admin123!'),
        'nome': 'Administrador AFS',
        'role': 'admin',
        'is_admin': True
    },
    'professor@afs.com': {
        'senha_hash': generate_password_hash('Professor123!'),
        'nome': 'Professor AFS',
        'role': 'professor',
        'is_admin': False
    },
    'aluno@afs.com': {
        'senha_hash': generate_password_hash('Aluno123!'),
        'nome': 'Aluno AFS',
        'role': 'aluno',
        'is_admin': False
    }
}


class AuthUser:
    """Wrapper para prover compatibilidade com chamadas no template Jinja."""
    def __init__(self, user_dict):
        self.nome_completo = user_dict.get('nome_completo', '')
        self.email = user_dict.get('email', '')
        self.role = user_dict.get('role', 'professor' if not user_dict.get('is_admin', False) else 'admin')
        self._is_admin = user_dict.get('is_admin', self.role == 'admin')

    def is_admin(self):
        return self._is_admin

    def is_professor(self):
        return self.role == 'professor'

    def is_student(self):
        return self.role == 'aluno'

    def is_authenticated(self):
        return True


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Realiza o login do usuário.
    """
    if 'user' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'GET':
        return render_template('auth/login.html')

    # POST - Processar login
    email = request.form.get('email', '').strip()
    senha = request.form.get('senha', '').strip()

    usuario = CREDENCIAIS.get(email)
    if usuario and check_password_hash(usuario['senha_hash'], senha):
        session['user'] = {
            'email': email,
            'nome_completo': usuario['nome'],
            'role': usuario['role'],
            'is_admin': usuario['is_admin']
        }
        logger.info(f'Usuário logado com sucesso: {email}')
        flash('Login realizado com sucesso!', 'sucesso')
        return redirect(url_for('dashboard.index'))
    else:
        logger.warning(f'Tentativa de login malsucedida para: {email}')
        flash('E-mail ou senha incorretos.', 'erro')
        return render_template('auth/login.html', erro='E-mail ou senha incorretos.')


@auth_bp.route('/logout')
def logout():
    """
    Realiza o logout do usuário.
    """
    email = session.get('user', {}).get('email')
    session.pop('user', None)
    logger.info(f'Usuário deslogado: {email}')
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/perfil', methods=['GET', 'POST'])
def perfil():
    """
    Exibe e atualiza o perfil do usuário logado.
    """
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    user_dict = session['user']

    if request.method == 'GET':
        professor = ProfessorWrapper(user_dict)
        return render_template('auth/perfil.html', professor=professor)

    # POST - Atualizar perfil (apenas nome completo)
    nome_completo = request.form.get('nome_completo', '').strip()
    if len(nome_completo) < 3:
        flash('O nome completo deve conter pelo menos 3 caracteres.', 'erro')
        professor = ProfessorWrapper(user_dict)
        return render_template('auth/perfil.html', professor=professor)

    # Atualizar session
    user_dict['nome_completo'] = nome_completo
    session['user'] = user_dict
    session.modified = True

    logger.info(f"Perfil do usuário {user_dict['email']} atualizado para: {nome_completo}")
    flash('Perfil atualizado com sucesso!', 'sucesso')
    return redirect(url_for('auth.perfil'))


@auth_bp.route('/alterar-senha', methods=['GET', 'POST'])
def alterar_senha():
    """
    Altera a senha do usuário (simulado).
    """
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        return render_template('auth/alterar_senha.html')

    # POST - Alterar senha
    senha_atual = request.form.get('senha_atual', '')
    senha_nova = request.form.get('senha_nova', '')
    confirmar_senha = request.form.get('confirmar_senha', '')

    # Validações básicas de senha
    if not senha_nova or len(senha_nova) < 8:
        flash('A nova senha deve ter pelo menos 8 caracteres.', 'erro')
        return render_template('auth/alterar_senha.html')

    if senha_nova != confirmar_senha:
        flash('A nova senha e a confirmação não conferem.', 'erro')
        return render_template('auth/alterar_senha.html')

    # Como não temos um DB de usuários persistente com senhas mutáveis, apenas simulamos
    logger.info(f"Senha de {session['user']['email']} alterada com sucesso (simulada)")
    flash('Senha alterada com sucesso!', 'sucesso')
    return redirect(url_for('auth.perfil'))
