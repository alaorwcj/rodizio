# 🔧 Como Limpar Cache do Navegador - Menu Organista

## 🚨 Problema
O menu "Restrição de Dias" não aparece para organistas devido ao cache agressivo do navegador.

---

## ✅ Solução Passo a Passo

### **Método 1: Hard Refresh (Mais Rápido)**

1. **Acesse:** https://localhost
2. **Pressione:** `Ctrl + Shift + R` (Windows/Linux) ou `Cmd + Shift + R` (Mac)
3. **Faça login novamente** com a organista

---

### **Método 2: Limpar Cache Completo (Mais Eficaz)**

#### **Google Chrome / Microsoft Edge:**

1. **Pressione:** `Ctrl + Shift + Delete`
2. **Selecione:**
   - ✅ **Imagens e arquivos em cache** (Cached images and files)
   - ⏱️ Período: **Última hora** ou **Todo o período**
3. **Clique em:** "Limpar dados" ou "Clear data"
4. **Feche o navegador completamente**
5. **Reabra e acesse:** https://localhost
6. **Faça login com a organista**

#### **Firefox:**

1. **Pressione:** `Ctrl + Shift + Delete`
2. **Selecione:**
   - ✅ **Cache**
   - ⏱️ Intervalo: **Última hora** ou **Tudo**
3. **Clique em:** "Limpar agora"
4. **Feche o navegador completamente**
5. **Reabra e acesse:** https://localhost
6. **Faça login com a organista**

---

### **Método 3: Modo Anônimo/Privado (Teste Rápido)**

1. **Pressione:** `Ctrl + Shift + N` (Chrome/Edge) ou `Ctrl + Shift + P` (Firefox)
2. **Acesse:** https://localhost
3. **Aceite o certificado SSL** (clique em Avançado → Continuar)
4. **Faça login com a organista**
5. **Teste o menu**

---

### **Método 4: Via DevTools (Para Desenvolvedores)**

1. **Pressione:** `F12` para abrir DevTools
2. **Clique com botão direito** no ícone de atualização (🔄)
3. **Selecione:** "Empty Cache and Hard Reload" ou "Esvaziar cache e recarregar"
4. **Faça login novamente**

---

## 🎯 Como Verificar se Funcionou

Após limpar o cache, você deve ver no **Console (F12)**:

```
👤 DEBUG USUÁRIO:
  ID: ieda
  Nome: Ieda
  Tipo: organista
  Is Master: false
⚡ [FIX IMEDIATO] Executando - isAdmin: false
🔧 Corrigindo menus mobile...
✅ Correção de menus concluída!
```

E no **Menu Mobile**:
- ✅ **"📅 Restrição de Dias"** deve aparecer
- ❌ **NÃO** deve ter "Minha Agenda"
- ❌ **NÃO** deve ter erros no console

---

## 📱 Se ainda não funcionar no celular

1. **No Chrome mobile:**
   - Toque nos **3 pontos** (⋮)
   - **Configurações** → **Privacidade**
   - **Limpar dados de navegação**
   - Marque **Imagens e arquivos em cache**
   - **Limpar dados**

2. **No Firefox mobile:**
   - Toque nos **3 pontos** (⋮)
   - **Configurações** → **Excluir dados de navegação**
   - Marque **Cache**
   - **Excluir dados**

3. **Feche o app completamente** e reabra

---

## 🔄 Alternativa: Modo Desenvolvedor

Se você tem acesso ao servidor, pode incrementar a versão no título da página:

```html
<title>Sistema de Rodízio de Organistas v2.2.{{ timestamp }}</title>
```

Isso força o navegador a tratar como página nova.

---

## ✅ Confirmação Final

Após limpar o cache, o menu deve funcionar assim:

**Para ORGANISTAS (tipo='organista'):**
```
☰ Menu
━━━━━━━━━━━━━
📊 Dashboard
🎵 Rodízios ▼
📅 Restrição de Dias  ← DEVE APARECER AQUI
```

**Para ADMINISTRADORES:**
```
☰ Menu
━━━━━━━━━━━━━
📊 Dashboard
🎵 Rodízios ▼
👤 Encarregado Local ▼
📅 Agenda Organista ▼
   📅 Minha Agenda
   🔐 Gerenciar Todas
```

---

## 🆘 Suporte

Se mesmo após limpar o cache o problema persistir:
1. Verifique se está logado com o usuário correto
2. Abra o Console (F12) e envie as mensagens de erro
3. Verifique se aparece `Is Master: false` no debug

**Build atual:** {{ timestamp }}
