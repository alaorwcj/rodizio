# 📅 Guia de Configuração de Dias e Horários de Culto

**Versão:** 2.2.0  
**Data:** 14/10/2025  
**Status:** ✅ Implementado

---

## 🎯 **Nova Funcionalidade**

Sistema agora permite configurar **dias de culto** e **horários específicos** para cada comum de forma individual, com interface visual completa.

---

## 📋 **Acesso à Configuração**

### **Quem pode configurar:**
- ✅ **Master** (admin_master) - Pode configurar qualquer comum
- ✅ **Encarregado de Comum** - Pode configurar apenas seu próprio comum
- ❌ **Organistas** - Não têm acesso

### **Como acessar:**
1. Login no sistema
2. Aba **"👤 Usuários"**
3. Role para baixo até **"⚙️ Configurações do Comum Atual"**

---

## 🔧 **Configurando Dias e Horários**

### **Estrutura Visual:**

Cada dia da semana tem sua própria seção com:
- ☑️ **Checkbox** - Ativa/desativa o dia
- ⏰ **Campos de horário** - Adicione quantos horários precisar
- ➕ **Botão adicionar** - Adiciona novo horário
- ✕ **Botão remover** - Remove horário específico

---

## 📖 **Passo a Passo Detalhado**

### **1. Selecionar Dias de Culto**

Marque os dias que **TÊM culto** no seu comum:

```
☑️ ☀️ Domingo      ← Clique para ativar
☐ 📅 Segunda
☑️ 📅 Terça        ← Clique para ativar
☐ 📅 Quarta
☐ 📅 Quinta
☑️ 📅 Sexta        ← Clique para ativar
☐ 📅 Sábado
```

**O que acontece ao marcar um dia:**
- ✅ Abre seção de horários automaticamente
- ✅ Adiciona um horário padrão (09:00)
- ✅ Permite adicionar mais horários

---

### **2. Configurar Horários de Cada Dia**

#### **Exemplo 1: Domingo com 2 cultos**

```
☑️ ☀️ Domingo
   Horários:
   [09:00] ✕    ← Culto da manhã
   [18:00] ✕    ← Culto da noite
   ➕ Adicionar Horário
```

**Como adicionar:**
1. Clique em **"➕ Adicionar Horário"**
2. Digite o horário no campo: `18:00`
3. Clique fora do campo para confirmar

**Como remover:**
- Clique no botão **✕** ao lado do horário indesejado

---

#### **Exemplo 2: Terça com 1 culto**

```
☑️ 📅 Terça
   Horários:
   [19:30] ✕    ← Culto único
   ➕ Adicionar Horário
```

---

#### **Exemplo 3: Sexta com 1 culto**

```
☑️ 📅 Sexta
   Horários:
   [20:00] ✕    ← Culto de oração
   ➕ Adicionar Horário
```

---

### **3. Definir Período do Rodízio**

Configure as datas de início e fim da escala:

```
📆 Período do Rodízio:
[01/11/2025] até [31/12/2025]
```

**Dicas:**
- Use período de 1-3 meses normalmente
- Período anual também é possível
- Não pode ser retroativo (deve iniciar hoje ou no futuro)

---

### **4. Configurar Fechamento de Publicação**

Defina **quantos dias antes** do culto os organistas devem marcar indisponibilidade:

```
⏱️ Fechamento de Publicação:
[ 7 dias antes (padrão) ▼]
```

**Opções:**
- 3 dias antes - Fechamento rápido
- 5 dias antes - Balanceado
- **7 dias antes** - Recomendado ⭐
- 10 dias antes - Mais tempo
- 15 dias antes - Planejamento longo

**Exemplo prático:**
```
Culto: Domingo 15/12/2025
Fechamento: 7 dias antes
Último dia para marcar indisponibilidade: 08/12/2025
```

---

### **5. Salvar Configurações**

Clique no botão:
```
[💾 Salvar Todas as Configurações]
```

**Validações automáticas:**
- ✅ Pelo menos 1 dia marcado
- ✅ Cada dia marcado tem pelo menos 1 horário
- ✅ Período válido (fim > início)
- ✅ Horários ordenados automaticamente

