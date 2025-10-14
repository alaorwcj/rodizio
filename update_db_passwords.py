#!/usr/bin/env python3
"""Script para adicionar senhas ao db.json"""

from werkzeug.security import generate_password_hash
import json

# Gerar hash para senha padrão "123456"
password_hash = generate_password_hash('123456')

db = {
    "admin": {
        "nome": "Administrador",
        "password_hash": password_hash
    },
    "organistas": [
        {
            "id": "ieda",
            "nome": "Ieda",
            "tipos": ["Culto", "Meia-hora"],
            "dias_permitidos": ["Domingo", "Terça"],
            "regras_especiais": {
                "domingo_outubro_impares": True,
                "domingo_novembro_pares": True
            },
            "password_hash": password_hash
        },
        {
            "id": "raquel",
            "nome": "Raquel",
            "tipos": ["Culto", "Meia-hora"],
            "dias_permitidos": ["Domingo"],
            "regras_especiais": {
                "apenas_domingos": True
            },
            "password_hash": password_hash
        },
        {
            "id": "yasmin.g",
            "nome": "Yasmin Gonçalves",
            "tipos": ["Culto", "Meia-hora"],
            "dias_permitidos": ["Domingo", "Terça"],
            "regras_especiais": {},
            "password_hash": password_hash
        },
        {
            "id": "milena",
            "nome": "Milena",
            "tipos": ["Culto", "Meia-hora"],
            "dias_permitidos": ["Domingo", "Terça"],
            "regras_especiais": {},
            "password_hash": password_hash
        }
    ],
    "indisponibilidades": [],
    "escala": [],
    "logs": [
        {
            "quando": "2025-10-14T16:00:00.000Z",
            "acao": "init",
            "por": "sistema",
            "payload": {
                "msg": "Sistema atualizado com autenticação - senha padrão: 123456"
            }
        }
    ],
    "config": {
        "bimestre": {
            "inicio": "2025-10-01",
            "fim": "2025-11-30"
        },
        "fechamento_publicacao_dias": 3
    }
}

with open('data/db.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print("✅ db.json atualizado com sucesso!")
print(f"🔑 Senha padrão para todos: 123456")
print(f"👤 Usuários disponíveis:")
print(f"   🔐 admin (Administrador - acesso total)")
print(f"   👤 ieda, raquel, yasmin.g, milena (Organistas)")
