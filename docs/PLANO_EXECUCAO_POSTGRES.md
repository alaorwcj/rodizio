# Plano de Execução - Migração PostgreSQL

**Projeto:** Rodízio de Organistas CCB  
**Objetivo:** Migração de db.json para PostgreSQL  
**Data:** 26 de outubro de 2025

---

## FASE 1: PREPARAÇÃO E SETUP (4 horas)

### 1.1 Setup do PostgreSQL Local

#### Passo 1: Criar Database
```sql
-- Conectar no PostgreSQL local
psql -U postgres

-- Criar usuário dedicado
CREATE USER rodizio_user WITH PASSWORD 'senha_segura_aqui';

-- Criar database
CREATE DATABASE rodizio
  WITH OWNER = rodizio_user
  ENCODING = 'UTF8'
  LC_COLLATE = 'pt_BR.UTF-8'
  LC_CTYPE = 'pt_BR.UTF-8'
  TEMPLATE = template0;

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE rodizio TO rodizio_user;

-- Conectar na base
\c rodizio

-- Habilitar extensões úteis
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- Para busca fuzzy
```

#### Passo 2: Testar Conexão
```bash
# Teste de conexão
psql -U rodizio_user -d rodizio -h localhost

# Ou com URL
psql postgresql://rodizio_user:senha@localhost:5432/rodizio
```

### 1.2 Atualizar Dependências Python

#### requirements.txt
```bash
# Adicionar ao arquivo existente
cat >> requirements.txt << EOF

# PostgreSQL Support
psycopg2-binary==2.9.9
SQLAlchemy==2.0.23
alembic==1.13.0
python-dotenv==1.0.0
EOF
```

#### Instalar
```bash
pip install -r requirements.txt
```

### 1.3 Configurar Variáveis de Ambiente

#### Criar .env
```bash
# /root/app/rodizio/.env
DATABASE_URL=postgresql://rodizio_user:senha_segura_aqui@localhost:5432/rodizio
ENVIRONMENT=development
SECRET_KEY=dev-secret-key-change-in-production

# Manter compatibilidade durante migração
USE_POSTGRES=false  # Alternar para true após migração
```

#### Atualizar .gitignore
```bash
echo ".env" >> .gitignore
echo "*.db" >> .gitignore
echo "data/rodizio.db*" >> .gitignore
```

---

## FASE 2: IMPLEMENTAÇÃO DO SCHEMA (3 horas)

### 2.1 Criar Arquivo de Schema

**Arquivo:** `/root/app/rodizio/database/schema.sql`

```sql
-- Ver conteúdo completo no documento de avaliação
-- Este arquivo contém:
-- - Criação de todas as tabelas
-- - Definição de índices
-- - Constraints e Foreign Keys
-- - Triggers para updated_at
```

### 2.2 Aplicar Schema

```bash
# Executar schema
psql -U rodizio_user -d rodizio -f database/schema.sql

# Verificar tabelas criadas
psql -U rodizio_user -d rodizio -c "\dt"
```

### 2.3 Criar Triggers para Timestamps

```sql
-- Função genérica para updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar em todas as tabelas relevantes
CREATE TRIGGER update_regionais_updated_at BEFORE UPDATE ON regionais
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sub_regionais_updated_at BEFORE UPDATE ON sub_regionais
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ... repetir para outras tabelas
```

---

## FASE 3: CAMADA DE DADOS (8 horas)

### 3.1 Estrutura de Arquivos

```
/root/app/rodizio/
├── database/
│   ├── __init__.py
│   ├── connection.py       # Engine e Session
│   ├── models.py           # Modelos SQLAlchemy
│   └── schema.sql          # Schema SQL
├── repositories/
│   ├── __init__.py
│   ├── base_repository.py
│   ├── regional_repo.py
│   ├── organista_repo.py
│   ├── escala_repo.py
│   ├── indisponibilidade_repo.py
│   ├── troca_repo.py
│   └── auditoria_repo.py
└── migrations/             # Alembic migrations
```

