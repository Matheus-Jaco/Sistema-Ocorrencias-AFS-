# ============================================================================
# SERVIÇO DE ALUNOS E TURMAS
# Lógica de negócio para gerenciamento de turmas e alunos
# ============================================================================

import re
import uuid
from datetime import datetime
from utils.sqlite_db import SQLiteDB
from utils.validators import Validador, sanitizar_input
from utils.logger import get_logger

logger = get_logger(__name__)


class ServicoAlunos:
    """Serviço para gerenciamento de turmas e alunos."""

    def __init__(self, caminho_dados):
        self.db = SQLiteDB(caminho_dados)
        self.validador = Validador()

    # --- GERENCIAMENTO DE TURMAS ---

    def obter_todas_turmas(self):
        """Retorna todas as turmas ordenadas por curso e ano."""
        try:
            return self.db.fetchall_dict(
                "SELECT * FROM turmas ORDER BY curso, ano"
            )
        except Exception as e:
            logger.error(f"Erro ao obter todas as turmas: {e}")
            return []

    def obter_turma_por_id(self, turma_id):
        """Busca uma turma pelo ID."""
        try:
            return self.db.fetchone(
                "SELECT * FROM turmas WHERE id = ?",
                (turma_id,)
            )
        except Exception as e:
            logger.error(f"Erro ao obter turma por ID ({turma_id}): {e}")
            return None

    def obter_turma_por_curso_e_ano(self, curso, ano):
        """Busca uma turma por curso e ano."""
        try:
            return self.db.fetchone(
                "SELECT * FROM turmas WHERE curso = ? AND ano = ?",
                (curso, ano)
            )
        except Exception as e:
            logger.error(f"Erro ao obter turma por curso/ano: {e}")
            return None

    def criar_turma(self, dados):
        """
        Cria uma nova turma se válida e não duplicada.
        """
        logger.info("Tentando criar turma")
        try:
            curso = sanitizar_input(dados.get('curso', ''))
            ano = sanitizar_input(dados.get('ano', ''))

            # Validações
            valido_curso, msg_curso = self.validador.validar_curso(curso)
            if not valido_curso:
                return {'sucesso': False, 'mensagem': msg_curso, 'campo': 'curso'}

            valido_ano, msg_ano = self.validador.validar_ano(ano)
            if not valido_ano:
                return {'sucesso': False, 'mensagem': msg_ano, 'campo': 'ano'}

            # Verificar duplicidade
            turma_existente = self.obter_turma_por_curso_e_ano(curso, ano)
            if turma_existente:
                return {
                    'sucesso': False, 
                    'mensagem': f"A turma de {curso} ({ano}) já está cadastrada."
                }

            turma_id = str(uuid.uuid4())
            self.db.execute(
                "INSERT INTO turmas (id, curso, ano) VALUES (?, ?, ?)",
                (turma_id, curso, ano)
            )

            logger.info(f"Turma criada com sucesso: {turma_id} ({curso} - {ano})")
            return {
                'sucesso': True,
                'mensagem': "Turma cadastrada com sucesso!",
                'dados': {'id': turma_id, 'curso': curso, 'ano': ano}
            }
        except Exception as e:
            logger.error(f"Erro ao criar turma: {e}")
            return {'sucesso': False, 'mensagem': f"Erro interno: {e}"}

    def deletar_turma(self, turma_id):
        """Remove uma turma e cascade alunos e ocorrências associadas."""
        logger.info(f"Deletando turma: {turma_id}")
        try:
            self.db.execute("DELETE FROM turmas WHERE id = ?", (turma_id,))
            return {'sucesso': True, 'mensagem': "Turma removida com sucesso!"}
        except Exception as e:
            logger.error(f"Erro ao deletar turma ({turma_id}): {e}")
            return {'sucesso': False, 'mensagem': f"Erro ao deletar: {e}"}

    # --- GERENCIAMENTO DE ALUNOS ---

    def obter_alunos_por_turma(self, turma_id):
        """Retorna a lista de alunos de uma turma."""
        try:
            return self.db.fetchall_dict(
                "SELECT * FROM alunos WHERE turma_id = ? ORDER BY nome_completo",
                (turma_id,)
            )
        except Exception as e:
            logger.error(f"Erro ao obter alunos da turma ({turma_id}): {e}")
            return []

    def obter_quantidade_alunos_turma(self, turma_id):
        """Conta quantos alunos estão na turma."""
        try:
            res = self.db.fetchone(
                "SELECT COUNT(*) as total FROM alunos WHERE turma_id = ?",
                (turma_id,)
            )
            return res['total'] if res else 0
        except Exception as e:
            logger.error(f"Erro ao contar alunos da turma ({turma_id}): {e}")
            return 0

    def obter_aluno_por_id(self, aluno_id):
        """Obtém os detalhes de um aluno por ID, incluindo curso e ano."""
        try:
            return self.db.fetchone(
                """
                SELECT a.*, t.curso, t.ano 
                FROM alunos a 
                JOIN turmas t ON a.turma_id = t.id 
                WHERE a.id = ?
                """,
                (aluno_id,)
            )
        except Exception as e:
            logger.error(f"Erro ao obter aluno por ID ({aluno_id}): {e}")
            return None

    def obter_responsaveis_por_aluno(self, aluno_id):
        """Retorna os responsáveis vinculados a um aluno."""
        try:
            return self.db.fetchall_dict(
                """
                SELECT r.*
                FROM responsaveis r
                JOIN aluno_responsaveis ar ON r.id = ar.responsavel_id
                WHERE ar.aluno_id = ?
                ORDER BY r.nome_completo
                """,
                (aluno_id,)
            )
        except Exception as e:
            logger.error(f"Erro ao obter responsáveis do aluno ({aluno_id}): {e}")
            return []

    def _obter_ou_criar_turma(self, curso, ano):
        turma = self.obter_turma_por_curso_e_ano(curso, ano)
        if turma:
            return turma

        turma_id = str(uuid.uuid4())
        self.db.execute(
            "INSERT INTO turmas (id, curso, ano) VALUES (?, ?, ?)",
            (turma_id, curso, ano)
        )
        return {'id': turma_id, 'curso': curso, 'ano': ano}

    def _construir_criterios_busca(self, nome, matricula, curso, ano):
        condicoes = []
        parametros = []

        if nome:
            condicoes.append("a.nome_completo LIKE ?")
            parametros.append(f"%{nome}%")

        if matricula:
            condicoes.append("a.matricula LIKE ?")
            parametros.append(f"%{matricula}%")

        if curso:
            condicoes.append("t.curso = ?")
            parametros.append(curso)

        if ano:
            condicoes.append("t.ano = ?")
            parametros.append(ano)

        where_clause = ""
        if condicoes:
            where_clause = " AND " + " AND ".join(condicoes)

        return where_clause, parametros

    def buscar_alunos(self, nome='', matricula='', curso='', ano='', page=1, page_size=10):
        """Busca alunos usando filtros com paginação."""
        try:
            nome = sanitizar_input(nome)
            matricula = sanitizar_input(matricula)
            curso = sanitizar_input(curso)
            ano = sanitizar_input(ano)

            where_clause, parametros = self._construir_criterios_busca(nome, matricula, curso, ano)

            count_query = f"""
                SELECT COUNT(*) as total
                FROM alunos a
                JOIN turmas t ON a.turma_id = t.id
                WHERE 1=1 {where_clause}
            """
            total_result = self.db.fetchone(count_query, parametros)
            total = total_result['total'] if total_result else 0

            offset = (page - 1) * page_size
            query = f"""
                SELECT a.*, t.curso, t.ano
                FROM alunos a
                JOIN turmas t ON a.turma_id = t.id
                WHERE 1=1 {where_clause}
                ORDER BY a.nome_completo COLLATE NOCASE ASC
                LIMIT ? OFFSET ?
            """
            alunos = self.db.fetchall_dict(query, parametros + [page_size, offset])

            return {'alunos': alunos, 'total': total, 'page_size': page_size}
        except Exception as e:
            logger.error(f"Erro ao buscar alunos: {e}")
            return {'alunos': [], 'total': 0, 'page_size': page_size}

    def _normalizar_nome(self, nome):
        if not isinstance(nome, str):
            return nome
        nome = nome.strip()
        nome = re.sub(r"\s+", " ", nome)
        return nome.lower()

    def obter_aluno_por_nome_e_turma(self, nome, turma_id):
        """Verifica se aluno com mesmo nome existe na mesma turma."""
        try:
            alunos = self.db.fetchall_dict(
                "SELECT * FROM alunos WHERE turma_id = ?",
                (turma_id,)
            )
            nome_normalizado = self._normalizar_nome(nome)
            for aluno in alunos:
                if self._normalizar_nome(aluno['nome_completo']) == nome_normalizado:
                    return aluno
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar aluno por nome/turma: {e}")
            return None

    def criar_aluno(self, dados):
        """
        Cria um aluno na turma respeitando limites e restrições.
        """
        try:
            # Extrair campos principais
            nome = sanitizar_input(dados.get('nome_completo', ''))
            turma_id = sanitizar_input(dados.get('turma_id', ''))
            matricula = sanitizar_input(dados.get('matricula', ''))
            data_nasc = sanitizar_input(dados.get('data_nascimento', ''))
            sexo = sanitizar_input(dados.get('sexo', ''))
            nacionalidade = sanitizar_input(dados.get('nacionalidade', ''))
            naturalidade_cidade = sanitizar_input(dados.get('naturalidade_cidade', ''))
            naturalidade_estado = sanitizar_input(dados.get('naturalidade_estado', ''))
            rua = sanitizar_input(dados.get('rua', ''))
            numero = sanitizar_input(dados.get('numero', ''))
            complemento = sanitizar_input(dados.get('complemento', ''))
            bairro = sanitizar_input(dados.get('bairro', ''))
            cep = sanitizar_input(dados.get('cep', ''))
            cidade = sanitizar_input(dados.get('cidade', ''))
            estado = sanitizar_input(dados.get('estado', ''))

            # Validações
            valido, msg = self.validador.validar_matricula(matricula)
            if not valido:
                return {'sucesso': False, 'mensagem': msg, 'campo': 'matricula'}

            valido_nome, msg_nome = self.validador.validar_nome_aluno(nome)
            if not valido_nome:
                return {'sucesso': False, 'mensagem': msg_nome, 'campo': 'nome_completo'}

            valido_data, msg_data = self.validador.validar_data_nascimento(data_nasc)
            if not valido_data:
                return {'sucesso': False, 'mensagem': msg_data, 'campo': 'data_nascimento'}

            valido_sexo, msg_sexo = self.validador.validar_genero(sexo)
            if not valido_sexo:
                return {'sucesso': False, 'mensagem': msg_sexo, 'campo': 'sexo'}

            if not turma_id:
                return {'sucesso': False, 'mensagem': "ID da turma é obrigatório.", 'campo': 'turma_id'}

            turma = self.obter_turma_por_id(turma_id)
            if not turma:
                return {'sucesso': False, 'mensagem': "Turma não encontrada.", 'campo': 'turma_id'}

            # Limite máximo de 45 alunos
            total_alunos = self.obter_quantidade_alunos_turma(turma_id)
            if total_alunos >= 45:
                return {
                    'sucesso': False,
                    'mensagem': "Não é possível adicionar aluno. A turma já atingiu a capacidade máxima de 45 alunos."
                }

            # Verificar matrícula única
            existente = self.db.fetchone("SELECT id FROM alunos WHERE matricula = ?", (matricula,))
            if existente:
                return {'sucesso': False, 'mensagem': 'Já existe um aluno com essa matrícula.', 'campo': 'matricula'}

            nome_formatado = re.sub(r"\s+", " ", nome).strip()

            aluno_id = str(uuid.uuid4())
            data_cadastro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.db.execute(
                '''INSERT INTO alunos (
                    id, matricula, nome_completo, turma_id, data_nascimento, sexo,
                    nacionalidade, naturalidade_cidade, naturalidade_estado,
                    rua, numero, complemento, bairro, cep, cidade, estado, data_cadastro
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    aluno_id, matricula, nome_formatado, turma_id, data_nasc, sexo,
                    nacionalidade, naturalidade_cidade, naturalidade_estado,
                    rua, numero, complemento, bairro, cep, cidade, estado, data_cadastro
                )
            )

            # Tratar responsáveis (listas)
            nomes = dados.getlist('responsavel_nome') if hasattr(dados, 'getlist') else dados.get('responsavel_nome', [])
            graus = dados.getlist('responsavel_parentesco') if hasattr(dados, 'getlist') else dados.get('responsavel_parentesco', [])
            celulares = dados.getlist('responsavel_celular') if hasattr(dados, 'getlist') else dados.get('responsavel_celular', [])
            residenciais = dados.getlist('responsavel_residencial') if hasattr(dados, 'getlist') else dados.get('responsavel_residencial', [])
            emails = dados.getlist('responsavel_email') if hasattr(dados, 'getlist') else dados.get('responsavel_email', [])

            for i, nome_r in enumerate(nomes):
                nome_r = sanitizar_input(nome_r)
                grau_r = sanitizar_input(graus[i]) if i < len(graus) else ''
                celular_r = sanitizar_input(celulares[i]) if i < len(celulares) else ''
                residencial_r = sanitizar_input(residenciais[i]) if i < len(residenciais) else ''
                email_r = sanitizar_input(emails[i]) if i < len(emails) else ''

                if not nome_r and not grau_r and not email_r and not celular_r and not residencial_r:
                    continue

                valido_resp, msg_resp = self.validador.validar_responsavel({
                    'nome': nome_r,
                    'grau': grau_r,
                    'celular': celular_r,
                    'email': email_r
                })
                if not valido_resp:
                    # Não interromper todo o cadastro por um responsável inválido, apenas informar
                    logger.warning(f"Responsável inválido ignorado: {msg_resp}")
                    continue

                responsavel_id = str(uuid.uuid4())
                self.db.execute(
                    "INSERT INTO responsaveis (id, nome_completo, grau_parentesco, celular, residencial, email) VALUES (?, ?, ?, ?, ?, ?)",
                    (responsavel_id, nome_r, grau_r, celular_r, residencial_r, email_r)
                )
                self.db.execute(
                    "INSERT INTO aluno_responsaveis (aluno_id, responsavel_id) VALUES (?, ?)",
                    (aluno_id, responsavel_id)
                )

            logger.info(f"Aluno cadastrado: {aluno_id} - {nome} na turma {turma_id}")
            return {
                'sucesso': True,
                'mensagem': "Aluno cadastrado com sucesso!",
                'dados': {
                    'id': aluno_id,
                    'nome_completo': nome,
                    'turma_id': turma_id,
                    'curso': turma['curso'],
                    'ano': turma['ano']
                }
            }
        except Exception as e:
            logger.error(f"Erro ao criar aluno: {e}")
            return {'sucesso': False, 'mensagem': f"Erro interno ao cadastrar aluno: {e}"}

    def atualizar_aluno(self, aluno_id, dados, editor_email=None):
        """Atualiza os dados de um aluno existente."""
        try:
            aluno_atual = self.obter_aluno_por_id(aluno_id)
            if not aluno_atual:
                return {'sucesso': False, 'mensagem': 'Aluno não encontrado.'}

            nome = sanitizar_input(dados.get('nome_completo', ''))
            matricula = sanitizar_input(dados.get('matricula', ''))
            data_nasc = sanitizar_input(dados.get('data_nascimento', ''))
            sexo = sanitizar_input(dados.get('sexo', ''))
            nacionalidade = sanitizar_input(dados.get('nacionalidade', ''))
            naturalidade_cidade = sanitizar_input(dados.get('naturalidade_cidade', ''))
            naturalidade_estado = sanitizar_input(dados.get('naturalidade_estado', ''))
            rua = sanitizar_input(dados.get('rua', ''))
            numero = sanitizar_input(dados.get('numero', ''))
            complemento = sanitizar_input(dados.get('complemento', ''))
            bairro = sanitizar_input(dados.get('bairro', ''))
            cep = sanitizar_input(dados.get('cep', ''))
            cidade = sanitizar_input(dados.get('cidade', ''))
            estado = sanitizar_input(dados.get('estado', ''))
            curso = sanitizar_input(dados.get('curso', ''))
            ano = sanitizar_input(dados.get('ano', ''))

            valido, msg = self.validador.validar_matricula(matricula)
            if not valido:
                return {'sucesso': False, 'mensagem': msg, 'campo': 'matricula'}

            valido_nome, msg_nome = self.validador.validar_nome_aluno(nome)
            if not valido_nome:
                return {'sucesso': False, 'mensagem': msg_nome, 'campo': 'nome_completo'}

            valido_data, msg_data = self.validador.validar_data_nascimento(data_nasc)
            if not valido_data:
                return {'sucesso': False, 'mensagem': msg_data, 'campo': 'data_nascimento'}

            valido_sexo, msg_sexo = self.validador.validar_genero(sexo)
            if not valido_sexo:
                return {'sucesso': False, 'mensagem': msg_sexo, 'campo': 'sexo'}

            if not curso:
                return {'sucesso': False, 'mensagem': 'Curso é obrigatório.', 'campo': 'curso'}
            if not ano:
                return {'sucesso': False, 'mensagem': 'Ano/Turma é obrigatório.', 'campo': 'ano'}

            existente = self.db.fetchone(
                "SELECT id FROM alunos WHERE matricula = ? AND id != ?",
                (matricula, aluno_id)
            )
            if existente:
                return {'sucesso': False, 'mensagem': 'Já existe outro aluno com essa matrícula.', 'campo': 'matricula'}

            turma = self._obter_ou_criar_turma(curso, ano)
            turma_id = turma['id']
            nome_formatado = re.sub(r"\s+", " ", nome).strip()

            self.db.execute(
                '''UPDATE alunos SET
                    matricula = ?, nome_completo = ?, turma_id = ?, data_nascimento = ?, sexo = ?,
                    nacionalidade = ?, naturalidade_cidade = ?, naturalidade_estado = ?,
                    rua = ?, numero = ?, complemento = ?, bairro = ?, cep = ?, cidade = ?, estado = ?
                WHERE id = ?''',
                (
                    matricula, nome_formatado, turma_id, data_nasc, sexo,
                    nacionalidade, naturalidade_cidade, naturalidade_estado,
                    rua, numero, complemento, bairro, cep, cidade, estado,
                    aluno_id
                )
            )

            self.db.execute("DELETE FROM aluno_responsaveis WHERE aluno_id = ?", (aluno_id,))
            self.db.execute(
                "DELETE FROM responsaveis WHERE id NOT IN (SELECT responsavel_id FROM aluno_responsaveis)")

            nomes = dados.getlist('responsavel_nome') if hasattr(dados, 'getlist') else dados.get('responsavel_nome', [])
            graus = dados.getlist('responsavel_parentesco') if hasattr(dados, 'getlist') else dados.get('responsavel_parentesco', [])
            celulares = dados.getlist('responsavel_celular') if hasattr(dados, 'getlist') else dados.get('responsavel_celular', [])
            residenciais = dados.getlist('responsavel_residencial') if hasattr(dados, 'getlist') else dados.get('responsavel_residencial', [])
            emails = dados.getlist('responsavel_email') if hasattr(dados, 'getlist') else dados.get('responsavel_email', [])

            for i, nome_r in enumerate(nomes):
                nome_r = sanitizar_input(nome_r)
                grau_r = sanitizar_input(graus[i]) if i < len(graus) else ''
                celular_r = sanitizar_input(celulares[i]) if i < len(celulares) else ''
                residencial_r = sanitizar_input(residenciais[i]) if i < len(residenciais) else ''
                email_r = sanitizar_input(emails[i]) if i < len(emails) else ''

                if not nome_r and not grau_r and not email_r and not celular_r and not residencial_r:
                    continue

                valido_resp, msg_resp = self.validador.validar_responsavel({
                    'nome': nome_r,
                    'grau': grau_r,
                    'celular': celular_r,
                    'email': email_r
                })
                if not valido_resp:
                    logger.warning(f"Responsável inválido ignorado: {msg_resp}")
                    continue

                responsavel_id = str(uuid.uuid4())
                self.db.execute(
                    "INSERT INTO responsaveis (id, nome_completo, grau_parentesco, celular, residencial, email) VALUES (?, ?, ?, ?, ?, ?)",
                    (responsavel_id, nome_r, grau_r, celular_r, residencial_r, email_r)
                )
                self.db.execute(
                    "INSERT INTO aluno_responsaveis (aluno_id, responsavel_id) VALUES (?, ?)",
                    (aluno_id, responsavel_id)
                )

            anterior = {
                'nome_completo': aluno_atual.get('nome_completo'),
                'matricula': aluno_atual.get('matricula'),
                'data_nascimento': aluno_atual.get('data_nascimento'),
                'sexo': aluno_atual.get('sexo'),
                'curso': aluno_atual.get('curso'),
                'ano': aluno_atual.get('ano'),
            }
            atual = {
                'nome_completo': nome_formatado,
                'matricula': matricula,
                'data_nascimento': data_nasc,
                'sexo': sexo,
                'curso': curso,
                'ano': ano,
            }
            logger.info(
                f"Aluno atualizado por {editor_email or 'desconhecido'}: {aluno_id}. "
                f"Antes: {anterior}. Depois: {atual}."
            )

            return {'sucesso': True, 'mensagem': 'Aluno atualizado com sucesso!'}
        except Exception as e:
            logger.error(f"Erro ao atualizar aluno ({aluno_id}): {e}")
            return {'sucesso': False, 'mensagem': f'Erro interno ao atualizar aluno: {e}'}

    def deletar_aluno(self, aluno_id):
        """Remove o aluno e cascade suas ocorrências."""
        logger.info(f"Deletando aluno: {aluno_id}")
        try:
            self.db.execute("DELETE FROM alunos WHERE id = ?", (aluno_id,))
            return {'sucesso': True, 'mensagem': "Aluno removido com sucesso!"}
        except Exception as e:
            logger.error(f"Erro ao deletar aluno ({aluno_id}): {e}")
            return {'sucesso': False, 'mensagem': f"Erro ao remover aluno: {e}"}
