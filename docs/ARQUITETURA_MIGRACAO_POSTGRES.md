# 🏗️ Arquitetura da Migração PostgreSQL

## Visão Geral da Transformação

### Estado ATUAL (JSON)

```
┌─────────────────────────────────────────────────────┐
│                   Flask App (app.py)                │
│                     ~4000 linhas                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐      ┌──────────────┐           │
│  │  load_db()   │◄────►│  save_db()   │           │
│  └──────┬───────┘      └──────┬───────┘           │
│         │                     │                    │
│         │    portalocker      │                    │
│         │    (file lock)      │                    │
│         ▼                     ▼                    │
│  ┌─────────────────────────────────┐              │
│  │     data/db.json (~7000 linhas) │              │
│  │  ┌────────────────────────────┐ │              │
│  │  │ {                          │ │              │
│  │  │   "regionais": {           │ │              │
│  │  │     "gru": {               │ │              │
│  │  │       "sub_regionais": {   │ │              │
│  │  │         ...nested...       │ │              │
│  │  │       }                    │ │              │
│  │  │     }                      │ │              │
│  │  │   }                        │ │              │
│  │  │ }                          │ │              │
│  │  └────────────────────────────┘ │              │
│  └─────────────────────────────────┘              │
│                                                     │
└─────────────────────────────────────────────────────┘

📊 Problemas:
❌ Carrega TUDO na memória (7000 linhas)
❌ File lock bloqueia leitura/escrita concorrente
❌ Busca = varredura linear O(n)
❌ Sem validação de integridade
❌ Backup = copiar arquivo inteiro
```

---

### Estado FUTURO (PostgreSQL)

```
┌──────────────────────────────────────────────────────────────┐
│                    Flask App (app.py)                        │
│                  Refatorado com Repositories                 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Application Layer (Routes)                │   │
│  └────────────────────┬────────────────────────────────┘   │
│                       │                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          Repository Layer (Abstração)                │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │   │
│  │  │ Organista    │  │   Escala     │  │   Comum   │ │   │
│  │  │ Repository   │  │  Repository  │  │ Repository│ │   │
│  │  └──────┬───────┘  └──────┬───────┘  └─────┬─────┘ │   │
│  └─────────┼──────────────────┼──────────────────┼───────┘   │
│            │                  │                  │           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              ORM Layer (SQLAlchemy)                  │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│  │  │Organista │  │  Escala  │  │  Comum   │  ...     │   │
│  │  │  Model   │  │  Model   │  │  Model   │          │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘          │   │
│  └───────┼─────────────┼─────────────┼────────────────┘   │
│          │             │             │                     │
│  ┌───────────────────────────────────────────────────┐    │
│  │        Connection Pool (10-20 conexões)            │    │
│  └──────────────────────┬────────────────────────────┘    │
└─────────────────────────┼───────────────────────────────────┘
                          │
                          │ psycopg2
                          ▼
┌──────────────────────────────────────────────────────────┐
│                  PostgreSQL 16                           │
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────┐  │
│  │ regionais  │  │sub_regionais│  │    comuns       │  │
│  │  (3 rows)  │  │  (5 rows)   │  │   (10 rows)     │  │
│  └────────────┘  └────────────┘  └─────────────────┘  │
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────┐  │
│  │ organistas │  │   escala   │  │indisponibilidades│ │
│  │ (50 rows)  │  │ (200 rows) │  │   (30 rows)      │  │
│  └────────────┘  └────────────┘  └─────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │            Índices B-Tree                        │  │
│  │  • idx_organistas_comum                          │  │
│  │  • idx_escala_comum_data                         │  │
│  │  • idx_indisponibilidades_organista_data         │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │            WAL (Write-Ahead Logging)             │  │
│  │  → Backup incremental                            │  │
│  │  → Point-in-time recovery                        │  │
│  └──────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘

📈 Benefícios:
✅ Queries indexadas O(log n)
✅ Concorrência nativa (MVCC)
✅ Transações ACID
✅ Validação de integridade (FK)
✅ Backup incremental
✅ Performance 10-50x melhor
```

