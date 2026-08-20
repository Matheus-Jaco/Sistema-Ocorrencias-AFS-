# ============================================================================
# MÓDULO DE VALIDAÇÃO
# Funções para validação de entrada de dados
# ============================================================================

import re
from datetime import datetime


class Validador:
    """Classe responsável por validações de dados."""
    
    @staticmethod
    def validar_nome_aluno(nome):
        """
        Valida nome do aluno.
        
        Args:
            nome (str): Nome do aluno
            
        Returns:
            tuple: (é_válido, mensagem_erro)
        """
        if not nome or not nome.strip():
            return False, "Nome do aluno é obrigatório"
        
        if len(nome.strip()) < 3:
            return False, "Nome deve ter pelo menos 3 caracteres"
        
        if len(nome.strip()) > 100:
            return False, "Nome não pode exceder 100 caracteres"
        
        # Verificar se contém apenas letras, espaços e alguns caracteres
        if not re.match(r"^[a-záàâãéèêíïóôõöúçñ\s'-]+$", nome, re.IGNORECASE):
            return False, "Nome contém caracteres inválidos"
        
        return True, ""
    
    @staticmethod
    def validar_curso(curso):
        """
        Valida curso.
        
        Args:
            curso (str): Curso do aluno
            
        Returns:
            tuple: (é_válido, mensagem_erro)
        """
        cursos_validos = ['Administração', 'Logística', 'Enfermagem', 'Informática', 'Desenvolvimento de Sistemas']
        
        if not curso or curso not in cursos_validos:
            return False, f"Curso inválido. Cursos válidos: {', '.join(cursos_validos)}"
        
        return True, ""
    
    @staticmethod
    def validar_ano(ano):
        """
        Valida ano.
        
        Args:
            ano (str): Ano do aluno
            
        Returns:
            tuple: (é_válido, mensagem_erro)
        """
        anos_validos = ['1º', '2º', '3º', '1º Ano', '2º Ano', '3º Ano']
        
        if not ano or ano not in anos_validos:
            return False, f"Ano inválido. Anos válidos: {', '.join(anos_validos)}"
        
        return True, ""
    
    @staticmethod
    def validar_data(data_str):
        """
        Valida data.
        
        Args:
            data_str (str): Data em formato 'YYYY-MM-DD'
            
        Returns:
            tuple: (é_válido, mensagem_erro)
        """
        if not data_str:
            return False, "Data é obrigatória"
        
        try:
            data = datetime.strptime(data_str, '%Y-%m-%d')
            
            # Validar se a data não é futura
            if data > datetime.now():
                return False, "A data não pode ser no futuro"
            
            return True, ""
        except ValueError:
            return False, "Formato de data inválido (use YYYY-MM-DD)"
    
    @staticmethod
    def validar_descricao(descricao):
        """
        Valida descrição da ocorrência.
        
        Args:
            descricao (str): Descrição da ocorrência
            
        Returns:
            tuple: (é_válido, mensagem_erro)
        """
        if not descricao or not descricao.strip():
            return False, "Descrição é obrigatória"
        
        if len(descricao.strip()) < 10:
            return False, "Descrição deve ter pelo menos 10 caracteres"
        
        if len(descricao.strip()) > 1000:
            return False, "Descrição não pode exceder 1000 caracteres"
        
        return True, ""
    
    @staticmethod
    def validar_gravidade(gravidade):
        """
        Valida gravidade da ocorrência.
        
        Args:
            gravidade (str): Gravidade da ocorrência
            
        Returns:
            tuple: (é_válido, mensagem_erro)
        """
        gravidades_validas = ['Leve', 'Média', 'Grave']
        
        if not gravidade or gravidade not in gravidades_validas:
            return False, f"Gravidade inválida. Gravidades válidas: {', '.join(gravidades_validas)}"
        
        return True, ""

    @staticmethod
    def validar_matricula(matricula):
        if not matricula or not matricula.strip():
            return False, "Matrícula é obrigatória"
        matricula = matricula.strip()
        if len(matricula) < 4 or len(matricula) > 30:
            return False, "Matrícula inválida"
        if not re.match(r"^[A-Za-z0-9\-_.]+$", matricula):
            return False, "Matrícula contém caracteres inválidos"
        return True, ""

    @staticmethod
    def validar_cep(cep):
        if not cep or not cep.strip():
            return False, "CEP é obrigatório"
        cep = re.sub(r"\D", "", cep)
        if not re.match(r"^\d{8}$", cep):
            return False, "CEP inválido"
        return True, ""

    @staticmethod
    def validar_telefone(telefone, obrigatório=False):
        if not telefone or not telefone.strip():
            return (False, "Telefone é obrigatório") if obrigatório else (True, "")
        t = re.sub(r"\D", "", telefone)
        if len(t) < 8 or len(t) > 11:
            return False, "Telefone inválido"
        return True, ""

    @staticmethod
    def validar_data_nascimento(data_str):
        if not data_str or not data_str.strip():
            return False, "Data de nascimento é obrigatória"
        try:
            data = datetime.strptime(data_str, '%Y-%m-%d')
            if data > datetime.now():
                return False, "Data de nascimento não pode ser no futuro"
            return True, ""
        except ValueError:
            return False, "Formato de data inválido (use YYYY-MM-DD)"

    @staticmethod
    def validar_genero(sexo):
        op = ['Masculino', 'Feminino', 'Outro']
        if not sexo or sexo not in op:
            return False, f"Sexo inválido. Opções: {', '.join(op)}"
        return True, ""

    @staticmethod
    def validar_responsavel(dados):
        nome = dados.get('nome', '')
        grau = dados.get('grau', '')
        celular = dados.get('celular', '')
        if not nome or not nome.strip():
            return False, 'Nome do responsável é obrigatório'
        if not grau or not grau.strip():
            return False, 'Grau de parentesco é obrigatório'
        ok, msg = Validador.validar_telefone(celular, obrigatório=False)
        if not ok:
            return False, msg
        return True, ''


def sanitizar_input(texto):
    """
    Sanitiza entrada de texto removendo espaços extras.
    
    Args:
        texto (str): Texto a sanitizar
        
    Returns:
        str: Texto sanitizado
    """
    if isinstance(texto, str):
        return texto.strip()
    return texto
