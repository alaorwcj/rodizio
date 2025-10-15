# 🐛 Correção - Cadastro de Organista com Seletor de Comum

**Data:** 14/10/2025  
**Versão:** 2.3.1  
**Status:** ✅ **CORRIGIDO**

---

## 🐛 **PROBLEMA IDENTIFICADO**

### **Erro:**
```
"Comum não encontrada" ao tentar cadastrar organista como Master
```

### **Causa Raiz:**
1. ✅ Frontend enviava `comum_id` no seletor
2. ❌ Backend **NÃO recebia** o `comum_id` no payload
3. ❌ Backend usava `comum_id = 'vila_paula'` hardcoded

---

## ✅ **CORREÇÕES IMPLEMENTADAS**

### **1. Backend (app.py)**

#### **Antes:**
```python
# Master: adicionar na primeira comum disponível (Vila Paula por padrão)
if current_user.is_master:
    comum_id = 'vila_paula'  # ❌ HARDCODED!
```

#### **Depois:**
```python
# Master: DEVE especificar o comum no payload
if current_user.is_master:
    comum_id = payload.get('comum_id')
    if not comum_id:
        return jsonify({
            "error": "Selecione o comum onde a organista atuará"
        }), 400
```

**Mudanças:**
- ✅ Lê `comum_id` do payload
- ✅ Retorna erro claro se não for especificado
- ✅ Mensagem amigável

---

### **2. Frontend (index.html)**

#### **Antes:**
```javascript
const payload = {
    id: ...,
    nome: ...,
    // comum_id NÃO era adicionado! ❌
};

if (selectComum && !comumId) {
    // Validação, mas não adicionava ao payload
}
```

#### **Depois:**
```javascript
const payload = {
    id: ...,
    nome: ...,
};

// Se é Master, adicionar comum_id ao payload
if (selectComum) {
    if (!comumId) {
        showAlert('alertOrganista', 'Selecione o comum...', 'error');
        return;
    }
    payload.comum_id = comumId;  // ✅ AGORA ENVIA!
}
```

**Mudanças:**
- ✅ Adiciona `comum_id` ao payload antes de enviar
- ✅ Validação com mensagem clara
- ✅ Funciona apenas para Master (encarregados não têm o campo)

---

## 🔄 **FLUXO CORRIGIDO**

### **Master Cadastra Organista:**

```
1. Login: admin_master
2. Aba "Organistas"
3. Ver campo: 📍 Comum
4. Selecionar: "GRU › Santa Isabel › Vila Paula"

Frontend:
  - Captura valor do select: "vila_paula"
  - Adiciona ao payload: {comum_id: "vila_paula"}
  
5. Clicar "Adicionar Organista"

Backend:
  - Recebe payload com comum_id
  - Busca comum usando find_comum_by_id()
  - Se encontrar: adiciona organista
  - Se não: retorna erro "Comum não encontrada"

6. ✅ Sucesso!
```

---

## 🧪 **TESTE AGORA**

### **Teste 1: Cadastrar Organista como Master**

```bash
1. Login: admin_master / admin123
2. Aba "Organistas"
3. Preencher:
   - 📍 Comum: [GRU › Santa Isabel › Vila Paula ▼]
   - ID: teste_org
   - Nome: Teste Organista
   - Email: teste@email.com
   - Telefone: (11) 12345-6789
   - Tipos: ☑️ Culto
   - Dias: ☑️ Domingo

4. Clicar "Adicionar Organista"

Esperado:
✅ "Organista adicionado com sucesso!"
✅ Organista aparece na lista
✅ Vinculada ao comum escolhido
```

### **Teste 2: Validação - Sem Selecionar Comum**

```bash
1. Login: admin_master
2. Aba "Organistas"
3. NÃO selecionar comum
4. Preencher outros campos
5. Tentar adicionar

Esperado:
❌ "Selecione o comum onde a organista atuará"
```

### **Teste 3: Encarregado Cadastra Organista**

```bash
1. Login: douglassilva / senha123
2. Aba "Organistas"
3. NÃO ver campo "📍 Comum"
4. Preencher dados
5. Adicionar

Esperado:
✅ Organista adicionada ao comum do encarregado
✅ Sem precisar selecionar (automático)
```

---

## 📊 **VALIDAÇÃO TÉCNICA**

### **Payload Enviado (Master):**
```json
{
  "comum_id": "vila_paula",
  "id": "teste_org",
  "nome": "Teste Organista",
  "email": "teste@email.com",
  "telefone": "(11) 12345-6789",
  "tipos": ["Culto"],
  "dias_permitidos": ["Domingo"],
  "regras_especiais": {}
}
```

### **Backend Processa:**
```python
comum_id = payload.get('comum_id')  # "vila_paula"
comum_data = find_comum_by_id(db, comum_id)  # Busca

# Se encontrar:
comum = comum_data['comum']  # Pega referência
organistas = comum.get('organistas', [])  # Lista
organistas.append(payload)  # Adiciona
# Salva no banco
```

### **Resultado no Banco (db.json):**
```json
{
  "regionais": {
    "gru": {
      "sub_regionais": {
        "santa_isabel": {
          "comuns": {
            "vila_paula": {
              "nome": "Vila Paula",
              "organistas": [
                {
                  "id": "teste_org",
                  "nome": "Teste Organista",
                  "comum_id": "vila_paula"
                }
              ]
            }
          }
        }
      }
    }
  }
}
```

---

## 🗂️ **ARQUIVOS MODIFICADOS**

### **Backend:**
- ✅ `app.py` (linha ~553-562)
  - Função `add_organista()`
  - Master agora usa `payload.get('comum_id')`
  - Validação obrigatória
  - Mensagem de erro clara

### **Frontend:**
- ✅ `templates/index.html` (linha ~2004-2011)
  - Função `addOrganista(event)`
  - Adiciona `comum_id` ao payload para Master
  - Validação antes de enviar

---

## 📝 **CHANGELOG**

```
v2.3.1 - 14/10/2025

[BUGFIX] Cadastro de organista com seletor de comum
  - Corrigido: campo comum_id não era enviado ao backend
  - Backend agora exige comum_id para Master
  - Mensagens de erro mais claras
  - Validação robusta
```

---

## ✅ **RESUMO DA CORREÇÃO**

| Item | Status |
|------|--------|
| **Frontend envia comum_id** | ✅ Corrigido |
| **Backend recebe comum_id** | ✅ Corrigido |
| **Validação obrigatória** | ✅ Implementada |
| **Mensagem de erro clara** | ✅ Implementada |
| **Teste Master** | ⏳ Aguardando teste |
| **Teste Encarregado** | ⏳ Aguardando teste |

---

**✅ CORREÇÃO IMPLEMENTADA E PRONTA!**

**Teste agora:** http://localhost:8080  
**Login:** admin_master / admin123  
**Aba:** Organistas → Selecione o comum → Cadastre!

**Se ainda houver erro, me avise com:**
- Screenshot da tela
- Logs do navegador (F12 → Console)
- Comum que tentou selecionar