### 3.2 Implementar database/connection.py

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL não configurada")

# Engine com pool de conexões
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Testar conexão antes de usar
    echo=False,  # True para debug SQL
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Thread-safe session
Session = scoped_session(SessionLocal)

# Base para modelos
Base = declarative_base()

@contextmanager
def get_db_session():
    """Context manager para sessões"""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def init_db():
    """Inicializar database (criar tabelas se não existirem)"""
    Base.metadata.create_all(bind=engine)
```

### 3.3 Implementar database/models.py

```python
from sqlalchemy import Column, String, Boolean, Integer, Date, Text, ForeignKey, TIMESTAMP, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base

class Regional(Base):
    __tablename__ = 'regionais'
    
    id = Column(String(50), primary_key=True)
    nome = Column(String(200), nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    sub_regionais = relationship("SubRegional", back_populates="regional", cascade="all, delete-orphan")

class SubRegional(Base):
    __tablename__ = 'sub_regionais'
    
    id = Column(String(50), primary_key=True)
    regional_id = Column(String(50), ForeignKey('regionais.id', ondelete='CASCADE'), nullable=False)
    nome = Column(String(200), nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    regional = relationship("Regional", back_populates="sub_regionais")
    comuns = relationship("Comum", back_populates="sub_regional", cascade="all, delete-orphan")

class Comum(Base):
    __tablename__ = 'comuns'
    
    id = Column(String(50), primary_key=True)
    sub_regional_id = Column(String(50), ForeignKey('sub_regionais.id', ondelete='CASCADE'), nullable=False)
    nome = Column(String(200), nullable=False)
    endereco = Column(Text)
    cidade = Column(String(100))
    ativo = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    sub_regional = relationship("SubRegional", back_populates="comuns")
    organistas = relationship("Organista", back_populates="comum", cascade="all, delete-orphan")
    # ... outros relacionamentos

class Organista(Base):
    __tablename__ = 'organistas'
    
    id = Column(String(50), primary_key=True)
    comum_id = Column(String(50), ForeignKey('comuns.id', ondelete='CASCADE'), nullable=False)
    nome = Column(String(200), nullable=False)
    password_hash = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    comum = relationship("Comum", back_populates="organistas")
    tipos = relationship("OrganistaTipo", back_populates="organista", cascade="all, delete-orphan")
    dias_permitidos = relationship("OrganistaDiaPermitido", back_populates="organista", cascade="all, delete-orphan")

# ... Continuar com outros modelos
```

### 3.4 Implementar Repositories

**Exemplo: repositories/organista_repo.py**

```python
from typing import List, Optional
from database.connection import get_db_session
from database.models import Organista, OrganistaTipo, OrganistaDiaPermitido

class OrganistaRepository:
    
    def get_by_id(self, organista_id: str) -> Optional[Organista]:
        with get_db_session() as session:
            return session.query(Organista).filter(Organista.id == organista_id).first()
    
    def get_by_comum(self, comum_id: str) -> List[Organista]:
        with get_db_session() as session:
            return session.query(Organista).filter(Organista.comum_id == comum_id).all()
    
    def create(self, data: dict) -> Organista:
        with get_db_session() as session:
            organista = Organista(
                id=data['id'],
                comum_id=data['comum_id'],
                nome=data['nome'],
                password_hash=data['password_hash']
            )
            session.add(organista)
            
            # Adicionar tipos
            for tipo in data.get('tipos', []):
                session.add(OrganistaTipo(organista_id=organista.id, tipo=tipo))
            
            # Adicionar dias permitidos
            for dia in data.get('dias_permitidos', []):
                session.add(OrganistaDiaPermitido(organista_id=organista.id, dia=dia))
            
            session.flush()
            return organista
    
    def update(self, organista_id: str, data: dict) -> Optional[Organista]:
        with get_db_session() as session:
            organista = session.query(Organista).filter(Organista.id == organista_id).first()
            if not organista:
                return None
            
            # Atualizar campos básicos
            for key, value in data.items():
                if key in ['nome', 'password_hash']:
                    setattr(organista, key, value)
            
            # Atualizar tipos se fornecido
            if 'tipos' in data:
                session.query(OrganistaTipo).filter(OrganistaTipo.organista_id == organista_id).delete()
                for tipo in data['tipos']:
                    session.add(OrganistaTipo(organista_id=organista_id, tipo=tipo))
            
            session.flush()
            return organista
    
    def delete(self, organista_id: str) -> bool:
        with get_db_session() as session:
            result = session.query(Organista).filter(Organista.id == organista_id).delete()
            return result > 0
```

---

## FASE 4: SCRIPT DE MIGRAÇÃO DE DADOS (4 horas)

### 4.1 Criar Script de Migração

**Arquivo:** `/root/app/rodizio/scripts/migrate_to_postgres.py`

```python
#!/usr/bin/env python3
"""
Script de migração de db.json para PostgreSQL
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Adicionar root ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import engine, Session
from database.models import (
    Regional, SubRegional, Comum, Organista, 
    OrganistaTipo, OrganistaDiaPermitido,
    Indisponibilidade, Escala, EscalaRJM,
    LogAuditoria
)

JSON_PATH = Path(__file__).parent.parent / 'data' / 'db.json'
BACKUP_DIR = Path(__file__).parent.parent / 'data' / 'backups'

def backup_json():
    """Criar backup do JSON antes da migração"""
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = BACKUP_DIR / f'db_pre_postgres_{timestamp}.json'
    
    import shutil
    shutil.copy2(JSON_PATH, backup_path)
    print(f"✅ Backup criado: {backup_path}")
    return backup_path

def load_json():
    """Carregar dados do JSON"""
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def migrate_hierarchy(session, data):
    """Migrar hierarquia: Regionais > Sub-Regionais > Comuns"""
    print("\n📊 Migrando hierarquia organizacional...")
    
    regionais_count = 0
    subs_count = 0
    comuns_count = 0
    
    for regional_id, regional_data in data.get('regionais', {}).items():
        # Criar Regional
        regional = Regional(
            id=regional_data.get('id', regional_id),
            nome=regional_data.get('nome', ''),
            ativo=regional_data.get('ativo', True)
        )
        session.add(regional)
        regionais_count += 1
        
        # Sub-Regionais
        for sub_id, sub_data in regional_data.get('sub_regionais', {}).items():
            sub_regional = SubRegional(
                id=sub_data.get('id', sub_id),
                regional_id=regional.id,
                nome=sub_data.get('nome', ''),
                ativo=sub_data.get('ativo', True)
            )
            session.add(sub_regional)
            subs_count += 1
            
            # Comuns
            for comum_id, comum_data in sub_data.get('comuns', {}).items():
                comum = Comum(
                    id=comum_data.get('id', comum_id),
                    sub_regional_id=sub_regional.id,
                    nome=comum_data.get('nome', ''),
                    endereco=comum_data.get('endereco', ''),
                    cidade=comum_data.get('cidade', ''),
                    ativo=comum_data.get('ativo', True)
                )
                session.add(comum)
                comuns_count += 1
    
    session.flush()
    print(f"   ✓ {regionais_count} Regionais")
    print(f"   ✓ {subs_count} Sub-Regionais")
    print(f"   ✓ {comuns_count} Comuns")

def migrate_organistas(session, data):
    """Migrar organistas e suas propriedades"""
    print("\n🎹 Migrando organistas...")
    
    organistas_count = 0
    tipos_count = 0
    dias_count = 0
    
    for regional_id, regional_data in data.get('regionais', {}).items():
        for sub_id, sub_data in regional_data.get('sub_regionais', {}).items():
            for comum_id, comum_data in sub_data.get('comuns', {}).items():
                
                for org_data in comum_data.get('organistas', []):
                    # Criar organista
                    organista = Organista(
                        id=org_data['id'],
                        comum_id=comum_data.get('id', comum_id),
                        nome=org_data['nome'],
                        password_hash=org_data.get('password_hash', '')
                    )
                    session.add(organista)
                    organistas_count += 1
                    
                    # Tipos
                    for tipo in org_data.get('tipos', []):
                        session.add(OrganistaTipo(
                            organista_id=organista.id,
                            tipo=tipo
                        ))
                        tipos_count += 1
                    
                    # Dias permitidos
                    for dia in org_data.get('dias_permitidos', []):
                        session.add(OrganistaDiaPermitido(
                            organista_id=organista.id,
                            dia=dia
                        ))
                        dias_count += 1
    
    session.flush()
    print(f"   ✓ {organistas_count} Organistas")
    print(f"   ✓ {tipos_count} Tipos")
    print(f"   ✓ {dias_count} Dias permitidos")

def migrate_indisponibilidades(session, data):
    """Migrar indisponibilidades"""
    print("\n📅 Migrando indisponibilidades...")
    count = 0
    
    for regional_id, regional_data in data.get('regionais', {}).items():
        for sub_id, sub_data in regional_data.get('sub_regionais', {}).items():
            for comum_id, comum_data in sub_data.get('comuns', {}).items():
                
                for ind in comum_data.get('indisponibilidades', []):
                    session.add(Indisponibilidade(
                        comum_id=comum_data.get('id', comum_id),
                        organista_id=ind.get('id'),
                        data=ind.get('data'),
                        motivo=ind.get('motivo'),
                        autor=ind.get('autor'),
                        status=ind.get('status')
                    ))
                    count += 1
    
    session.flush()
    print(f"   ✓ {count} Indisponibilidades")

# ... Continuar com outras funções de migração

def validate_migration(session, original_data):
    """Validar se migração foi bem-sucedida"""
    print("\n✅ Validando migração...")
    
    # Contar registros
    from sqlalchemy import func
    
    checks = [
        ('Regionais', Regional, len(original_data.get('regionais', {}))),
        ('Organistas', Organista, sum(
            len(c.get('organistas', [])) 
            for r in original_data.get('regionais', {}).values()
            for s in r.get('sub_regionais', {}).values()
            for c in s.get('comuns', {}).values()
        )),
        # ... outros checks
    ]
    
    all_ok = True
    for name, model, expected in checks:
        actual = session.query(func.count(model.id)).scalar()
        status = "✓" if actual == expected else "✗"
        print(f"   {status} {name}: {actual}/{expected}")
        if actual != expected:
            all_ok = False
    
    return all_ok

def main():
    print("=" * 60)
    print("MIGRAÇÃO DB.JSON → POSTGRESQL")
    print("=" * 60)
    
    # 1. Backup
    backup_path = backup_json()
    
    # 2. Carregar JSON
    print("\n📂 Carregando db.json...")
    data = load_json()
    print(f"   ✓ {len(data)} chaves principais")
    
    # 3. Conectar PostgreSQL
    print("\n🔌 Conectando PostgreSQL...")
    session = Session()
    
    try:
        # 4. Migrar dados
        migrate_hierarchy(session, data)
        migrate_organistas(session, data)
        migrate_indisponibilidades(session, data)
        # ... outras migrações
        
        # 5. Validar
        if validate_migration(session, data):
            session.commit()
            print("\n" + "=" * 60)
            print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("=" * 60)
        else:
            session.rollback()
            print("\n❌ Validação falhou - rollback executado")
            sys.exit(1)
            
    except Exception as e:
        session.rollback()
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()

if __name__ == '__main__':
    main()
```

### 4.2 Executar Migração

```bash
# Dry-run primeiro (opcional - adicionar flag)
python scripts/migrate_to_postgres.py --dry-run

# Executar migração real
python scripts/migrate_to_postgres.py

# Verificar dados
psql -U rodizio_user -d rodizio -c "SELECT COUNT(*) FROM organistas;"
```

---

## FASE 5: REFATORAÇÃO DO app.py (8 horas)

### 5.1 Criar Camada de Abstração

**Arquivo:** `database/db_adapter.py`

```python
"""
Adapter para abstrair acesso a dados.
Permite usar JSON ou PostgreSQL de forma transparente.
"""
import os
from typing import Dict, List, Optional

USE_POSTGRES = os.getenv('USE_POSTGRES', 'false').lower() == 'true'

if USE_POSTGRES:
    from repositories import *
    # Usar repositories PostgreSQL
else:
    # Usar JSON legado
    pass

class DatabaseAdapter:
    """Interface unificada para acesso a dados"""
    
    def __init__(self):
        self.use_postgres = USE_POSTGRES
        if self.use_postgres:
            from repositories.organista_repo import OrganistaRepository
            self.organista_repo = OrganistaRepository()
            # ... outros repos
    
    def get_organista(self, organista_id: str):
        if self.use_postgres:
            return self.organista_repo.get_by_id(organista_id)
        else:
            # Fallback para JSON
            db = load_db()  # função legada
            # ... buscar no JSON
            pass
    
    # ... outros métodos
```

### 5.2 Refatorar Gradualmente

**Estratégia:**
1. Criar `DatabaseAdapter` com métodos espelhando funções atuais
2. Substituir chamadas no `app.py` uma por vez
3. Testar cada mudança
4. Quando todas estiverem OK, remover código JSON legado

**Exemplo de refatoração:**

```python
# ANTES
@app.route('/api/organistas/<comum_id>')
def get_organistas(comum_id):
    db = load_db()
    # Navegar JSON...
    organistas = []
    for r in db['regionais'].values():
        for s in r['sub_regionais'].values():
            for c in s['comuns'].values():
                if c['id'] == comum_id:
                    organistas = c.get('organistas', [])
    return jsonify(organistas)

# DEPOIS
@app.route('/api/organistas/<comum_id>')
def get_organistas(comum_id):
    from repositories.organista_repo import OrganistaRepository
    repo = OrganistaRepository()
    organistas = repo.get_by_comum(comum_id)
    return jsonify([o.to_dict() for o in organistas])
```

---

## FASE 6: DOCKER & DEPLOYMENT (2 horas)

### 6.1 Atualizar docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: rodizio-postgres
    environment:
      POSTGRES_DB: rodizio
      POSTGRES_USER: rodizio_user
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql
    networks:
      - rodizio-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U rodizio_user"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  rodizio-app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: rodizio-organistas
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://rodizio_user:${DB_PASSWORD:-changeme}@postgres:5432/rodizio
      - USE_POSTGRES=true
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./data:/app/data  # Manter para backups
    networks:
      - rodizio-network
    restart: unless-stopped

  nginx:
    # ... configuração existente

volumes:
  postgres_data:
    driver: local

networks:
  rodizio-network:
    driver: bridge
```

### 6.2 Atualizar Dockerfile

```dockerfile
# Adicionar ao Dockerfile existente
# Instalar dependências PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Resto permanece igual
```

### 6.3 Script de Deploy

```bash
#!/bin/bash
# deploy_postgres.sh

echo "🚀 Iniciando deploy com PostgreSQL..."

# 1. Backup do JSON
cp data/db.json data/backups/db_pre_deploy_$(date +%Y%m%d_%H%M%S).json

# 2. Build das imagens
docker-compose build

# 3. Subir PostgreSQL primeiro
docker-compose up -d postgres

# 4. Aguardar PostgreSQL ficar pronto
echo "⏳ Aguardando PostgreSQL..."
docker-compose exec postgres pg_isready -U rodizio_user
while [ $? -ne 0 ]; do
  sleep 2
  docker-compose exec postgres pg_isready -U rodizio_user
done

# 5. Executar migração de dados (se necessário)
if [ "$1" == "--migrate" ]; then
  echo "📊 Executando migração de dados..."
  docker-compose exec rodizio-app python scripts/migrate_to_postgres.py
fi

# 6. Subir aplicação
docker-compose up -d rodizio-app

# 7. Verificar saúde
docker-compose ps
docker-compose logs --tail=50 rodizio-app

echo "✅ Deploy concluído!"
```

---

## FASE 7: TESTES E VALIDAÇÃO (3 horas)

### 7.1 Testes de Unidade

```python
# tests/test_repositories.py
import pytest
from database.connection import Session
from repositories.organista_repo import OrganistaRepository

@pytest.fixture
def db_session():
    session = Session()
    yield session
    session.rollback()
    session.close()

def test_create_organista(db_session):
    repo = OrganistaRepository()
    data = {
        'id': 'test_org',
        'comum_id': 'test_comum',
        'nome': 'Teste',
        'password_hash': 'hash',
        'tipos': ['Culto'],
        'dias_permitidos': ['Domingo']
    }
    
    organista = repo.create(data)
    assert organista.id == 'test_org'
    assert len(organista.tipos) == 1
```

### 7.2 Testes de Integração

```bash
# Criar ambiente de teste
createdb rodizio_test
psql rodizio_test < database/schema.sql

# Executar testes
pytest tests/
```

### 7.3 Checklist de Validação

- [ ] Todas as tabelas criadas corretamente
- [ ] Dados migrados com sucesso
- [ ] Contagem de registros bate com JSON
- [ ] Login funciona
- [ ] Criação de escala funciona
- [ ] Indisponibilidades funcionam
- [ ] Trocas funcionam
- [ ] Logs de auditoria salvos
- [ ] Performance aceitável
- [ ] Backup automatizado configurado

---

## ROLLBACK PLAN

### Se algo der errado:

```bash
# 1. Parar containers
docker-compose down

# 2. Restaurar código
git checkout main  # ou branch anterior

# 3. Restaurar JSON
cp data/backups/db_pre_deploy_*.json data/db.json

# 4. Subir com configuração antiga
USE_POSTGRES=false docker-compose up -d

# 5. Verificar funcionamento
curl http://localhost/health
```

---

## CRONOGRAMA DETALHADO

### Semana 1: Preparação e Estrutura
- **Dia 1 (Segunda):** Setup PostgreSQL, dependências, schema
- **Dia 2 (Terça):** Models e connection layer
- **Dia 3 (Quarta):** Repositories básicos
- **Dia 4 (Quinta):** Repositories completos
- **Dia 5 (Sexta):** Testes de repositories

### Semana 2: Migração e Deploy
- **Dia 1 (Segunda):** Script de migração de dados
- **Dia 2 (Terça):** Refatoração app.py (parte 1)
- **Dia 3 (Quarta):** Refatoração app.py (parte 2)
- **Dia 4 (Quinta):** Docker, testes integração
- **Dia 5 (Sexta):** Deploy, validação, ajustes

---

## MÉTRICAS DE SUCESSO

### Critérios de Aceitação
✅ 100% dos dados migrados sem perda  
✅ Todas as funcionalidades existentes funcionam  
✅ Performance igual ou melhor que JSON  
✅ Testes passando (cobertura >80%)  
✅ Documentação atualizada  
✅ Backup automatizado configurado  

### KPIs de Performance
- Query de listagem: < 100ms
- Criação de escala: < 500ms
- Login: < 200ms
- Carga da página: < 1s

---

## PRÓXIMOS PASSOS

1. ✅ **Aprovar este plano**
2. 🔧 **Criar branch:** `git checkout -b feature/postgres-migration`
3. 📋 **Setup inicial:** PostgreSQL + dependências
4. 🏗️ **Implementação:** Seguir fases 2-7
5. ✅ **Review e merge**
6. 🚀 **Deploy gradual**

---

**Preparado para execução!** 🚀
