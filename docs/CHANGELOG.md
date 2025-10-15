# 📝 Changelog - Sistema de Rodízio de Organistas

## Versão 2.3.0 - Melhorias em Cadastro
**Data**: 14 de Outubro de 2025

### 🎯 **MELHORIAS - Fluxo de Cadastro Otimizado**

#### **Configuração no Cadastro do Comum**
- **Criar comum já configurado** - Dias e horários definidos NA MESMA TELA
  - ✅ Modal expandido com checkboxes de dias
  - ✅ Campos de horário inline (formato: `09:00, 18:00`)
  - ✅ Validação automática de formato HH:MM
  - ✅ Seleção de fechamento de publicação (3-15 dias)
  - ✅ Comum nasce completamente configurado
  - ✅ Elimina necessidade de configurar depois

#### **Seletor de Contexto para Organistas (Master)**
- **Master escolhe qual comum** ao cadastrar organista
  - ✅ Novo campo "📍 Comum" no formulário (visível só para Master)
  - ✅ Lista todos os comuns disponíveis (Regional › Sub › Comum)
  - ✅ Dias Permitidos carregam automaticamente do comum selecionado
  - ✅ Encarregados continuam cadastrando apenas no próprio comum
  - ✅ Fluxo mais rápido (sem trocar contexto)

#### **Melhorias Técnicas**
- **Backend:**
  - `criar_comum()` aceita objeto `config` no payload
  - Mescla configuração fornecida com padrão
  - Validação robusta de estrutura

- **Frontend:**
  - `toggleModalHorarios()` - Mostra/oculta campos de horário
  - `carregarComunsParaOrganista()` - Popula dropdown de comuns
  - `carregarDiasDoComum()` - Carrega dias do comum selecionado
  - `criarComum()` - Valida e envia config completa

#### **Benefícios**
- ⚡ **Menos cliques** - Criar + configurar em 1 etapa
- 🎯 **Impossível esquecer** - Config obrigatória na criação
- 🚀 **Master mais produtivo** - Cadastra em qualquer comum direto
- 📊 **Consistência** - Dias sempre sincronizados com o comum

**Documentação:** Ver `FEATURE_CADASTRO_V2.md`

---

## Versão 2.2.0 - Gestão de Horários
**Data**: 14 de Outubro de 2025

### 🎉 **NOVA FUNCIONALIDADE - Administração de Horários**
- **Interface completa para configurar dias e horários de culto por comum**
  - ✅ Cada dia da semana pode ter múltiplos horários
  - ✅ Adicionar/remover horários dinamicamente via interface
  - ✅ Validação automática (horários obrigatórios para dias marcados)
  - ✅ Ordenação automática dos horários
  - ✅ Visual intuitivo com cards expansíveis por dia
  - ✅ Suporta configurações individuais por comum
  - ✅ Configuração de fechamento de publicação (3-15 dias antes)
  
- **Funcionalidades:**
  - 📅 Checkbox para ativar/desativar cada dia da semana
  - ⏰ Campos de horário com formato HH:MM
  - ➕ Botão para adicionar múltiplos horários no mesmo dia
  - ✕ Botão para remover horários específicos
  - 💾 Salvamento com validação completa
  - 🔄 Carregamento automático de configurações existentes
  
- **Estrutura de dados:**
  - `dias_culto`: Array de dias ativos
  - `horarios`: Objeto com arrays de horários por dia
  - `fechamento_publicacao_dias`: Dias antes para fechar publicação
  - `periodo`: Data início e fim da escala

- **Documentação:** Ver `CONFIGURACAO_HORARIOS.md`

---

## Versão 2.1.1 - Hotfix Autenticação
**Data**: 14 de Outubro de 2025

### 🐛 **BUGFIX CRÍTICO**
- **Autenticação de Usuários**: Corrigido bug que impedia login de usuários criados via interface
  - **Causa**: Campo `senha_hash` na criação vs `password_hash` no login
  - **Solução**: Padronizado `password_hash` em todo código + script de migração
  - **Impacto**: Todos os usuários criados desde v2.1 precisavam de migração
  - **Arquivo**: `fix_password_field.py` - migração automática com backup
  - **Documentação**: Ver `BUGFIX_AUTENTICACAO.md` para detalhes completos

---

## Versão 1.1 - Escala Anual
**Data**: 14 de Outubro de 2025

### 🎯 Mudanças Principais
- ✅ **Período Flexível**: Sistema agora suporta qualquer período (não apenas bimestral)
- ✅ Possibilidade de configurar escala anual completa (01/01 a 31/12)
- ✅ Interface atualizada: "Bimestre" → "Período" em todos os textos
- ✅ Documentação atualizada para refletir a nova flexibilidade
- ✅ **Funcionalidade de Agenda**: Organistas podem adicionar eventos à agenda externa
  - Suporte para Google Calendar, Outlook, Apple Calendar
  - Formato iCalendar (.ics) universal
  - Horários corretos: Domingos 18h, Terças 19h
  - Lembrete automático 1 hora antes

