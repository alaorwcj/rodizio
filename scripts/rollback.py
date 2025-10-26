#!/usr/bin/env python3
"""
Script de ROLLBACK - Reverter para db.json
Versão: 1.0
Data: 26/10/2025

Este script reverte a migração e restaura o sistema para usar JSON.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import psycopg2
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
BACKUP_DIR = DATA_DIR / 'backups'
ENV_FILE = BASE_DIR / '.env'

class Colors:
    HEADER = '\033[95m'
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

def list_backups():
    """Listar backups disponíveis"""
    if not BACKUP_DIR.exists():
        return []
    
    backups = sorted(
        [f for f in BACKUP_DIR.glob('db_*.json')],
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    return backups

def select_backup():
    """Permitir usuário selecionar backup para restaurar"""
    backups = list_backups()
    
    if not backups:
        print_error("Nenhum backup encontrado!")
        return None
    
    print_header("BACKUPS DISPONÍVEIS")
    print("\nSelecione o backup para restaurar:\n")
    
    for i, backup in enumerate(backups[:10], 1):  # Mostrar últimos 10
        size = backup.stat().st_size / 1024  # KB
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        print(f"  {i}. {backup.name}")
        print(f"     Tamanho: {size:.1f} KB")
        print(f"     Data: {mtime.strftime('%d/%m/%Y %H:%M:%S')}")
        print()
    
    print("  0. Cancelar\n")
    
    try:
        choice = int(input("Digite o número do backup: "))
        if choice == 0:
            return None
        if 1 <= choice <= len(backups[:10]):
            return backups[choice - 1]
        else:
            print_error("Opção inválida!")
            return None
    except ValueError:
        print_error("Opção inválida!")
        return None

def restore_backup(backup_path):
    """Restaurar backup do JSON"""
    print_header("RESTAURANDO BACKUP")
    
    # Fazer backup do db.json atual antes de sobrescrever
    current_json = DATA_DIR / 'db.json'
    if current_json.exists():
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safety_backup = BACKUP_DIR / f'db_before_rollback_{timestamp}.json'
        import shutil
        shutil.copy2(current_json, safety_backup)
        print_success(f"Backup de segurança criado: {safety_backup.name}")
    
    # Restaurar backup selecionado
    import shutil
    shutil.copy2(backup_path, current_json)
    print_success(f"Restaurado: {backup_path.name} → db.json")
    
    return True

def update_env_file():
    """Atualizar .env para desabilitar PostgreSQL"""
    print_header("ATUALIZANDO CONFIGURAÇÃO")
    
    if not ENV_FILE.exists():
        print_warning(".env não encontrado - criar manualmente")
        return False
    
    # Ler .env atual
    with open(ENV_FILE, 'r') as f:
        lines = f.readlines()
    
    # Atualizar flags
    new_lines = []
    for line in lines:
        if line.startswith('USE_POSTGRES='):
            new_lines.append('USE_POSTGRES=false\n')
            print_success("USE_POSTGRES=false")
        elif line.startswith('PERSISTENCE='):
            new_lines.append('PERSISTENCE=json\n')
            print_success("PERSISTENCE=json")
        else:
            new_lines.append(line)
    
    # Escrever de volta
    with open(ENV_FILE, 'w') as f:
        f.writelines(new_lines)
    
    print_success("Arquivo .env atualizado")
    return True

def clear_postgres_data():
    """Opcionalmente limpar dados do PostgreSQL"""
    print_header("LIMPEZA DO POSTGRESQL")
    
    response = input("\nDeseja LIMPAR todos os dados do PostgreSQL? (s/N): ").lower()
    
    if response != 's':
        print_warning("PostgreSQL mantido com dados atuais")
        return False
    
    print_warning("\n⚠️  ATENÇÃO: Isso apagará TODOS os dados do PostgreSQL!")
    confirm = input("Digite 'CONFIRMAR' para prosseguir: ")
    
    if confirm != 'CONFIRMAR':
        print_warning("Operação cancelada")
        return False
    
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Obter todas as tabelas
        cur.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        tables = [row[0] for row in cur.fetchall()]
        
        # Truncar todas as tabelas
        for table in tables:
            cur.execute(f"TRUNCATE TABLE {table} CASCADE")
            print_success(f"Tabela limpa: {table}")
        
        conn.commit()
        conn.close()
        
        print_success("PostgreSQL limpo com sucesso")
        return True
        
    except Exception as e:
        print_error(f"Erro ao limpar PostgreSQL: {e}")
        return False

def restart_app():
    """Instruções para reiniciar aplicação"""
    print_header("PRÓXIMOS PASSOS")
    
    print("\n✅ Rollback concluído com sucesso!\n")
    print("Para aplicar as mudanças:\n")
    print("  1. Reiniciar aplicação:")
    print("     docker-compose restart rodizio-app")
    print("\n  2. Verificar logs:")
    print("     docker-compose logs -f rodizio-app")
    print("\n  3. Testar aplicação:")
    print("     Acessar: https://seu-dominio.com")
    print("\n  4. Se tudo OK, pode deletar dados do PostgreSQL:")
    print("     python3 scripts/rollback.py --clean-postgres")
    print()

def main():
    """Função principal de rollback"""
    print_header("ROLLBACK: POSTGRESQL → JSON")
    
    print_warning("\n⚠️  ATENÇÃO: Este script reverte para db.json")
    print_warning("⚠️  Certifique-se de ter backups antes de prosseguir!\n")
    
    response = input("Deseja continuar? (s/N): ").lower()
    if response != 's':
        print("Operação cancelada.")
        return
    
    # 1. Selecionar backup
    backup_path = select_backup()
    if not backup_path:
        print_error("Rollback cancelado.")
        return
    
    # 2. Restaurar backup
    if not restore_backup(backup_path):
        print_error("Falha ao restaurar backup!")
        return
    
    # 3. Atualizar .env
    update_env_file()
    
    # 4. Opcionalmente limpar PostgreSQL
    if '--clean-postgres' in sys.argv:
        clear_postgres_data()
    
    # 5. Instruções finais
    restart_app()

if __name__ == '__main__':
    main()
