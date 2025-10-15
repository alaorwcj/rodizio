# 📖 Manual de Uso - Sistema de Rodízio de Organistas

## 🎯 Visão Geral

Sistema para gerenciar a escala bimestral de organistas, com:
- **Geração automática** de escalas respeitando indisponibilidades
- **Visualização separada por mês** para melhor organização
- **Controle de acesso**: Admin tem controle total, organistas marcam apenas suas indisponibilidades

---

## 👥 Tipos de Usuários

### 🔑 Administrador
**Login**: `admin` | **Senha**: `123456`

**Permissões**:
- ✅ Gerenciar organistas (adicionar/editar/remover)
- ✅ Visualizar todas as indisponibilidades
- ✅ Configurar período bimestral
- ✅ **Gerar escala automática**
- ✅ **Editar escala manualmente** (trocar organistas a qualquer momento)
- ✅ **Publicar escala**

### 🎹 Organistas
**Logins disponíveis**: `ieda`, `raquel`, `yasmin.g`, `milena` | **Senha**: `123456`

**Permissões**:
- ✅ Marcar suas próprias indisponibilidades
- ✅ Visualizar a escala publicada
- ❌ Não pode gerar ou editar escalas

---

## 📅 Entendendo a Escala

### Estrutura dos Cultos

**Domingos**:
- **Meia-hora**: Período antes do culto (30 minutos)
- **Culto**: Período principal do culto
- São **duas posições separadas**, podem ser organistas diferentes

**Terças-feiras**:
- **Única posição**: A mesma organista cobre meia-hora e culto

### Regras Especiais

O sistema já aplica automaticamente:
- **Indisponibilidades**: Organistas marcadas como indisponíveis não são alocadas
- **Distribuição justa**: O algoritmo equilibra as alocações entre todas
- **Regras específicas** (ex: Ieda em dias ímpares de outubro, pares de novembro)
- **Fallback inteligente**: Se não há organista para Meia-hora, quem está no Culto cobre ambas

---

## 🚀 Como Usar (Administrador)

### 1️⃣ Configurar o Bimestre

1. Faça login como **admin**
2. Vá na aba **"Configurações"**
3. Defina:
   - Data de início do bimestre (ex: 01/10/2025)
   - Data de fim do bimestre (ex: 30/11/2025)
   - Prazo para marcar indisponibilidade
4. Clique em **"💾 Salvar Configurações"**

### 2️⃣ Gerenciar Organistas

1. Vá na aba **"Organistas"**
2. Para adicionar:
   - Preencha nome, tipos (Meia-hora/Culto), dias permitidos (Domingo/Terça)
   - Configure regras especiais se necessário
   - Clique em **"Adicionar Organista"**
3. Para editar/remover: Use os botões ✏️ ou 🗑️

### 3️⃣ Monitorar Indisponibilidades

1. Vá na aba **"Todas Indisponibilidades"**
2. Filtre por organista para ver detalhes
3. Use **"🔄 Atualizar"** para recarregar

### 4️⃣ Gerar Escala Automaticamente

1. Vá na aba **"Escala"**
2. Clique em **"🎲 Gerar Escala Automaticamente"**
3. O sistema irá:
   - Buscar todos os domingos e terças do bimestre
   - Aplicar as regras de negócio
   - Distribuir de forma justa
   - Mostrar **logs de decisão**
4. Revise a escala gerada (separada por mês)
5. Veja as **estatísticas** de distribuição

### 5️⃣ Editar Manualmente (Quando Necessário)

**IMPORTANTE**: Você pode editar a escala **a qualquer momento**, mesmo após publicada!

Para cada dia:
1. Localize a linha na tabela (organizada por mês)
2. Use os **dropdowns** para trocar a organista
3. Clique em **"💾 Salvar"** na mesma linha
4. A alteração é salva imediatamente

**Exemplo de uso**:
- Uma organista avisou que não pode em determinado dia
- Você precisa trocar Meia-hora ou Culto
- Basta selecionar outra organista no dropdown e salvar

### 6️⃣ Publicar Escala

