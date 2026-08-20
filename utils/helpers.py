# ============================================================================
# MÓDULO DE UTILITÁRIOS DIVERSOS
# Funções auxiliares gerais
# ============================================================================

from datetime import datetime


def formatar_data_br(data_str):
    """
    Formata data para formato brasileiro.
    
    Args:
        data_str (str): Data em formato ISO (YYYY-MM-DD)
        
    Returns:
        str: Data formatada (DD/MM/YYYY)
    """
    try:
        data = datetime.strptime(data_str, '%Y-%m-%d')
        return data.strftime('%d/%m/%Y')
    except:
        return data_str


def formatar_datetime_br(datetime_str):
    """
    Formata datetime para formato brasileiro.
    
    Args:
        datetime_str (str): DateTime em formato ISO
        
    Returns:
        str: DateTime formatado
    """
    try:
        data = datetime.fromisoformat(datetime_str)
        return data.strftime('%d/%m/%Y %H:%M')
    except:
        return datetime_str


def gerar_cor_gravidade(gravidade):
    """
    Retorna classe de cor baseada na gravidade.
    
    Args:
        gravidade (str): Nível de gravidade
        
    Returns:
        str: Classe CSS de cor
    """
    cores = {
        'Leve': 'badge-info',
        'Média': 'badge-warning',
        'Grave': 'badge-danger'
    }
    return cores.get(gravidade, 'badge-secondary')


def paginar_resultados(itens, pagina, itens_por_pagina=10):
    """
    Pagina resultados.
    
    Args:
        itens (list): Lista de itens
        pagina (int): Número da página (começa em 1)
        itens_por_pagina (int): Itens por página
        
    Returns:
        dict: Dados paginados
    """
    total_itens = len(itens)
    total_paginas = (total_itens + itens_por_pagina - 1) // itens_por_pagina
    
    # Validar número de página
    pagina = max(1, min(pagina, total_paginas)) if total_paginas > 0 else 1
    
    inicio = (pagina - 1) * itens_por_pagina
    fim = inicio + itens_por_pagina
    
    return {
        'itens': itens[inicio:fim],
        'pagina_atual': pagina,
        'total_paginas': total_paginas,
        'total_itens': total_itens,
        'itens_por_pagina': itens_por_pagina
    }
