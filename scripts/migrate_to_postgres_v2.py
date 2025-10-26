#!/usr/bin/env python3
"""
Script de migração de db.json para PostgreSQL (Schema Normalizado v2)
Versão: 2.0
Data: 26/10/2025

IMPORTANTE: Este script faz backup automático antes de migrar!
"""

import json
import os
import sys
import uuid
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
    backup_path = BACKUP_DIR / f'db_pre_migrate_v2_{timestamp}.json'
    
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
            """INSERT INTO regionais (id, nome) 
               VALUES (%s, %s) 
               ON CONFLICT (id) DO UPDATE SET nome = EXCLUDED.nome""",
            (
                regional_data.get('id', regional_id),
                regional_data.get('nome', '')
            )
        )
        counts['regionais'] += 1
        
        # Sub-Regionais
        for sub_id, sub_data in regional_data.get('sub_regionais', {}).items():
            cur.execute(
                """INSERT INTO sub_regionais (id, regional_id, nome) 
                   VALUES (%s, %s, %s)
                   ON CONFLICT (id) DO UPDATE SET nome = EXCLUDED.nome""",
                (
                    sub_data.get('id', sub_id),
                    regional_data.get('id', regional_id),
                    sub_data.get('nome', '')
                )
            )
            counts['sub_regionais'] += 1
            
            # Comuns
            for comum_id, comum_data in sub_data.get('comuns', {}).items():
                cur.execute(
                    """INSERT INTO comuns (id, sub_regional_id, nome) 
                       VALUES (%s, %s, %s)
                       ON CONFLICT (id) DO UPDATE SET nome = EXCLUDED.nome""",
                    (
                        comum_data.get('id', comum_id),
                        sub_data.get('id', sub_id),
                        comum_data.get('nome', '')
                    )
                )
                counts['comuns'] += 1
    
    conn.commit()
    print_success(f"Regionais: {counts['regionais']}")
    print_success(f"Sub-Regionais: {counts['sub_regionais']}")
    print_success(f"Comuns: {counts['comuns']}")
    
    return counts

def migrate_organistas(conn, data):
    """Migrar organistas"""
    print_header("MIGRANDO ORGANISTAS")
    
    cur = conn.cursor()
    count = 0
    
    # Mapear tipos de organistas do JSON para IDs
    tipo_map = {
        'Titular': 1,
        'Auxiliar': 2,
        'Substituto': 3
    }
    
    regionais = data.get('regionais', {})
    
    for regional_id, regional_data in regionais.items():
        for sub_id, sub_data in regional_data.get('sub_regionais', {}).items():
            for comum_id, comum_data in sub_data.get('comuns', {}).items():
                organistas = comum_data.get('organistas', [])
                
                for org in organistas:
                    # Determinar tipo_id
                    tipo_str = org.get('tipo', 'Titular')
                    tipo_id = tipo_map.get(tipo_str, 1)
                    
                    # Inserir organista
                    cur.execute(
                        """INSERT INTO organistas 
                           (id, comum_id, nome, telefone, email, tipo_id, ativo) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s)
                           ON CONFLICT (id) DO UPDATE SET 
                               nome = EXCLUDED.nome,
                               telefone = EXCLUDED.telefone,
                               email = EXCLUDED.email,
                               tipo_id = EXCLUDED.tipo_id,
                               ativo = EXCLUDED.ativo""",
                        (
                            org.get('id', str(uuid.uuid4())),
                            comum_data.get('id', comum_id),
                            org.get('nome', ''),
                            org.get('telefone'),
                            org.get('email'),
                            tipo_id,
                            org.get('ativo', True)
                        )
                    )
                    count += 1
                    
                    # Dias permitidos
                    org_id = org.get('id')
                    dias_permitidos = org.get('dias_permitidos', [])
                    if dias_permitidos and org_id:
                        for dia in dias_permitidos:
                            cur.execute(
                                """INSERT INTO organista_dias_permitidos (organista_id, dia_semana)
                                   VALUES (%s, %s)
                                   ON CONFLICT (organista_id, dia_semana) DO NOTHING""",
                                (org_id, dia)
                            )
    
    conn.commit()
    print_success(f"Organistas migrados: {count}")
    
    return count

def migrate_indisponibilidades(conn, data):
    """Migrar indisponibilidades"""
    print_header("MIGRANDO INDISPONIBILIDADES")
    
    cur = conn.cursor()
    count = 0
    
    indisps = data.get('indisponibilidades', [])
    
    for indisp in indisps:
        indisp_id = indisp.get('id', str(uuid.uuid4()))
        
        cur.execute(
            """INSERT INTO indisponibilidades 
               (id, organista_id, mes, motivo)
               VALUES (%s, %s, %s, %s)
               ON CONFLICT (organista_id, mes) DO UPDATE SET
                   motivo = EXCLUDED.motivo""",
            (
                indisp_id,
                indisp.get('organista_id'),
                indisp.get('mes'),
                indisp.get('motivo')
            )
        )
        count += 1
    
    conn.commit()
    print_success(f"Indisponibilidades migradas: {count}")
    
    return count

