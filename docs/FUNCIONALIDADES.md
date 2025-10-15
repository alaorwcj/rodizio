# 📋 Funcionalidades Detalhadas do Sistema

## 🎹 Rodízio de Organistas - Vila Paula

### Versão Atual: 1.0

Data da última atualização: 14/10/2025

---

## 🔐 Sistema de Autenticação

### Login
- Interface limpa e moderna
- Validação de credenciais com senha criptografada
- Redirecionamento automático após login
- Logout seguro com confirmação

### Perfis de Usuário
1. **Administrador**:
   - Acesso completo ao sistema
   - Gerenciamento de organistas
   - Criação e edição de escalas
   - Configurações do sistema
   - Visualização de todas as escalas

2. **Organista**:
   - Marcação de indisponibilidades
   - Visualização dos próprios dias
   - Troca de senha
   - Consulta da escala completa

### Troca de Senha
- Disponível para todos os usuários
- Validações:
  - Senha atual obrigatória
  - Mínimo 6 caracteres
  - Confirmação de senha
- Atualização segura com hash Werkzeug

---

## 👥 Gestão de Organistas (Admin)

### Cadastro de Organistas
- **ID único**: Identificador do organista
- **Nome completo**: Nome para exibição
- **Tipos permitidos**:
  - Meia-hora: Toca 30min antes
  - Culto: Toca durante o culto
  - Ambos: Pode tocar em qualquer fase
- **Dias permitidos**:
  - Domingo
  - Terça
  - Ambos

### Validações
- ID único (não pode duplicar)
- Nome obrigatório
- Pelo menos um tipo selecionado
- Pelo menos um dia selecionado

### Lista de Organistas
- Visualização em tabela
- Tipos e dias exibidos claramente
- Botão de remoção
- Atualização em tempo real

---

## 📅 Indisponibilidades

### Marcação de Datas
- Calendário organizado por mês
- Seleção múltipla de datas
- Validação automática:
  - Apenas datas do bimestre
  - Não permite datas passadas (após publicação)
- Visual intuitivo

### Calendário Simplificado
- Organização por mês, semana e dia
- Mostra apenas domingos e terças
- Destaque visual das datas selecionadas
- Contador de indisponibilidades

### Impacto na Escala
- Organistas indisponíveis ficam desabilitados nos dropdowns
- Indicação visual (strikethrough + vermelho)
- Impossibilita seleção acidental

---

## 📊 Sistema de Escala Manual

### Criação de Escala Vazia
1. Admin acessa aba "Escala"
2. Clica em "Criar Escala Vazia"
3. Sistema gera:
   - Todos os domingos do bimestre
   - Todas as terças do bimestre
   - 2 posições por dia (Meia-hora + Culto)

### Estrutura da Escala

#### Para Domingos:
- **Meia-hora**: Organista que toca 30min antes
- **Culto**: Organista que toca durante o culto
- Podem ser pessoas diferentes ou a mesma (se tiver permissão "Ambos")

#### Para Terças:
- **Meia-hora**: Organista que toca 30min antes
- **Culto**: Organista que toca durante a reunião
- Podem ser pessoas diferentes ou a mesma (se tiver permissão "Ambos")

### Seleção Manual (Dropdowns)

#### Dropdowns Inteligentes:
- Mostram apenas organistas permitidos para aquele dia
- Bloqueiam organistas indisponíveis (visual: strikethrough + vermelho)
- Bloqueiam organistas sem permissão de fase:
  - Meia-hora: Só mostra quem pode tocar "Meia-hora" ou "Ambos"
  - Culto: Só mostra quem pode tocar "Culto" ou "Ambos"

#### Indicações Visuais:
- ✓ Nome normal: Disponível
- ~~Nome~~ (vermelho): Indisponível naquela data
- Nome (italic vermelho): Sem permissão de fase + sufixo "(só Meia-hora)" ou "(só Culto)"

### Salvamento
- **Botão único**: "💾 Salvar Todas as Alterações"
- Salva todos os dropdowns de uma vez
- Feedback visual de sucesso/erro
- Atualização automática do dashboard

### Visualização da Escala

#### Organização:
- Separação por mês
- Tabela com colunas:
  - Data
  - Dia da semana
  - 🎹 Meia-hora
  - 🎵 Culto

#### Cores:
- Verde: Domingos
- Amarelo: Terças
- Cinza: Datas vazias

---

## 📱 Dashboard

### Para Administradores

#### "📅 Próximas Escalas"
- Mostra as próximas 10 escalas
- Filtro automático (apenas datas futuras)
- Cards com:
  - Data grande e destacada
  - Dia da semana com emoji
  - Meia-hora e Culto
  - Nome dos organistas

#### Status do Sistema
- Quantidade de organistas cadastrados
- Quantidade de indisponibilidades marcadas
- Quantidade de escalas cadastradas

### Para Organistas

#### "🎹 Meus Dias de Rodízio"
- Mostra **apenas os dias do organista logado**
- Filtro inteligente:
  - Apenas datas futuras
  - Apenas onde está escalado (Meia-hora ou Culto)
