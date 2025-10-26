# Avaliação: Migração de db.json para PostgreSQL

**Data da Avaliação:** 26 de outubro de 2025  
**Status:** Análise de Viabilidade - SEM ALTERAÇÕES

---

## 1. RESUMO EXECUTIVO

✅ **MIGRAÇÃO É VIÁVEL E RECOMENDADA**

A migração do atual sistema de persistência baseado em arquivo JSON (`db.json`) para PostgreSQL é **totalmente viável** e trará **benefícios significativos** para a aplicação.

### Principais Vantagens
- ✅ Melhor desempenho em operações de leitura/escrita
- ✅ Transações ACID garantidas
- ✅ Suporte nativo a concorrência
- ✅ Queries mais eficientes e indexação
- ✅ Backup e recuperação mais robustos
- ✅ Escalabilidade horizontal futura

### Complexidade da Migração
- 🟡 **MÉDIA** - Requer planejamento mas é executável
- Tempo estimado: 16-24 horas de trabalho
- Baixo risco se bem planejado

---

## 2. ANÁLISE DO ESTADO ATUAL

### 2.1 Estrutura do Banco de Dados Atual (db.json)

**Arquivo:** `/root/app/rodizio/data/db.json`
- **Tamanho:** 7.030 linhas
- **Formato:** JSON hierárquico aninhado
- **Persistência:** Arquivo texto com locking (portalocker)

**Estrutura de Dados Identificada:**

```json
{
  "sistema": {...},           // Metadados do sistema
  "regionais": {              // Hierarquia: Regional > Sub-Regional > Comum
    "gru": {
      "sub_regionais": {
        "santa_isabel": {
          "comuns": {
            "vila_paula": {
              "organistas": [...],
              "indisponibilidades": [...],
              "escala": [...],
              "escala_rjm": [...],
              "trocas": [...],
              "config": {...}
            }
          }
        }
      }
    }
  },
  "usuarios": [...],          // Usuários do sistema
  "logs": [...],              // Logs operacionais
  "logs_auditoria": [...],    // Logs de auditoria
  "escala_rjm": [...],        // Escalas RJM globais
  "escala": [...],            // Escalas globais
  "escala_publicada_em": "...",
  "escala_publicada_por": "..."
}
```

### 2.2 Dependências Atuais

**Framework:** Flask 3.0.0
**Persistência Atual:**
- JSON puro (stdlib)
- `portalocker==2.8.2` - Lock de arquivo para concorrência
- Operações síncronas de I/O

**Outras Dependências Relevantes:**
```
Flask==3.0.0
Flask-Login==0.6.3
Werkzeug==3.0.1
```

### 2.3 Infraestrutura Existente

**Docker Compose Atual:**
- Serviço: `rodizio-app` (Flask)
- Serviço: `nginx` (Reverse proxy)
- Serviço: `certbot` (SSL)
- Volume: `./data:/app/data` (persistência JSON)

**PostgreSQL:**
- ✅ Já instalado localmente
- 🆕 Criar nova base: `rodizio`

---

## 3. SCHEMA PROPOSTO PARA POSTGRESQL

### 3.1 Script de Migração Existente

Já existe um script parcial de migração para SQLite em:
📄 `/root/app/rodizio/scripts/migrate_json_to_sqlite.py`

Este script pode ser adaptado para PostgreSQL com modificações mínimas.

### 3.2 Modelo de Dados Relacional

