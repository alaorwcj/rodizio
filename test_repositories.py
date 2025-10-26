#!/usr/bin/env python3
"""
Script de teste para validar repositories
Testa conexão e operações básicas com PostgreSQL
"""

import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from repositories import (
    OrganistaRepository,
    EscalaRepository,
    IndisponibilidadeRepository,
    ComumRepository,
    UsuarioRepository,
    TrocaRepository
)


def test_database_connection():
    """Testar conexão básica com PostgreSQL"""
    print("🔍 Testando conexão com PostgreSQL...")
    try:
        from database import get_db_session
        from sqlalchemy import text
        
        with get_db_session() as session:
            result = session.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Conexão OK! PostgreSQL: {version[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False


def test_comum_repository():
    """Testar ComumRepository"""
    print("\n🔍 Testando ComumRepository...")
    try:
        repo = ComumRepository()
        
        # Listar regionais
        regionais = repo.get_all_regionais()
        print(f"  ✅ Regionais encontradas: {len(regionais)}")
        
        if regionais:
            regional = regionais[0]
            print(f"     Exemplo: {regional['nome']}")
            
            # Listar sub-regionais
            sub_regionais = repo.get_sub_regionais_by_regional(regional['id'])
            print(f"  ✅ Sub-regionais: {len(sub_regionais)}")
            
            if sub_regionais:
                # Listar comuns
                comuns = repo.get_comuns_by_sub_regional(sub_regionais[0]['id'])
                print(f"  ✅ Comuns: {len(comuns)}")
        
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_organista_repository():
    """Testar OrganistaRepository"""
    print("\n🔍 Testando OrganistaRepository...")
    try:
        repo_comum = ComumRepository()
        repo = OrganistaRepository()
        
        # Buscar uma comum para testar
        regionais = repo_comum.get_all_regionais()
        if not regionais:
            print("  ⚠️  Sem regionais no banco")
            return True
        
        comuns = repo_comum.get_all_comuns_by_regional(regionais[0]['id'])
        if not comuns:
            print("  ⚠️  Sem comuns no banco")
            return True
        
        comum_id = comuns[0]['id']
        
        # Listar organistas
        organistas = repo.get_by_comum(comum_id)
        print(f"  ✅ Organistas na comum '{comuns[0]['nome']}': {len(organistas)}")
        
        if organistas:
            org = organistas[0]
            print(f"     Exemplo: {org['nome']} - {org.get('tipo_nome', 'N/A')}")
            
            # Buscar por ID
            org_completo = repo.get_by_id(org['id'])
            print(f"  ✅ Busca por ID funcionou")
            
            # Listar tipos
            tipos = repo.get_tipos()
            print(f"  ✅ Tipos de organistas: {len(tipos)}")
        
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_escala_repository():
    """Testar EscalaRepository"""
    print("\n🔍 Testando EscalaRepository...")
    try:
        repo_comum = ComumRepository()
        repo = EscalaRepository()
        
        # Buscar uma comum
        regionais = repo_comum.get_all_regionais()
        if not regionais:
            print("  ⚠️  Sem regionais no banco")
            return True
        
        comuns = repo_comum.get_all_comuns_by_regional(regionais[0]['id'])
        if not comuns:
            print("  ⚠️  Sem comuns no banco")
            return True
        
        comum_id = comuns[0]['id']
        
        # Buscar escalas do mês atual
        from datetime import date
        mes_atual = date.today().strftime('%Y-%m')
        
        escalas = repo.get_by_comum_mes(comum_id, mes_atual)
        print(f"  ✅ Escalas em {mes_atual}: {len(escalas)}")
        
        if escalas:
            esc = escalas[0]
            print(f"     Exemplo: {esc['data']} {esc.get('horario', '')} - {esc.get('organista_nome', 'Sem organista')}")
        
        # Buscar RJM
        rjms = repo.get_rjm_by_comum_mes(comum_id, mes_atual)
        print(f"  ✅ RJMs em {mes_atual}: {len(rjms)}")
        
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_indisponibilidade_repository():
    """Testar IndisponibilidadeRepository"""
    print("\n🔍 Testando IndisponibilidadeRepository...")
    try:
        repo_comum = ComumRepository()
        repo = IndisponibilidadeRepository()
        
        # Buscar uma comum
        regionais = repo_comum.get_all_regionais()
        if not regionais:
            print("  ⚠️  Sem regionais no banco")
            return True
        
        comuns = repo_comum.get_all_comuns_by_regional(regionais[0]['id'])
        if not comuns:
            print("  ⚠️  Sem comuns no banco")
            return True
        
        comum_id = comuns[0]['id']
        
        # Buscar indisponibilidades do mês atual
        from datetime import date
        mes_atual = date.today().strftime('%Y-%m')
        
        indisps = repo.get_by_comum_mes(comum_id, mes_atual)
        print(f"  ✅ Indisponibilidades em {mes_atual}: {len(indisps)}")
        
        if indisps:
            ind = indisps[0]
            print(f"     Exemplo: {ind.get('organista_nome', 'N/A')} - {ind.get('motivo', 'Sem motivo')}")
        
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_usuario_repository():
    """Testar UsuarioRepository"""
    print("\n🔍 Testando UsuarioRepository...")
    try:
        repo = UsuarioRepository()
        
        # Listar todos usuários
        usuarios = repo.get_all()
        print(f"  ✅ Usuários cadastrados: {len(usuarios)}")
        
        if usuarios:
            user = usuarios[0]
            print(f"     Exemplo: {user['nome']} ({user['username']}) - Nível: {user['nivel']}")
            
            # Buscar por username
            user_by_username = repo.get_by_username(user['username'])
            print(f"  ✅ Busca por username funcionou")
        
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_troca_repository():
    """Testar TrocaRepository"""
    print("\n🔍 Testando TrocaRepository...")
    try:
        repo_comum = ComumRepository()
        repo = TrocaRepository()
        
        # Buscar uma comum
        regionais = repo_comum.get_all_regionais()
        if not regionais:
            print("  ⚠️  Sem regionais no banco")
            return True
        
        comuns = repo_comum.get_all_comuns_by_regional(regionais[0]['id'])
        if not comuns:
            print("  ⚠️  Sem comuns no banco")
            return True
        
        comum_id = comuns[0]['id']
        
        # Buscar trocas pendentes
        trocas = repo.get_pendentes_by_comum(comum_id)
        print(f"  ✅ Trocas pendentes: {len(trocas)}")
        
        # Estatísticas
        stats = repo.get_estatisticas(comum_id)
        print(f"  ✅ Estatísticas: {stats}")
        
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executar todos os testes"""
    print("=" * 60)
    print("  TESTE DE REPOSITORIES - PostgreSQL")
    print("=" * 60)
    
    tests = [
        ("Conexão PostgreSQL", test_database_connection),
        ("ComumRepository", test_comum_repository),
        ("OrganistaRepository", test_organista_repository),
        ("EscalaRepository", test_escala_repository),
        ("IndisponibilidadeRepository", test_indisponibilidade_repository),
        ("UsuarioRepository", test_usuario_repository),
        ("TrocaRepository", test_troca_repository),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ Erro fatal em {name}: {e}")
            results.append((name, False))
    
    # Sumário
    print("\n" + "=" * 60)
    print("  SUMÁRIO DOS TESTES")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{status} - {name}")
    
    print(f"\nResultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 Todos os repositories estão funcionando!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam")
        return 1


if __name__ == "__main__":
    sys.exit(main())
