// SCRIPT DE OCORRÊNCIAS
// Funções específicas para gerenciamento de ocorrências

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar event listeners
    inicializarEventListeners();
});

/**
 * Inicializa todos os event listeners
 */
function inicializarEventListeners() {
    // Botões de delete de ocorrência
    const botoesDelete = document.querySelectorAll('.delete-btn');
    botoesDelete.forEach(btn => {
        btn.addEventListener('click', function() {
            abrirModalConfirmacao(this.dataset.id);
        });
    });
    
    // Botões de delete de aluno
    const botoesDeleteAluno = document.querySelectorAll('.delete-aluno-btn');
    botoesDeleteAluno.forEach(btn => {
        btn.addEventListener('click', function() {
            abrirModalConfirmacaoDeleteAluno(this.dataset.alunoId);
        });
    });
    
    // Filtros em tempo real
    const formFiltros = document.getElementById('formFiltros');
    if (formFiltros) {
        const inputs = formFiltros.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('change', debounce(function() {
                aplicarFiltros();
            }, 300));
        });
    }
}

/**
 * Abre modal de confirmação de exclusão
 * @param {string} ocorrenciaId - ID da ocorrência
 */
function abrirModalConfirmacao(ocorrenciaId) {
    showConfirmation(
        'Deletar Ocorrência',
        'Tem certeza que deseja deletar esta ocorrência? Esta ação não pode ser desfeita.',
        () => deletarOcorrencia(ocorrenciaId)
    );
}

/**
 * Deleta uma ocorrência via API
 * @param {string} ocorrenciaId - ID da ocorrência
 */
async function deletarOcorrencia(ocorrenciaId) {
    const loader = showLoading('Deletando ocorrência...');
    
    try {
        const response = await fetch(`/ocorrencias/api/${ocorrenciaId}/deletar`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        hideLoading();
        
        if (data.sucesso) {
            showNotification(data.mensagem, 'success', 2000);
            setTimeout(() => {
                location.reload();
            }, 2000);
        } else {
            showNotification(data.mensagem, 'error');
        }
    } catch (error) {
        hideLoading();
        showNotification('Erro ao deletar ocorrência', 'error');
        console.error('Erro:', error);
    }
}

/**
 * Abre modal de confirmação para deletar ocorrências do aluno
 * @param {string} alunoId - ID do aluno
 */
function abrirModalConfirmacaoDeleteAluno(alunoId) {
    showConfirmation(
        'Deletar Ocorrências',
        'Tem certeza que deseja deletar TODAS as ocorrências deste aluno? Esta ação não pode ser desfeita.',
        () => deletarOcorrenciasDoAluno(alunoId)
    );
}

/**
 * Deleta todas as ocorrências de um aluno
 * @param {string} alunoId - ID do aluno
 */
async function deletarOcorrenciasDoAluno(alunoId) {
    const loader = showLoading('Deletando ocorrências do aluno...');
    
    try {
        // Encontrar o botão de deletar para obter os IDs das ocorrências
        const botaoDelete = document.querySelector(`button[data-aluno-id="${alunoId}"].delete-aluno-btn`);
        
        if (!botaoDelete) {
            hideLoading();
            showNotification('Erro: botão de deletar não encontrado', 'error');
            return;
        }
        
        // Obter IDs das ocorrências do atributo data
        const ocorrenciaIdsStr = botaoDelete.getAttribute('data-ocorrencia-ids');
        
        if (!ocorrenciaIdsStr || ocorrenciaIdsStr.trim() === '') {
            hideLoading();
            showNotification('Nenhuma ocorrência encontrada para deletar', 'warning');
            return;
        }
        
        const ocorrenciaIds = ocorrenciaIdsStr.split(',').filter(id => id.trim() !== '');
        
        if (ocorrenciaIds.length === 0) {
            hideLoading();
            showNotification('Nenhuma ocorrência encontrada para deletar', 'warning');
            return;
        }
        
        // Deletar cada ocorrência sequencialmente
        let deletadas = 0;
        for (const ocorrenciaId of ocorrenciaIds) {
            const response = await fetch(`/ocorrencias/api/${ocorrenciaId.trim()}/deletar`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.sucesso) {
                    deletadas++;
                }
            }
        }
        
        hideLoading();
        
        if (deletadas > 0) {
            showNotification(`${deletadas} ocorrência(s) deletada(s) com sucesso!`, 'success', 2000);
            setTimeout(() => {
                location.reload();
            }, 2000);
        } else {
            showNotification('Erro ao deletar ocorrências', 'error');
        }
    } catch (error) {
        hideLoading();
        showNotification('Erro ao deletar ocorrências do aluno', 'error');
        console.error('Erro:', error);
    }
}

