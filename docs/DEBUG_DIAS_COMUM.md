# 🔍 Debug - Dias da Comum Errados

**Data:** 14/10/2025  
**Problema:** Encarregados veem sempre dias da "Vila Paula" independente da sua comum

---

## 🧪 **TESTE COM LOGS**

### **1. Login como Encarregado**
- URL: http://localhost:8080
- Usuário: `enc_central`
- Senha: (sua senha)

### **2. Abrir Console (F12)**
- Pressione F12
- Aba "Console"
- Limpe o console

### **3. Ir para Aba Organistas**

**Logs esperados:**

```javascript
👤 DEBUG USUÁRIO:
  ID: enc_central
  Nome: ...
  Tipo: encarregado_comum
  Contexto ID: central  ← VERIFICAR SE APARECE!
  Is Master: false

🔄 carregarComunsParaOrganista() chamada
  📋 selectComum encontrado: true
  📋 hiddenComumId encontrado: true
  📋 hiddenComumId.value: central  ← DEVE SER "central"!
👤 Usuário é Encarregado de Comum, carregando contexto específico...
[... logs de carregamento ...]
🎉 Comum carregada com sucesso!

🔑 carregarDiasDoComum: usando comum_id do hidden: central
📡 Buscando config da comum: /api/comuns/central/config
✅ Config recebida da comum central: {...}
  📅 Dias de culto: ["Domingo", "Quarta"]  ← DIAS CORRETOS DA CENTRAL!
✅ Carregando 2 dias da config
  ➕ Adicionado dia: Domingo
  ➕ Adicionado dia: Quarta
```

---

### **4. Verificar Logs do Docker**

```bash
docker logs rodizio-organistas --tail 50
```

**Logs esperados no backend:**

```
🔍 [API] GET /api/comuns/central/config
  👤 Usuário: enc_central (tipo: encarregado_comum)
  🔑 Contexto: central
  ✅ Comum encontrado: Central
  ✅ Config retornada: dias_culto=['Domingo', 'Quarta']
```

---

## ❓ **POSSÍVEIS PROBLEMAS**

### **Problema 1: hiddenComumId.value vazio**
```
📋 hiddenComumId.value: (vazio)
```
**Causa:** contexto_id não está definido no usuário  
**Solução:** Verificar banco de dados

### **Problema 2: Comum não encontrada**
```
❌ Erro HTTP 404 ao buscar config da comum central
```
**Causa:** Comum "central" não existe no banco  
**Solução:** Verificar se foi criada corretamente

### **Problema 3: Sem permissão**
```
❌ Erro HTTP 403
```
**Backend mostra:**
```
❌ Encarregado tentando acessar comum diferente do seu contexto
   Contexto do usuário: pedrabranca
   Comum solicitado: central
```
**Causa:** contexto_id do usuário não bate com ID da comum  
**Solução:** Corrigir contexto_id no banco

### **Problema 4: Config sem dias_culto**
```
⚠️ Config sem dias_culto, usando fallback
```
**Causa:** Comum criada sem configurar dias  
**Solução:** Editar comum e adicionar dias de culto

---

## 📋 **VERIFICAR NO BANCO**

### **Usuário enc_central:**

```bash
cat data/db.json | jq '.usuarios.enc_central'
```

**Deve retornar:**
```json
{
  "id": "enc_central",
  "nome": "...",
  "tipo": "encarregado_comum",
  "contexto_id": "central",  ← DEVE SER O ID DA COMUM!
  "ativo": true
}
```

### **Comum Central:**

```bash
cat data/db.json | jq '.regionais.gru.sub_regionais.santa_isabel.comuns.central'
```

**Deve retornar:**
```json
{
  "nome": "Central",
  "config": {
    "dias_culto": ["Domingo", "Quarta"],  ← DIAS CONFIGURADOS!
    "horarios": {
      "Domingo": ["09:00", "18:00"],
      "Quarta": ["19:30"]
    }
  }
}
```

---

## 🚀 **ME ENVIE:**

1. ✅ **Logs do console** após clicar em "Organistas"
2. ✅ **Logs do Docker** (docker logs rodizio-organistas --tail 50)
3. ✅ **Screenshot** do campo "Dias Permitidos"
4. ✅ **Resultado de:**
   ```bash
   cat data/db.json | jq '.usuarios.enc_central'
   cat data/db.json | jq '.regionais.gru.sub_regionais.santa_isabel.comuns.central'
   ```

Com essas informações identificarei o problema! 🎯
