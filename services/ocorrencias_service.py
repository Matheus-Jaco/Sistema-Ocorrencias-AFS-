# ============================================================================
# SERVIÇO DE OCORRÊNCIAS
# Lógica de negócio para gerenciamento de ocorrências relacionais
# ============================================================================

import uuid
from datetime import datetime
from utils.sqlite_db import SQLiteDB
from utils.validators import Validador, sanitizar_input
from utils.helpers import paginar_resultados
from utils.logger import get_logger
from services.alunos_service import ServicoAlunos

logger = get_logger(__name__)


class ServicoOcorrencias:
    """Serviço centralizado para gerenciamento de ocorrências."""

    def __init__(self, caminho_dados):
        self.db = SQLiteDB(caminho_dados)
        self.validador = Validador()
        self.servico_alunos = ServicoAlunos(caminho_dados)

    def _normalizar_ano(self, ano):
        if not ano:
            return ano
        ano = ano.strip()
        if ano in ['1º', '2º', '3º']:
            return f"{ano} Ano"
        return ano

    def _obter_aluno_por_dados(self, nome_aluno, curso, ano):
        if not nome_aluno or not curso or not ano:
            return None
        ano_normalizado = self._normalizar_ano(ano)
        turma = self.servico_alunos.obter_turma_por_curso_e_ano(curso, ano_normalizado)
        if not turma:
            return None
        return self.servico_alunos.obter_aluno_por_nome_e_turma(nome_aluno, turma['id'])

    def criar_ocorrencia(self, dados):
        """
        Cria nova ocorrência com validações.
        """
        logger.info('Iniciando criação de ocorrência relacional')

        try:
            # Obter e sanitizar entradas
            aluno_id = sanitizar_input(dados.get('aluno_id', ''))
            nome_aluno = sanitizar_input(dados.get('nome_aluno', ''))
            curso = sanitizar_input(dados.get('curso', ''))
            ano = self._normalizar_ano(sanitizar_input(dados.get('ano', '')))
            data = sanitizar_input(dados.get('data_ocorrencia', ''))
            descricao = sanitizar_input(dados.get('descricao', ''))
            gravidade = sanitizar_input(dados.get('gravidade', ''))
            observacoes = sanitizar_input(dados.get('observacoes', ''))

            if not aluno_id:
                if not nome_aluno:
                    return {
                        'sucesso': False,
                        'mensagem': 'Erro: O aluno deve ser selecionado ou o nome precisa ser informado.',
                        'campo': 'aluno_id'
                    }
                if not curso or not ano:
                    return {
                        'sucesso': False,
                        'mensagem': 'Erro: Curso e ano são necessários quando o aluno não está cadastrado.',
                        'campo': 'curso'
                    }

                aluno_existente = self._obter_aluno_por_dados(nome_aluno, curso, ano)
                if aluno_existente:
                    aluno_id = aluno_existente['id']
                    logger.info(f'Aluno existente encontrado e reaproveitado: {aluno_id} - {aluno_existente["nome_completo"]}')
                else:
                    turma = self.servico_alunos.obter_turma_por_curso_e_ano(curso, ano)
                    if not turma:
                        return {
                            'sucesso': False,
                            'mensagem': 'Erro: Turma não encontrada para curso e ano informados.',
                            'campo': 'curso'
                        }
                    resultado_aluno = self.servico_alunos.criar_aluno({
                        'nome_completo': nome_aluno,
                        'turma_id': turma['id']
                    })
                    if not resultado_aluno['sucesso']:
                        return resultado_aluno
                    aluno_id = resultado_aluno['dados']['id']

            # Buscar dados do aluno no DB para garantir vínculo
            aluno = self.db.fetchone(
                """
                SELECT a.nome_completo, t.curso, t.ano 
                FROM alunos a 
                JOIN turmas t ON a.turma_id = t.id 
                WHERE a.id = ?
                """,
                (aluno_id,)
            )

            if not aluno:
                return {
                    'sucesso': False,
                    'mensagem': 'Erro: Aluno não cadastrado ou não encontrado.',
                    'campo': 'aluno_id'
                }

            # Validações dos outros campos
            validacoes = [
                (self.validador.validar_data(data), 'data'),
                (self.validador.validar_descricao(descricao), 'descricao'),
                (self.validador.validar_gravidade(gravidade), 'gravidade'),
            ]

            for (valido, mensagem), campo in validacoes:
                if not valido:
                    logger.warning(f'Validação falhou para {campo}: {mensagem}')
                    return {
                        'sucesso': False,
                        'mensagem': f'Erro em {campo}: {mensagem}',
                        'campo': campo
                    }

            ocorrencia_id = str(uuid.uuid4())
            agora = datetime.now().isoformat()

            self.db.execute(
                '''
                INSERT INTO ocorrencias (
                    id, aluno_id, data_ocorrencia,
                    descricao, gravidade, observacoes, data_criacao
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    ocorrencia_id,
                    aluno_id,
                    data,
                    descricao,
                    gravidade,
                    observacoes,
                    agora
                )
            )

            ocorrencia = {
                'id': ocorrencia_id,
                'aluno_id': aluno_id,
                'nome_aluno': aluno['nome_completo'],
                'curso': aluno['curso'],
                'ano': aluno['ano'],
                'data_ocorrencia': data,
                'descricao': descricao,
                'gravidade': gravidade,
                'observacoes': observacoes,
                'data_criacao': agora,
                'data_atualizacao': None
            }

            logger.info(f'Ocorrência criada com sucesso: {ocorrencia_id} para o aluno: {aluno["nome_completo"]}')
            return {
                'sucesso': True,
                'mensagem': 'Ocorrência registrada com sucesso!',
                'dados': ocorrencia
            }

        except Exception as e:
            logger.error(f'Erro ao criar ocorrência: {str(e)}')
            return {
                'sucesso': False,
                'mensagem': f'Erro ao registrar ocorrência: {str(e)}'
            }

    def obter_todas_ocorrencias(self):
        """
        Obtém todas as ocorrências ordenadas por data de ocorrência.
        """
        return self.db.fetchall_dict(
            '''
            SELECT o.*, a.nome_completo AS nome_aluno, t.curso, t.ano 
            FROM ocorrencias o 
            JOIN alunos a ON o.aluno_id = a.id 
            JOIN turmas t ON a.turma_id = t.id 
            ORDER BY o.data_ocorrencia DESC, o.data_criacao DESC
            '''
        )

    def obter_ocorrencia_por_id(self, ocorrencia_id):
        """
        Obtém ocorrência específica com dados do aluno e turma.
        """
        return self.db.fetchone(
            '''
            SELECT o.*, a.nome_completo AS nome_aluno, t.curso, t.ano 
            FROM ocorrencias o 
            JOIN alunos a ON o.aluno_id = a.id 
            JOIN turmas t ON a.turma_id = t.id 
            WHERE o.id = ?
            ''',
            (ocorrencia_id,)
        )

    def obter_ocorrencias_por_aluno(self, aluno_id):
        """
        Obtém o histórico de ocorrências de um aluno específico.
        """
        return self.db.fetchall_dict(
            '''
            SELECT o.*, a.nome_completo AS nome_aluno, t.curso, t.ano 
            FROM ocorrencias o 
            JOIN alunos a ON o.aluno_id = a.id 
            JOIN turmas t ON a.turma_id = t.id 
            WHERE o.aluno_id = ?
            ORDER BY o.data_ocorrencia DESC, o.data_criacao DESC
            ''',
            (aluno_id,)
        )

    def filtrar_ocorrencias(self, criterios):
        """
        Filtra ocorrências por múltiplos critérios.
        """
        query = '''
            SELECT o.*, a.nome_completo AS nome_aluno, t.curso, t.ano 
            FROM ocorrencias o 
            JOIN alunos a ON o.aluno_id = a.id 
            JOIN turmas t ON a.turma_id = t.id
        '''
        filtros = []
        parametros = []

        if criterios.get('nome'):
            filtros.append('LOWER(a.nome_completo) LIKE ?')
            parametros.append(f"%{criterios['nome'].strip().lower()}%")

        if criterios.get('matricula'):
            filtros.append('LOWER(a.matricula) LIKE ?')
            parametros.append(f"%{criterios['matricula'].strip().lower()}%")

        if criterios.get('curso') and criterios['curso'] != 'todos':
            filtros.append('t.curso = ?')
            parametros.append(criterios['curso'])

        if criterios.get('ano') and criterios['ano'] != 'todos':
            ano_filtro = criterios['ano']
            # Normalizar para "Xº Ano" caso seja passado como "Xº"
            if not ano_filtro.endswith('Ano') and ano_filtro in ['1º', '2º', '3º']:
                ano_filtro = f"{ano_filtro} Ano"
            filtros.append('t.ano = ?')
            parametros.append(ano_filtro)

        if criterios.get('gravidade') and criterios['gravidade'] != 'todos':
            filtros.append('o.gravidade = ?')
            parametros.append(criterios['gravidade'])

        if filtros:
            query += ' WHERE ' + ' AND '.join(filtros)

        query += ' ORDER BY o.data_ocorrencia DESC, o.data_criacao DESC'
        return self.db.fetchall_dict(query, tuple(parametros))

    def agrupar_ocorrencias_por_aluno(self, ocorrencias):
        """
        Agrupa ocorrências por aluno para exibição única por aluno.
        """
        agrupados = {}
        for ocorrencia in ocorrencias:
            aluno_id = ocorrencia['aluno_id']
            if aluno_id not in agrupados:
                agrupados[aluno_id] = {
                    'aluno_id': aluno_id,
                    'nome_aluno': ocorrencia['nome_aluno'],
                    'curso': ocorrencia['curso'],
                    'ano': ocorrencia['ano'],
                    'ocorrencias': []
                }
            agrupados[aluno_id]['ocorrencias'].append(ocorrencia)
        return list(agrupados.values())

    def atualizar_ocorrencia(self, ocorrencia_id, dados):
        """
        Atualiza campos mutáveis de uma ocorrência existente (gravidade, descrição, observações).
        """
        logger.info(f'Atualizando ocorrência: {ocorrencia_id}')

        try:
            ocorrencia = self.obter_ocorrencia_por_id(ocorrencia_id)
            if not ocorrencia:
                return {
                    'sucesso': False,
                    'mensagem': 'Ocorrência não encontrada'
                }

            campos = []
            parametros = []

            if 'descricao' in dados:
                descricao = sanitizar_input(dados.get('descricao', ''))
                valido, msg = self.validador.validar_descricao(descricao)
                if not valido:
                    return {'sucesso': False, 'mensagem': msg}
                campos.append('descricao = ?')
                parametros.append(descricao)

            if 'gravidade' in dados:
                gravidade = sanitizar_input(dados.get('gravidade', ''))
                valido, msg = self.validador.validar_gravidade(gravidade)
                if not valido:
                    return {'sucesso': False, 'mensagem': msg}
                campos.append('gravidade = ?')
                parametros.append(gravidade)

            if 'observacoes' in dados:
                observacoes = sanitizar_input(dados.get('observacoes', ''))
                campos.append('observacoes = ?')
                parametros.append(observacoes)

            if not campos:
                return {
                    'sucesso': False,
                    'mensagem': 'Nenhum campo mutável enviado para atualização'
                }

            campos.append('data_atualizacao = ?')
            parametros.append(datetime.now().isoformat())
            
            # Parametro do ID para a cláusula WHERE
            parametros.append(ocorrencia_id)

            query = f"UPDATE ocorrencias SET {', '.join(campos)} WHERE id = ?"
            self.db.execute(query, tuple(parametros))

            ocorrencia_atualizada = self.obter_ocorrencia_por_id(ocorrencia_id)

            logger.info(f'Ocorrência atualizada com sucesso: {ocorrencia_id}')
            return {
                'sucesso': True,
                'mensagem': 'Ocorrência atualizada com sucesso!',
                'dados': ocorrencia_atualizada
            }

        except Exception as e:
            logger.error(f'Erro ao atualizar ocorrência: {str(e)}')
            return {
                'sucesso': False,
                'mensagem': f'Erro ao atualizar: {str(e)}'
            }

    def deletar_ocorrencia(self, ocorrencia_id):
        """
        Deleta ocorrência.
        """
        logger.info(f'Deletando ocorrência: {ocorrencia_id}')

        try:
            cursor = self.db.execute(
                'DELETE FROM ocorrencias WHERE id = ?',
                (ocorrencia_id,)
            )

            if cursor.rowcount == 0:
                logger.warning(f'Ocorrência não encontrada para exclusão: {ocorrencia_id}')
                return {
                    'sucesso': False,
                    'mensagem': 'Ocorrência não encontrada'
                }

            logger.info(f'Ocorrência deletada com sucesso: {ocorrencia_id}')
            return {
                'sucesso': True,
                'mensagem': 'Ocorrência removida com sucesso!'
            }

        except Exception as e:
            logger.error(f'Erro ao deletar ocorrência: {str(e)}')
            return {
                'sucesso': False,
                'mensagem': f'Erro ao remover: {str(e)}'
            }

    def obter_estatisticas(self):
        """
        Obtém estatísticas gerais das ocorrências.
        """
        ocorrencias = self.obter_todas_ocorrencias()

        stats = {
            'total': len(ocorrencias),
            'por_gravidade': {},
            'por_curso': {},
            'por_ano': {}
        }

        for ocorrencia in ocorrencias:
            gravidade = ocorrencia.get('gravidade')
            stats['por_gravidade'][gravidade] = stats['por_gravidade'].get(gravidade, 0) + 1

            curso = ocorrencia.get('curso')
            stats['por_curso'][curso] = stats['por_curso'].get(curso, 0) + 1

            ano = ocorrencia.get('ano')
            stats['por_ano'][ano] = stats['por_ano'].get(ano, 0) + 1

        return stats