def migrate_escalas(conn, data):
    """Migrar escalas"""
    print_header("MIGRANDO ESCALAS")
    
    cur = conn.cursor()
    count = 0
    
    # Escalas estão dentro das comuns na hierarquia
    regionais = data.get('regionais', {})
    
    for regional_id, regional_data in regionais.items():
        for sub_id, sub_data in regional_data.get('sub_regionais', {}).items():
            for comum_id, comum_data in sub_data.get('comuns', {}).items():
                escalas = comum_data.get('escala', [])
                comum_real_id = comum_data.get('id', comum_id)
                
                for esc in escalas:
                    esc_id = esc.get('id', str(uuid.uuid4()))
                    
                    # No JSON original, 'meia_hora' e 'culto' contêm nomes de organistas
                    # Não são horários ou tipos de culto
                    # Vamos deixar horario=NULL e observacao com info do JSON
                    organista_nome = esc.get('meia_hora') or esc.get('culto')
                    observacao = f"Dia: {esc.get('dia_semana', '')} - Org: {organista_nome}" if organista_nome else None
                    
                    cur.execute(
                        """INSERT INTO escala 
                           (id, comum_id, data, horario, organista_id, tipo, observacao)
                           VALUES (%s, %s, %s, %s, %s, %s, %s)
                           ON CONFLICT (id) DO UPDATE SET
                               data = EXCLUDED.data,
                               horario = EXCLUDED.horario,
                               organista_id = EXCLUDED.organista_id,
                               tipo = EXCLUDED.tipo,
                               observacao = EXCLUDED.observacao""",
                        (
                            esc_id,
                            comum_real_id,
                            esc.get('data'),
                            None,  # horario será NULL
                            None,  # organista_id será NULL (nome está em observacao)
                            esc.get('tipo', 'normal'),
                            observacao
                        )
                    )
                    count += 1
    
    conn.commit()
    print_success(f"Escalas migradas: {count}")
    
    return count

def migrate_escalas_rjm(conn, data):
    """Migrar escalas RJM"""
    print_header("MIGRANDO ESCALAS RJM")
    
    cur = conn.cursor()
    count = 0
    
    # Escalas RJM estão dentro das comuns na hierarquia
    regionais = data.get('regionais', {})
    
    for regional_id, regional_data in regionais.items():
        for sub_id, sub_data in regional_data.get('sub_regionais', {}).items():
            for comum_id, comum_data in sub_data.get('comuns', {}).items():
                escalas_rjm = comum_data.get('escala_rjm', [])
                comum_real_id = comum_data.get('id', comum_id)
                
                for esc in escalas_rjm:
                    esc_id = esc.get('id', str(uuid.uuid4()))
                    
                    # Similar às escalas normais, 'culto' pode conter nome do organista
                    organista_nome = esc.get('culto')
                    observacao = f"Dia: {esc.get('dia_semana', '')} - Hora: {esc.get('hora', '')} - Org: {organista_nome}" if organista_nome else None
                    
                    cur.execute(
                        """INSERT INTO escala_rjm 
                           (id, comum_id, data, horario, organista_id, observacao)
                           VALUES (%s, %s, %s, %s, %s, %s)
                           ON CONFLICT (id) DO UPDATE SET
                               data = EXCLUDED.data,
                               horario = EXCLUDED.horario,
                               organista_id = EXCLUDED.organista_id,
                               observacao = EXCLUDED.observacao""",
                        (
                            esc_id,
                            comum_real_id,
                            esc.get('data'),
                            None,  # horario será NULL
                            None,  # organista_id será NULL (nome está em observacao)
                            observacao
                        )
                    )
                    count += 1
    
    conn.commit()
    print_success(f"Escalas RJM migradas: {count}")
    
    return count

