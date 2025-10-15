#!/usr/bin/env python3
"""
Script para corrigir campo senha_hash -> password_hash nos usuários
"""
import json
from datetime import datetime

def fix_password_fields():
    # Carregar banco de dados
    with open('data/db.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    # Criar backup antes
    backup_file = f'data/db_backup_fix_password_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print(f"✅ Backup criado: {backup_file}")
    
    # Corrigir usuários
    if 'usuarios' in db:
        usuarios_corrigidos = 0
        for user_id, usuario in db['usuarios'].items():
            # Se tem senha_hash mas não tem password_hash
            if 'senha_hash' in usuario and 'password_hash' not in usuario:
                usuario['password_hash'] = usuario['senha_hash']
                del usuario['senha_hash']
                usuarios_corrigidos += 1
                print(f"  🔧 Corrigido usuário: {user_id}")
            
            # Adicionar campo 'id' se não existir
            if 'id' not in usuario:
                usuario['id'] = user_id
                print(f"  ➕ Adicionado campo 'id' para: {user_id}")
        
        print(f"\n✅ Total de usuários corrigidos: {usuarios_corrigidos}")
    
    # Salvar banco corrigido
    with open('data/db.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Banco de dados atualizado com sucesso!")
    print(f"\n📋 Usuários no sistema:")
    for user_id, usuario in db.get('usuarios', {}).items():
        print(f"  - {user_id} ({usuario['nome']}) - Tipo: {usuario['tipo']}")

if __name__ == '__main__':
    print("🔧 Corrigindo campos de senha nos usuários...\n")
    fix_password_fields()
    print("\n✅ Processo concluído!")