```sql
-- Hierarquia Organizacional
CREATE TABLE regionais (
  id VARCHAR(50) PRIMARY KEY,
  nome VARCHAR(200) NOT NULL,
  ativo BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE sub_regionais (
  id VARCHAR(50) PRIMARY KEY,
  regional_id VARCHAR(50) NOT NULL REFERENCES regionais(id) ON DELETE CASCADE,
  nome VARCHAR(200) NOT NULL,
  ativo BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE comuns (
  id VARCHAR(50) PRIMARY KEY,
  sub_regional_id VARCHAR(50) NOT NULL REFERENCES sub_regionais(id) ON DELETE CASCADE,
  nome VARCHAR(200) NOT NULL,
  endereco TEXT,
  cidade VARCHAR(100),
  ativo BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Organistas
CREATE TABLE organistas (
  id VARCHAR(50) PRIMARY KEY,
  comum_id VARCHAR(50) NOT NULL REFERENCES comuns(id) ON DELETE CASCADE,
  nome VARCHAR(200) NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE organista_tipos (
  organista_id VARCHAR(50) NOT NULL REFERENCES organistas(id) ON DELETE CASCADE,
  tipo VARCHAR(50) NOT NULL,
  PRIMARY KEY (organista_id, tipo)
);

CREATE TABLE organista_dias_permitidos (
  organista_id VARCHAR(50) NOT NULL REFERENCES organistas(id) ON DELETE CASCADE,
  dia VARCHAR(20) NOT NULL,
  PRIMARY KEY (organista_id, dia)
);

-- Indisponibilidades
CREATE TABLE indisponibilidades (
  id SERIAL PRIMARY KEY,
  comum_id VARCHAR(50) NOT NULL REFERENCES comuns(id) ON DELETE CASCADE,
  organista_id VARCHAR(50) NOT NULL REFERENCES organistas(id) ON DELETE CASCADE,
  data DATE NOT NULL,
  motivo TEXT,
  autor VARCHAR(50),
  status VARCHAR(20),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Escalas
CREATE TABLE escala (
  id SERIAL PRIMARY KEY,
  comum_id VARCHAR(50) NOT NULL REFERENCES comuns(id) ON DELETE CASCADE,
  data DATE NOT NULL,
  dia_semana VARCHAR(20),
  meia_hora VARCHAR(200),
  culto VARCHAR(200),
  criado_em TIMESTAMPTZ DEFAULT NOW(),
  publicado_em TIMESTAMPTZ,
  publicado_por VARCHAR(50)
);

CREATE TABLE escala_rjm (
  id VARCHAR(100) PRIMARY KEY,
  comum_id VARCHAR(50) NOT NULL REFERENCES comuns(id) ON DELETE CASCADE,
  data DATE NOT NULL,
  dia_semana VARCHAR(20),
  organista VARCHAR(200),
  criado_em TIMESTAMPTZ DEFAULT NOW()
);

-- Configurações
CREATE TABLE comum_config (
  comum_id VARCHAR(50) PRIMARY KEY REFERENCES comuns(id) ON DELETE CASCADE,
  periodo_inicio DATE,
  periodo_fim DATE,
  fechamento_publicacao_dias INTEGER,
  dias_culto JSONB,  -- Array de dias permitidos
  horarios JSONB,    -- Configurações de horários
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sistema de Trocas
CREATE TABLE trocas (
  id VARCHAR(100) PRIMARY KEY,
  comum_id VARCHAR(50) NOT NULL REFERENCES comuns(id) ON DELETE CASCADE,
  status VARCHAR(20),
  modalidade VARCHAR(50),
  tipo VARCHAR(50),
  data DATE,
  slot VARCHAR(50),
  solicitante_id VARCHAR(50),
  solicitante_nome VARCHAR(200),
  alvo_id VARCHAR(50),
  alvo_nome VARCHAR(200),
  motivo TEXT,
  criado_em TIMESTAMPTZ DEFAULT NOW(),
  atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE trocas_historico (
  id SERIAL PRIMARY KEY,
  troca_id VARCHAR(100) NOT NULL REFERENCES trocas(id) ON DELETE CASCADE,
  quando TIMESTAMPTZ NOT NULL,
  acao VARCHAR(50),
  por VARCHAR(200)
);

-- Usuários do Sistema
CREATE TABLE usuarios (
  id VARCHAR(50) PRIMARY KEY,
  nome VARCHAR(200) NOT NULL,
  password_hash TEXT NOT NULL,
  tipo VARCHAR(50) NOT NULL,  -- master, admin_regional, encarregado_sub, etc
  nivel VARCHAR(50) NOT NULL,  -- sistema, regional, sub_regional, comum
  contexto_id VARCHAR(50),     -- ID da regional/sub/comum
  ativo BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Auditoria
CREATE TABLE logs_auditoria (
  id VARCHAR(100) PRIMARY KEY,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  tipo VARCHAR(50),
  categoria VARCHAR(50),
  acao VARCHAR(100),
  descricao TEXT,
  usuario_id VARCHAR(50),
  usuario_nome VARCHAR(200),
  usuario_tipo VARCHAR(50),
  regional_id VARCHAR(50),
  sub_regional_id VARCHAR(50),
  comum_id VARCHAR(50),
  status VARCHAR(20),
  ip VARCHAR(45),
  user_agent TEXT,
  dados_antes JSONB,
  dados_depois JSONB
);

-- Índices para Performance
CREATE INDEX idx_organistas_comum ON organistas(comum_id);
CREATE INDEX idx_indisponibilidades_comum_data ON indisponibilidades(comum_id, data);
CREATE INDEX idx_indisponibilidades_organista ON indisponibilidades(organista_id);
CREATE INDEX idx_escala_comum_data ON escala(comum_id, data);
CREATE INDEX idx_escala_rjm_comum_data ON escala_rjm(comum_id, data);
CREATE INDEX idx_trocas_comum_status ON trocas(comum_id, status);
CREATE INDEX idx_logs_timestamp ON logs_auditoria(timestamp DESC);
CREATE INDEX idx_logs_usuario ON logs_auditoria(usuario_id);
CREATE INDEX idx_logs_comum ON logs_auditoria(comum_id);
```

