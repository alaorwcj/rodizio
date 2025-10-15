# 🎯 Guia Rápido - Cadastro de Usuários e Configurações

## ✅ SISTEMA FUNCIONANDO!

### 📋 **Como Usar a Aba "Usuários"**

#### 1. **Acessar como Master**
```
http://localhost:8080
Login: admin_master
Senha: admin123
```

#### 2. **Ir para Aba "Usuários"**
- No menu superior, clique na aba **"👤 Usuários"**
- Você verá duas seções:
  - **Lista de Usuários** (todos os encarregados cadastrados)
  - **Configurações do Comum Atual** (dias de culto)

---

## 👤 **Cadastrar Novo Encarregado**

### Passo a Passo:

1. **Clique no botão** `➕ Novo Usuário`

2. **Preencha o formulário:**

   **ID do Usuário (login):**
   ```
   Exemplo: encarregado_itaquera
   Regra: apenas letras minúsculas e underscore
   ```

   **Nome Completo:**
   ```
   Exemplo: João Silva
   ```

   **Tipo de Usuário:**
   - 🔐 **Master** - Acesso total (não precisa de contexto)
   - 🏙️ **Admin Regional** - Gerencia uma regional inteira
   - 📍 **Encarregado Sub-Regional** - Gerencia uma sub-regional
   - ⛪ **Encarregado de Comum** - Gerencia UM comum específico ⭐

   **Contexto (Atribuição):**
   - Aparece automaticamente após selecionar o tipo
   - Para **Encarregado de Comum**: Escolha o comum que ele vai gerenciar
   - Exemplo: "GRU › Santa Isabel › Vila Paula"

   **Email:** (opcional)
   ```
   Exemplo: joao@email.com
   ```

   **Telefone:** (opcional)
   ```
   Exemplo: (11) 98765-4321
   ```

   **Senha Inicial:** (opcional)
   ```
   Deixe vazio = senha123 (padrão)
   Ou defina uma senha personalizada
   ```

3. **Clique em** `✅ Criar Usuário`

4. **Anote as credenciais que aparecem na notificação:**
   ```
   ✅ Usuário "João Silva" criado com sucesso!
   Login: encarregado_itaquera
   Senha: senha123
   ```

---

## ⚙️ **Configurar Dias de Culto do Comum**

### Passo a Passo:

1. **Na mesma aba "Usuários"**, role para baixo até **"Configurações do Comum Atual"**

2. **Marque os dias de culto:**
   ```
   ☑️ Domingo
   ☑️ Segunda
   ☑️ Terça
   ☑️ Quarta
   ☑️ Quinta
   ☑️ Sexta
   ☑️ Sábado
   ```
   
   **Exemplo Vila Paula:**
   ```
   ☑️ Domingo
   ☐ Segunda
   ☑️ Terça
   ☐ Quarta
   ☐ Quinta
   ☐ Sexta
   ☐ Sábado
   ```

3. **Defina o período:**
   - **Data de Início:** `01/01/2025`
   - **Data de Fim:** `28/02/2025`

4. **Clique em** `💾 Salvar Configurações`

5. **Veja a notificação:**
   ```
   ✅ Configurações salvas com sucesso!
   ```

---

## 🔄 **Testar o Novo Encarregado**

### 1. Fazer Logout
- Clique em `🚪 Sair` no header

### 2. Login com o Novo Usuário
```
Login: encarregado_itaquera
Senha: senha123 (ou a que você definiu)
```

### 3. O que ele verá:
- ✅ **Aba Dashboard** - Apenas do SEU comum
- ✅ **Aba Organistas** - Cadastra organistas do seu comum
- ✅ **Aba Restrições** - Gerencia indisponibilidades
- ✅ **Aba Configurações** - Configura período e dias
- ✅ **Aba Culto Oficial** - Cria escalas
- ✅ **Aba RJM** - Escala RJM

- ❌ **NÃO vê:** Hierarquia, Usuários (apenas Master)
- ❌ **NÃO vê:** Dados de outros comuns

---

## 📊 **Exemplo Real de Uso**

### **Cenário: Criar Encarregado para Itaquera**

#### Passo 1: Master cria o comum
```
1. Login: admin_master / admin123
2. Aba "Hierarquia"
3. Criar Regional: SPO - São Paulo
4. Criar Sub-Regional: Zona Leste
5. Criar Comum: Itaquera
```

