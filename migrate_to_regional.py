#!/usr/bin/env python3
"""
Script de migração: Estrutura plana -> Estrutura regionalizada

Este script converte o db.json atual para a nova estrutura hierárquica:
Regional -> Sub-Regional -> Comum

Uso: python migrate_to_regional.py
"""

import json
import os
import shutil
from datetime import datetime

DATA_PATH = "data/db.json"
BACKUP_PATH = f"data/db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

def load_old_db():
    """Carrega estrutura antiga"""
    if not os.path.exists(DATA_PATH):
        print("❌ Arquivo db.json não encontrado!")
        return None
    
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_new_db(db):
    """Salva nova estrutura"""
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def backup_old_db():
    """Cria backup do db.json antigo"""
    if os.path.exists(DATA_PATH):
        shutil.copy2(DATA_PATH, BACKUP_PATH)
        print(f"✅ Backup criado: {BACKUP_PATH}")
        return True
    return False

def migrate():
    """Executa a migração"""
    print("\n" + "="*60)
    print("🔄 MIGRAÇÃO PARA ESTRUTURA REGIONALIZADA")
    print("="*60 + "\n")
    
    # 1. Carregar dados antigos
    print("1. Carregando dados antigos...")
    old_db = load_old_db()
    if not old_db:
        return False
    
    print(f"   ✅ {len(old_db.get('organistas', []))} organistas encontradas")
    print(f"   ✅ {len(old_db.get('indisponibilidades', []))} indisponibilidades")
    print(f"   ✅ {len(old_db.get('escala', []))} itens na escala")
    print(f"   ✅ {len(old_db.get('escala_rjm', []))} itens na escala RJM")
    
    # 2. Criar backup
    print("\n2. Criando backup...")
    if not backup_old_db():
        print("   ⚠️  Backup não criado (db.json não existe)")
    
    # 3. Criar nova estrutura
    print("\n3. Criando nova estrutura hierárquica...")
    
    new_db = {
        "sistema": {
            "nome": "Rodízio de Organistas CCB",
            "versao": "2.0",
            "data_migracao": datetime.now().isoformat()
        },
        "regionais": {
            "gru": {
                "id": "gru",
                "nome": "Regional GRU",
                "ativo": True,
                "sub_regionais": {
                    "santa_isabel": {
                        "id": "santa_isabel",
                        "nome": "Sub-Regional Santa Isabel",
                        "ativo": True,
                        "comuns": {
                            "vila_paula": {
                                "id": "vila_paula",
                                "nome": "Comum Vila Paula",
                                "endereco": "",
                                "cidade": "Santa Isabel",
                                "ativo": True,
                                "organistas": old_db.get("organistas", []),
                                "indisponibilidades": old_db.get("indisponibilidades", []),
                                "escala": old_db.get("escala", []),
                                "escala_rjm": old_db.get("escala_rjm", []),
                                "config": old_db.get("config", {
                                    "periodo": {
                                        "inicio": "2025-10-01",
                                        "fim": "2025-11-30"
                                    },
                                    "fechamento_publicacao_dias": 3,
                                    "horarios": {
                                        "domingo": {
                                            "meia_hora": "18:00",
                                            "culto": "18:30"
                                        },
                                        "terca": {
                                            "meia_hora": "19:00",
                                            "culto": "19:30"
                                        }
                                    },
                                    "rjm": {
                                        "ativo": True,
                                        "horario": "10:00",
                                        "dia": "Domingo",
                                        "duracao": "1h30"
                                    }
                                })
                            }
                        }
                    }
                }
            }
        },
        "usuarios": {
            "admin_master": {
                "id": "admin_master",
                "nome": old_db.get("admin", {}).get("nome", "Administrador Master"),
                "tipo": "master",
                "nivel": "sistema",
                "password_hash": old_db.get("admin", {}).get("password_hash", ""),
                "ativo": True,
                "permissoes": [
                    "gerenciar_regionais",
                    "gerenciar_sub_regionais",
                    "gerenciar_comuns",
                    "visualizar_todos_relatorios"
                ]
            }
        },
        "logs": old_db.get("logs", [])
    }
    
    # Adicionar log da migração
    new_db["logs"].append({
        "quando": datetime.now().isoformat(),
        "acao": "migracao_para_regional",
        "por": "sistema",
        "detalhes": {
            "versao_anterior": "1.0",
            "versao_nova": "2.0",
            "organistas_migradas": len(old_db.get("organistas", [])),
            "escala_migrada": len(old_db.get("escala", []))
        }
    })
    
    print("   ✅ Estrutura hierárquica criada:")
    print("      └─ Regional GRU")
    print("         └─ Sub-Regional Santa Isabel")
    print("            └─ Comum Vila Paula")
    
    # 4. Salvar nova estrutura
    print("\n4. Salvando nova estrutura...")
    save_new_db(new_db)
    print("   ✅ Arquivo db.json atualizado")
    
    # 5. Resumo
    print("\n" + "="*60)
    print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*60)
    print(f"\n📊 Dados migrados:")
    print(f"   • Regional: GRU")
    print(f"   • Sub-Regional: Santa Isabel")
    print(f"   • Comum: Vila Paula")
    print(f"   • Organistas: {len(old_db.get('organistas', []))}")
    print(f"   • Indisponibilidades: {len(old_db.get('indisponibilidades', []))}")
    print(f"   • Itens na escala: {len(old_db.get('escala', []))}")
    print(f"   • Itens RJM: {len(old_db.get('escala_rjm', []))}")
    print(f"\n💾 Backup salvo em: {BACKUP_PATH}")
    print(f"\n⚠️  IMPORTANTE:")
    print(f"   1. Verifique o arquivo db.json")
    print(f"   2. Reconstrua o container: docker-compose down && docker-compose build && docker-compose up -d")
    print(f"   3. Faça login com: admin_master (mesma senha do admin antigo)")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = migrate()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERRO na migração: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