### 3.3 Vantagens do Schema PostgreSQL

1. **Normalização Adequada**
   - Elimina redundância de dados
   - Integridade referencial com FOREIGN KEYS
   - Triggers para atualização automática de timestamps

2. **Performance**
   - Índices específicos para queries frequentes
   - JSONB para dados semi-estruturados (config, logs)
   - Queries otimizadas vs varredura em JSON

3. **Transações ACID**
   - Elimina necessidade de file locking manual
   - Rollback automático em caso de erro
   - Consistência garantida

4. **Recursos Avançados**
   - Full-text search nativo
   - Particionamento de tabelas (futuro)
   - Replicação e backup incremental

---

## 4. PLANO DE MIGRAÇÃO

### 4.1 Fase 1: Preparação (2-3 horas)

#### 4.1.1 Instalação de Dependências
```bash
# Adicionar ao requirements.txt
psycopg2-binary==2.9.9  # Driver PostgreSQL
SQLAlchemy==2.0.23      # ORM (opcional, mas recomendado)
alembic==1.13.0         # Migrations (recomendado)
```

#### 4.1.2 Criar Base de Dados
```sql
-- No PostgreSQL local
CREATE DATABASE rodizio
  WITH OWNER = postgres
  ENCODING = 'UTF8'
  LC_COLLATE = 'pt_BR.UTF-8'
  LC_CTYPE = 'pt_BR.UTF-8'
  TEMPLATE = template0;
```

#### 4.1.3 Configurar Variáveis de Ambiente
```bash
# .env ou docker-compose.yml
DATABASE_URL=postgresql://usuario:senha@localhost:5432/rodizio
```

### 4.2 Fase 2: Implementação da Camada de Dados (6-8 horas)

#### 4.2.1 Criar Módulo de Database
```
/root/app/rodizio/
  ├── database.py          # Conexão e engine
  ├── models.py            # Modelos SQLAlchemy (ORM)
  └── repositories/        # Padrão Repository
      ├── __init__.py
      ├── regional_repo.py
      ├── organista_repo.py
      ├── escala_repo.py
      └── auditoria_repo.py
```

#### 4.2.2 Implementar Repositories
- Abstrair lógica de acesso a dados
- Manter interfaces compatíveis com código atual
- Facilitar testes unitários

### 4.3 Fase 3: Refatoração do app.py (6-8 horas)

#### Substituir:
```python
# ANTES
db = load_db()
db['regionais'][rid]['sub_regionais'][sid]...
save_db(db)

# DEPOIS
from repositories import RegionalRepository
repo = RegionalRepository()
regional = repo.get_by_id(rid)
sub = repo.get_sub_regional(rid, sid)
```

