"""
Configuração de conexão com PostgreSQL
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# URL de conexão
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL não configurada no arquivo .env")

# Engine com pool de conexões
engine = create_engine(
    DATABASE_URL,
    pool_size=10,           # Conexões permanentes no pool
    max_overflow=20,        # Conexões adicionais se necessário
    pool_pre_ping=True,     # Testar conexão antes de usar
    echo=False,             # True para debug SQL
    pool_recycle=3600,      # Reciclar conexões a cada hora
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Thread-safe session
Session = scoped_session(SessionLocal)

# Base para modelos ORM
Base = declarative_base()

@contextmanager
def get_db_session():
    """
    Context manager para sessões de banco de dados.
    
    Uso:
        with get_db_session() as session:
            organista = session.query(Organista).filter_by(id='teste').first()
            # ... operações
            # commit automático no sucesso
            # rollback automático em exceção
    """
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

def init_db():
    """
    Inicializar database (criar tabelas se não existirem).
    Apenas para desenvolvimento - em produção use Alembic migrations.
    """
    Base.metadata.create_all(bind=engine)

def test_connection():
    """
    Testar conexão com o banco de dados.
    Retorna True se conectou com sucesso.
    """
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            return True
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return False
