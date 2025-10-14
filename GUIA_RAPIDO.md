# 🚀 Guia Rápido - Sistema de Rodízio de Organistas

## 🎹 Vila Paula - Versão 1.0

Sistema está rodando em: **http://localhost:8080**

---

## 🔑 Como Fazer Login

### 1️⃣ Administrador (Acesso Total)
```
Usuário: admin
Senha: admin123
```

⚠️ **IMPORTANTE**: Troque a senha no primeiro acesso!

**O admin pode:**
- ✅ Gerenciar organistas (adicionar, remover)
- ✅ Criar e editar escalas manualmente
- ✅ Ver todas as indisponibilidades
- ✅ Configurar datas do bimestre
- ✅ Exportar PDF da escala
- ✅ Ver todas as próximas escalas

### 2️⃣ Organistas (Acesso Limitado)

**Credenciais fornecidas pelo administrador**

⚠️ **IMPORTANTE**: Troque a senha no primeiro acesso!

**Os organistas podem:**
- ✅ Marcar suas próprias indisponibilidades
- ✅ Ver a escala completa
- ✅ Ver "Meus Dias de Rodízio" (apenas suas datas)
- ✅ Trocar senha a qualquer momento

---

## 📱 Como Usar - ORGANISTA

### 1. Primeiro Acesso
1. Acesse http://localhost:8080
2. Digite seu usuário (fornecido pelo admin)
3. Digite a senha temporária
4. Clique em "🔐 Entrar"
5. **Importante**: Clique em "🔐 Trocar Senha"
6. Preencha:
   - Senha atual
   - Nova senha (mínimo 6 caracteres)
   - Confirmar nova senha
7. Clique em "✓ Alterar Senha"

### 2. Ver "Meus Dias de Rodízio"
1. No Dashboard inicial
2. Veja apenas os dias que você vai tocar
3. Cards com destaque verde:
   - ✓ "Você" indica seus serviços
   - Data, dia da semana e horário
4. Filtro automático (só mostra datas futuras)

### 3. Marcar Indisponibilidades
1. Clique na aba "📅 Todas Indisponibilidades"
2. Veja o calendário organizado por mês
3. Clique nas datas que não pode tocar
4. Botão "Adicionar Indisponibilidade"
5. Sistema bloqueia automaticamente na escala

### 4. Ver Escala Completa
1. Acesse aba "📅 Escala" (somente leitura)
2. Veja toda a programação do bimestre
3. Separado por mês
4. Cores: Verde (Domingo), Amarelo (Terça)

### 5. Sair
- Clique no botão "🚪 Sair" no topo

---

## 🔐 Como Usar - ADMINISTRADOR

### 1. Primeiro Acesso
1. Acesse http://localhost:8080
2. Digite: `admin`
3. Senha: `admin123`
4. **IMPORTANTE**: Clique em "🔐 Trocar Senha" e altere imediatamente

### 2. Configurar Período
1. Clique em "⚙️ Configurações"
2. Defina:
   - Data de início do período (ex: 01/01/2025 para anual)
   - Data de fim do período (ex: 31/12/2025 para anual)
   - Prazo para indisponibilidades (padrão: 3 dias)
3. Clique em "💾 Salvar Configurações"
4. Sistema recarrega automaticamente

### 3. Gerenciar Organistas

#### Adicionar Organista
1. Clique em "👥 Organistas"
2. Preencha:
   - **ID único** (ex: `maria`) - usado para login
   - **Nome** (ex: `Maria Silva`) - nome completo
   - **Tipos** (Ctrl+clique para múltiplos):
     - `Meia-hora` - toca 30min antes
     - `Culto` - toca durante o culto
     - Selecione ambos para "Ambos"
   - **Dias Permitidos** (Ctrl+clique):
     - `Domingo`
     - `Terça`
     - Selecione ambos se pode tocar nos dois dias
3. Clique em "Adicionar Organista"
4. Senha inicial será: `123456` (organista deve trocar)

#### Remover Organista
1. Na tabela, clique em "Remover"
2. Confirme a ação

### 4. Criar Escala Manual

#### Criar Escala Vazia
1. Clique em "📅 Escala"
2. Clique em "Criar Escala Vazia"
3. Sistema gera:
   - Todos os domingos do período configurado
   - Todas as terças do período configurado
   - 2 posições por dia (Meia-hora + Culto)

#### Preencher Manualmente
1. Use os dropdowns para selecionar organistas
2. Dropdowns inteligentes:
   - ✓ Nome normal: Disponível
   - ~~Nome~~ (vermelho): Indisponível (bloqueado)
   - Nome (italic): Sem permissão de fase (bloqueado)
