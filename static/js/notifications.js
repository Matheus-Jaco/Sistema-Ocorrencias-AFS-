// SISTEMA DE NOTIFICAÇÕES (TOAST)
/**
 * Exibe uma notificação (toast) na tela
 * @param {string} mensagem - Mensagem a exibir
 * @param {string} tipo - Tipo: 'success', 'error', 'warning', 'info'
 * @param {number} duracao - Duração em ms (0 = sem auto-close)
 */
function showNotification(mensagem, tipo = 'info', duracao = 4000) {
    const container = document.getElementById('toastContainer');
    
    // Cores por tipo
    const cores = {
        success: { bg: 'bg-green-500', icon: 'fa-check-circle' },
        error: { bg: 'bg-red-500', icon: 'fa-exclamation-circle' },
        warning: { bg: 'bg-yellow-500', icon: 'fa-warning' },
        info: { bg: 'bg-blue-500', icon: 'fa-info-circle' }
    };
    
    const config = cores[tipo] || cores.info;
    
    // Criar elemento
    const toast = document.createElement('div');
    toast.className = `${config.bg} text-white px-6 py-4 rounded-lg shadow-lg mb-3 animate-slide-in-down flex items-center gap-3 max-w-md`;
    toast.innerHTML = `
        <i class="fas ${config.icon}"></i>
        <span>${mensagem}</span>
        <button class="ml-auto text-lg hover:opacity-70" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(toast);
    
    // Auto-remover após duração
    if (duracao > 0) {
        setTimeout(() => {
            toast.style.animation = 'slideInUp 0.3s ease-out reverse';
            setTimeout(() => toast.remove(), 300);
        }, duracao);
    }
}

/**
 * Exibe um modal de confirmação
 * @param {string} titulo - Título do modal
 * @param {string} mensagem - Mensagem do modal
 * @param {function} callback - Função a executar ao confirmar
 */
function showConfirmation(titulo, mensagem, callback) {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 animate-fade-in';
    modal.innerHTML = `
        <div class="bg-white rounded-xl max-w-sm w-full p-6 animate-slide-in-down">
            <div class="flex items-center justify-center w-12 h-12 rounded-full bg-yellow-100 mx-auto mb-4">
                <i class="fas fa-exclamation text-yellow-600 text-xl"></i>
            </div>
            <h3 class="text-lg font-bold text-gray-900 text-center mb-2">${titulo}</h3>
            <p class="text-gray-600 text-center mb-6">${mensagem}</p>
            <div class="flex gap-3">
                <button type="button" 
                        class="flex-1 px-4 py-2 bg-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-300 transition-all"
                        onclick="this.closest('.fixed').remove()">
                    Cancelar
                </button>
                <button type="button" 
                        class="flex-1 px-4 py-2 bg-red-500 text-white font-medium rounded-lg hover:bg-red-600 transition-all"
                        id="btnConfirm">
                    Confirmar
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    document.getElementById('btnConfirm').addEventListener('click', () => {
        callback();
        modal.remove();
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
}

/**
 * Mostra loading spinner
 * @param {string} mensagem - Mensagem
 * @returns {HTMLElement} - Elemento do spinner
 */
function showLoading(mensagem = 'Carregando...') {
    const loader = document.createElement('div');
    loader.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    loader.innerHTML = `
        <div class="bg-white rounded-xl p-8 flex flex-col items-center gap-4">
            <div class="w-12 h-12 border-4 border-gray-200 border-t-green-500 rounded-full spinner"></div>
            <p class="text-gray-700 font-medium">${mensagem}</p>
        </div>
    `;
    
    document.body.appendChild(loader);
    return loader;
}

/**
 * Remove o loading spinner
 */
function hideLoading() {
    const loaders = document.querySelectorAll('.fixed');
    loaders.forEach(loader => {
        if (loader.innerHTML.includes('spinner')) {
            loader.remove();
        }
    });
}
