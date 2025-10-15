# ✅ TESTE DE AUTENTICAÇÃO - Passo a Passo

**Data:** 14/10/2025  
**Status:** 🔧 Bug corrigido - TESTE AGORA!

---

## 🎯 **O QUE FOI CORRIGIDO**

❌ **ANTES:**
```
1. Criar usuário "douglassilva" via aba Usuários
2. Logout
3. Login: douglassilva / senha123
   ❌ ERRO: "Senha incorreta"
```

✅ **AGORA:**
```
1. Criar usuário via aba Usuários
2. Logout
3. Login com credenciais criadas
   ✅ FUNCIONA!
```

---

## 🧪 **TESTE RÁPIDO - 3 MINUTOS**

### Passo 1: Limpar Sessão
```
1. Abra http://localhost:8080
2. Se estiver logado, clique em "Sair"
```

### Passo 2: Login Master
```
Login: admin_master
Senha: admin123
✅ Deve entrar normalmente
```

### Passo 3: Criar Novo Usuário
```
1. Clique na aba "👤 Usuários"
2. Clique em "➕ Novo Usuário"
3. Preencha:
   - ID: teste_auth
   - Nome: Teste Autenticação
   - Tipo: Encarregado de Comum
   - Contexto: GRU › Santa Isabel › Vila Paula
   - Email: (deixar vazio)
   - Telefone: (deixar vazio)
   - Senha: (deixar vazio = senha123)
4. Clique em "✅ Criar Usuário"
5. Anote as credenciais que aparecem:
   ✅ Login: teste_auth
   ✅ Senha: senha123
```

### Passo 4: Logout
```
1. Clique em "🚪 Sair" (canto superior direito)
2. Você será redirecionado para a tela de login
```

### Passo 5: 🔥 TESTE CRÍTICO - Login com Novo Usuário
```
Login: teste_auth
Senha: senha123

✅ ESPERADO: Sistema deve fazer login com sucesso
✅ ESPERADO: Você deve ver o dashboard do comum
✅ ESPERADO: Nome "Teste Autenticação" aparece no header
✅ ESPERADO: Apenas vê dados de "Vila Paula"

❌ SE DER ERRO: Tire screenshot e avise!
```

---

## 🧪 **TESTE COMPLETO - 5 MINUTOS**

Execute TODOS os testes abaixo:

### Teste 1: Login Admin Master (Usuário Original)
```
Login: admin_master
Senha: admin123
✅ Status: _____________
```

### Teste 2: Login Usuário Migrado
```
Login: douglassilva
Senha: senha123
✅ Status: _____________
(Este usuário foi migrado pelo script)
```

### Teste 3: Criar e Logar Usuário Novo
```
1. Login como master
2. Criar usuário: teste_auth
3. Logout
4. Login: teste_auth / senha123
✅ Status: _____________
```

### Teste 4: Criar Vários Tipos de Usuários
```
Criar 1 de cada tipo e testar login:

A) Admin Regional:
   - ID: admin_gru
   - Contexto: GRU - Guarulhos
   ✅ Login funciona: _____________

B) Encarregado Sub-Regional:
   - ID: enc_santa_isabel
   - Contexto: GRU › Santa Isabel
   ✅ Login funciona: _____________

C) Encarregado Comum:
   - ID: enc_vila_paula
   - Contexto: GRU › Santa Isabel › Vila Paula
   ✅ Login funciona: _____________
```

### Teste 5: Senha Customizada
```
1. Criar usuário: teste_senha_custom
2. Senha: MinhaSenha123!
3. Logout
4. Login: teste_senha_custom / MinhaSenha123!
✅ Status: _____________
```

### Teste 6: Senha Incorreta (Deve Falhar)
```
1. Login: teste_auth
2. Senha: senhaerrada
❌ Deve mostrar: "Usuário ou senha incorretos"
✅ Status: _____________
```

### Teste 7: Editar Senha de Usuário
```
1. Login como master
2. Aba Usuários
3. Editar "teste_auth"
4. Nova senha: NovaSenh@456
5. Logout
6. Login: teste_auth / NovaSenh@456
✅ Status: _____________
```

---

## 📊 **VERIFICAÇÃO DO BANCO DE DADOS**

