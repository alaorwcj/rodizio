#!/usr/bin/env python3
"""
Script para corrigir IDs de comuns que estão como null
"""
import json
import re

def slugify(text):
    """Converte texto para formato de ID (minúsculas, sem espaços, sem acentos)"""
    text = text.lower()
    text = re.sub(r'[àáâãäå]', 'a', text)
    text = re.sub(r'[èéêë]', 'e', text)
    text = re.sub(r'[ìíîï]', 'i', text)
    text = re.sub(r'[òóôõö]', 'o', text)
    text = re.sub(r'[ùúûü]', 'u', text)
    text = re.sub(r'[ç]', 'c', text)
    text = re.sub(r'[^a-z0-9]+', '_', text)
    text = re.sub(r'_+', '_', text)
    text = text.strip('_')
    return text

def fix_comum_ids():
    """Corrige IDs de comuns que estão como null"""
    print("🔧 Iniciando correção dos IDs de comuns...")
    
    # Carregar banco de dados
    try:
        with open('data/db.json', 'r', encoding='utf-8') as f:
            db = json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo data/db.json não encontrado!")
        return
    
    total_corrigido = 0
    
    # Corrigir estrutura (regionais)
    if 'regionais' in db:
        for regional_id, regional in db['regionais'].items():
            for sub_regional_id, sub_regional in regional.get('sub_regionais', {}).items():
                for comum_id, comum in sub_regional.get('comuns', {}).items():
                    # Verificar se o ID interno está null
                    if comum.get('id') is None or comum.get('id') == '':
                        nome = comum.get('nome', '')
                        if nome:
                            novo_id = slugify(nome)
                            comum['id'] = novo_id
                            total_corrigido += 1
                            print(f"  ✓ Corrigido: '{nome}' -> ID: '{novo_id}' (chave: {comum_id})")
                        else:
                            print(f"  ⚠️ Comum sem nome encontrado na chave {comum_id}")
    
    if total_corrigido > 0:
        # Salvar banco corrigido
        with open('data/db.json', 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print(f"\n✅ {total_corrigido} IDs de comuns corrigidos com sucesso!")
    else:
        print("\n✅ Nenhuma correção necessária - todos os IDs já estão configurados!")

if __name__ == '__main__':
    fix_comum_ids()
