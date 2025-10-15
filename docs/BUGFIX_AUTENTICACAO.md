# 🔧 Correção de Bug - Autenticação de Usuários

**Data:** 14/10/2025 21:41  
**Status:** ✅ CORRIGIDO

---

## 🐛 **Problema Encontrado**

### Sintoma:
- Usuário cadastrado através da aba "Usuários"
- Login com credenciais corretas retornava "Senha incorreta"
- Sistema criava usuário mas não conseguia autenticar

### Causa Raiz:
**Inconsistência nos nomes dos campos de senha:**

#### Na criação de usuário (`POST /api/usuarios`):
```python
db["usuarios"][user_id] = {
    "nome": nome,
    "senha_hash": generate_password_hash(senha),  # ❌ ERRADO
    ...
}
```

#### Na autenticação (`/login`):
```python
if check_password_hash(usuario.get('password_hash', ''), password):  # ✅ CORRETO
    # Login bem-sucedido
```

**Resultado:** Sistema criava `senha_hash` mas procurava `password_hash` → Autenticação sempre falhava!

---

## ✅ **Solução Implementada**

### 1. **Correção no Código (app.py)**

#### Criação de usuário (linha ~2115):
```python
# ANTES (ERRADO):
"senha_hash": generate_password_hash(senha)

# DEPOIS (CORRETO):
"password_hash": generate_password_hash(senha)
```

#### Edição de senha (linha ~2167):
```python
# ANTES (ERRADO):
usuario['senha_hash'] = generate_password_hash(data['senha'])

# DEPOIS (CORRETO):
usuario['password_hash'] = generate_password_hash(data['senha'])
```

#### Campo 'id' adicionado:
```python
db["usuarios"][user_id] = {
    "id": user_id,  # ✅ NOVO - Para compatibilidade com load_user()
    "nome": nome,
    "password_hash": generate_password_hash(senha),
    ...
}
```

### 2. **Migração de Dados Existentes**

Criado script: `fix_password_field.py`

**O que faz:**
1. ✅ Cria backup automático do `db.json`
2. ✅ Converte `senha_hash` → `password_hash` em todos usuários
3. ✅ Adiciona campo `id` se não existir
4. ✅ Lista todos os usuários corrigidos

**Execução:**
```bash
python3 fix_password_field.py
```

**Resultado:**
```
✅ Backup criado: data/db_backup_fix_password_20251014_214118.json
🔧 Corrigido usuário: douglassilva
➕ Adicionado campo 'id' para: douglassilva

✅ Total de usuários corrigidos: 1
```

---

## 🧪 **Testes Realizados**

### Antes da Correção:
```
1. Cadastrar usuário "douglassilva"
   ✅ POST /api/usuarios → 200 (criação OK)

2. Login com douglassilva/senha123
   ❌ POST /login → 200 mas retorna página de login
   ❌ Mensagem: "Senha incorreta"
```

### Depois da Correção:
```
1. Usuário existente migrado automaticamente
   ✅ senha_hash → password_hash

2. Login com douglassilva/senha123
   ✅ POST /login → 302 (redirect)
   ✅ Autenticação bem-sucedida
   ✅ Acesso ao sistema liberado
```

---

## 📋 **Checklist de Verificação**

Para garantir que a correção está funcionando:

- [x] Script de migração executado
- [x] Backup criado (`db_backup_fix_password_*.json`)
- [x] Campo `password_hash` presente em todos usuários
- [x] Campo `id` presente em todos usuários
- [x] Container reconstruído com código corrigido
- [x] Login de usuários existentes funcionando
- [x] Criação de novos usuários gerando `password_hash` correto

---

## 🔄 **Processo de Correção**

```bash
# 1. Corrigir código fonte (app.py)
#    - Substituir "senha_hash" por "password_hash"
#    - Adicionar campo "id" na criação

# 2. Migrar dados existentes
cd /mnt/f/rodizio
python3 fix_password_field.py

# 3. Reconstruir container
docker-compose down
docker-compose up -d --build

# 4. Verificar logs
docker logs rodizio-organistas --tail 20

# 5. Testar login
#    Acessar: http://localhost:8080
#    Login com usuários existentes
```

---

## 📊 **Impacto da Correção**

### ✅ **Problemas Resolvidos:**
1. Autenticação de usuários criados via interface funciona
2. Consistência nos nomes dos campos em todo código
3. Retrocompatibilidade mantida (script de migração)
4. Novos usuários já criados corretamente

### 🔒 **Segurança Mantida:**
- Hash de senha permanece usando `scrypt` (Werkzeug)
- Nenhuma senha em texto plano
- Backups automáticos antes de modificar dados
- Validações de permissão mantidas

---

## 🎯 **Como Testar Agora**

### Teste 1: Criar Novo Usuário
```
1. Login: admin_master / admin123
2. Aba "Usuários"
3. ➕ Novo Usuário
   - ID: teste_novo
   - Nome: Teste Novo
   - Tipo: Encarregado de Comum
   - Contexto: GRU › Santa Isabel › Vila Paula
   - Senha: (deixar vazio = senha123)
4. Criar
5. Logout
6. Login: teste_novo / senha123
   ✅ Deve funcionar!
```

### Teste 2: Usuário Existente Migrado
```
1. Login: douglassilva / senha123
   ✅ Deve funcionar (após migração)
```

### Teste 3: Admin Master
```
1. Login: admin_master / admin123
   ✅ Sempre funcionou (não foi afetado)
```

---

## 🗂️ **Arquivos Modificados**

### Código:
- ✅ `app.py` (linhas ~2115, ~2167)
  - Criação de usuário
  - Edição de senha

### Scripts:
- ✅ `fix_password_field.py` (novo)
  - Migração de dados

### Banco de Dados:
- ✅ `data/db.json` (migrado)
  - Usuários com `password_hash` correto
- ✅ `data/db_backup_fix_password_*.json` (backup)

---

## 💡 **Lição Aprendida**

### Problema:
- **Falta de padrão nos nomes de campos** entre criação e leitura
- Sistema criava um campo mas procurava outro

### Prevenção Futura:
1. ✅ Usar constantes para nomes de campos:
   ```python
   PASSWORD_FIELD = "password_hash"
   ```
2. ✅ Validar schema ao salvar/carregar
3. ✅ Testes automatizados de autenticação
4. ✅ Code review focado em consistência

---

## 🚀 **Próximos Passos (Opcional)**

### Melhorias de Segurança:
- [ ] Implementar política de senha forte
- [ ] Adicionar tempo de expiração de senha
- [ ] Log de tentativas de login falhadas
- [ ] Bloqueio temporário após N tentativas

### Melhorias de UX:
- [ ] Recuperação de senha por email
- [ ] Primeiro login forçar troca de senha
- [ ] Visualizar senha ao digitar (toggle)
- [ ] Gerador de senha segura

---

**Status Final:** ✅ **BUG CORRIGIDO - SISTEMA OPERACIONAL**

**Tempo de Resolução:** ~10 minutos  
**Impacto:** CRÍTICO (autenticação não funcionava)  
**Complexidade:** BAIXA (erro de nomenclatura)  
**Risco de Regressão:** NENHUM (correção simples e direta)

---

📞 **Suporte:**
- Logs: `docker logs rodizio-organistas`
- Backups: `data/db_backup_*.json`
- Documentação: `SISTEMA_COMPLETO.md`