- Cards destacados em verde:
  - ✓ "Você" nos serviços escalados
  - Fundo verde claro
  - Borda verde mais grossa

#### Mensagens:
- "Você não está escalado(a) em nenhuma data próxima" (se vazio)
- "Nenhuma escala cadastrada ainda" (sem dados)

---

## 📄 Exportação PDF

### Características
- Layout profissional
- Separação por mês
- Tabela organizada:
  - Data
  - Dia da semana
  - Meia-hora
  - Culto
- Sem textos desnecessários
- Pronto para impressão

### Como Exportar
1. Acesse aba "Escala"
2. Clique em "📄 Exportar PDF"
3. PDF baixa automaticamente

---

## ⚙️ Configurações (Admin)

### Bimestre
- **Data de início**: Primeira data do período
- **Data de fim**: Última data do período
- Validação: Fim deve ser após início
- Atualização automática ao salvar

### Prazo de Indisponibilidades
- Dias antes da publicação para marcar indisponibilidades
- Valor padrão: 3 dias

### Atualização Automática
- Ao salvar configurações
- Sistema recarrega a página
- Todas as datas atualizam:
  - Header
  - Dashboard
  - Calendários
  - Escala

---

## 🎨 Interface

### Design
- Gradient roxo/roxo-escuro no header
- Cards brancos com sombras
- Botões coloridos:
  - Verde: Ações positivas (Salvar)
  - Azul: Ações neutras (Criar)
  - Amarelo: Atenção (Trocar Senha)
  - Vermelho: Ações negativas (Sair, Remover)

### Responsividade
- Layout em grid adaptativo
- Cards empilham em telas pequenas
- Tabelas com scroll horizontal
- Mobile-friendly

### Navegação
- Abas no topo:
  - 📊 Dashboard
  - 👥 Organistas
  - 📅 Todas Indisponibilidades
  - ⚙️ Configurações (Admin)
  - 📅 Escala (Admin)

---

## 🔒 Segurança

### Senhas
- Hash com Werkzeug (pbkdf2:sha256)
- Salt automático
- Impossível recuperar senha original

### Sessões
- Flask-Login para gerenciamento
- @login_required nas rotas protegidas
- Timeout automático

### Validações
- Backend valida todas as operações
- Frontend valida antes de enviar
- Sanitização de inputs

---

## 📊 Banco de Dados

### Estrutura (db.json)

```json
{
  "admin": {
    "username": "admin",
    "password_hash": "...",
    "is_admin": true,
    "nome": "Administrador"
  },
  "organistas": [
    {
      "id": "ieda",
      "nome": "Iêda",
      "tipos": ["Meia-hora", "Culto"],
      "dias_permitidos": ["Domingo", "Terça"],
      "password_hash": "..."
    }
  ],
  "indisponibilidades": [
    {
      "organista_id": "ieda",
      "data": "2025-10-20",
      "criado_em": "2025-10-14T10:00:00"
    }
  ],
  "escala": [
    {
      "data": "2025-10-20",
      "dia_semana": "Sunday",
      "meia_hora": "Iêda",
      "culto": "Maria"
    }
  ],
  "config": {
    "bimestre": {
      "inicio": "2025-10-14",
      "fim": "2025-11-30"
    },
    "fechamento_publicacao_dias": 3
  },
  "logs": []
}
```

---

## 🐛 Tratamento de Erros

### Validações de Negócio
- Organista sem permissão de fase
- Organista indisponível
- Datas fora do bimestre
- Campos obrigatórios vazios

### Mensagens ao Usuário
- Alertas visuais (verde/vermelho)
- Textos claros e objetivos
- Instruções de correção

### Logs
- Todas as ações são registradas
- Timestamp e usuário responsável
- Facilita auditoria e debug

---

## 🚀 Performance

### Otimizações
- Carregamento assíncrono (fetch API)
- Atualização parcial da página
- Cache no navegador
- Compressão de assets

### Servidor
- Gunicorn com 2 workers
- 4 threads por worker
- Timeout de 120s

---

## 📝 Fluxo de Uso Completo

### 1. Primeiro Acesso (Admin)
1. Login com admin/admin123
2. Trocar senha
3. Configurar datas do bimestre
4. Cadastrar organistas

### 2. Configuração (Admin)
1. Criar escala vazia
2. Preencher manualmente os dropdowns
3. Salvar todas as alterações
4. Exportar PDF para compartilhar

### 3. Uso pelos Organistas
1. Receber credenciais
2. Trocar senha no primeiro acesso
3. Marcar indisponibilidades
4. Consultar "Meus Dias de Rodízio"

### 4. Ajustes e Manutenção
1. Admin pode editar a escala a qualquer momento
2. Organistas podem adicionar mais indisponibilidades
3. Exportar PDF atualizado conforme necessário

---

## 📖 Documentação Adicional

- `README.md`: Instalação e visão geral
- `GUIA_RAPIDO.md`: Tutorial rápido
- `MANUAL_USO.md`: Manual completo
- `TROUBLESHOOTING.md`: Solução de problemas
- `COMO_FUNCIONA.md`: Detalhes técnicos
- `EXPORTACAO_PDF.md`: Detalhes do PDF