### 📅 Eventos da Agenda
- **Domingos**: Meia-hora (18:00-18:30) + Culto (18:30-20:00)
- **Terças**: Meia-hora (19:00-19:30) + Culto (19:30-21:00)
- Botão "📅 Adicionar à Agenda" nos cards de "Meus Dias de Rodízio"

### 🎨 Melhorias Visuais
- Ícones animados (GIF) para botões PDF e WhatsApp
- Botão de agenda com hover effect

---

## Versão 1.0 - Release Inicial
**Data**: 14 de Outubro de 2025

---

## 🎉 Funcionalidades Principais

### 🔐 Sistema de Autenticação
- ✅ Login com usuário e senha
- ✅ Perfis: Administrador e Organista
- ✅ Senhas criptografadas (Werkzeug pbkdf2:sha256)
- ✅ Troca de senha para todos os usuários
- ✅ Sessões seguras com Flask-Login
- ✅ Logout com confirmação

### 👥 Gestão de Organistas (Admin)
- ✅ CRUD completo de organistas
- ✅ Tipos de permissão: Meia-hora, Culto, Ambos
- ✅ Dias permitidos: Domingo, Terça, Ambos
- ✅ ID único para login
- ✅ Validações de negócio

### 📅 Gestão de Indisponibilidades
- ✅ Organistas marcam datas indisponíveis
- ✅ Calendário simplificado por mês
- ✅ Mostra apenas domingos e terças
- ✅ Validação de datas (dentro do bimestre)
- ✅ Admin pode gerenciar todas as indisponibilidades

### 📊 Sistema de Escala Manual
- ✅ Criação de escala vazia para o bimestre
- ✅ Geração automática de domingos e terças
- ✅ Sistema de 2 fases (Meia-hora + Culto) para TODOS os dias
- ✅ Seleção manual via dropdowns inteligentes
- ✅ Validações automáticas:
  - ✓ Bloqueio de indisponíveis
  - ✓ Bloqueio por falta de permissão de fase
  - ✓ Validação de dias permitidos
- ✅ Indicações visuais nos dropdowns:
  - Nome normal: Disponível
  - ~~Strikethrough vermelho~~: Indisponível
  - Italic vermelho: Sem permissão + sufixo
- ✅ Botão único "Salvar Todas as Alterações"
- ✅ Salvamento em batch (todas as alterações de uma vez)

### 📱 Dashboard Personalizado
- ✅ **Para Admin**: "📅 Próximas Escalas"
  - Mostra próximas 10 escalas
  - Todas as datas futuras
  - Cards coloridos por tipo de dia
- ✅ **Para Organista**: "🎹 Meus Dias de Rodízio"
  - Mostra apenas os dias do organista logado
  - Filtro automático (só datas futuras)
  - Destaque verde nos serviços
  - ✓ "Você" nos cards
- ✅ Cards responsivos em grid
- ✅ Informações claras: Data, dia da semana, serviços

### 📄 Exportação PDF
- ✅ Geração de PDF profissional
- ✅ Separação por mês
- ✅ Tabela organizada: Data, Dia, Meia-hora, Culto
- ✅ Layout limpo (sem textos desnecessários)
- ✅ Pronto para impressão
- ✅ Download automático

### ⚙️ Configurações do Sistema (Admin)
- ✅ Configuração de datas do bimestre
- ✅ Prazo para marcação de indisponibilidades
- ✅ Atualização automática ao salvar
- ✅ Recarga da página para atualizar todas as datas

### 🎨 Interface do Usuário
- ✅ Design moderno com gradientes
- ✅ Header personalizado: "🎹 Rodízio de Organistas - Vila Paula"
- ✅ Navegação por abas
- ✅ Cards com sombras e hover effects
- ✅ Cores diferenciadas:
  - Verde: Domingos
  - Amarelo: Terças
  - Roxo: Admin/Sistema
- ✅ Responsivo (mobile-friendly)
- ✅ Feedback visual de ações

---

## 🔄 Decisões de Design

### Sistema Manual (Não Automático)
**Decisão**: O sistema gera estrutura vazia, mas seleção é 100% manual.

**Motivo**: 
- Maior controle do administrador
- Flexibilidade para casos especiais
- Evita conflitos com preferências não capturadas
- Mais simples de entender e usar

### Dashboard por Perfil
**Decisão**: Admin vê todas as escalas, Organista vê apenas seus dias.

