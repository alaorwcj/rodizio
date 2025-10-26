#!/bin/bash
# Script para Ativar PostgreSQL
# Reverter o rollback e voltar a usar PostgreSQL

set -e

echo "============================================================"
echo "           ATIVAR PostgreSQL"
echo "============================================================"
echo ""

# 1. Parar aplicação
echo "⏸️  Parando aplicação..."
docker-compose stop rodizio-app

# 2. Backup do db.json atual
echo "💾 Backup do db.json..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp data/db.json "data/backups/db_before_postgres_${TIMESTAMP}.json"

# 3. Atualizar .env para PostgreSQL
echo "📝 Configurando .env para PostgreSQL..."
sed -i 's/USE_POSTGRES=false/USE_POSTGRES=true/' .env
sed -i 's/PERSISTENCE=json/PERSISTENCE=postgres/' .env

# 4. Copiar .env para container
echo "📋 Atualizando container..."
docker cp .env rodizio-organistas:/app/.env

# 5. Reiniciar aplicação
echo "🔄 Reiniciando aplicação com PostgreSQL..."
docker-compose start rodizio-app

# 6. Verificar conexão
sleep 3
echo ""
docker exec rodizio-organistas python3 -c "
import psycopg2
try:
    conn = psycopg2.connect('postgresql://rodizio_user:TFQ8fjRBLty6kofZR502VxIL1@172.23.0.1:5433/rodizio')
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM organistas')
    count = cur.fetchone()[0]
    print(f'✅ PostgreSQL ativo! {count} organistas no banco')
    conn.close()
except Exception as e:
    print(f'❌ Erro: {e}')
    exit(1)
"

echo ""
echo "============================================================"
echo "              PostgreSQL ATIVADO!"
echo "============================================================"
echo ""
echo "✅ Aplicação usando PostgreSQL"
echo "💾 Backup db.json: data/backups/db_before_postgres_${TIMESTAMP}.json"
echo ""