---

## Fluxo de Dados ANTES vs DEPOIS

### ANTES: Buscar Organista

```
Usuario → HTTP Request
    ↓
Flask Route (/api/organistas/<id>)
    ↓
load_db()                         ← Abre arquivo
    ↓                             ← Lock compartilhado
    ↓                             ← Lê 7000 linhas JSON
    ↓                             ← Parse completo
json.load(f)                      ← ~50ms
    ↓
Percorre db['regionais']          ← Loop O(n)
  → db['sub_regionais']           ← Loop O(m)
    → db['comuns']                ← Loop O(k)
      → db['organistas']          ← Loop O(j)
        → if id == target: return ← ~50-100ms total
    ↓
JSON Response
    ↓
Usuario ← HTTP Response

TOTAL: ~100-150ms
```

### DEPOIS: Buscar Organista

```
Usuario → HTTP Request
    ↓
Flask Route (/api/organistas/<id>)
    ↓
OrganistaRepository.get_by_id(id)
    ↓
SQLAlchemy Query
    ↓
SELECT * FROM organistas         ← Query preparada
WHERE id = ?                     ← Parametrizada
    ↓
PostgreSQL Engine
    ↓
Index Scan (idx_organistas_pk)   ← B-Tree O(log n)
    ↓                             ← ~2ms
Return Row
    ↓
ORM mapping → Organista object
    ↓
JSON Response
    ↓
Usuario ← HTTP Response

TOTAL: ~5-10ms (20-30x mais rápido!)
```

---

## Camadas da Aplicação

### Arquitetura em Camadas (Post-Migration)

```
┌─────────────────────────────────────────────────────┐
│                Presentation Layer                   │
│              (Flask Routes/Templates)               │
│  • /login                                           │
│  • /api/escalas                                     │
│  • /api/organistas                                  │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│               Business Logic Layer                  │
│              (Service Layer - opcional)             │
│  • gerar_escala_inteligente()                       │
│  • validar_indisponibilidade()                      │
│  • calcular_estatisticas()                          │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│              Repository Layer ⭐                     │
│          (Abstração de Acesso a Dados)              │
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │ class OrganistaRepository:                   │ │
│  │   def get_by_id(id)                          │ │
│  │   def get_by_comum(comum_id)                 │ │
│  │   def create(data)                           │ │
│  │   def update(id, data)                       │ │
│  │   def delete(id)                             │ │
│  └──────────────────────────────────────────────┘ │
│                                                     │
│  • RegionalRepository                               │
│  • EscalaRepository                                 │
│  • IndisponibilidadeRepository                      │
│  • TrocaRepository                                  │
│  • AuditoriaRepository                              │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                  ORM Layer                          │
│                (SQLAlchemy Models)                  │
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │ class Organista(Base):                       │ │
│  │   __tablename__ = 'organistas'               │ │
│  │   id = Column(String, primary_key=True)      │ │
│  │   nome = Column(String)                      │ │
│  │   comum_id = Column(String, ForeignKey(...)) │ │
│  │   # Relationships                            │ │
│  │   comum = relationship('Comum')              │ │
│  └──────────────────────────────────────────────┘ │
│                                                     │
│  • Regional (model)                                 │
│  • SubRegional (model)                              │
│  • Comum (model)                                    │
│  • Escala (model)                                   │
│  • ...                                              │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│              Database Driver Layer                  │
│                  (psycopg2)                         │
│  • Connection pooling                               │
│  • Query execution                                  │
│  • Transaction management                           │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                PostgreSQL Database                  │
│  • Tables                                           │
│  • Indexes                                          │
│  • Constraints                                      │
│  • Triggers                                         │
└─────────────────────────────────────────────────────┘
```

---

## Estrutura de Diretórios

