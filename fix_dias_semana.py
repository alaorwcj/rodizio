#!/usr/bin/env python3
"""
Script para corrigir os dias da semana na escala de português para inglês.
Isso garante compatibilidade com a renderização do frontend.
"""
import json

# Mapeamento de português para inglês
DIAS_MAP = {
    'Domingo': 'Sunday',
    'Segunda': 'Monday',
    'Terça': 'Tuesday',
    'Quarta': 'Wednesday',
    'Quinta': 'Thursday',
    'Sexta': 'Friday',
    'Sábado': 'Saturday'
}

def fix_dias_semana():
    """Corrige os dias da semana em todas as escalas"""
    print("🔧 Iniciando correção dos dias da semana...")
    
    # Carregar banco de dados
    try:
        with open('data/db.json', 'r', encoding='utf-8') as f:
            db = json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo data/db.json não encontrado!")
        return
    
    total_corrigido = 0
    
    # Corrigir nova estrutura (regionais)
    if 'regionais' in db:
        for regional_id, regional in db['regionais'].items():
            for sub_regional_id, sub_regional in regional.get('sub_regionais', {}).items():
                for comum_id, comum in sub_regional.get('comuns', {}).items():
                    # Corrigir escala
                    if 'escala' in comum and isinstance(comum['escala'], list):
                        for item in comum['escala']:
                            if 'dia_semana' in item and item['dia_semana'] in DIAS_MAP:
                                old_dia = item['dia_semana']
                                item['dia_semana'] = DIAS_MAP[old_dia]
                                total_corrigido += 1
                                print(f"  ✓ {comum.get('nome', comum_id)}: {old_dia} → {item['dia_semana']}")
                    
                    # Corrigir escala_rjm
                    if 'escala_rjm' in comum and isinstance(comum['escala_rjm'], list):
                        for item in comum['escala_rjm']:
                            if 'dia_semana' in item and item['dia_semana'] in DIAS_MAP:
                                old_dia = item['dia_semana']
                                item['dia_semana'] = DIAS_MAP[old_dia]
                                total_corrigido += 1
                                print(f"  ✓ RJM {comum.get('nome', comum_id)}: {old_dia} → {item['dia_semana']}")
    
    # Corrigir estrutura antiga
    else:
        # Corrigir escala principal
        if 'escala' in db and isinstance(db['escala'], list):
            for item in db['escala']:
                if 'dia_semana' in item and item['dia_semana'] in DIAS_MAP:
                    old_dia = item['dia_semana']
                    item['dia_semana'] = DIAS_MAP[old_dia]
                    total_corrigido += 1
                    print(f"  ✓ Escala: {old_dia} → {item['dia_semana']}")
        
        # Corrigir escala_rjm
        if 'escala_rjm' in db and isinstance(db['escala_rjm'], list):
            for item in db['escala_rjm']:
                if 'dia_semana' in item and item['dia_semana'] in DIAS_MAP:
                    old_dia = item['dia_semana']
                    item['dia_semana'] = DIAS_MAP[old_dia]
                    total_corrigido += 1
                    print(f"  ✓ RJM: {old_dia} → {item['dia_semana']}")
    
    if total_corrigido > 0:
        # Salvar banco corrigido
        with open('data/db.json', 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print(f"\n✅ {total_corrigido} dias corrigidos com sucesso!")
    else:
        print("\n✅ Nenhuma correção necessária - todos os dias já estão em inglês!")

if __name__ == '__main__':
    fix_dias_semana()