### Comando 1: Ver Estrutura do Usuário
```bash
docker exec -it rodizio-organistas python3 -c "
import json
with open('data/db.json', 'r') as f:
    db = json.load(f)
    usuarios = db.get('usuarios', {})
    for user_id, user in usuarios.items():
        print(f'{user_id}:')
        print(f'  - password_hash: {\"password_hash\" in user}')
        print(f'  - senha_hash: {\"senha_hash\" in user}')
        print(f'  - id presente: {\"id\" in user}')
        print()
"
```

**Esperado:**
```
admin_master:
  - password_hash: True    ✅
  - senha_hash: False      ✅
  - id presente: True      ✅

douglassilva:
  - password_hash: True    ✅
  - senha_hash: False      ✅
  - id presente: True      ✅

teste_auth:
  - password_hash: True    ✅
  - senha_hash: False      ✅
  - id presente: True      ✅
```

### Comando 2: Ver Hash de Senha
```bash
docker exec -it rodizio-organistas python3 -c "
import json
with open('data/db.json', 'r') as f:
    db = json.load(f)
    user = db['usuarios']['teste_auth']
    print('Hash:', user.get('password_hash', 'AUSENTE')[:50] + '...')
"
```

**Esperado:**
```
Hash: scrypt:32768:8:1$...
```

---

## 🔍 **LOGS DE DEBUG**

### Ver Logs de Login:
```bash
docker logs rodizio-organistas --tail 50 | grep -i "login\|POST /login"
```

### Ver Erros:
```bash
docker logs rodizio-organistas --tail 50 | grep -i "error\|exception"
```

### Ver Criação de Usuários:
```bash
docker logs rodizio-organistas --tail 50 | grep -i "POST /api/usuarios"
```

---

## ✅ **CHECKLIST FINAL**

Marque conforme testa:

### Autenticação Básica:
- [ ] Login admin_master funciona
- [ ] Login usuário migrado (douglassilva) funciona
- [ ] Login usuário novo criado funciona
- [ ] Senha incorreta retorna erro apropriado

### Tipos de Usuário:
- [ ] Admin Regional loga e vê apenas sua regional
- [ ] Encarregado Sub loga e vê apenas sua sub-regional
- [ ] Encarregado Comum loga e vê apenas seu comum

### CRUD de Usuários:
- [ ] Criar usuário via interface funciona
- [ ] Editar nome de usuário funciona
- [ ] Editar senha de usuário funciona
- [ ] Deletar usuário funciona (exceto master)

### Segurança:
- [ ] Senhas são hasheadas (não aparecem em texto plano)
- [ ] Campo usado é `password_hash` em todos usuários
- [ ] Backup foi criado antes da migração
- [ ] Não há mais campo `senha_hash` no banco

---

## 🚨 **SE ALGO FALHAR**

### Opção 1: Reverter do Backup
```bash
# Parar container
docker-compose down

# Listar backups
ls -lh data/db_backup_*.json

# Restaurar backup
cp data/db_backup_fix_password_20251014_214118.json data/db.json

# Subir container
docker-compose up -d
```

### Opção 2: Recriar Usuário
```bash
# Login como master
# Aba Usuários
# Deletar usuário problemático
# Criar novamente com mesmo ID
```

### Opção 3: Executar Migração Novamente
```bash
cd /mnt/f/rodizio
python3 fix_password_field.py
docker-compose restart
```

---

## 📞 **REPORTAR PROBLEMA**

Se algum teste falhar, forneça:

1. **Qual teste falhou?**
2. **Screenshot da tela de erro**
3. **Logs do container:**
   ```bash
   docker logs rodizio-organistas --tail 100 > logs_erro.txt
   ```
4. **Conteúdo do usuário no banco:**
   ```bash
   # Substituir USER_ID pelo ID que falhou
   docker exec -it rodizio-organistas python3 -c "
   import json
   with open('data/db.json', 'r') as f:
       db = json.load(f)
       print(json.dumps(db['usuarios']['USER_ID'], indent=2))
   "
   ```

---

**🎯 OBJETIVO:** Garantir que 100% dos testes passem!  
**⏱️ TEMPO:** 5-10 minutos  
**📝 STATUS:** [ ] NÃO TESTADO  [ ] TESTANDO  [ ] ✅ TUDO OK  [ ] ❌ FALHOU
