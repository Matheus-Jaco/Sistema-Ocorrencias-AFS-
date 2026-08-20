# 👨‍💻 GUIA DE DESENVOLVIMENTO - Sistema de Ocorrências AFS

## Arquitetura MVC + Blueprints

```
REQUEST → ROUTE (Blueprint) → SERVICE (Lógica) → UTILS (Validação) → DB (JSON)
                ↓
              TEMPLATE (Jinja2) ou JSON
```

---

## 📁 Onde Adicionar Funcionalidades

### 1. Nova Rota
**Arquivo:** `routes/ocorrencias.py`

```python
from flask import Blueprint, render_template, request
ocorrencias_bp = Blueprint('ocorrencias', __name__, url_prefix='/ocorrencias')

@ocorrencias_bp.route('/nova-funcao', methods=['GET', 'POST'])
def nova_funcao():
    # Sua lógica aqui
    pass
```

### 2. Nova Validação
**Arquivo:** `utils/validators.py`

```python
class Validador:
    @staticmethod
    def validar_novo_campo(valor):
        """Valida novo campo"""
        if not valor:
            return False, "Campo obrigatório"
        return True, ""
```

### 3. Novo Serviço
**Arquivo:** `services/ocorrencias_service.py`

```python
def nova_operacao(self, dados):
    """Descrição da nova operação"""
    try:
        # Lógica aqui
        logger.info('Operação realizada')
        return {'sucesso': True, 'mensagem': 'OK'}
    except Exception as e:
        logger.error(f'Erro: {e}')
        return {'sucesso': False, 'mensagem': str(e)}
```

### 4. Novo Template
**Arquivo:** `templates/novo_template.html`

```html
{% extends 'base.html' %}

{% block title %}Novo Template{% endblock %}

{% block content %}
<!-- HTML aqui -->
{% endblock %}
```

---

## 🔄 Fluxo de Criação de Funcionalidade

### Exemplo: Adicionar Campo "Testemunhas"

#### Passo 1: Atualizar Validador
```python
# utils/validators.py
def validar_testemunhas(testemunhas):
    if len(testemunhas) > 300:
        return False, "Máximo 300 caracteres"
    return True, ""
```

#### Passo 2: Atualizar Serviço
```python
# services/ocorrencias_service.py
def criar_ocorrencia(self, dados):
    # ... validações existentes ...
    
    # Nova validação
    valido, msg = self.validador.validar_testemunhas(dados.get('testemunhas', ''))
    if not valido:
        return {'sucesso': False, 'mensagem': msg}
    
    # Adicionar ao objeto
    ocorrencia['testemunhas'] = dados.get('testemunhas', '')
    # ...
```

#### Passo 3: Atualizar Template
```html
<!-- templates/ocorrencias/criar.html -->
<div>
    <label>Testemunhas</label>
    <textarea name="testemunhas" maxlength="300"></textarea>
</div>
```

#### Passo 4: Atualizar Listagem
```html
<!-- templates/ocorrencias/listar.html -->
<th>Testemunhas</th>
<!-- ... -->
<td>{{ ocorrencia.testemunhas }}</td>
```

---

## 🔗 APIs e Endpoints

### Para Adicionar Novo Endpoint

#### 1. Backend
```python
# routes/ocorrencias.py
@ocorrencias_bp.route('/api/novo-endpoint', methods=['GET', 'POST'])
def novo_endpoint():
    try:
        servico = ServicoOcorrencias(current_app.config['DATA_PATH'])
        resultado = servico.nova_operacao()
        return jsonify(resultado), 200
    except Exception as e:
        logger.error(f'Erro: {e}')
        return jsonify({'erro': str(e)}), 500
```

#### 2. Frontend
```javascript
// static/js/ocorrencias.js
async function novaOperacao() {
    try {
        const response = await fetch('/ocorrencias/api/novo-endpoint', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        const data = await response.json();
        showNotification(data.mensagem, 'success');
    } catch (error) {
        showNotification('Erro ao processar', 'error');
    }
}
```

---

## 🎨 Padrões de Código

### Logs
```python
from utils.logger import get_logger
logger = get_logger(__name__)

logger.debug('Mensagem de debug')
logger.info('Informação importante')
logger.warning('Aviso')
logger.error('Erro crítico')
```

