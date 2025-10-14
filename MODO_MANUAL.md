# 🎹 Sistema de Escala Manual - Guia Completo

## 📋 Visão Geral

O sistema agora opera em **modo 100% manual**, permitindo que o administrador tenha controle total sobre as alocações dos organistas.

## ✅ O Que Foi Alterado

### ❌ Removido
- ~~Botão "Gerar Escala Automaticamente"~~
- ~~Algoritmo de geração automática~~
- ~~Logs de geração~~
- ~~Preview de escala antes de publicar~~

### ✅ Mantido
- ✔️ CRUD completo de organistas
- ✔️ Gerenciamento de indisponibilidades
- ✔️ Edição manual via dropdowns
- ✔️ Exportação para PDF
- ✔️ Controle de fases (Meia-hora / Culto)
- ✔️ Visualização separada por mês
- ✔️ Estatísticas da escala

### 🆕 Adicionado
- ✨ **Botão "Criar Nova Escala"**: Gera estrutura vazia com todas as datas do bimestre
- 🚫 **Bloqueio inteligente nos dropdowns**:
  - Organistas indisponíveis aparecem com ~~tachado~~ e "(indisponível)"
  - Organistas sem habilitação para a fase aparecem em *vermelho itálico* e "(não habilitado)"
  - Não é possível selecionar organistas bloqueados

## 🎯 Como Usar

### 1. Criar Nova Escala

1. Faça login como **administrador**
2. Vá até a seção **"Gerenciamento de Escala"**
3. Clique em **"➕ Criar Nova Escala"**
4. O sistema criará automaticamente uma escala vazia com:
   - Todos os **domingos** do bimestre (com colunas Meia-hora e Culto)
   - Todas as **terças-feiras** do bimestre (com coluna única)

### 2. Preencher Manualmente

1. Para cada data, use os **dropdowns** para selecionar:
   - **Domingo**: 
     - Meia-hora (30min antes)
     - Culto (durante o culto)
   - **Terça-feira**:
     - Uma única pessoa (cobre ambas as fases)

2. Observe os indicadores:
   - ✅ **Nome normal**: Disponível e habilitado
   - ~~Tachado~~ **(indisponível)**: Organista marcou indisponibilidade nesta data
   - *Vermelho itálico* **(não habilitado)**: Organista não tem esta fase habilitada

3. Clique em **"💾 Salvar"** após cada edição

### 3. Exportar PDF

Após preencher a escala, clique em **"📄 Exportar PDF"** para gerar o documento.

## 🔐 Controle de Fases

O sistema respeita rigorosamente as **atribuições de fase** de cada organista:

### Exemplo de Configuração

```json
{
  "id": "yasminc",
  "nome": "Yasmin C.",
  "tipos": ["Meia-hora"],          // ← Só pode tocar na Meia-hora
  "dias_permitidos": ["Domingo"]
}

{
  "id": "milena",
  "nome": "Milena",
  "tipos": ["Meia-hora", "Culto"], // ← Pode tocar em ambas as fases
  "dias_permitidos": ["Domingo", "Terça"]
}
```

### Regras Aplicadas

1. **Yasmin C.** só aparecerá disponível para **Meia-hora** nos domingos
2. **Yasmin C.** aparecerá como *"(não habilitado)"* para **Culto**
3. **Milena** pode tocar em qualquer fase (Meia-hora, Culto, Terça)

## 🚫 Bloqueio por Indisponibilidade

Quando um organista marca indisponibilidade:

1. O nome aparece ~~tachado~~ no dropdown
2. Aparece o sufixo **(indisponível)**
3. **Não pode ser selecionado** (opção desabilitada)
4. Se já estava alocado, **permanece** mas com aviso visual

## 📊 Estatísticas

O sistema continua calculando:
- Total de alocações por organista
- Distribuição Meia-hora vs Culto vs Terça
- Domingos e Terças separadamente

## 🔧 Configurações

### Atualizar Período do Bimestre

1. Vá até **"Configurações"**
2. Altere as datas:
   - **Data Início**: Primeiro dia do bimestre
   - **Data Fim**: Último dia do bimestre
3. Clique em **"Salvar Configurações"**
4. Crie uma nova escala para refletir o novo período

## 💡 Dicas

- ✅ Crie a escala no início do bimestre
- ✅ Verifique as indisponibilidades ANTES de alocar
- ✅ Use as cores como guia (verde = Meia-hora, azul = Culto, amarelo = Terça)
- ✅ Exporte o PDF apenas quando a escala estiver completa
- ✅ Use "Carregar Escala Atual" para voltar à última versão salva

## 🆘 Problemas Comuns

### "Não consigo selecionar um organista"

**Causas possíveis:**
1. Organista marcou indisponibilidade nesta data
2. Organista não tem habilitação para esta fase (ex: só toca Meia-hora)
3. Organista não tem permissão para este dia (ex: só toca Domingos)

**Solução:** Verifique a configuração do organista ou remova a indisponibilidade.

### "Perdi as alterações"

**Causa:** Não clicou em "Salvar" após editar.

**Solução:** Sempre clique em "💾 Salvar" após cada edição de data.

---

## 📝 Resumo das Ações Disponíveis

| Ação | Descrição | Acesso |
|------|-----------|--------|
| **Criar Nova Escala** | Gera estrutura vazia do bimestre | Admin |
| **Carregar Escala Atual** | Carrega última escala salva | Todos |
| **Editar Alocação** | Alterar organista via dropdown | Admin |
| **Salvar Edição** | Confirmar alteração | Admin |
| **Exportar PDF** | Gerar documento para impressão | Todos |
| **Ver Estatísticas** | Visualizar distribuição | Todos |

---

✅ **Sistema atualizado em**: 14/10/2025