/**
 * Aplica filtros e recarrega página
 */
function aplicarFiltros() {
    const formFiltros = document.getElementById('formFiltros');
    if (!formFiltros) return;
    
    const formData = new FormData(formFiltros);
    const params = new URLSearchParams();
    
    formData.forEach((value, key) => {
        if (value) {
            params.append(key, value);
        }
    });
    
    // Recarregar com novos parâmetros
    const url = new URL(window.location);
    url.search = params.toString();
    window.history.pushState({}, '', url);
    location.reload();
}

/**
 * Exporta ocorrências para CSV
 */
function exportarOcorrencias() {
    showNotification('Funcionalidade em desenvolvimento', 'info');
}

/**
 * Imprime ocorrência
 * @param {string} ocorrenciaId - ID da ocorrência
 */
function imprimirOcorrencia(ocorrenciaId) {
    const printWindow = window.open(`/ocorrencias/${ocorrenciaId}`, '_blank');
    printWindow.addEventListener('load', function() {
        printWindow.print();
    });
}

/**
 * Valida formulário de ocorrência
 * @returns {boolean}
 */
function validarFormularioOcorrencia() {
    const form = document.getElementById('formOcorrencia');
    if (!form) return true;
    
    const campos = {
        nome_aluno: 'Nome do aluno',
        curso: 'Curso',
        ano: 'Ano',
        data_ocorrencia: 'Data da ocorrência',
        descricao: 'Descrição',
        gravidade: 'Gravidade'
    };
    
    for (let [campo, label] of Object.entries(campos)) {
        const input = form.elements[campo];
        if (!input || !input.value.trim()) {
            showNotification(`${label} é obrigatório`, 'warning');
            input?.focus();
            return false;
        }
    }
    
    return true;
}

/**
 * Formata dados de ocorrência para exibição
 * @param {object} ocorrencia - Objeto da ocorrência
 * @returns {object}
 */
function formatarOcorrencia(ocorrencia) {
    return {
        ...ocorrencia,
        data_ocorrencia_formatada: formatarDataBR(ocorrencia.data_ocorrencia),
        gravidade_classe: obterClasseGravidade(ocorrencia.gravidade)
    };
}

/**
 * Obtém classe CSS para gravidade
 * @param {string} gravidade - Nível de gravidade
 * @returns {string}
 */
function obterClasseGravidade(gravidade) {
    const classes = {
        'Leve': 'bg-green-100 text-green-800',
        'Média': 'bg-yellow-100 text-yellow-800',
        'Grave': 'bg-red-100 text-red-800'
    };
    
    return classes[gravidade] || 'bg-gray-100 text-gray-800';
}

/**
 * Obtém classe de ícone para gravidade
 * @param {string} gravidade - Nível de gravidade
 * @returns {string}
 */
function obterIconeGravidade(gravidade) {
    const icones = {
        'Leve': 'fa-check-circle',
        'Média': 'fa-exclamation-circle',
        'Grave': 'fa-times-circle'
    };
    
    return icones[gravidade] || 'fa-question-circle';
}
