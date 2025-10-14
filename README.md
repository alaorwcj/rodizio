# 🎹 Sistema de Rodízio de Organistas - Vila Paula

Sistema web para gestão manual da escala bimestral de organistas, com controle de indisponibilidades, autenticação de usuários e visualização personalizada por perfil.

## 🚀 Características

### ✅ Funcionalidades Implementadas

- **Sistema de Autenticação**: 
  - Login com usuário e senha
  - Perfis de Administrador e Organista
  - Troca de senha para todos os usuários
  - Senhas criptografadas com Werkzeug

- **Gestão de Organistas** (Admin):
  - CRUD completo com tipos (Meia-hora, Culto, Ambos)
  - Dias permitidos (Domingo, Terça)
  - Regras especiais personalizadas

- **Gestão de Indisponibilidades**:
  - Organistas marcam datas indisponíveis
  - Calendário simplificado por mês
  - Validação automática de datas

- **Escala Manual**:
  - Criação de escala vazia para o bimestre
  - Seleção manual via dropdowns
  - Validação de fase (Meia-hora/Culto)
  - Bloqueio de organistas indisponíveis
  - Botão único "Salvar Todas as Alterações"
  - Sistema de 2 fases para Domingos E Terças

- **Dashboard Personalizado**:
  - **Admin**: Visualiza todas as próximas 10 escalas
  - **Organista**: Visualiza apenas "Meus Dias de Rodízio"
  - Cards coloridos e responsivos
  - Filtro automático por data (apenas futuros)

- **Exportação PDF**:
  - Geração limpa e profissional
  - Separação por mês
  - Layout organizado em tabela
  - Pronto para impressão

- **Configurações**:
  - Ajuste de datas do bimestre
  - Atualização automática ao salvar
  - Prazo para marcação de indisponibilidades

## 📋 Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+

## 🐳 Instalação e Execução com Docker

### 1. Clone o repositório

```bash
git clone <seu-repo>
cd rodizio
```

### 2. Build e execução com Docker Compose (Recomendado)

```bash
# Build e iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar
docker-compose down

# Parar e remover volumes (limpar dados)
docker-compose down -v
```

### 3. Ou build manual com Docker

```bash
# Build da imagem
docker build -t rodizio-organistas:latest .

# Executar container
docker run -d \
  --name rodizio-app \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  rodizio-organistas:latest

# Ver logs
docker logs -f rodizio-app

# Parar e remover
docker stop rodizio-app
docker rm rodizio-app
```

### 4. Acessar a aplicação

Abra seu navegador em: **http://localhost:8080**

**Credenciais padrão:**
- Administrador: `admin` / `admin123`

⚠️ **IMPORTANTE**: Troque a senha no primeiro acesso!

## 🎯 Como Usar o Sistema

### Para Administradores

1. **Configurar Bimestre**:
   - Acesse "⚙️ Configurações"
   - Defina data de início e fim do bimestre
   - Sistema atualiza automaticamente

2. **Cadastrar Organistas**:
   - Acesse "👥 Organistas"
   - Adicione organistas com:
     - Nome
     - Tipos permitidos (Meia-hora, Culto ou Ambos)
     - Dias permitidos (Domingo, Terça ou Ambos)

3. **Criar Escala**:
   - Acesse "📅 Escala"
   - Clique em "Criar Escala Vazia"
   - Sistema gera todos os domingos e terças do bimestre
   - Use os dropdowns para selecionar organistas manualmente
   - Clique em "💾 Salvar Todas as Alterações"

4. **Exportar PDF**:
   - Na aba "📅 Escala"
   - Clique em "📄 Exportar PDF"
   - PDF pronto para impressão

### Para Organistas

1. **Primeiro Acesso**:
   - Login com credenciais fornecidas
   - Troque a senha em "🔐 Trocar Senha"

2. **Marcar Indisponibilidades**:
   - Acesse "📅 Todas Indisponibilidades"
   - Selecione as datas que não pode tocar
   - Sistema bloqueia automaticamente na escala

3. **Ver Seus Dias**:
   - Dashboard mostra "🎹 Meus Dias de Rodízio"
   - Visualização destacada dos seus serviços
   - Apenas datas futuras

## 📁 Estrutura do Projeto

