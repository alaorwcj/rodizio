# Sistema de Regionalização - Documentação Completa

## 🎯 Visão Geral

O sistema agora suporta uma estrutura hierárquica completa que permite gerenciar múltiplas congregações (comuns) organizadas em sub-regionais e regionais.

## 📊 Estrutura Hierárquica

```
Regional (GRU)
    └── Sub-Regional (Santa Isabel)
        └── Comum (Vila Paula)
            ├── Organistas
            ├── Escalas
            ├── Indisponibilidades
            └── Configurações
```

## 👥 Níveis de Usuário

### 1. **Master** (Administrador Geral)
- **Acesso**: Total ao sistema
- **Permissões**:
  - Visualizar e gerenciar TODAS as regionais, sub-regionais e comuns
  - Trocar de contexto livremente usando o seletor no header
  - Gerenciar usuários de todos os níveis
  - Configurar períodos e regras globais
- **Credenciais padrão**: `admin_master` / `admin123`

### 2. **Admin Regional**
- **Acesso**: Toda a regional atribuída
- **Permissões**:
  - Visualizar todas sub-regionais e comuns da sua regional
  - Gerenciar encarregados de sub-regionais
  - Visualizar relatórios consolidados da regional

### 3. **Encarregado Sub-Regional**
- **Acesso**: Toda a sub-regional atribuída
- **Permissões**:
  - Visualizar todos os comuns da sua sub-regional
  - Gerenciar encarregados de comuns
  - Visualizar relatórios consolidados da sub-regional

### 4. **Encarregado Comum**
- **Acesso**: Apenas o comum atribuído
- **Permissões**:
  - Gerenciar organistas do seu comum
  - Criar e editar escalas
  - Gerenciar indisponibilidades
  - Exportar relatórios (PDF, WhatsApp)

### 5. **Organista**
- **Acesso**: Visualização dos próprios dados
- **Permissões**:
  - Visualizar suas escalas
  - Marcar suas indisponibilidades
  - Ver escala geral do comum

## 🔧 Funcionalidades Implementadas

### ✅ Backend

1. **Estrutura de Dados Hierárquica**
   - Base de dados JSON reestruturada
   - Migração automática de dados existentes
   - Backup de segurança gerado

2. **Sistema de Autenticação Multi-Nível**
   - Login contextualizado por nível
   - Permissões granulares por endpoint
   - Sessão mantém contexto do usuário

3. **APIs de Navegação Hierárquica**
   - `GET /api/regionais` - Lista todas as regionais
   - `GET /api/regionais/{id}/sub-regionais` - Lista sub-regionais de uma regional
   - `GET /api/regionais/{id}/sub-regionais/{id}/comuns` - Lista comuns de uma sub-regional
   - `GET /api/contexto/atual` - Retorna contexto atual do usuário
   - `POST /api/contexto/selecionar` - Permite Master alterar contexto

4. **Endpoints Atualizados**
   - Todos os endpoints agora respeitam o contexto hierárquico
   - Dados isolados por comum
   - Filtros automáticos baseados em permissões

### ✅ Frontend

1. **Seletor de Contexto Dinâmico** (Master)
   - Dropdowns em cascata: Regional → Sub-Regional → Comum
   - Atualização automática de dados ao trocar contexto
   - Interface intuitiva no header

2. **Indicador de Contexto Atual**
   - Título mostra o comum atual
   - Visual claro da localização na hierarquia

3. **Sistema de Notificações**
   - Feedback visual para ações do usuário
   - Confirmação de troca de contexto
   - Alertas de erro

## 🚀 Como Usar

### Para Usuários Master

1. **Fazer Login**
   - Usuário: `admin_master`
   - Senha: `admin123`

2. **Selecionar Contexto**
   - No header, você verá três dropdowns em cascata
   - Selecione a **Regional** desejada
   - Selecione a **Sub-Regional** desejada
   - Selecione o **Comum** que deseja gerenciar
   - O sistema carrega automaticamente os dados do comum selecionado

3. **Gerenciar o Comum**
   - Todos os recursos normais estão disponíveis
   - Organistas, escalas e indisponibilidades são específicos do comum selecionado
   - Você pode trocar de comum a qualquer momento

### Para Outros Níveis

