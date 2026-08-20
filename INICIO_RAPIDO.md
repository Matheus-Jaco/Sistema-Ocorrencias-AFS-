# 🚀 INÍCIO RÁPIDO - Sistema de Ocorrências Escolares AFS

## ⚡ Em 3 passos você está rodando:

### 1️⃣ Instalar Dependências (primeira vez)
```bash
pip install -r requirements.txt
```

### 2️⃣ Iniciar o Servidor
```bash
python app.py
```

### 3️⃣ Acessar no Navegador
```
http://localhost:5000
```

---

## 📍 URLs Principais

| URL | Função |
|-----|--------|
| `http://localhost:5000/` | Dashboard |
| `http://localhost:5000/ocorrencias/` | Listar ocorrências |
| `http://localhost:5000/ocorrencias/criar` | Criar nova ocorrência |

---

## 🎯 Primeira Vez Usando

1. Acesse o **Dashboard** para ver estatísticas
2. Clique em **"Nova Ocorrência"** para cadastrar
3. Preencha o formulário com os dados
4. Clique em **"Registrar Ocorrência"**
5. Veja na listagem de **Ocorrências**
6. Use **filtros** para buscar rapidamente

---

## 📋 O Que Fazer em Cada Página

### Dashboard
- Visualizar **total de ocorrências**
- Ver **contagem por gravidade**
- Verificar **distribuição por curso/ano**
- Clicar em **"Registrar Nova Ocorrência"**

### Criar Ocorrência
- Preencher **nome do aluno**
- Selecionar **curso** (Informática, Eletrônica, Mecânica, Administração)
- Selecionar **ano** (1º, 2º, 3º)
- Escolher **data da ocorrência**
- Escrever **descrição detalhada**
- Escolher **gravidade** (Leve, Média, Grave)
- Adicionar **observações** (opcional)
- Clicar **"Registrar Ocorrência"**

### Listagem de Ocorrências
- **Buscar** por nome do aluno
- **Filtrar** por curso, ano, gravidade
- Clicar em **ícone olho** para ver detalhes
- Clicar em **ícone lápis** para editar
- Clicar em **ícone lixeira** para deletar

### Detalhes
- Ver **todas as informações** do registro
- Clicar **"Editar"** para modificar
- Clicar **"Deletar"** para remover

### Editar
- Modificar **nome do aluno, descrição, gravidade**
- Clicar **"Salvar Alterações"**
- Outros campos **não podem ser alterados** (data, curso, ano)

---

## ✨ Recursos Disponíveis

✅ **Dashboard com estatísticas**  
✅ **Cadastro de ocorrências com validação**  
✅ **Listagem com filtros avançados**  
✅ **Busca em tempo real**  
✅ **Visualização completa de cada registro**  
✅ **Edição de dados**  
✅ **Exclusão segura com confirmação**  
✅ **Persistência em arquivo JSON**  
✅ **Design responsivo (mobile, tablet, desktop)**  
✅ **Notificações elegantes**  

---

## 🔧 Troubleshooting Rápido

### Porta 5000 já em uso?
```bash
# Windows - Parar processo na porta 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Dependências não instaladas?
```bash
pip install -r requirements.txt
```

### Arquivo JSON desapareceu?
- Será recriado automaticamente na próxima execução

### Esqueceu a senha?
- Este sistema não possui autenticação (adicione depois)

---

## 💡 Dicas de Uso

1. **Backup regular** - Copie `data/ocorrencias.json` regularmente
2. **Filtros** - Use combine de filtros para buscas precisas
3. **Observações** - Use para anotações adicionais importantes
4. **Edição** - Alguns campos não podem ser alterados por integridade
5. **Exclusão** - Confirmação obrigatória para segurança

---

## 📞 Informações

- **Servidor:** http://localhost:5000
- **Banco de Dados:** data/ocorrencias.json
- **Logs:** logs/sistema.log
- **Versão:** 1.0.0

---

## 🎉 Pronto!

Seu sistema está funcionando perfeitamente!

**Aproveite! 🚀**