**Após salvar:**
```
✅ Configurações salvas com sucesso!
```

---

## 💡 **Exemplos de Configuração**

### **Exemplo A: Comum Vila Paula**

```
☑️ Domingo
   [10:00] ✕  ← Culto matinal
   [19:00] ✕  ← Culto noturno

☑️ Terça
   [20:00] ✕  ← Culto de doutrina

☑️ Quinta
   [20:00] ✕  ← Culto de oração

📆 Período: 01/01/2025 até 28/02/2025
⏱️ Fechamento: 7 dias antes
```

**Resultado:**
- 4 cultos por semana
- 2 horários no domingo
- 1 horário nas terças e quintas
- Escala de 2 meses

---

### **Exemplo B: Comum Centro**

```
☑️ Domingo
   [09:30] ✕  ← Escola Dominical
   [18:00] ✕  ← Culto principal
   [20:00] ✕  ← Culto evangelístico

☑️ Quarta
   [19:30] ✕  ← Culto de jovens

☑️ Sexta
   [19:30] ✕  ← Culto de ensino

📆 Período: 15/11/2025 até 15/01/2026
⏱️ Fechamento: 10 dias antes
```

**Resultado:**
- 5 cultos por semana
- 3 horários no domingo
- Escala de 2 meses
- Fechamento com antecedência maior

---

### **Exemplo C: Comum Pequeno**

```
☑️ Domingo
   [19:00] ✕  ← Culto único

📆 Período: 01/12/2025 até 31/12/2025
⏱️ Fechamento: 3 dias antes
```

**Resultado:**
- 1 culto por semana
- Escala mensal
- Fechamento rápido (comum pequeno)

---

## 🔄 **Como o Sistema Usa as Configurações**

### **1. Geração de Escala**

Quando você cria uma nova escala, o sistema:

1. ✅ Lê os **dias de culto** configurados
2. ✅ Lê os **horários** de cada dia
3. ✅ Gera automaticamente todos os cultos do período
4. ✅ Distribui organistas conforme disponibilidade

**Exemplo:**
```
Configuração:
- Domingo: 10:00, 19:00
- Terça: 20:00
- Período: 01/11 até 07/11 (1 semana)

Escala gerada:
- 03/11 (Domingo) 10:00 → João
- 03/11 (Domingo) 19:00 → Maria
- 05/11 (Terça) 20:00 → Pedro
```

---

### **2. Indisponibilidades**

Organistas marcam indisponibilidade **até o fechamento**:

```
Culto: Domingo 15/12 às 19:00
Fechamento: 7 dias antes = 08/12
Organista pode marcar indisponível até: 08/12 23:59
Após 08/12: Sistema não permite alteração
```

---

### **3. Visualização**

Organistas veem apenas os cultos **configurados**:

```
🎹 Meus Dias de Rodízio

📅 Domingo 15/12
   ⏰ 10:00 - Culto Matinal
   ⏰ 19:00 - Culto Noturno

📅 Terça 17/12
   ⏰ 20:00 - Culto de Doutrina
```

---

## ⚙️ **Alterar Configurações Existentes**

### **Como Modificar:**

1. Acesse aba **"Usuários"**
2. Role até **"Configurações do Comum Atual"**
3. **Faça as alterações:**
   - Adicionar novo dia: Marcar checkbox
   - Remover dia: Desmarcar checkbox
   - Adicionar horário: Clicar **"➕ Adicionar Horário"**
   - Remover horário: Clicar no **✕**
   - Mudar período: Alterar datas
4. Clique **"💾 Salvar Todas as Configurações"**

---

### **⚠️ Impacto em Escalas Existentes:**

**IMPORTANTE:**
- ✅ Configurações se aplicam a **NOVAS escalas**
- ⚠️ Escalas já criadas **NÃO mudam automaticamente**
- 💡 Para aplicar mudanças: Criar nova escala

**Exemplo:**
```
Situação:
1. Configurou: Domingo 19:00
2. Criou escala para Novembro
3. Mudou para: Domingo 10:00, 19:00
4. Escala de Novembro ainda tem só 19:00

Solução:
- Criar nova escala para Dezembro (terá 10:00 e 19:00)
```

