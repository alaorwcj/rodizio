# 🚀 Guia Rápido - Sistema de Rodízio de Organistas

## ✅ Sistema Pronto!

O sistema está rodando em: **http://localhost:8080**

---

## 🔑 Como Fazer Login

### 1️⃣ Administrador (Acesso Total)
```
Usuário: admin
Senha: 123456
```

**O admin pode:**
- ✅ Gerenciar todas as organistas
- ✅ Ver e editar indisponibilidades de todas
- ✅ Configurar o sistema
- ✅ Gerar escalas

### 2️⃣ Organistas (Acesso Limitado)
```
Usuários disponíveis:
- ieda
- raquel
- yasmin.g
- milena

Senha para todas: 123456
```

**As organistas podem:**
- ✅ Marcar suas próprias indisponibilidades
- ✅ Ver a escala publicada

---

## 📱 Como Usar - ORGANISTA

### 1. Fazer Login
1. Acesse http://localhost:8080
2. Digite seu usuário (ex: `ieda`)
3. Digite a senha: `123456`
4. Clique em "🔐 Entrar"

### 2. Marcar Indisponibilidades
1. Clique na aba "🗓️ Minhas Indisponibilidades"
2. Veja o calendário do bimestre
3. **Verde** = Disponível | **Vermelho** = Indisponível
4. Clique numa data verde para marcar como indisponível
5. Clique numa data vermelha para desmarcar

> 💡 **Dica:** Só aparecem Domingos e Terças (dias de culto)

### 3. Ver Suas Indisponibilidades
- Na parte inferior do calendário aparecem todas as datas marcadas
- Para remover, basta clicar na data vermelha novamente

### 4. Sair
- Clique no botão "🚪 Sair" no topo

---

## 🔐 Como Usar - ADMINISTRADOR

### 1. Fazer Login
1. Acesse http://localhost:8080
2. Digite: `admin`
3. Senha: `123456`
4. Clique em "🔐 Entrar"

### 2. Gerenciar Organistas

#### Adicionar Nova Organista
1. Clique em "👥 Organistas"
2. Preencha o formulário:
   - **ID único** (ex: `maria`)
   - **Nome** (ex: `Maria Silva`)
   - **Tipos** (Ctrl+clique para múltiplos):
     - `Meia-hora` - toca antes do culto
     - `Culto` - toca durante o culto
     - Selecione ambos se a pessoa pode tocar nos dois
   - **Dias Permitidos** (Ctrl+clique):
     - `Domingo`
     - `Terça`
3. Clique em "Adicionar Organista"

#### Remover Organista
1. Na tabela de organistas
2. Clique em "Remover" na linha da pessoa
3. Confirme

### 3. Ver Todas as Indisponibilidades

1. Clique em "🗓️ Todas Indisponibilidades"
2. Veja lista agrupada por organista
3. Para remover uma indisponibilidade:
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

### Início do Bimestre (Admin)
1. Login como `admin`
2. Verificar/atualizar datas do bimestre em "⚙️ Configurações"
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