- O contexto é **fixo** baseado na sua atribuição
- Você verá apenas os dados do seu contexto (regional, sub-regional ou comum)
- Não há seletor de contexto no header

## 📁 Estrutura do Banco de Dados

```json
{
  "sistema": {
    "versao": "2.0",
    "data_migracao": "2025-10-14T20:38:33"
  },
  "regionais": {
    "gru": {
      "nome": "GRU - Guarulhos",
      "sub_regionais": {
        "santa_isabel": {
          "nome": "Santa Isabel",
          "comuns": {
            "vila_paula": {
              "nome": "Vila Paula",
              "organistas": [...],
              "indisponibilidades": [...],
              "escala": [...],
              "escala_rjm": [...],
              "config": {...}
            }
          }
        }
      }
    }
  },
  "usuarios": {
    "admin_master": {
      "nome": "Administrador Master",
      "senha_hash": "...",
      "tipo": "master",
      "email": "admin@sistema.com"
    }
  },
  "logs": []
}
```

## 🔄 Migração de Dados

A migração foi executada automaticamente com os seguintes resultados:

- ✅ **6 organistas** migrados
- ✅ **34 escalas** migradas
- ✅ **17 itens da escala RJM** migrados
- ✅ **11 indisponibilidades** migradas
- ✅ **Backup criado**: `data/db_backup_20251014_203833.json`
- ✅ **Configurações preservadas**: Períodos e regras mantidos

### Estrutura Migrada

Todos os dados foram organizados em:
- **Regional**: GRU (Guarulhos)
- **Sub-Regional**: Santa Isabel
- **Comum**: Vila Paula (dados originais)

## 🎨 Interface Visual

### Seletor de Contexto (Master)
```
📍 Contexto: [GRU ▼] › [Santa Isabel ▼] › [Vila Paula ▼]
```

### Indicador de Localização
```
🎹 Rodízio de Organistas - Vila Paula
Período: 01/01/2025 até 28/02/2025
```

## 🔐 Segurança

1. **Autenticação por Sessão**
   - Flask-Login gerencia sessões
   - Timeout automático
   - Proteção CSRF

2. **Autorização por Nível**
   - Decorators validam permissões
   - Acesso negado para contextos não autorizados
   - Logs de todas as ações

3. **Isolamento de Dados**
   - Cada comum tem seus próprios dados
   - Usuários só veem o que têm permissão
   - Queries filtradas por contexto

## 📈 Funcionalidades Completadas

### ✅ **IMPLEMENTADO - Interface de Gerenciamento Administrativo**
   - ✅ Criar/editar/remover regionais (aba Hierarquia)
   - ✅ Criar/editar/remover sub-regionais (aba Hierarquia)
   - ✅ Criar/editar/remover comuns (aba Hierarquia)
   - ✅ Gerenciar usuários por nível e contexto (aba Usuários)
   - ✅ Configurar dias de culto por comum (aba Usuários)
   - ✅ Configurar horários específicos por comum
   - ✅ Configurar períodos individuais por comum

### 🔜 Melhorias Futuras Sugeridas

1. **Dashboard Consolidado**
   - Visão geral para Master
   - Estatísticas por regional/sub-regional
   - Comparativos entre comuns
   - Gráficos e métricas

2. **Relatórios Multi-Comum**
   - Exportação consolidada em PDF
   - Análises comparativas
   - Excel com todos comuns
   - Envio automático por email

3. **Notificações Automáticas**
   - Email/SMS para organistas
   - Lembretes de indisponibilidade
   - Alertas para encarregados

## 🐛 Troubleshooting

### Não vejo o seletor de contexto
- **Solução**: O seletor só aparece para usuários Master. Faça login com `admin_master`.

### Dados não aparecem após trocar contexto
- **Solução**: Verifique se o comum selecionado tem dados cadastrados. Comum vazio aparece sem organistas/escalas.

### Erro ao selecionar contexto
- **Solução**: Verifique os logs do container: `docker logs rodizio-organistas --tail 50`

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs: `docker logs rodizio-organistas`
2. Consulte este documento
3. Verifique o backup em `data/db_backup_*.json`

---

**Versão**: 2.0  
**Data de Implementação**: 14/10/2025  
**Status**: ✅ Produção