---

## 🧪 **Testando a Configuração**

### **Checklist de Teste:**

- [ ] 1. Login como Master ou Encarregado
- [ ] 2. Aba "Usuários"
- [ ] 3. Ver seção "Configurações do Comum Atual"
- [ ] 4. Marcar checkbox de um dia (ex: Domingo)
- [ ] 5. Ver campo de horário aparecer automaticamente
- [ ] 6. Clicar "➕ Adicionar Horário"
- [ ] 7. Ver segundo campo de horário aparecer
- [ ] 8. Preencher horários (ex: 09:00, 18:00)
- [ ] 9. Marcar mais dias se necessário
- [ ] 10. Preencher período
- [ ] 11. Escolher fechamento de publicação
- [ ] 12. Clicar "Salvar Todas as Configurações"
- [ ] 13. Ver notificação de sucesso
- [ ] 14. Recarregar página
- [ ] 15. Verificar se configurações foram mantidas

---

## 🐛 **Troubleshooting**

### **Problema: Não vejo os horários ao marcar dia**

**Causa:** JavaScript não carregou  
**Solução:**
```
1. Recarregar página (F5)
2. Limpar cache do navegador
3. Verificar console do navegador (F12)
```

---

### **Problema: Erro ao salvar**

**Causa:** Validação falhou  
**Verifique:**
- ✅ Pelo menos 1 dia marcado
- ✅ Cada dia tem pelo menos 1 horário
- ✅ Data fim > data início
- ✅ Horários no formato correto (HH:MM)

---

### **Problema: Configurações não aparecem após salvar**

**Solução:**
```bash
# Verificar no banco de dados
docker exec -it rodizio-organistas python3 -c "
import json
db = json.load(open('data/db.json', 'r'))
# Buscar seu comum
for r_id, regional in db['regionais'].items():
    for s_id, sub in regional['sub_regionais'].items():
        for c_id, comum in sub['comuns'].items():
            if c_id == 'vila_paula':  # Substituir pelo ID do seu comum
                print(json.dumps(comum.get('config', {}), indent=2))
"
```

---

### **Problema: Escala não usa novos horários**

**Causa:** Escala foi criada ANTES da configuração  
**Solução:**
```
1. Aba "Culto Oficial"
2. Criar nova escala
3. Nova escala usará configurações atualizadas
```

---

## 📊 **Estrutura no Banco de Dados**

```json
{
  "regionais": {
    "gru": {
      "sub_regionais": {
        "santa_isabel": {
          "comuns": {
            "vila_paula": {
              "nome": "Vila Paula",
              "config": {
                "dias_culto": ["Domingo", "Terça", "Quinta"],
                "horarios": {
                  "Domingo": ["10:00", "19:00"],
                  "Terça": ["20:00"],
                  "Quinta": ["20:00"]
                },
                "periodo": {
                  "inicio": "2025-11-01",
                  "fim": "2025-12-31"
                },
                "fechamento_publicacao_dias": 7
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

## 🎯 **Benefícios da Nova Funcionalidade**

### **Antes:**
- ❌ Dias fixos para todos os comuns
- ❌ Horários hardcoded no código
- ❌ Difícil personalizar por comum
- ❌ Necessário alterar código para mudar

### **Agora:**
- ✅ Cada comum escolhe seus dias
- ✅ Horários configuráveis via interface
- ✅ Total flexibilidade
- ✅ Mudanças sem tocar no código
- ✅ Interface visual intuitiva
- ✅ Múltiplos horários por dia
- ✅ Validação automática

---

## 📚 **Documentação Relacionada**

- `SISTEMA_COMPLETO.md` - Visão geral do sistema
- `GUIA_USUARIOS.md` - Guia para usuários finais
- `MANUAL_USO.md` - Manual de uso geral

---

**✅ FUNCIONALIDADE PRONTA!**  
**Teste agora: http://localhost:8080**

Login: `admin_master` / Senha: `admin123`  
Aba: **"👤 Usuários"** → **"⚙️ Configurações do Comum Atual"**
