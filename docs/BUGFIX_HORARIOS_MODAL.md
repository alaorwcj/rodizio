# 🐛 Correção - Campos de Horário não Apareciam no Modal

**Data:** 14/10/2025  
**Status:** ✅ **CORRIGIDO**

---

## 🎯 **PROBLEMA**

Ao criar uma Comum e marcar os dias de culto (Terça, Sexta, etc.):
- ❌ Os campos de horário **não apareciam**
- ❌ Não era possível digitar os horários
- ❌ Checkboxes marcados mas sem campos visíveis

**Screenshot do problema:**
```
☑️ Terça    [campo não aparece]
☑️ Sexta    [campo não aparece]
```

---

## 🔍 **CAUSA RAIZ**

O evento `onchange` estava no elemento **errado**:

### ❌ **ANTES (ERRADO):**
```html
<label onchange="toggleModalHorarios(this)">
    <input type="checkbox" name="modal_dias_culto" value="Terça">
    <strong>📅 Terça</strong>
    <input type="text" class="modal-horarios-input" style="display: none;">
</label>
```

**Problema:**
- O evento `onchange` no `<label>` **não é disparado** quando você clica no checkbox
- O checkbox muda de estado, mas o evento não acontece
- A função `toggleModalHorarios()` nunca é chamada

---

## ✅ **SOLUÇÃO**

Mover o `onchange` para o **checkbox** e passar o `parentElement`:

### ✅ **DEPOIS (CORRETO):**
```html
<label>
    <input type="checkbox" 
           name="modal_dias_culto" 
           value="Terça" 
           onchange="toggleModalHorarios(this.parentElement)">
    <strong>📅 Terça</strong>
    <input type="text" class="modal-horarios-input" style="display: none;">
</label>
```

**Por que funciona:**
1. **Evento no checkbox:** `onchange` dispara quando o checkbox muda
2. **`this.parentElement`:** Passa o `<label>` (elemento pai) para a função
3. **Função encontra os elementos:** Dentro do label, localiza o input de horário
4. **Toggle display:** Mostra/esconde o campo corretamente

---

## 🛠️ **MUDANÇAS TÉCNICAS**

### **Arquivo:** `templates/index.html`

**Linhas alteradas:** 1290-1320 (todos os 7 dias)

**De:**
```javascript
onchange="toggleModalHorarios(this)"  // no <label>
```

**Para:**
```javascript
onchange="toggleModalHorarios(this.parentElement)"  // no <input checkbox>
```

**Função `toggleModalHorarios` (permanece igual):**
```javascript
function toggleModalHorarios(label) {
    const checkbox = label.querySelector('input[type="checkbox"]');
    const inputHorarios = label.querySelector('.modal-horarios-input');
    
    if (checkbox.checked) {
        inputHorarios.style.display = 'block';  // ✅ Mostra
        inputHorarios.required = true;
        inputHorarios.focus();
    } else {
        inputHorarios.style.display = 'none';   // ✅ Esconde
        inputHorarios.required = false;
        inputHorarios.value = '';
    }
}
```

---

## 🧪 **TESTE DE VALIDAÇÃO**

### **Como testar:**

1. **Login:** `admin_master` / `admin123`
2. **Aba:** "Hierarquia"
3. **Clique:** "➕ Criar Comum"
4. **Preencha:**
   - Regional: `GRU - Guarulhos`
   - Sub-Regional: `Santa Isabel`
   - ID: `teste_horario`
   - Nome: `Teste Horário`

5. **Marque Terça:**
   - ✅ Clique no checkbox "Terça"
   - ✅ Campo de horário **deve aparecer instantaneamente**
   - ✅ Digite: `19:30, 20:00`

6. **Marque Sexta:**
   - ✅ Clique no checkbox "Sexta"
   - ✅ Campo de horário **aparece**
   - ✅ Digite: `19:00`

7. **Desmarque Terça:**
   - ✅ Clique novamente no checkbox "Terça"
   - ✅ Campo **desaparece**
   - ✅ Valor é limpo

---

## 📊 **COMPORTAMENTO ESPERADO**

| Ação | Resultado |
|------|-----------|
| ☑️ **Marcar** checkbox | Campo de horário **aparece** (display: block) |
| ☐ **Desmarcar** checkbox | Campo **desaparece** (display: none) |
| Digite horários | Aceita formato: `09:00, 18:00, 20:00` |
| Campo vazio com dia marcado | **required** = true (obrigatório) |

---

## 🎯 **RESULTADO**

Agora ao criar uma Comum:

```
Dias de Culto:

☐ ☀️ Domingo

☐ 📅 Segunda

☑️ 📅 Terça      [19:30, 20:00_________]  ← Campo aparece!

☐ 📅 Quarta

☐ 📅 Quinta

☑️ 📅 Sexta      [19:00________________]  ← Campo aparece!

☐ 📅 Sábado
```

---

## 💡 **LIÇÕES APRENDIDAS**

1. **Eventos em labels:** `onchange` no label não dispara com checkbox
2. **Elementos corretos:** Eventos de formulário devem estar nos inputs
3. **`this` vs `this.parentElement`:** Passar referência correta para funções
4. **querySelector:** Permite buscar elementos dentro de um pai específico

---

## ✅ **CHECKLIST DE CORREÇÃO**

- [x] Identificado problema: evento no elemento errado
- [x] Movido `onchange` para os 7 checkboxes
- [x] Ajustado parâmetro: `this.parentElement`
- [x] Container reconstruído
- [x] Testado: campos aparecem/desaparecem corretamente
- [x] Documentação criada

---

**STATUS FINAL:** ✅ Sistema funcionando corretamente  
**TESTE:** Marque qualquer dia → campo de horário aparece instantaneamente! 🎉
