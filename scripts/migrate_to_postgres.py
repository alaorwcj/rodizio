#!/usr/bin/env python3
"""
Script de migração de db.json para PostgreSQL
Versão: 1.0
Data: 26/10/2025

IMPORTANTE: Este script faz backup automático antes de migrar!
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Caminhos
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
JSON_PATH = DATA_DIR / 'db.json'
BACKUP_DIR = DATA_DIR / 'backups'

# Conexão PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL')

class Colors:
    """Cores para output no terminal"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(msg):
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{msg.center(60)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

def print_success(msg):
    print(f"{Colors.OKGREEN}✓ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}✗ {msg}{Colors.ENDC}")

def print_warning(msg):
    print(f"{Colors.WARNING}⚠ {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.OKCYAN}ℹ {msg}{Colors.ENDC}")

def backup_json():
    """Criar backup do JSON antes da migração"""
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = BACKUP_DIR / f'db_pre_migrate_{timestamp}.json'
    
    if JSON_PATH.exists():
        import shutil
        shutil.copy2(JSON_PATH, backup_path)
        print_success(f"Backup criado: {backup_path}")
        return backup_path
    else:
        print_error(f"JSON não encontrado: {JSON_PATH}")
        return None

def load_json():
    """Carregar dados do JSON"""
    print_info("Carregando db.json...")
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print_success(f"JSON carregado: {len(data)} chaves principais")
    return data

def connect_db():
    """Conectar ao PostgreSQL"""
    print_info("Conectando ao PostgreSQL...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print_success("Conexão estabelecida!")
        return conn
    except Exception as e:
        print_error(f"Erro ao conectar: {e}")
        sys.exit(1)

def migrate_hierarchy(conn, data):
    """Migrar hierarquia: Regionais > Sub-Regionais > Comuns"""
    print_header("MIGRANDO HIERARQUIA ORGANIZACIONAL")
    
    cur = conn.cursor()
    counts = {'regionais': 0, 'sub_regionais': 0, 'comuns': 0}
    
    regionais = data.get('regionais', {})
    
    for regional_id, regional_data in regionais.items():
        # Inserir Regional
        cur.execute(
            """INSERT INTO regionais (id, nome, ativo) 
               VALUES (%s, %s, %s) 
               ON CONFLICT (id) DO UPDATE SET nome = EXCLUDED.nome, ativo = EXCLUDED.ativo""",
            (
                regional_data.get('id', regional_id),
                regional_data.get('nome', ''),
                regional_data.get('ativo', True)
            )
        )
        counts['regionais'] += 1
        
        # Sub-Regionais
        for sub_id, sub_data in regional_data.get('sub_regionais', {}).items():
            cur.execute(
                """INSERT INTO sub_regionais (id, regional_id, nome, ativo) 
                   VALUES (%s, %s, %s, %s)
                   ON CONFLICT (id) DO UPDATE SET nome = EXCLUDED.nome, ativo = EXCLUDED.ativo""",
                (
                    sub_data.get('id', sub_id),
                    regional_data.get('id', regional_id),
                    sub_data.get('nome', ''),
                    sub_data.get('ativo', True)
                )
            )
            counts['sub_regionais'] += 1
            
            # Comuns
            for comum_id, comum_data in sub_data.get('comuns', {}).items():
                cur.execute(
                    """INSERT INTO comuns (id, sub_regional_id, nome, endereco, cidade, ativo) 
                       VALUES (%s, %s, %s, %s, %s, %s)
                       ON CONFLICT (id) DO UPDATE SET 
                           nome = EXCLUDED.nome, 
                           endereco = EXCLUDED.endereco,
                           cidade = EXCLUDED.cidade,
                           ativo = EXCLUDED.ativo""",
                    (
                        comum_data.get('id', comum_id),
                        sub_data.get('id', sub_id),
                        comum_data.get('nome', ''),
                        comum_data.get('endereco', ''),
                        comum_data.get('cidade', ''),
                        comum_data.get('ativo', True)
                    )
                )
                counts['comuns'] += 1
    
    conn.commit()
    print_success(f"Regionais: {counts['regionais']}")
    print_success(f"Sub-Regionais: {counts['sub_regionais']}")
    print_success(f"Comuns: {counts['comuns']}")
    
    return counts

def migrate_organistas(conn, data):
    """Migrar organistas e suas propriedades"""
    print_header("MIGRANDO ORGANISTAS")
    
    cur = conn.cursor()
    counts = {'organistas': 0, 'tipos': 0, 'dias': 0}
    
    regionais = data.get('regionais', {})
    
    for regional_data in regionais.values():
        for sub_data in regional_data.get('sub_regionais', {}).values():
            for comum_id, comum_data in sub_data.get('comuns', {}).items():
                comum_id_real = comum_data.get('id', comum_id)
                
                for org in comum_data.get('organistas', []):
                    # Inserir organista
                    cur.execute(
                        """INSERT INTO organistas (id, comum_id, nome, password_hash) 
                           VALUES (%s, %s, %s, %s)
                           ON CONFLICT (id) DO UPDATE SET 
                               nome = EXCLUDED.nome,
                               password_hash = EXCLUDED.password_hash""",
                        (
                            org['id'],
                            comum_id_real,
                            org['nome'],
                            org.get('password_hash', '')
                        )
                    )
                    counts['organistas'] += 1
                    
                    # Limpar tipos e dias antigos
                    cur.execute("DELETE FROM organista_tipos WHERE organista_id = %s", (org['id'],))
                    cur.execute("DELETE FROM organista_dias_permitidos WHERE organista_id = %s", (org['id'],))
                    
                    # Tipos
                    for tipo in org.get('tipos', []):
                        cur.execute(
                            "INSERT INTO organista_tipos (organista_id, tipo) VALUES (%s, %s)",
                            (org['id'], tipo)
                        )
                        counts['tipos'] += 1
                    
                    # Dias permitidos
                    for dia in org.get('dias_permitidos', []):
                        cur.execute(
                            "INSERT INTO organista_dias_permitidos (organista_id, dia) VALUES (%s, %s)",
                            (org['id'], dia)
                        )
                        counts['dias'] += 1
    
    conn.commit()
    print_success(f"Organistas: {counts['organistas']}")
    print_success(f"Tipos: {counts['tipos']}")
    print_success(f"Dias permitidos: {counts['dias']}")
    
    return counts

def migrate_indisponibilidades(conn, data):
    """Migrar indisponibilidades"""
    print_header("MIGRANDO INDISPONIBILIDADES")
    
    cur = conn.cursor()
    count = 0
    
    # Limpar indisponibilidades antigas
    cur.execute("DELETE FROM indisponibilidades")
    
    regionais = data.get('regionais', {})
    
    for regional_data in regionais.values():
        for sub_data in regional_data.get('sub_regionais', {}).values():
            for comum_id, comum_data in sub_data.get('comuns', {}).items():
                comum_id_real = comum_data.get('id', comum_id)
                
                for ind in comum_data.get('indisponibilidades', []):
                    cur.execute(
                        """INSERT INTO indisponibilidades 
                           (comum_id, organista_id, data, motivo, autor, status) 
                           VALUES (%s, %s, %s, %s, %s, %s)""",
                        (
                            comum_id_real,
                            ind.get('id'),
                            ind.get('data'),
                            ind.get('motivo'),
                            ind.get('autor'),
                            ind.get('status')
                        )
                    )
                    count += 1
    
    conn.commit()
    print_success(f"Indisponibilidades: {count}")
    
    return count

def migrate_escalas(conn, data):
    """Migrar escalas (culto e RJM)"""
    print_header("MIGRANDO ESCALAS")
    
    cur = conn.cursor()
    counts = {'escala': 0, 'rjm': 0}
    
    # Limpar escalas antigas
    cur.execute("DELETE FROM escala")
    cur.execute("DELETE FROM escala_rjm")
    
    regionais = data.get('regionais', {})
    
    for regional_data in regionais.values():
        for sub_data in regional_data.get('sub_regionais', {}).values():
            for comum_id, comum_data in sub_data.get('comuns', {}).items():
                comum_id_real = comum_data.get('id', comum_id)
                
                # Escala regular
                for esc in comum_data.get('escala', []):
                    cur.execute(
                        """INSERT INTO escala 
                           (comum_id, data, dia_semana, meia_hora, culto) 
                           VALUES (%s, %s, %s, %s, %s)""",
                        (
                            comum_id_real,
                            esc.get('data'),
                            esc.get('dia_semana'),
                            esc.get('meia_hora'),
                            esc.get('culto')
                        )
                    )
                    counts['escala'] += 1
                
                # Escala RJM
                for rjm in comum_data.get('escala_rjm', []):
                    cur.execute(
                        """INSERT INTO escala_rjm 
                           (id, comum_id, data, dia_semana, organista) 
                           VALUES (%s, %s, %s, %s, %s)
                           ON CONFLICT (id) DO UPDATE SET 
                               data = EXCLUDED.data,
                               organista = EXCLUDED.organista""",
                        (
                            rjm.get('id'),
                            comum_id_real,
                            rjm.get('data'),
                            rjm.get('dia_semana'),
                            rjm.get('organista')
                        )
                    )
                    counts['rjm'] += 1
    
    conn.commit()
    print_success(f"Escalas regulares: {counts['escala']}")
    print_success(f"Escalas RJM: {counts['rjm']}")
    
    return counts

def migrate_usuarios(conn, data):
    """Migrar usuários do sistema"""
    print_header("MIGRANDO USUÁRIOS")
    
    cur = conn.cursor()
    count = 0
    
    # Limpar usuários antigos
    cur.execute("DELETE FROM usuarios")
    
    usuarios = data.get('usuarios', {})
    
    # Verificar se é dict ou list
    if isinstance(usuarios, dict):
        usuarios_list = list(usuarios.values())
    else:
        usuarios_list = usuarios
    
    for user in usuarios_list:
        # Inferir nivel se não existir
        nivel = user.get('nivel')
        if not nivel:
            tipo = user.get('tipo', '')
            if tipo == 'master':
                nivel = 'sistema'
            elif tipo == 'admin_regional':
                nivel = 'regional'
            elif tipo == 'encarregado_sub_regional':
                nivel = 'sub_regional'
            elif tipo == 'encarregado_comum':
                nivel = 'comum'
            else:
                nivel = 'comum'  # default
        
        cur.execute(
            """INSERT INTO usuarios 
               (id, nome, password_hash, tipo, nivel, contexto_id, ativo) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                user.get('id'),
                user.get('nome'),
                user.get('password_hash'),
                user.get('tipo'),
                nivel,
                user.get('contexto_id'),
                user.get('ativo', True)
            )
        )
        count += 1
    
    conn.commit()
    print_success(f"Usuários: {count}")
    
    return count

def migrate_logs_auditoria(conn, data):
    """Migrar logs de auditoria"""
    print_header("MIGRANDO LOGS DE AUDITORIA")
    
    cur = conn.cursor()
    count = 0
    
    # Limpar logs antigos
    cur.execute("DELETE FROM logs_auditoria")
    
    logs = data.get('logs_auditoria', [])
    
    for log in logs:
        contexto = log.get('contexto', {})
        cur.execute(
            """INSERT INTO logs_auditoria 
               (id, timestamp, tipo, categoria, acao, descricao, 
                usuario_id, usuario_nome, usuario_tipo,
                regional_id, sub_regional_id, comum_id,
                status, ip, user_agent, dados_antes, dados_depois) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (id) DO NOTHING""",
            (
                log.get('id'),
                log.get('timestamp'),
                log.get('tipo'),
                log.get('categoria'),
                log.get('acao'),
                log.get('descricao'),
                log.get('usuario_id'),
                log.get('usuario_nome'),
                log.get('usuario_tipo'),
                contexto.get('regional_id') if isinstance(contexto, dict) else None,
                contexto.get('sub_regional_id') if isinstance(contexto, dict) else None,
                contexto.get('comum_id') if isinstance(contexto, dict) else None,
                log.get('status'),
                log.get('ip'),
                log.get('user_agent'),
                json.dumps(log.get('dados_antes')) if log.get('dados_antes') else None,
                json.dumps(log.get('dados_depois')) if log.get('dados_depois') else None
            )
        )
        count += 1
    
    conn.commit()
    print_success(f"Logs de auditoria: {count}")
    
    return count

def validate_migration(conn, original_data):
    """Validar se migração foi bem-sucedida"""
    print_header("VALIDANDO MIGRAÇÃO")
    
    cur = conn.cursor()
    all_ok = True
    
    # Contar registros esperados do JSON
    # Usar set para contar IDs únicos de organistas
    organistas_ids = set()
    for r in original_data.get('regionais', {}).values():
        for s in r.get('sub_regionais', {}).values():
            for c in s.get('comuns', {}).values():
                for org in c.get('organistas', []):
                    organistas_ids.add(org.get('id'))
    
    usuarios = original_data.get('usuarios', {})
    if isinstance(usuarios, dict):
        usuarios_count = len(usuarios)
    else:
        usuarios_count = len(usuarios)
    
    expected = {
        'regionais': len(original_data.get('regionais', {})),
        'organistas': len(organistas_ids),
        'usuarios': usuarios_count,
        'logs': len(original_data.get('logs_auditoria', []))
    }
    
    # Verificar contagens no PostgreSQL
    checks = [
        ('Regionais', 'regionais', expected['regionais']),
        ('Organistas', 'organistas', expected['organistas']),
        ('Usuários', 'usuarios', expected['usuarios']),
        ('Logs Auditoria', 'logs_auditoria', expected['logs'])
    ]
    
    for name, table, expected_count in checks:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        actual_count = cur.fetchone()[0]
        
        if actual_count == expected_count:
            print_success(f"{name}: {actual_count}/{expected_count} ✓")
        else:
            print_error(f"{name}: {actual_count}/{expected_count} ✗")
            all_ok = False
    
    return all_ok

def main():
    """Função principal de migração"""
    print_header("MIGRAÇÃO DB.JSON → POSTGRESQL")
    
    # 1. Verificar se JSON existe
    if not JSON_PATH.exists():
        print_error(f"Arquivo JSON não encontrado: {JSON_PATH}")
        sys.exit(1)
    
    # 2. Backup
    backup_path = backup_json()
    if not backup_path:
        print_error("Falha ao criar backup!")
        sys.exit(1)
    
    # 3. Carregar JSON
    try:
        data = load_json()
    except Exception as e:
        print_error(f"Erro ao carregar JSON: {e}")
        sys.exit(1)
    
    # 4. Conectar PostgreSQL
    conn = connect_db()
    
    try:
        # 5. Migrar dados (ordem importante por causa das FK)
        migrate_hierarchy(conn, data)
        migrate_organistas(conn, data)
        migrate_indisponibilidades(conn, data)
        migrate_escalas(conn, data)
        migrate_usuarios(conn, data)
        migrate_logs_auditoria(conn, data)
        
        # 6. Validar
        if validate_migration(conn, data):
            print_header("MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            print_success(f"Backup disponível em: {backup_path}")
            print_info("Próximos passos:")
            print_info("  1. Verificar dados no PostgreSQL")
            print_info("  2. Testar aplicação com USE_POSTGRES=true")
            print_info("  3. Se tudo OK, atualizar docker-compose.yml")
        else:
            print_error("Validação falhou! Verifique os logs acima.")
            conn.rollback()
            sys.exit(1)
            
    except Exception as e:
        conn.rollback()
        print_error(f"ERRO durante migração: {e}")
        import traceback
        traceback.print_exc()
        print_warning(f"Banco revertido (rollback). Backup disponível em: {backup_path}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == '__main__':
    main()