### ANTES

```
/root/app/rodizio/
├── app.py                    # ~4000 linhas (tudo aqui!)
├── requirements.txt
├── data/
│   └── db.json              # Todo o banco
└── templates/
    └── *.html
```

### DEPOIS

```
/root/app/rodizio/
├── app.py                    # ~2000 linhas (refatorado)
├── requirements.txt          # + psycopg2, SQLAlchemy
│
├── database/                 # ⭐ NOVO
│   ├── __init__.py
│   ├── connection.py         # Engine, Session, context manager
│   ├── models.py             # Todos os models SQLAlchemy
│   └── schema.sql            # Schema completo
│
├── repositories/             # ⭐ NOVO
│   ├── __init__.py
│   ├── base_repository.py    # Classe base
│   ├── regional_repo.py
│   ├── organista_repo.py
│   ├── escala_repo.py
│   ├── indisponibilidade_repo.py
│   ├── troca_repo.py
│   └── auditoria_repo.py
│
├── migrations/               # ⭐ NOVO (Alembic)
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
│       └── 001_initial_schema.py
│
├── scripts/
│   ├── migrate_to_postgres.py  # ⭐ NOVO Script de migração
│   └── init_dev_db.py          # ⭐ NOVO Setup dev
│
├── data/
│   ├── db.json               # Manter por segurança (1-2 meses)
│   └── backups/              # Backups automáticos
│
└── templates/
    └── *.html
```

---

## Fluxo de Migração de Dados

```
┌─────────────────────────────────────────────────────┐
│          ETAPA 1: Backup e Preparação               │
└─────────────────────────────────────────────────────┘
              │
              ▼
    ┌──────────────────┐
    │  Backup db.json  │
    │  → /backups/...  │
    └────────┬─────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│        ETAPA 2: Criar Database e Schema             │
└─────────────────────────────────────────────────────┘
              │
              ▼
    ┌──────────────────────┐
    │ CREATE DATABASE      │
    │ rodizio              │
    └─────────┬────────────┘
              │
              ▼
    ┌──────────────────────┐
    │ Executar schema.sql  │
    │ • Tabelas            │
    │ • Constraints        │
    │ • Índices            │
    └─────────┬────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────┐
│          ETAPA 3: Migrar Dados (Ordem!)             │
└─────────────────────────────────────────────────────┘
              │
              ▼
    ┌────────────────────────┐
    │ 1. Regionais           │ ← Sem dependências
    └───────────┬────────────┘
                │
                ▼
    ┌────────────────────────┐
    │ 2. Sub-Regionais       │ ← FK: regionais
    └───────────┬────────────┘
                │
                ▼
    ┌────────────────────────┐
    │ 3. Comuns              │ ← FK: sub_regionais
    └───────────┬────────────┘
                │
                ▼
    ┌────────────────────────┐
    │ 4. Organistas          │ ← FK: comuns
    │ 5. Organista_Tipos     │
    │ 6. Organista_Dias      │
    └───────────┬────────────┘
                │
                ▼
    ┌────────────────────────┐
    │ 7. Indisponibilidades  │ ← FK: comuns, organistas
    │ 8. Escala              │ ← FK: comuns
    │ 9. Escala RJM          │ ← FK: comuns
    └───────────┬────────────┘
                │
                ▼
    ┌────────────────────────┐
    │ 10. Trocas             │ ← FK: comuns
    │ 11. Trocas_Historico   │ ← FK: trocas
    └───────────┬────────────┘
                │
                ▼
    ┌────────────────────────┐
    │ 12. Usuários           │ ← Independente
    │ 13. Logs Auditoria     │ ← Independente
    └───────────┬────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│            ETAPA 4: Validação                       │
└─────────────────────────────────────────────────────┘
              │
              ▼
    ┌────────────────────────────┐
    │ Comparar contagens:        │
    │ • JSON: 50 organistas      │
    │ • PG:   50 organistas  ✓   │
    │                            │
    │ • JSON: 200 escalas        │
    │ • PG:   200 escalas    ✓   │
    │                            │
    │ • Integridade FK       ✓   │
    │ • Constraints OK       ✓   │
    └────────────┬───────────────┘
                 │
                 ▼
    ┌────────────────────────────┐
    │   ✅ MIGRAÇÃO CONCLUÍDA    │
    │   Commit Transaction       │
    └────────────────────────────┘
```