#### Principais Mudanças:
1. Substituir `load_db()` / `save_db()` por repositories
2. Converter navegação JSON para queries ORM
3. Adaptar funções de busca/filtro
4. Implementar transações

### 4.4 Fase 4: Script de Migração de Dados (3-4 horas)

Adaptar `/root/app/rodizio/scripts/migrate_json_to_sqlite.py` para PostgreSQL:

```python
# migrate_json_to_postgres.py
import psycopg2
from psycopg2.extras import Json

def migrate_data():
    # 1. Backup do db.json
    # 2. Conectar PostgreSQL
    # 3. Criar schema
    # 4. Migrar dados hierarquia
    # 5. Migrar organistas
    # 6. Migrar escalas
    # 7. Migrar logs
    # 8. Validar migração
    pass
```

### 4.5 Fase 5: Atualizar Docker Compose (1 hora)

```yaml
services:
  postgres:
    image: postgres:16-alpine
    container_name: rodizio-postgres
    environment:
      POSTGRES_DB: rodizio
      POSTGRES_USER: rodizio_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=pt_BR.UTF-8"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - rodizio-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U rodizio_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  rodizio-app:
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://rodizio_user:${DB_PASSWORD}@postgres:5432/rodizio

volumes:
  postgres_data:
```

### 4.6 Fase 6: Testes (2-3 horas)

1. **Testes de Unidade**
   - Repositories
   - Modelos ORM

2. **Testes de Integração**
   - Autenticação
   - Criação de escalas
   - Gestão de indisponibilidades
   - Trocas
   - Auditoria

3. **Teste de Migração**
   - Comparar dados JSON vs PostgreSQL
   - Validar integridade

---

## 5. RISCOS E MITIGAÇÕES

### 5.1 Riscos Identificados

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Perda de dados durante migração | Baixa | Alto | Backup completo antes; validação pós-migração |
| Incompatibilidade de código | Média | Médio | Testes extensivos; migração gradual |
| Downtime da aplicação | Média | Médio | Migração em ambiente de staging primeiro |
| Performance inicial ruim | Baixa | Baixo | Índices adequados; tuning pós-migração |
| Conexões não fechadas | Média | Médio | Connection pooling; context managers |

### 5.2 Estratégias de Mitigação

1. **Backup Triplo**
   - Backup do db.json atual
   - Export SQL do PostgreSQL
   - Snapshot do volume Docker

2. **Migração Gradual**
   - Ambiente de desenvolvimento primeiro
   - Testes completos
   - Staging com dados reais
   - Produção com janela de manutenção

3. **Rollback Plan**
   - Manter db.json como fallback
   - Script de rollback automatizado
   - Documentar procedimento de reversão

---

## 6. CRONOGRAMA ESTIMADO

### Opção 1: Migração Total (1 sprint - 2 semanas)
```
Semana 1:
├─ Dia 1-2: Preparação e setup PostgreSQL
├─ Dia 3-4: Implementação camada de dados
└─ Dia 5: Refatoração inicial

Semana 2:
├─ Dia 1-2: Refatoração completa
├─ Dia 3: Script de migração
├─ Dia 4: Testes
└─ Dia 5: Deploy e validação
```

### Opção 2: Migração Incremental (2 sprints - 4 semanas)
```
Sprint 1 (Setup + Leitura):
├─ Preparação PostgreSQL
├─ Implementar camada de dados
├─ Migração de queries de leitura
└─ Testes parciais

Sprint 2 (Escrita + Migração):
├─ Migração de queries de escrita
├─ Script de migração de dados
├─ Testes completos
└─ Deploy gradual
```

---

## 7. CUSTO-BENEFÍCIO

### Investimento Necessário
- ⏱️ Tempo: 16-24 horas de desenvolvimento
- 💰 Infraestrutura: Minimal (PostgreSQL já disponível)
- 📚 Curva de aprendizado: Baixa (tecnologias conhecidas)

