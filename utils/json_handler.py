# ============================================================================
# MÓDULO DE GERENCIAMENTO JSON
# Responsável por leitura e escrita de dados em JSON
# ============================================================================

import json
import os
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)


class GerenciadorJSON:
    """Gerenciador de persistência de dados em JSON."""
    
    def __init__(self, caminho_arquivo):
        """
        Inicializa o gerenciador.
        
        Args:
            caminho_arquivo (str): Caminho do arquivo JSON
        """
        self.caminho_arquivo = caminho_arquivo
        self._garantir_arquivo_existe()
    
    def _garantir_arquivo_existe(self):
        """Garante que o arquivo JSON existe, criando se necessário."""
        if not os.path.exists(self.caminho_arquivo):
            os.makedirs(os.path.dirname(self.caminho_arquivo), exist_ok=True)
            self.escrever([])
            logger.info(f'Arquivo JSON criado: {self.caminho_arquivo}')
    
    def ler(self):
        """
        Lê todos os dados do arquivo JSON.
        
        Returns:
            list: Lista de ocorrências
        """
        try:
            with open(self.caminho_arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                logger.debug(f'Dados lidos: {len(dados)} ocorrências')
                return dados if isinstance(dados, list) else []
        except json.JSONDecodeError:
            logger.error('Erro ao decodificar JSON')
            return []
        except Exception as e:
            logger.error(f'Erro ao ler arquivo JSON: {e}')
            return []
    
    def escrever(self, dados):
        """
        Escreve dados no arquivo JSON.
        
        Args:
            dados (list): Dados a escrever
            
        Returns:
            bool: Sucesso da operação
        """
        try:
            with open(self.caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
            logger.debug(f'Dados escritos: {len(dados)} ocorrências')
            return True
        except Exception as e:
            logger.error(f'Erro ao escrever arquivo JSON: {e}')
            return False
    
    def obter_por_id(self, ocorrencia_id):
        """
        Obtém uma ocorrência pelo ID.
        
        Args:
            ocorrencia_id (str): ID da ocorrência
            
        Returns:
            dict: Ocorrência encontrada ou None
        """
        dados = self.ler()
        for ocorrencia in dados:
            if ocorrencia.get('id') == ocorrencia_id:
                return ocorrencia
        return None
    
    def adicionar(self, ocorrencia):
        """
        Adiciona nova ocorrência.
        
        Args:
            ocorrencia (dict): Dados da ocorrência
            
        Returns:
            dict: Ocorrência adicionada com ID
        """
        dados = self.ler()
        
        # Gerar ID único
        novo_id = str(int(datetime.now().timestamp() * 1000))
        ocorrencia['id'] = novo_id
        ocorrencia['data_criacao'] = datetime.now().isoformat()
        
        dados.append(ocorrencia)
        self.escrever(dados)
        
        logger.info(f'Ocorrência adicionada: {novo_id}')
        return ocorrencia
    
    def atualizar(self, ocorrencia_id, dados_atualizados):
        """
        Atualiza uma ocorrência existente.
        
        Args:
            ocorrencia_id (str): ID da ocorrência
            dados_atualizados (dict): Dados a atualizar
            
        Returns:
            dict: Ocorrência atualizada ou None
        """
        dados = self.ler()
        
        for i, ocorrencia in enumerate(dados):
            if ocorrencia.get('id') == ocorrencia_id:
                ocorrencia.update(dados_atualizados)
                ocorrencia['data_atualizacao'] = datetime.now().isoformat()
                dados[i] = ocorrencia
                self.escrever(dados)
                logger.info(f'Ocorrência atualizada: {ocorrencia_id}')
                return ocorrencia
        
        logger.warning(f'Ocorrência não encontrada para atualização: {ocorrencia_id}')
        return None
    
    def deletar(self, ocorrencia_id):
        """
        Deleta uma ocorrência.
        
        Args:
            ocorrencia_id (str): ID da ocorrência
            
        Returns:
            bool: Sucesso da operação
        """
        dados = self.ler()
        
        dados_filtrados = [o for o in dados if o.get('id') != ocorrencia_id]
        
        if len(dados) == len(dados_filtrados):
            logger.warning(f'Ocorrência não encontrada para exclusão: {ocorrencia_id}')
            return False
        
        self.escrever(dados_filtrados)
        logger.info(f'Ocorrência deletada: {ocorrencia_id}')
        return True