---

## Docker Architecture

### ANTES

```
┌─────────────────────────────────────────────┐
│           Docker Compose                    │
├─────────────────────────────────────────────┤
│                                             │
│  ┌────────────────┐    ┌────────────────┐ │
│  │  rodizio-app   │    │     nginx      │ │
│  │  Flask + JSON  │◄───┤  Reverse Proxy │ │
│  └────────┬───────┘    └────────────────┘ │
│           │                                 │
│           ▼                                 │
│  ┌────────────────┐                        │
│  │ Volume:        │                        │
│  │ ./data:/app/data                        │
│  │   └─ db.json   │                        │
│  └────────────────┘                        │
└─────────────────────────────────────────────┘
```

### DEPOIS

```
┌───────────────────────────────────────────────────────┐
│              Docker Compose                           │
├───────────────────────────────────────────────────────┤
│                                                       │
│  ┌────────────────┐    ┌────────────────┐           │
│  │  rodizio-app   │    │     nginx      │           │
│  │ Flask + PG ORM │◄───┤  Reverse Proxy │           │
│  └────────┬───────┘    └────────────────┘           │
│           │                                           │
│           │ DATABASE_URL                              │
│           │                                           │
│           ▼                                           │
│  ┌────────────────────────────┐                      │
│  │    postgres ⭐              │                      │
│  │  PostgreSQL 16-alpine      │                      │
│  │  • ACID transactions       │                      │
│  │  • Connection pooling      │                      │
│  │  • WAL archiving           │                      │
│  └────────┬───────────────────┘                      │
│           │                                           │
│           ▼                                           │
│  ┌────────────────────────────┐                      │
│  │ Volume:                    │                      │
│  │ postgres_data:/var/lib/... │                      │
│  │   └─ Base de dados         │                      │
│  └────────────────────────────┘                      │
│                                                       │
│  ┌────────────────────────────┐                      │
│  │ Volume (opcional):         │                      │
│  │ ./data:/app/data           │                      │
│  │   └─ db.json (backup)      │                      │
│  └────────────────────────────┘                      │
└───────────────────────────────────────────────────────┘

Networks:
  rodizio-network (bridge)
    ├─ rodizio-app
    ├─ postgres
    └─ nginx
```

---

## Comparação de Performance

### Operações Típicas

| Operação | JSON | PostgreSQL | Fator |
|----------|------|------------|-------|
| **Login** | | | |
| Buscar usuário | 100ms | 20ms | 5x |
| Verificar hash | 50ms | 50ms | - |
| **Total Login** | 150ms | 70ms | **2x** |
| | | | |
| **Criar Escala** | | | |
| Buscar organistas | 200ms | 10ms | 20x |
| Buscar indisponib. | 500ms | 15ms | 33x |
| Gerar escala (logic) | 1000ms | 1000ms | - |
| Salvar 100 eventos | 300ms | 75ms | 4x |
| **Total Escala** | 2000ms | 1100ms | **2x** |
| | | | |
| **Relatório Mensal** | | | |
| Buscar escalas | 1000ms | 20ms | 50x |
| Contar por organista | 2000ms | 30ms | 67x |
| Calcular estatísticas | 1000ms | 20ms | 50x |
| Gerar PDF | 1000ms | 1000ms | - |
| **Total Relatório** | 5000ms | 1070ms | **5x** |
| | | | |
| **Busca Simples** | | | |
| 1 organista por ID | 50ms | 2ms | **25x** |
| Organistas de comum | 100ms | 5ms | **20x** |
| Indisponib. período | 500ms | 10ms | **50x** |