1. Após revisar e fazer ajustes necessários
2. Clique em **"✅ Publicar Escala"**
3. Confirme a publicação
4. A escala fica visível para todas as organistas

### 7️⃣ Recarregar Escala Atual

- Use **"🔄 Carregar Escala Atual"** para ver a última escala publicada
- Útil para verificar o estado atual

---

## 🎹 Como Usar (Organista)

### 1️⃣ Marcar Indisponibilidades

1. Faça login com seu usuário (ex: `ieda`)
2. Vá na aba **"Minhas Indisponibilidades"**
3. Clique nas datas do calendário onde você **NÃO** estará disponível
4. As datas indisponíveis ficam **vermelhas**
5. Clique novamente para remover a indisponibilidade

**Dicas**:
- Marque com antecedência
- Apenas domingos e terças aparecem no calendário
- Verde = Disponível | Vermelho = Indisponível

### 2️⃣ Visualizar Escala

1. Vá na aba **"Escala"**
2. Veja a escala publicada organizada por mês
3. Confira suas alocações:
   - **Domingos**: Meia-hora e/ou Culto
   - **Terças**: Ambos períodos

---

## 📊 Visualização por Mês

A escala é exibida separadamente para cada mês:

```
📅 Outubro de 2025
┌─────────────┬───────────┬─────────────┬─────────┬────────┐
│ Data        │ Dia       │ Meia-hora   │ Culto   │ Ações  │
├─────────────┼───────────┼─────────────┼─────────┼────────┤
│ 05/10/2025  │ Domingo   │ Ieda        │ Raquel  │ 💾     │
│ 07/10/2025  │ Terça     │ Milena      │         │ 💾     │
└─────────────┴───────────┴─────────────┴─────────┴────────┘

📅 Novembro de 2025
┌─────────────┬───────────┬─────────────┬─────────┬────────┐
│ Data        │ Dia       │ Meia-hora   │ Culto   │ Ações  │
├─────────────┼───────────┼─────────────┼─────────┼────────┤
│ 02/11/2025  │ Domingo   │ Yasmin      │ Ieda    │ 💾     │
└─────────────┴───────────┴─────────────┴─────────┴────────┘
```

**Benefícios**:
- ✅ Visualização mais clara
- ✅ Fácil de imprimir por mês
- ✅ Melhor organização
- ✅ Mantém geração bimestral automática

---

## 🎨 Cores e Indicadores

- **Verde claro**: Linha de domingo
- **Amarelo claro**: Linha de terça-feira
- **Gradiente roxo**: Cabeçalhos e títulos
- **Hover**: Destaque ao passar o mouse

---

## 🔧 Manutenção

### Alterar Senhas

Edite o arquivo `update_db_passwords.py` e execute:
```bash
docker-compose exec rodizio-app python update_db_passwords.py
docker-compose restart
```

### Backup do Banco

```bash
cp data/db.json data/db_backup_$(date +%Y%m%d).json
```

### Ver Logs

```bash
docker-compose logs -f rodizio-app
```

---

## ❓ Perguntas Frequentes

**P: Posso editar a escala após publicar?**
R: ✅ Sim! O admin pode editar a qualquer momento usando os dropdowns.

**P: Como desfazer uma alocação?**
R: Selecione "-- Selecione --" no dropdown e salve.

**P: A escala respeita as indisponibilidades?**
R: ✅ Sim, automaticamente. Organistas indisponíveis não são alocadas.

**P: Posso gerar uma nova escala?**
R: ✅ Sim, mas sobrescreverá a anterior. Faça backup se necessário.

**P: Como funciona a distribuição justa?**
R: O algoritmo conta quantas vezes cada organista foi alocada e prioriza quem tem menos alocações.

---

## 🆘 Suporte

**Problemas técnicos**: Verifique logs com `docker-compose logs`
**Dúvidas de uso**: Consulte este manual
**Container não inicia**: Execute `docker-compose down && docker-compose up -d --build`

---

**Versão**: 2.0 - Fase 2 Completa
**Data**: Outubro 2025
