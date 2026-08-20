# ============================================================================
# MÓDULO DE GERENCIAMENTO SQLITE
# Responsável pela conexão e inicialização do banco de dados SQLite.
# ============================================================================

import os
import sqlite3
import uuid
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)


class SQLiteDB:
    """Gerenciador de banco de dados SQLite."""

    def __init__(self, caminho_banco):
        self.caminho_banco = caminho_banco
        self._garantir_banco_existe()

    def _garantir_banco_existe(self):
        os.makedirs(os.path.dirname(self.caminho_banco), exist_ok=True)
        
        # Verificar se precisa de migração antes de abrir conexão com chaves estrangeiras ativas
        precisa_migrar = False
        dados_antigos = []

        if os.path.exists(self.caminho_banco):
            # Conexão temporária para verificar esquema
            conn_temp = sqlite3.connect(self.caminho_banco)
            conn_temp.row_factory = sqlite3.Row
            cursor_temp = conn_temp.cursor()
            try:
                # Verificar se a tabela ocorrencias existe
                cursor_temp.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ocorrencias'")
                if cursor_temp.fetchone():
                    # Verificar se possui coluna nome_aluno
                    cursor_temp.execute("PRAGMA table_info(ocorrencias)")
                    colunas = [col['name'] for col in cursor_temp.fetchall()]
                    if 'nome_aluno' in colunas:
                        logger.info("Estrutura antiga detectada. Lendo dados para migração...")
                        precisa_migrar = True
                        cursor_temp.execute("SELECT * FROM ocorrencias")
                        dados_antigos = [dict(row) for row in cursor_temp.fetchall()]
            except Exception as e:
                logger.error(f"Erro ao verificar necessidade de migração: {e}")
            finally:
                conn_temp.close()

        with self._connect() as conexao:
            if precisa_migrar:
                logger.info("Iniciando processo de migração de dados do banco de dados...")
                try:
                    # Iniciar transação manualmente para segurança
                    conexao.execute("BEGIN TRANSACTION;")
                    
                    # Criar novas tabelas
                    conexao.execute('''
                        CREATE TABLE IF NOT EXISTS turmas (
                            id TEXT PRIMARY KEY,
                            curso TEXT NOT NULL,
                            ano TEXT NOT NULL,
                            UNIQUE(curso, ano)
                        )
                    ''')

                    conexao.execute('''
                        CREATE TABLE IF NOT EXISTS alunos (
                            id TEXT PRIMARY KEY,
                            nome_completo TEXT NOT NULL,
                            turma_id TEXT NOT NULL,
                            data_cadastro TEXT,
                            FOREIGN KEY(turma_id) REFERENCES turmas(id) ON DELETE CASCADE,
                            UNIQUE(nome_completo, turma_id)
                        )
                    ''')

                    conexao.execute('''
                        CREATE TABLE IF NOT EXISTS ocorrencias_novas (
                            id TEXT PRIMARY KEY,
                            aluno_id TEXT NOT NULL,
                            data_ocorrencia TEXT NOT NULL,
                            descricao TEXT NOT NULL,
                            gravidade TEXT NOT NULL,
                            observacoes TEXT,
                            data_criacao TEXT NOT NULL,
                            data_atualizacao TEXT,
                            FOREIGN KEY(aluno_id) REFERENCES alunos(id) ON DELETE CASCADE
                        )
                    ''')

                    # Dicionários em memória para mapear e evitar duplicados
                    mapa_turmas = {} # (curso, ano) -> turma_id
                    mapa_alunos = {} # (nome_completo, turma_id) -> aluno_id

                    # Migrar registros
                    for registro in dados_antigos:
                        curso = registro.get('curso', '').strip()
                        ano = registro.get('ano', '').strip()
                        
                        # Garantir que a turma existe
                        turma_chave = (curso, ano)
                        if turma_chave not in mapa_turmas:
                            # Tentar obter se já foi inserida no banco nesta transação
                            cursor = conexao.execute(
                                "SELECT id FROM turmas WHERE curso = ? AND ano = ?",
                                (curso, ano)
                            )
                            row = cursor.fetchone()
                            if row:
                                turma_id = row['id']
                            else:
                                turma_id = str(uuid.uuid4())
                                conexao.execute(
                                    "INSERT INTO turmas (id, curso, ano) VALUES (?, ?, ?)",
                                    (turma_id, curso, ano)
                                )
                            mapa_turmas[turma_chave] = turma_id
                        else:
                            turma_id = mapa_turmas[turma_chave]

                        # Garantir que o aluno existe
                        nome_aluno = registro.get('nome_aluno', '').strip()
                        aluno_chave = (nome_aluno, turma_id)
                        if aluno_chave not in mapa_alunos:
                            cursor = conexao.execute(
                                "SELECT id FROM alunos WHERE nome_completo = ? AND turma_id = ?",
                                (nome_aluno, turma_id)
                            )
                            row = cursor.fetchone()
                            if row:
                                aluno_id = row['id']
                            else:
                                aluno_id = str(uuid.uuid4())
                                conexao.execute(
                                    "INSERT INTO alunos (id, nome_completo, turma_id) VALUES (?, ?, ?)",
                                    (aluno_id, nome_aluno, turma_id)
                                )
                            mapa_alunos[aluno_chave] = aluno_id
                        else:
                            aluno_id = mapa_alunos[aluno_chave]

                        # Inserir ocorrência mapeada
                        conexao.execute(
                            '''
                            INSERT INTO ocorrencias_novas (
                                id, aluno_id, data_ocorrencia, descricao, 
                                gravidade, observacoes, data_criacao, data_atualizacao
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ''',
                            (
                                registro.get('id'),
                                aluno_id,
                                registro.get('data_ocorrencia'),
                                registro.get('descricao'),
                                registro.get('gravidade'),
                                registro.get('observacoes'),
                                registro.get('data_criacao'),
                                registro.get('data_atualizacao')
                            )
                        )
                    
                    # Dropar tabela antiga e renomear nova
                    conexao.execute("DROP TABLE ocorrencias")
                    conexao.execute("ALTER TABLE ocorrencias_novas RENAME TO ocorrencias")
                    conexao.commit()
                    logger.info("Migração de dados realizada com sucesso!")
                except Exception as ex:
                    conexao.rollback()
                    logger.error(f"Erro na migração de dados. Revertendo alterações: {ex}")
                    raise ex
            else:
                # Criar tabelas se não existirem (fluxo normal)
                conexao.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS turmas (
                        id TEXT PRIMARY KEY,
                        curso TEXT NOT NULL,
                        ano TEXT NOT NULL,
                        UNIQUE(curso, ano)
                    )
                    '''
                )
                conexao.execute(
                    '''
                CREATE TABLE IF NOT EXISTS alunos (
                        id TEXT PRIMARY KEY,
                        matricula TEXT UNIQUE NOT NULL,
                        nome_completo TEXT NOT NULL,
                        turma_id TEXT NOT NULL,
                        data_nascimento TEXT NOT NULL,
                        sexo TEXT NOT NULL,
                        nacionalidade TEXT,
                        naturalidade_cidade TEXT,
                        naturalidade_estado TEXT,
                        rua TEXT,
                        numero TEXT,
                        complemento TEXT,
                        bairro TEXT,
                        cep TEXT,
                        cidade TEXT,
                        estado TEXT,
                        data_cadastro TEXT,
                        FOREIGN KEY(turma_id) REFERENCES turmas(id) ON DELETE CASCADE
                    )
                    '''
                )
                conexao.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS ocorrencias (
                        id TEXT PRIMARY KEY,
                        aluno_id TEXT NOT NULL,
                        data_ocorrencia TEXT NOT NULL,
                        descricao TEXT NOT NULL,
                        gravidade TEXT NOT NULL,
                        observacoes TEXT,
                        data_criacao TEXT NOT NULL,
                        data_atualizacao TEXT,
                        FOREIGN KEY(aluno_id) REFERENCES alunos(id) ON DELETE CASCADE
                    )
                    '''
                )
                # Tabela de responsáveis e relação muitos-para-muitos (um responsável pode ter vários alunos)
                conexao.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS responsaveis (
                        id TEXT PRIMARY KEY,
                        nome_completo TEXT NOT NULL,
                        grau_parentesco TEXT NOT NULL,
                        celular TEXT,
                        residencial TEXT,
                        email TEXT
                    )
                    '''
                )

                conexao.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS aluno_responsaveis (
                        aluno_id TEXT NOT NULL,
                        responsavel_id TEXT NOT NULL,
                        PRIMARY KEY(aluno_id, responsavel_id),
                        FOREIGN KEY(aluno_id) REFERENCES alunos(id) ON DELETE CASCADE,
                        FOREIGN KEY(responsavel_id) REFERENCES responsaveis(id) ON DELETE CASCADE
                    )
                    '''
                )
                cursor = conexao.execute("PRAGMA table_info(alunos)")
                colunas_alunos = [row['name'] for row in cursor.fetchall()]
                if 'data_cadastro' not in colunas_alunos:
                    conexao.execute("ALTER TABLE alunos ADD COLUMN data_cadastro TEXT")

                cursor = conexao.execute("PRAGMA table_info(responsaveis)")
                colunas_resp = [row['name'] for row in cursor.fetchall()]
                if 'email' not in colunas_resp:
                    conexao.execute("ALTER TABLE responsaveis ADD COLUMN email TEXT")

                conexao.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS aluno_responsaveis (
                        aluno_id TEXT NOT NULL,
                        responsavel_id TEXT NOT NULL,
                        PRIMARY KEY(aluno_id, responsavel_id),
                        FOREIGN KEY(aluno_id) REFERENCES alunos(id) ON DELETE CASCADE,
                        FOREIGN KEY(responsavel_id) REFERENCES responsaveis(id) ON DELETE CASCADE
                    )
                    '''
                )

                cursor = conexao.execute("PRAGMA table_info(alunos)")
                colunas = [row['name'] for row in cursor.fetchall()]
                if 'data_cadastro' not in colunas:
                    conexao.execute("ALTER TABLE alunos ADD COLUMN data_cadastro TEXT")

                conexao.commit()
        logger.info(f'Banco SQLite inicializado em {self.caminho_banco}')

    def _connect(self):
        conexao = sqlite3.connect(self.caminho_banco, timeout=30, check_same_thread=False)
        conexao.row_factory = sqlite3.Row
        # Garantir chaves estrangeiras ativas
        conexao.execute("PRAGMA foreign_keys = ON;")
        return conexao

    def fetchall(self, query, parametros=()):
        conexao = self._connect()
        try:
            cursor = conexao.execute(query, parametros)
            return [dict(linha) for linha in cursor.fetchall()]
        finally:
            conexao.close()

    def fetchall_dict(self, query, parametros=()):
        conexao = self._connect()
        try:
            cursor = conexao.execute(query, parametros)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conexao.close()

    def fetchone(self, query, parametros=()):
        conexao = self._connect()
        try:
            cursor = conexao.execute(query, parametros)
            linha = cursor.fetchone()
            return dict(linha) if linha else None
        finally:
            conexao.close()

    def execute(self, query, parametros=()):
        conexao = self._connect()
        try:
            cursor = conexao.execute(query, parametros)
            conexao.commit()
            return cursor
        except Exception as e:
            conexao.rollback()
            raise e
        finally:
            # Não fechamos a conexão imediatamente se precisarmos ler do cursor,
            # mas como na transação commit() já foi executada, podemos fechar com segurança
            # e a maioria dos dados continuará acessível (como rowcount) no cursor do SQLite3.
            conexao.close()

