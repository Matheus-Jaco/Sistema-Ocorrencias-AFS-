// UTILIDADES GERAIS

/**
 * Formata data para formato brasileiro
 * @param {string} data - Data em formato ISO
 * @returns {string} - Data formatada
 */
function formatarDataBR(data) {
    const d = new Date(data + 'T00:00:00');
    return d.toLocaleDateString('pt-BR');
}

/**
 * Debounce para funções
 * @param {function} func - Função a executar
 * @param {number} wait - Tempo de espera em ms
 * @returns {function}
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle para funções
 * @param {function} func - Função a executar
 * @param {number} limit - Limite em ms
 * @returns {function}
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Fetch com tratamento de erros
 * @param {string} url - URL
 * @param {object} options - Opções do fetch
 * @returns {Promise}
 */
async function fetchAPI(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Erro na requisição:', error);
        showNotification('Erro ao processar requisição', 'error');
        throw error;
    }
}

/**
 * Valida email
 * @param {string} email - Email
 * @returns {boolean}
 */
function validarEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

/**
 * Valida CPF
 * @param {string} cpf - CPF
 * @returns {boolean}
 */
function validarCPF(cpf) {
    const limpo = cpf.replace(/\D/g, '');
    if (limpo.length !== 11) return false;
    
    let soma = 0;
    for (let i = 0; i < 9; i++) {
        soma += parseInt(limpo[i]) * (10 - i);
    }
    
    let resto = soma % 11;
    const dv1 = resto < 2 ? 0 : 11 - resto;
    
    soma = 0;
    for (let i = 0; i < 10; i++) {
        soma += parseInt(limpo[i]) * (11 - i);
    }
    
    resto = soma % 11;
    const dv2 = resto < 2 ? 0 : 11 - resto;
    
    return parseInt(limpo[9]) === dv1 && parseInt(limpo[10]) === dv2;
}

/**
 * Sanitiza texto removendo tags HTML
 * @param {string} texto - Texto
 * @returns {string}
 */
function sanitizarTexto(texto) {
    const div = document.createElement('div');
    div.textContent = texto;
    return div.innerHTML;
}

/**
 * Copia texto para área de transferência
 * @param {string} texto - Texto a copiar
 */
async function copiarParaClipboard(texto) {
    try {
        await navigator.clipboard.writeText(texto);
        showNotification('Copiado para área de transferência!', 'success', 2000);
    } catch {
        showNotification('Erro ao copiar', 'error');
    }
}

/**
 * Exporta dados para CSV
 * @param {array} dados - Array de objetos
 * @param {string} nomeArquivo - Nome do arquivo
 */
function exportarCSV(dados, nomeArquivo = 'export.csv') {
    if (!dados || dados.length === 0) {
        showNotification('Nenhum dado para exportar', 'warning');
        return;
    }
    
    const chaves = Object.keys(dados[0]);
    const csv = [
        chaves.join(','),
        ...dados.map(obj => chaves.map(chave => {
            const valor = obj[chave];
            return typeof valor === 'string' && valor.includes(',') 
                ? `"${valor}"` 
                : valor;
        }).join(','))
    ].join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = nomeArquivo;
    link.click();
}

/**
 * Formata valores monetários
 * @param {number} valor - Valor
 * @returns {string}
 */
function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}

/**
 * Formata números com separadores
 * @param {number} numero - Número
 * @returns {string}
 */
function formatarNumero(numero) {
    return numero.toLocaleString('pt-BR');
}

/**
 * Calcula tempo decorrido (ex: há 2 horas)
 * @param {string} data - Data ISO
 * @returns {string}
 */
function tempoDecorrido(data) {
    const agora = new Date();
    const dataObj = new Date(data);
    const diferenca = agora - dataObj;
    const segundos = Math.floor(diferenca / 1000);
    
    if (segundos < 60) return 'agora mesmo';
    if (segundos < 3600) return `há ${Math.floor(segundos / 60)} minuto(s)`;
    if (segundos < 86400) return `há ${Math.floor(segundos / 3600)} hora(s)`;
    if (segundos < 604800) return `há ${Math.floor(segundos / 86400)} dia(s)`;
    
    return formatarDataBR(data);
}
