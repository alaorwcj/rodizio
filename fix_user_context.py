#!/usr/bin/env python3
"""
Script para atualizar contexto_id dos usuários para corresponder aos IDs corrigidos das comuns
"""
import json

def fix_user_context_ids():
    """Atualiza contexto_id dos usuários"""
    print("🔧 Iniciando correção dos contexto_id...")
    
    # Carregar banco de dados
    try:
        with open('data/db.json', 'r', encoding='utf-8') as f:
            db = json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo data/db.json não encontrado!")
        return
    
    # Mapeamento de IDs antigos para novos
    id_map = {
        'pedrabranca': 'pedra_branca',
    }
    
    total_corrigido = 0
    
    usuarios = db.get('usuarios', {})
    if isinstance(usuarios, dict):
        for user_id, user in usuarios.items():
            old_context = user.get('contexto_id', '')
            if old_context in id_map:
                new_context = id_map[old_context]
                user['contexto_id'] = new_context
                total_corrigido += 1
                print(f"  ✓ {user_id}: {old_context} -> {new_context}")
    
    if total_corrigido > 0:
        # Salvar banco corrigido
        with open('data/db.json', 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print(f"\n✅ {total_corrigido} contexto_id corrigidos com sucesso!")
    else:
        print("\n✅ Nenhuma correção necessária!")

if __name__ == '__main__':
    fix_user_context_ids()
