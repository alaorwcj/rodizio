# 🔧 Troubleshooting - Sistema de Rodízio de Organistas

## ❌ Erro: "allOrganistas is not defined"

### 🐛 Sintoma
Ao clicar em "Gerar Escala Automaticamente" aparece erro em vermelho:
```
Erro: allOrganistas is not defined
```

### ✅ Solução Aplicada
1. **Correção da variável**: Mudado de `allOrganistas` para `organistas`
2. **Carregamento preventivo**: Lista de organistas é carregada antes de gerar escala
3. **Logs de debug**: Console mostra quando organistas são carregadas

### 🔄 Como Verificar se Está Funcionando

1. **Faça login como admin**:
   - Usuário: `admin`
   - Senha: `123456`

2. **Abra o Console do Navegador** (F12):
   - Procure por mensagens: `"Organistas carregadas: 4"`
   - Não deve haver erros em vermelho

3. **Clique em "Gerar Escala Automaticamente"**:
   - Deve aparecer: "Gerando escala automaticamente..."
   - Depois: Escala separada por mês
   - Não deve aparecer erro

4. **Verifique os dropdowns**:
   - Cada posição deve ter dropdown com nomes das organistas
   - Dropdowns devem estar populados (não vazios)

---

## 🚫 Erro: "Nenhuma organista cadastrada"

### 🐛 Sintoma
Sistema não gera escala dizendo que não há organistas.

### ✅ Solução

1. **Verificar banco de dados**:
```bash
cat data/db.json | grep -A 5 "organistas"
```

2. **Recriar banco de dados**:
```bash
docker-compose exec rodizio-app python update_db_passwords.py
docker-compose restart
```

3. **Verificar na interface**:
   - Login como admin
   - Aba "Organistas"
   - Deve mostrar: Ieda, Raquel, Milena, Yasmin G.

---

## 🔐 Erro: "Redirecting to login"

### 🐛 Sintoma
Ao tentar acessar rotas, é redirecionado para login.

### ✅ Solução

1. **Fazer login novamente**
2. **Verificar sessão**:
   - Não feche o navegador
   - Não use modo anônimo
   - Cookies devem estar habilitados

3. **Restartar container**:
```bash
docker-compose restart
```

---

## 📅 Erro: "Data fora do bimestre"

### 🐛 Sintoma
Não consegue marcar indisponibilidade ou gerar escala.

### ✅ Solução

1. **Configurar período bimestral**:
   - Login como admin
   - Aba "Configurações"
   - Definir data início e fim do bimestre
   - Exemplo: 01/10/2025 a 30/11/2025

2. **Verificar datas**:
   - Data de início deve ser menor que data de fim
   - Deve abranger pelo menos 2 meses

---

## 🎲 Escala não é gerada

### 🐛 Sintoma
Clica em "Gerar Escala" mas nada acontece.

### ✅ Verificações

1. **Console do navegador (F12)**:
   - Procure por erros em vermelho
   - Verifique mensagens de carregamento

2. **Logs do container**:
```bash
docker-compose logs --tail=50 rodizio-app
```

3. **Testar rota manualmente**:
```bash
# Login
curl -c /tmp/cookies.txt -X POST http://localhost:8080/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=123456"

# Gerar escala
curl -b /tmp/cookies.txt -X POST http://localhost:8080/escala/gerar
```

---

## 💾 Edição não salva

### 🐛 Sintoma
Troca organista no dropdown, clica em "Salvar", mas não persiste.

### ✅ Solução

1. **Verificar se há escala publicada**:
   - Deve ter clicado em "Publicar Escala" antes

2. **Testar novamente**:
   - Troque a organista
   - Clique em "💾 Salvar" na mesma linha
   - Recarregue a página
   - Verifique se manteve a mudança

3. **Verificar logs**:
```bash
docker-compose logs --tail=20 rodizio-app | grep -i edit
```

---

## 🔄 Container não inicia

### 🐛 Sintoma
```
ERROR: Worker failed to boot
```

### ✅ Solução

1. **Ver erro completo**:
```bash
docker-compose logs rodizio-app
```

2. **Reconstruir container**:
```bash
docker-compose down
docker-compose up -d --build
```

3. **Verificar portas**:
```bash
# Porta 8080 deve estar livre
netstat -an | grep 8080
```

---

## 🌐 Não abre no navegador

### 🐛 Sintoma
`http://localhost:8080` não carrega.

### ✅ Solução

1. **Verificar se container está rodando**:
```bash
docker-compose ps
```
- Status deve ser "Up" e "healthy"

2. **Verificar logs**:
```bash
docker-compose logs --tail=20 rodizio-app
```

3. **Testar com curl**:
```bash
curl http://localhost:8080/health
```
- Deve retornar JSON com status "healthy"

4. **Usar IP ao invés de localhost**:
```
http://127.0.0.1:8080
```

---

## 🗄️ Backup e Restauração

### Fazer Backup

```bash
# Backup do banco de dados
cp data/db.json data/db_backup_$(date +%Y%m%d_%H%M%S).json

# Listar backups
ls -lh data/db_backup_*
```

### Restaurar Backup

```bash
# Parar container
docker-compose down

# Restaurar
cp data/db_backup_YYYYMMDD_HHMMSS.json data/db.json

# Reiniciar
docker-compose up -d
```

---

## 🧪 Testes Rápidos

### 1. Testar Health Check
```bash
curl http://localhost:8080/health
```
**Esperado**: `{"status":"healthy",...}`

### 2. Testar Login
```bash
curl -X POST http://localhost:8080/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=123456"
```
**Esperado**: Redirect para "/"

### 3. Testar Organistas
```bash
curl -c /tmp/cookies.txt -X POST http://localhost:8080/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=123456"

curl -b /tmp/cookies.txt http://localhost:8080/organistas
```
**Esperado**: JSON com lista de organistas

### 4. Verificar Console do Navegador
- Abra F12
- Aba "Console"
- Não deve ter erros em vermelho
- Deve ter: "Organistas carregadas: 4"

---

## 📞 Comandos Úteis

### Reiniciar tudo
```bash
docker-compose restart
```

### Ver logs em tempo real
```bash
docker-compose logs -f rodizio-app
```

### Entrar no container
```bash
docker-compose exec rodizio-app bash
```

### Resetar banco de dados
```bash
docker-compose exec rodizio-app python update_db_passwords.py
docker-compose restart
```

### Verificar espaço em disco
```bash
df -h
docker system df
```

---

## 🆘 Último Recurso

Se nada funcionar:

```bash
# 1. Parar tudo
docker-compose down

# 2. Fazer backup
cp data/db.json data/db_backup_emergency.json

# 3. Limpar volumes (CUIDADO: apaga dados)
docker-compose down -v

# 4. Reconstruir tudo
docker-compose up -d --build

# 5. Recriar banco
docker-compose exec rodizio-app python update_db_passwords.py
```

---

## ✅ Checklist de Validação

Após qualquer correção, verifique:

- [ ] Container está "Up" e "healthy"
- [ ] Health check retorna status "healthy"
- [ ] Login funciona (admin/123456)
- [ ] Aba "Organistas" mostra 4 organistas
- [ ] Console do navegador sem erros
- [ ] "Gerar Escala" não dá erro
- [ ] Dropdowns estão populados
- [ ] Estatísticas são exibidas
- [ ] Edição salva corretamente

---

**Atualizado**: Outubro 2025  
**Versão**: 2.0