3. **Sistema valida automaticamente**:
   - Meia-hora: Só mostra quem pode tocar "Meia-hora" ou "Ambos"
   - Culto: Só mostra quem pode tocar "Culto" ou "Ambos"
4. Pode ser a mesma pessoa nos dois (se tiver "Ambos")

#### Salvar Alterações
1. Preencha todos os dropdowns necessários
2. Clique em "💾 Salvar Todas as Alterações"
3. Sistema salva tudo de uma vez
4. Dashboard atualiza automaticamente

### 5. Exportar PDF
1. Na aba "📅 Escala"
2. Clique em "📄 Exportar PDF"
3. PDF baixa automaticamente
4. Layout profissional, pronto para impressão

### 6. Ver Todas as Indisponibilidades
1. Clique em "� Todas Indisponibilidades"
2. Veja lista por organista
3. Pode adicionar indisponibilidades para qualquer organista
   - Clique no **✕** ao lado da data
   - Confirme a remoção

### 4. Configurar o Sistema

1. Clique em "⚙️ Configurações"
2. Ajuste:
   - **Data de Início do Bimestre**
   - **Data de Fim do Bimestre**
   - **Prazo para marcar indisponibilidade** (dias antes da publicação)
3. Clique em "💾 Salvar Configurações"
4. **Importante:** Recarregue a página (F5)

---

## 🗓️ Formato de Datas

✅ Todas as datas estão no formato brasileiro:
- **dd/mm/aaaa** (ex: 14/10/2025)
- **HH:mm** para horários (ex: 15:30)

---

## 📊 Entendendo o Dashboard

### Status Atual
- ✅ **X organista(s) cadastrado(s)** - Total de organistas no sistema
- ✅ **X indisponibilidade(s) marcada(s)** - Total de datas indisponíveis
- 📋 **Escala** - Status da escala (será implementado na Fase 2)

---

## 🎯 Fluxo Típico de Uso

### Início do Período (Admin)
1. Login como `admin`
2. Verificar/atualizar datas do período em "⚙️ Configurações"
3. Verificar lista de organistas em "👥 Organistas"
4. Comunicar às organistas para marcarem indisponibilidades

### Marcação de Indisponibilidades (Organistas)
1. Cada organista faz login
2. Marca suas datas indisponíveis
3. Pode alterar até X dias antes da publicação

### Geração da Escala (Admin - Futuro)
1. Admin revisa indisponibilidades em "🗓️ Todas Indisponibilidades"
2. Clica em "Gerar Escala" (Fase 2)
3. Sistema distribui automaticamente respeitando:
   - Indisponibilidades
   - Regras especiais
   - Justiça na distribuição
4. Admin ajusta manualmente se necessário
5. Publica a escala

---

## ⚠️ Dicas Importantes

### Para Organistas
- ⚠️ Marque suas indisponibilidades com antecedência
- ⚠️ Só é possível marcar datas dentro do bimestre configurado
- ⚠️ Após a publicação da escala, alterações precisam de aprovação do admin
- ✅ Você pode marcar/desmarcar quantas vezes quiser antes da publicação

### Para Admin
- 🔐 **Nunca compartilhe a senha de admin**
- 💾 Faça backup regular do `db.json`
- 📊 Revise as indisponibilidades antes de gerar a escala
- ⚙️ Configure o prazo adequado para marcação de indisponibilidades
- 👥 Ao adicionar uma organista, a senha padrão é `123456`

---

## 🆘 Problemas Comuns

### ❌ Não consigo fazer login
- Verifique se digitou o usuário corretamente (minúsculas)
- Senha padrão: `123456`
- Se esqueceu a senha alterada, contate o administrador

### ❌ Não vejo o calendário
- Organistas: certifique-se de estar na aba "🗓️ Minhas Indisponibilidades"
- Admin vê mensagem informativa (use "🗓️ Todas Indisponibilidades")

### ❌ Calendário está vazio
- Verifique se o bimestre está configurado corretamente
- Apenas Domingos e Terças aparecem no calendário

### ❌ Não consigo adicionar organista
- Verifique se você está logado como `admin`
- O ID da organista deve ser único
- Preencha todos os campos obrigatórios

---

## 🔄 Atualizações Futuras

### Fase 2 (Em Desenvolvimento)
- Geração automática de escala
- Algoritmo de distribuição justa
- Edição manual da escala

### Fase 3 (Planejado)
- Exportação para PDF
- Exportação para Excel
- Impressão otimizada

---

## 📞 Suporte

Se precisar de ajuda:
1. Verifique este guia primeiro
2. Veja os logs: `docker-compose logs -f`
3. Reinicie o sistema: `docker-compose restart`

---

**🎹 Sistema de Rodízio de Organistas v2.0**  
*Desenvolvido para facilitar a gestão de escalas*