```
rodizio/
├── app.py                 # Aplicação Flask principal
├── requirements.txt       # Dependências Python
├── Dockerfile            # Imagem Docker multi-stage
├── docker-compose.yml    # Orquestração Docker
├── .dockerignore         # Arquivos ignorados no build
├── entrypoint.sh         # Script de inicialização
├── data/
│   └── db.json          # Banco de dados JSON (persistido)
├── templates/
│   └── index.html       # Interface web
└── static/              # CSS/JS/imagens
```

## 🔧 Comandos Úteis

### Gerenciamento do Container

```bash
# Verificar status
docker-compose ps

# Reiniciar serviço
docker-compose restart

# Ver logs em tempo real
docker-compose logs -f rodizio-app

# Executar comando dentro do container
docker-compose exec rodizio-app bash

# Verificar health check
docker-compose exec rodizio-app curl http://localhost:8080/health
```

### Backup e Restore dos Dados

```bash
# Backup do banco de dados
docker cp rodizio-organistas:/app/data/db.json ./backup-$(date +%Y%m%d).json

# Restore do banco de dados
docker cp ./backup-20251014.json rodizio-organistas:/app/data/db.json
docker-compose restart
```

### Desenvolvimento

Para desenvolvimento local com hot-reload, descomente as linhas de volume no `docker-compose.yml`:

```yaml
volumes:
  - ./data:/app/data
  - ./templates:/app/templates  # Descomentar
  - ./static:/app/static        # Descomentar
```

## 🏗️ Arquitetura do Container

### Multi-stage Build
- **Stage 1 (builder)**: Instala dependências Python
- **Stage 2 (runtime)**: Copia apenas o necessário, reduzindo o tamanho final

### Segurança
- ✅ Usuário não-root (`appuser`)
- ✅ Imagem base slim (Python 3.11)
- ✅ Sem cache de pip
- ✅ Health checks configurados

### Performance
- **Gunicorn** com 2 workers e 4 threads
- Worker temporário em `/dev/shm` (memória)
- Timeout de 120s para operações longas

## 📊 Monitoramento

### Health Check

```bash
curl http://localhost:8080/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-14T12:00:00",
  "organistas_count": 4,
  "indisponibilidades_count": 2
}
```

### Métricas do Container

```bash
# CPU, Memória, Network
docker stats rodizio-organistas

# Logs de acesso do Gunicorn
docker-compose logs rodizio-app | grep "GET\|POST"
```

## 🔐 Variáveis de Ambiente

Configuráveis no `docker-compose.yml`:

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `FLASK_ENV` | `production` | Ambiente Flask |
| `TZ` | `America/Sao_Paulo` | Timezone |

## 🐛 Troubleshooting

### Container não inicia

```bash
# Ver logs detalhados
docker-compose logs rodizio-app

# Verificar permissões
ls -la data/
```

### Porta 8080 já em uso

Edite `docker-compose.yml`:
```yaml
ports:
  - "8081:8080"  # Mude para 8081 ou outra porta
```

### Dados não persistem

Verifique se o volume está montado:
```bash
docker-compose exec rodizio-app ls -la /app/data
```

## 📝 Status do Projeto

### ✅ Implementado

- [x] **Fase 1**: Autenticação e CRUD de Organistas
- [x] **Fase 1.1**: Gestão de Indisponibilidades
- [x] **Fase 1.2**: Sistema Manual de Escala (Dropdowns)
- [x] **Fase 1.3**: Dashboard Personalizado por Perfil
- [x] **Fase 1.4**: Exportação para PDF
- [x] **Fase 1.5**: Troca de Senha
- [x] **Fase 1.6**: Validações de Fase (Meia-hora/Culto)

### 🔜 Próximos Passos

- [ ] **Fase 2**: Exportação para Excel
- [ ] **Fase 3**: Migração para SQLite
- [ ] **Fase 4**: Sistema de notificações por email
- [ ] **Fase 5**: Aplicativo mobile (PWA)
- [ ] **Fase 6**: Relatórios e estatísticas avançadas

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👥 Autores

- **Equipe de Desenvolvimento** - *Trabalho inicial*

## 🙏 Agradecimentos

- Igreja que inspirou o sistema
- Comunidade Flask e Docker