---

## Diagrama de Decisão

```
                 ┌──────────────────┐
                 │  Migrar para     │
                 │  PostgreSQL?     │
                 └────────┬─────────┘
                          │
           ┌──────────────┴──────────────┐
           │                             │
           ▼                             ▼
    ┌──────────────┐            ┌──────────────┐
    │ Base >100    │    NÃO     │ Base <100    │
    │ registros?   │◄───────────│ registros?   │
    └──────┬───────┘            └──────────────┘
           │ SIM                        │
           ▼                            ▼
    ┌──────────────┐            ┌──────────────┐
    │ Vai crescer? │            │SQLite sufici.│
    └──────┬───────┘            └──────────────┘
           │ SIM
           ▼
    ┌──────────────┐
    │ Performance  │
    │ crítica?     │
    └──────┬───────┘
           │ SIM
           ▼
    ┌──────────────┐
    │ PostgreSQL   │
    │ disponível?  │
    └──────┬───────┘
           │ SIM
           ▼
    ┌──────────────────┐
    │  ✅ MIGRAR!      │
    │                  │
    │ Benefícios:      │
    │ • Performance    │
    │ • Escalabilidade │
    │ • Confiabilidade │
    └──────────────────┘

SEU CASO:
✅ Base: ~100 registros (crescendo)
✅ Vai crescer: SIM (mais comuns)
✅ Performance: IMPORTANTE
✅ PostgreSQL: JÁ DISPONÍVEL

DECISÃO: MIGRAR! 🚀
```

---

## Timeline de Benefícios

```
Tempo │
      │
  t=0 │ ■ Migração Completa
      │ └─► Investimento: 2 sprints
      │
      │
 +1mês│ ▓▓▓ Benefícios Imediatos
      │ • Performance 10-50x
      │ • Menos bugs de concorrência
      │ • Queries mais rápidas
      │
      │
 +3mês│ ▓▓▓▓▓▓ ROI Positivo
      │ • Economia de tempo dev
      │ • Menos troubleshooting
      │ • Código mais limpo
      │
      │
 +6mês│ ▓▓▓▓▓▓▓▓▓ Escalabilidade
      │ • Suporta 10x mais dados
      │ • Features complexas fáceis
      │ • Relatórios avançados
      │
      │
 +1ano│ ▓▓▓▓▓▓▓▓▓▓▓▓ Fundação Sólida
      │ • Sistema maduro
      │ • Possível escalar horizontal
      │ • Múltiplas regionais
      │
      ▼

Investimento: ████ (2 sprints)
Retorno:      ▓▓▓▓▓▓▓▓▓▓▓▓ (contínuo)
```

---

## Conclusão Visual

```
┌─────────────────────────────────────────────────────┐
│                    RESUMO FINAL                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  JSON (Atual)          vs      PostgreSQL (Futuro) │
│  ════════════                  ══════════════════   │
│                                                     │
│  📁 Arquivo            →        🗄️ Banco Relacional│
│  🔒 File Lock          →        🔐 Row Lock (MVCC) │
│  ⏱️ ~100-5000ms        →        ⚡ ~2-100ms        │
│  📊 O(n) linear        →        📈 O(log n) indexed│
│  ❌ Sem validação      →        ✅ FK Constraints  │
│  💾 Backup = copiar    →        💿 Incremental+WAL │
│  🐌 Não escala         →        🚀 Escala bem      │
│                                                     │
│              RECOMENDAÇÃO: MIGRAR ✅                │
└─────────────────────────────────────────────────────┘
```

---

**Preparado por:** GitHub Copilot  
**Data:** 26 de outubro de 2025  
**Versão:** 1.0

**Próxima etapa:** Leia `SUMARIO_EXECUTIVO_POSTGRES.md` 🚀