#### Passo 2: Master cria o encarregado
```
1. Aba "Usuários"
2. ➕ Novo Usuário
3. ID: encarregado_itaquera
4. Nome: Pedro Santos
5. Tipo: Encarregado de Comum
6. Contexto: SPO › Zona Leste › Itaquera
7. Email: pedro@email.com
8. Criar
```

#### Passo 3: Master configura Itaquera
```
1. Seletor de contexto: SPO › Zona Leste › Itaquera
2. Aba "Usuários"
3. Configurações do Comum:
   - ☑️ Domingo (10:00, 19:00)
   - ☑️ Quarta (20:00)
   - ☑️ Sexta (20:00)
   - Período: 01/11/2025 até 31/12/2025
4. Salvar
```

#### Passo 4: Pedro gerencia Itaquera
```
1. Logout do Master
2. Login: encarregado_itaquera / senha123
3. Trocar senha (opcional)
4. Aba "Organistas": Cadastra João, Maria, José
5. Aba "Culto Oficial": Cria escala
   - Sistema gera automaticamente para:
     * Domingos 10:00 e 19:00
     * Quartas 20:00
     * Sextas 20:00
6. Organistas recebem dias conforme configuração
```

---

## ✏️ **Editar/Deletar Usuários**

### Editar:
1. Na lista de usuários
2. Clique no botão **✏️** (azul)
3. Digite o novo nome
4. Confirmar

### Deletar:
1. Na lista de usuários
2. Clique no botão **🗑️** (vermelho)
3. Confirmar exclusão
4. ⚠️ **Não é possível deletar admin_master**

---

## 🎯 **Dicas Importantes**

### ✅ **Boas Práticas:**

1. **IDs de usuários:**
   - Use padrão: `encarregado_<nome_comum>`
   - Exemplo: `encarregado_vila_paula`, `encarregado_itaquera`
   - Apenas minúsculas e underscore

2. **Tipos de usuário:**
   - **1 Master** por sistema (admin_master)
   - **1 Admin Regional** por regional
   - **1 Encarregado Sub** por sub-regional
   - **1 Encarregado Comum** por comum
   - **Vários Organistas** por comum

3. **Dias de culto:**
   - Configure ANTES de criar escalas
   - Escalas são geradas baseadas nos dias marcados
   - Pode mudar depois, mas escalas antigas não mudam

4. **Senha padrão:**
   - Sempre: `senha123`
   - Encarregado pode trocar no primeiro login
   - Use senhas fortes em produção

### ⚠️ **Evite:**

- ❌ Criar usuário sem contexto (exceto Master)
- ❌ Dois encarregados para o mesmo comum
- ❌ IDs com espaços ou caracteres especiais
- ❌ Deletar admin_master

---

## 🐛 **Troubleshooting**

### Problema: "Erro ao criar usuário"
**Solução:** ID já existe, use outro ID

### Problema: "Contexto inválido"
**Solução:** Crie o comum primeiro na aba Hierarquia

### Problema: "Sem permissão"
**Solução:** Apenas Master pode criar usuários

### Problema: Configurações não salvam
**Solução:** Marque pelo menos 1 dia de culto

### Problema: Encarregado não vê dados
**Solução:** Verifique se o contexto está correto no cadastro

---

## 📞 **Ajuda Rápida**

### Comandos Docker:
```bash
# Ver logs
docker logs rodizio-organistas --tail 50

# Reiniciar
docker-compose restart

# Rebuild completo
docker-compose down && docker-compose up -d --build
```

### Arquivos Importantes:
- `data/db.json` - Banco de dados
- `data/db_backup_*.json` - Backups automáticos
- `SISTEMA_COMPLETO.md` - Documentação completa

---

## ✅ **Checklist de Teste**

Teste tudo na sequência:

- [ ] 1. Login como admin_master
- [ ] 2. Aba Hierarquia: Criar Regional/Sub/Comum
- [ ] 3. Aba Usuários: Criar encarregado
- [ ] 4. Aba Usuários: Configurar dias de culto
- [ ] 5. Logout
- [ ] 6. Login como encarregado criado
- [ ] 7. Aba Organistas: Cadastrar 3 organistas
- [ ] 8. Aba Culto Oficial: Criar escala
- [ ] 9. Verificar se escalas estão corretas (apenas dias configurados)
- [ ] 10. Logout e login como admin_master
- [ ] 11. Trocar para outro comum no seletor
- [ ] 12. Verificar isolamento de dados

---

**Tudo funcionando!** 🎉  
**Versão:** 2.1  
**Data:** 14/10/2025
