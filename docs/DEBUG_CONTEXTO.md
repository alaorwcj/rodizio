# 🐛 Debug - Problema de Carregamento de Contexto

**Data:** 14/10/2025  
**Status:** 🔍 **EM INVESTIGAÇÃO COM LOGS DETALHADOS**

---

## 🎯 **PROBLEMA REPORTADO**

Ao tentar cadastrar organista como Master:
- Campo "📍 Comum" mostra: **"Carregando..."**
- Não carrega os comuns disponíveis
- Permanece em estado de carregamento

---

## ✅ **CORREÇÃO APLICADA**

### **Logs de Debug Adicionados**

Agora o sistema tem logs MUITO detalhados no console do navegador. Você verá:

```javascript
🔄 Iniciando carregamento de comuns...
✅ Regionais carregadas: 1 [...]
📍 Processando regional: GRU - Guarulhos (gru)
  ✅ Sub-regionais: 1 [...]
    📍 Processando sub-regional: Santa Isabel (santa_isabel)
      ✅ Comuns: 2 [...]
        ✅ Adicionado: Vila Paula (ID: vila_paula)
        ✅ Adicionado: Pedra Branca (ID: 002)
🎉 Total de comuns carregados: 2
✅ Seletor habilitado com 2 comuns
```

Ou, se houver erro:
```javascript
❌ ERRO CRÍTICO ao carregar comuns: [detalhes do erro]
```

---

## 🔍 **COMO INVESTIGAR**

### **Passo 1: Abrir Console do Navegador**

1. No navegador, pressione **F12**
2. Clique na aba **"Console"**
3. Limpe o console (ícone 🚫 ou Ctrl+L)

### **Passo 2: Acessar Aba Organistas**

1. Faça login: `admin_master` / `admin123`
2. Clique na aba **"Organistas"**
3. **OBSERVE O CONSOLE** - você verá os logs aparecerem

### **Passo 3: Verificar os Logs**

Procure por:

#### ✅ **Sucesso:**
```
🔄 Iniciando carregamento de comuns...
✅ Regionais carregadas: X
📍 Processando regional: ...
  ✅ Sub-regionais: X
    📍 Processando sub-regional: ...
      ✅ Comuns: X
        ✅ Adicionado: [nome] (ID: [id])
🎉 Total de comuns carregados: X
✅ Seletor habilitado com X comuns
```

#### ❌ **Erro:**
```
⚠️ Campo orgComumId não encontrado
```
→ **Você não está logado como Master**

```
❌ HTTP 404: Not Found
```
→ **Endpoints não encontrados - problema no backend**

```
❌ ERRO CRÍTICO ao carregar comuns: [erro]
```
→ **Erro JavaScript - veja detalhes**

```
⚠️ Array de regionais vazio ou inválido
```
→ **Não há regionais cadastradas**

```
⚠️ Nenhum comum foi carregado
```
→ **Não há comuns cadastrados**

---

## 🧪 **TESTES DE VALIDAÇÃO**

### **Teste 1: Verificar se é Master**

```bash
# No console do navegador (F12 → Console), digite:
console.log('Usuário Master?', document.getElementById('orgComumId') !== null);
```

**Resultado esperado:**
```
Usuário Master? true
```

Se for `false`: **Você não está logado como Master**

---

### **Teste 2: Verificar Regionais**

```bash
# No console do navegador:
fetch('/api/regionais').then(r => r.json()).then(d => console.log('Regionais:', d));
```

**Resultado esperado:**
```json
Regionais: [
  {
    "id": "gru",
    "nome": "GRU - Guarulhos"
  }
]
```

---

### **Teste 3: Verificar Sub-Regionais**

```bash
# No console:
fetch('/api/regionais/gru/sub-regionais').then(r => r.json()).then(d => console.log('Subs:', d));
```

**Resultado esperado:**
```json
Subs: [
  {
    "id": "santa_isabel",
    "nome": "Santa Isabel"
  }
]
```

---

### **Teste 4: Verificar Comuns**

```bash
# No console:
fetch('/api/regionais/gru/sub-regionais/santa_isabel/comuns').then(r => r.json()).then(d => console.log('Comuns:', d));
```

**Resultado esperado:**
```json
Comuns: [
  {
    "id": "vila_paula",
    "nome": "Vila Paula"
  },
  {
    "id": "002",
    "nome": "Pedra Branca"
  }
]
```

---

### **Teste 5: Forçar Carregamento Manual**

```bash
# No console:
carregarComunsParaOrganista();
```

**Resultado esperado:**
- Logs detalhados no console
- Seletor popula com comuns

---

## 🔧 **POSSÍVEIS CAUSAS E SOLUÇÕES**

### **Causa 1: Não está logado como Master**

**Sintoma:**
```
⚠️ Campo orgComumId não encontrado
```

**Solução:**
1. Fazer logout
2. Login: `admin_master` / `admin123`
3. Tentar novamente

---

### **Causa 2: JavaScript não carrega**

**Sintoma:**
- Nenhum log aparece no console
- Campo permanece "Carregando..."

**Solução:**
```bash
# Limpar cache do navegador
Ctrl + Shift + Delete → Limpar cache

# Ou recarregar sem cache
Ctrl + F5
```

---

### **Causa 3: Função não é chamada**

**Sintoma:**
- Nenhum log ao abrir aba Organistas

**Solução:**
```bash
# Verificar se showTab chama a função
# No console:
showTab('organistas');
```

---

### **Causa 4: Nenhum comum cadastrado**

**Sintoma:**
```
⚠️ Nenhum comum foi carregado
```

**Solução:**
1. Aba "Hierarquia"
2. Criar pelo menos 1 comum
3. Tentar novamente

---

### **Causa 5: Erro de rede**

**Sintoma:**
```
❌ HTTP 500: Internal Server Error
```

**Solução:**
```bash
# Ver logs do container
docker logs rodizio-organistas --tail 50

# Reiniciar container
docker-compose restart
```

---

## 📊 **ESTRUTURA ESPERADA DO BANCO**

O sistema precisa desta estrutura mínima:

```json
{
  "regionais": {
    "gru": {
      "nome": "GRU - Guarulhos",
      "sub_regionais": {
        "santa_isabel": {
          "nome": "Santa Isabel",
          "comuns": {
            "vila_paula": {
              "nome": "Vila Paula",
              "config": {
                "dias_culto": ["Domingo", "Terça"],
                "horarios": {...}
              }
            }
          }
        }
      }
    }
  }
}
```

---

## 🚀 **PRÓXIMOS PASSOS**

1. **Abra o console (F12)**
2. **Acesse aba "Organistas"**
3. **Veja os logs detalhados**
4. **Me envie:**
   - Screenshot do console
   - Ou copie/cole os logs aqui
   
Com essas informações conseguirei identificar exatamente onde está o problema!

---

## 📝 **CHECKLIST DE VERIFICAÇÃO**

- [ ] Login como `admin_master` / `admin123`
- [ ] Console do navegador aberto (F12)
- [ ] Aba "Organistas" acessada
- [ ] Logs aparecem no console?
- [ ] Campo "📍 Comum" existe?
- [ ] Teste 2 (Regionais) retorna dados?
- [ ] Teste 3 (Sub-regionais) retorna dados?
- [ ] Teste 4 (Comuns) retorna dados?
- [ ] Teste 5 (Forçar) funciona?

---

**STATUS:** Sistema com logs detalhados instalados ✅  
**AÇÃO:** Verifique o console do navegador e me informe o que aparece! 🔍