### Retorno de Função de Serviço
```python
return {
    'sucesso': True/False,
    'mensagem': 'Descrição clara',
    'dados': {} ou None,
    'campo': 'campo com erro' (opcional)
}
```

### Validação
```python
valido, mensagem = self.validador.validar_campo(valor)
if not valido:
    logger.warning(f'Validação falhou: {mensagem}')
    return {'sucesso': False, 'mensagem': mensagem}
```

---

## 📦 Adicionar Dependência

### 1. Instalar
```bash
pip install novo-pacote
```

### 2. Adicionar ao requirements.txt
```
novo-pacote==1.0.0
```

### 3. Usar no Código
```python
import novo_pacote
novo_pacote.funcao()
```

---

## 🗄️ Migrar para Banco de Dados

### Estrutura Preparada

```python
# 1. Criar arquivo novo
# database/db.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Ocorrencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_aluno = db.Column(db.String(100), nullable=False)
    # ... demais campos

# 2. Atualizar app.py
from database.db import db
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/db'
db.init_app(app)

# 3. Usar em services/ocorrencias_service.py
ocorrencias = Ocorrencia.query.all()
```

---

## 🔐 Adicionar Autenticação

### 1. Instalar Flask-Login
```bash
pip install flask-login flask-wtf
```

### 2. Criar modelo de Usuário
```python
# database/models.py
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
```

### 3. Proteger Rotas
```python
from flask_login import login_required

@ocorrencias_bp.route('/')
@login_required
def listar():
    # Apenas usuários logados
    pass
```

---

## 🧪 Testes

### Adicionar Testes
```python
# tests/test_ocorrencias.py
import unittest
from app import create_app

class TestOcorrencias(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
    
    def test_dashboard(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
```

---

## 📊 Performance

### Otimizações Sugeridas

1. **Cache** - Redis para estatísticas
2. **Índices** - No banco de dados (após migração)
3. **Paginação** - Aumentar limite conforme necessário
4. **Lazy Loading** - Carregar dados sob demanda
5. **Compressão** - Gzip para respostas HTTP

---

## 🚀 Deploy para Produção

### Substituir Debug Mode
```python
# app.py
if __name__ == '__main__':
    app.run(
        debug=False,  # ← Mudar para False
        host='0.0.0.0',
        port=5000
    )
```

### Usar WSGI Production
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Variáveis de Ambiente
```python
import os
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite')
```

---

## 📝 Documentação de Código

### Padrão de Docstring
```python
def funcao(parametro):
    """
    Descrição breve em uma linha.
    
    Descrição detalhada se necessário.
    
    Args:
        parametro (tipo): Descrição do parâmetro
        
    Returns:
        dict: {'sucesso': bool, 'mensagem': str}
        
    Raises:
        ValueError: Se parametro inválido
    """
    pass
```

---

## 🐛 Debugging

### Usar Debugger Flask
```python
from flask import current_app

@app.route('/debug')
def debug():
    current_app.logger.debug('Mensagem de debug')
    breakpoint()  # Parar aqui no debugger
    return 'OK'
```

### Inspecionar Logs
```bash
tail -f logs/sistema.log
```

---

## 📚 Recursos Úteis

- [Flask Docs](https://flask.palletsprojects.com/)
- [Jinja2 Templates](https://jinja.palletsprojects.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Flask Blueprints](https://flask.palletsprojects.com/blueprints/)

---

## ✅ Checklist para Novas Features

- [ ] Criar validação em `utils/validators.py`
- [ ] Implementar lógica em `services/ocorrencias_service.py`
- [ ] Adicionar rota em `routes/ocorrencias.py`
- [ ] Criar/atualizar template em `templates/`
- [ ] Adicionar scripts em `static/js/`
- [ ] Escrever testes
- [ ] Atualizar documentação
- [ ] Testar em todos os tamanhos de tela
- [ ] Testar validações
- [ ] Revisar logs

---

## 🎯 Próximas Melhorias de Desenvolvimento

1. **Testes Automatizados** - Adicionar suite de testes
2. **CI/CD** - GitHub Actions para deploy automático
3. **Dockerização** - Container para deploy fácil
4. **API GraphQL** - Alternativa REST
5. **Websockets** - Notificações em tempo real
6. **Caching** - Redis para performance
7. **Monitoramento** - Sentry para erros
8. **Analytics** - Análise de uso do sistema

---

Boa sorte desenvolvendo! 🚀