### Benefícios Esperados
- ⚡ **Performance**: 10-100x mais rápido em queries complexas
- 🔒 **Confiabilidade**: Transações ACID, sem corrupção de dados
- 📈 **Escalabilidade**: Suporta crescimento sem refatoração
- 🛠️ **Manutenibilidade**: Código mais limpo e testável
- 🔍 **Observabilidade**: Logs de query, explain plans, monitoring

### ROI (Return on Investment)
- **Curto prazo** (1-3 meses): Menos bugs, deploys mais confiáveis
- **Médio prazo** (6 meses): Menor tempo de desenvolvimento de features
- **Longo prazo** (1+ ano): Escalabilidade sem reescrita

---

## 8. RECOMENDAÇÕES

### ✅ Recomendamos a Migração pelos seguintes motivos:

1. **Fundação Sólida**
   - PostgreSQL é padrão da indústria
   - Suporte de longo prazo garantido
   - Comunidade ativa

2. **Crescimento Futuro**
   - Sistema está em fase de crescimento
   - Mais comuns e usuários serão adicionados
   - JSON não escalará bem

3. **Manutenibilidade**
   - Código atual está acoplado ao JSON
   - Dificulta testes e manutenção
   - Refatoração trará benefícios além do DB

4. **Timing Adequado**
   - Sistema ainda em desenvolvimento ativo
   - Base de código relativamente pequena
   - Melhor fazer agora que depois

### 🎯 Abordagem Recomendada

**MIGRAÇÃO INCREMENTAL EM 2 FASES:**

**Fase 1 (2 semanas):**
- Setup PostgreSQL
- Implementar camada de dados com SQLAlchemy
- Migrar operações de leitura
- Manter escrita em JSON (fallback)

**Fase 2 (2 semanas):**
- Migrar operações de escrita
- Executar migração de dados
- Testes exaustivos
- Deploy em produção

### 📋 Próximos Passos Sugeridos

1. ✅ **Aprovação desta avaliação**
2. 🔧 **Setup do ambiente PostgreSQL local**
3. 📝 **Criar branch `feature/postgres-migration`**
4. 🏗️ **Implementar schema e models**
5. 🔄 **Refatoração incremental**
6. ✅ **Testes e validação**
7. 🚀 **Deploy gradual**

---

## 9. CONSIDERAÇÕES TÉCNICAS ADICIONAIS

### 9.1 Connection Pooling
```python
# Usar SQLAlchemy com pool de conexões
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True  # Verificar conexões antes de usar
)
```

### 9.2 Migrations com Alembic
```bash
# Gerenciar mudanças de schema
alembic init migrations
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

### 9.3 Backup Automatizado
```bash
# Cronjob para backup diário
0 2 * * * pg_dump -U rodizio_user rodizio | gzip > /backups/rodizio_$(date +\%Y\%m\%d).sql.gz
```

### 9.4 Monitoring
```python
# Usar pg_stat_statements
CREATE EXTENSION pg_stat_statements;

# Monitorar queries lentas
SELECT * FROM pg_stat_statements 
WHERE mean_exec_time > 1000 
ORDER BY mean_exec_time DESC;
```

---

## 10. CONCLUSÃO

A migração de `db.json` para PostgreSQL é **VIÁVEL**, **RECOMENDADA** e deve ser **PRIORIZADA** no roadmap de desenvolvimento.

**Veredito Final: 🟢 APROVADO PARA EXECUÇÃO**

### Fatores de Sucesso
- ✅ PostgreSQL já disponível localmente
- ✅ Script de migração existente (SQLite) pode ser adaptado
- ✅ Estrutura de dados bem definida
- ✅ Benefícios superam custos significativamente
- ✅ Timing ideal para migração

### Próxima Ação Recomendada
**Iniciar Fase 1 da migração:**
1. Criar base `rodizio` no PostgreSQL local
2. Instalar dependências Python (psycopg2, SQLAlchemy)
3. Implementar schema e models básicos
4. Validar conexão e queries simples

---

**Documento preparado por:** GitHub Copilot  
**Data:** 26 de outubro de 2025  
**Versão:** 1.0  
**Status:** Aguardando aprovação para execução