def migrate_usuarios(conn, data):
    """Migrar usuários"""
    print_header("MIGRANDO USUÁRIOS")
    
    cur = conn.cursor()
    count = 0
    
    usuarios_dict = data.get('usuarios', {})
    
    # Converter dict para lista de valores
    usuarios = list(usuarios_dict.values()) if isinstance(usuarios_dict, dict) else usuarios_dict
    
    for user in usuarios:
        # Inferir nivel se não existir
        nivel = user.get('nivel')
        if not nivel or nivel == 'sistema':
            tipo = user.get('tipo', '')
            if tipo == 'master':
                nivel = 'master'
            elif tipo == 'admin_regional':
                nivel = 'regional'
            elif tipo == 'encarregado_sub':
                nivel = 'sub_regional'
            elif tipo == 'encarregado_comum':
                nivel = 'comum'
            else:
                nivel = 'comum'
        
        # Usar 'id' como username se username não existir
        username = user.get('username') or user.get('id', str(uuid.uuid4()))
        
        cur.execute(
            """INSERT INTO usuarios 
               (id, username, password_hash, nome, tipo, nivel, contexto_id, ativo)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (id) DO UPDATE SET
                   username = EXCLUDED.username,
                   password_hash = EXCLUDED.password_hash,
                   nome = EXCLUDED.nome,
                   tipo = EXCLUDED.tipo,
                   nivel = EXCLUDED.nivel,
                   contexto_id = EXCLUDED.contexto_id,
                   ativo = EXCLUDED.ativo""",
            (
                user.get('id', str(uuid.uuid4())),
                username,
                user.get('password_hash', user.get('password', '')),
                user.get('nome'),
                user.get('tipo', 'organista'),
                nivel,
                user.get('contexto_id'),
                user.get('ativo', True)
            )
        )
        count += 1
    
    conn.commit()
    print_success(f"Usuários migrados: {count}")
    
    return count

def migrate_logs(conn, data):
    """Migrar logs de auditoria"""
    print_header("MIGRANDO LOGS DE AUDITORIA")
    
    cur = conn.cursor()
    count = 0
    
    logs = data.get('logs_auditoria', [])
    
    for log in logs:
        cur.execute(
            """INSERT INTO logs_auditoria 
               (id, timestamp, tipo, categoria, usuario_id, usuario_nome, usuario_tipo,
                acao, descricao, contexto, dados_antes, dados_depois, 
                ip, user_agent, status, mensagem_erro)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (id) DO NOTHING""",
            (
                log.get('id', str(uuid.uuid4())),
                log.get('timestamp'),
                log.get('tipo'),
                log.get('categoria'),
                log.get('usuario_id'),
                log.get('usuario_nome'),
                log.get('usuario_tipo'),
                log.get('acao'),
                log.get('descricao'),
                json.dumps(log.get('contexto', {})),
                json.dumps(log.get('dados_antes')),
                json.dumps(log.get('dados_depois')),
                log.get('ip'),
                log.get('user_agent'),
                log.get('status'),
                log.get('mensagem_erro')
            )
        )
        count += 1
    
    conn.commit()
    print_success(f"Logs migrados: {count}")
    
    return count

def validate_migration(conn):
    """Validar dados migrados"""
    print_header("VALIDANDO MIGRAÇÃO")
    
    cur = conn.cursor()
    
    checks = [
        ("Regionais", "SELECT COUNT(*) FROM regionais"),
        ("Sub-Regionais", "SELECT COUNT(*) FROM sub_regionais"),
        ("Comuns", "SELECT COUNT(*) FROM comuns"),
        ("Organistas", "SELECT COUNT(*) FROM organistas"),
        ("Indisponibilidades", "SELECT COUNT(*) FROM indisponibilidades"),
        ("Escalas", "SELECT COUNT(*) FROM escala"),
        ("Escalas RJM", "SELECT COUNT(*) FROM escala_rjm"),
        ("Usuários", "SELECT COUNT(*) FROM usuarios"),
        ("Logs", "SELECT COUNT(*) FROM logs_auditoria"),
    ]
    
    print_info("Contagem de registros no PostgreSQL:")
    for name, query in checks:
        cur.execute(query)
        count = cur.fetchone()[0]
        print(f"  {name}: {count}")
    
    return True

def main():
    """Função principal"""
    print_header("MIGRAÇÃO JSON → PostgreSQL v2.0 (Schema Normalizado)")
    
    # Verificar se JSON existe
    if not JSON_PATH.exists():
        print_error(f"Arquivo JSON não encontrado: {JSON_PATH}")
        sys.exit(1)
    
    # Backup do JSON
    backup_path = backup_json()
    if not backup_path:
        sys.exit(1)
    
    # Carregar JSON
    data = load_json()
    
    # Conectar ao PostgreSQL
    conn = connect_db()
    
    try:
        # Migrar dados
        migrate_hierarchy(conn, data)
        migrate_organistas(conn, data)
        migrate_indisponibilidades(conn, data)
        migrate_escalas(conn, data)
        migrate_escalas_rjm(conn, data)
        migrate_usuarios(conn, data)
        migrate_logs(conn, data)
        
        # Validar
        validate_migration(conn)
        
        print_header("MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print_success(f"Backup JSON: {backup_path}")
        print_success("Todos os dados foram migrados para PostgreSQL")
        print_info("Próximo passo: Testar repositories com test_repositories.py")
        
    except Exception as e:
        print_error(f"Erro durante migração: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        sys.exit(1)
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()