**Motivo**:
- Organistas só precisam saber quando vão tocar
- Reduz informação desnecessária
- Melhor experiência do usuário
- Foco no que é relevante

### Dropdowns Inteligentes
**Decisão**: Dropdowns mostram e bloqueiam automaticamente.

**Motivo**:
- Previne erros de alocação
- Validação visual imediata
- Impossibilita seleção inválida
- Transparência nas restrições

### Botão Único de Salvar
**Decisão**: Um único botão salva todas as alterações.

**Motivo**:
- UX mais simples
- Menos clicks
- Operação atômica
- Menos chance de esquecer de salvar

### Estrutura de 2 Fases para Todos os Dias
**Decisão**: Domingos E Terças têm Meia-hora + Culto.

**Motivo**:
- Consistência na estrutura
- Flexibilidade (podem ser pessoas diferentes)
- Mesmo modelo para ambos os tipos de dia
- Permite otimizar uso de recursos

---

## 📊 Tecnologias Utilizadas

### Backend
- Python 3.11
- Flask 3.0.0
- Flask-Login 0.6.3
- Werkzeug 3.0.1 (hash de senhas)
- ReportLab 4.0.7 (geração de PDF)
- Gunicorn 21.2.0 (servidor WSGI)

### Frontend
- HTML5
- CSS3 (com gradientes e animações)
- JavaScript (Vanilla, Fetch API)
- Design responsivo

### Infraestrutura
- Docker (multi-stage build)
- Docker Compose
- Python 3.11-slim
- Volume persistente para dados

### Banco de Dados
- JSON file (data/db.json)
- Estrutura simples e fácil de auditar
- Backups simples (cópia de arquivo)

---

## 🔒 Segurança

### Implementado
- ✅ Senhas criptografadas (Werkzeug pbkdf2:sha256)
- ✅ Salt automático por senha
- ✅ Sessões seguras (Flask-Login)
- ✅ @login_required em rotas protegidas
- ✅ Validações no backend
- ✅ Sanitização de inputs
- ✅ Usuário não-root no Docker
- ✅ Health checks configurados

### Recomendações Futuras
- [ ] HTTPS obrigatório
- [ ] Rate limiting
- [ ] Logs de segurança
- [ ] Backup automático
- [ ] 2FA (autenticação de dois fatores)

---

## 🐛 Correções e Melhorias

### Correções Importantes
1. **Unificação da estrutura de dados**: Terças agora usam meia_hora/culto (antes usava "unica")
2. **Validação de fase**: Dropdowns respeitam permissões (Meia-hora/Culto/Ambos)
3. **Atualização automática**: Ao salvar configurações, página recarrega
4. **Filtro de dashboard**: Organistas veem apenas seus dias
5. **Bloqueio de indisponíveis**: Visual claro e bloqueio efetivo

### Melhorias de UX
1. **Cards mais compactos**: Layout em grid responsivo
2. **Textos simplificados**: Removido texto explicativo redundante
3. **Headers limpos**: Apenas informação essencial
4. **Calendário simplificado**: Organizado por mês/semana/dia
5. **Página de login limpa**: Sem credenciais expostas

---

## 📈 Métricas do Sistema

### Performance
- Tempo de carregamento inicial: < 1s
- Tamanho da imagem Docker: ~150MB
- Workers Gunicorn: 2
- Threads por worker: 4
- Timeout: 120s

### Capacidade
- Organistas suportados: Ilimitado (prático: ~20)
- Indisponibilidades: Ilimitadas
- Escalas: 1 bimestre por vez (60 dias típico)
- Histórico: Mantido em logs

---

## 🚀 Próximos Passos (Roadmap)

### Fase 2: Exportação Excel
- [ ] Geração de arquivo .xlsx
- [ ] Formatação condicional
- [ ] Múltiplas planilhas (por mês)
- [ ] Estatísticas incluídas

### Fase 3: Banco SQL
- [ ] Migração para SQLite
- [ ] Queries mais eficientes
- [ ] Relacionamentos definidos
- [ ] Backup mais robusto

### Fase 4: Notificações
- [ ] Email de lembrete
- [ ] Notificação de nova escala
- [ ] Aviso de prazo de indisponibilidade

### Fase 5: Melhorias de UX
- [ ] PWA (Progressive Web App)
- [ ] Modo offline
- [ ] Notificações push
- [ ] App mobile nativo

### Fase 6: Relatórios
- [ ] Estatísticas de participação
- [ ] Gráficos de distribuição
- [ ] Histórico de escalas
- [ ] Análise de tendências

---

## 🙏 Agradecimentos

Sistema desenvolvido para a **Igreja Vila Paula**, com o objetivo de facilitar a gestão da escala de organistas.

**Versão**: 1.0  
**Data**: 14/10/2025  
**Status**: ✅ Pronto para produção
