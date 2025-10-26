#!/bin/bash
# Script de Rollback - Reverter para db.json
# Data: 26/10/2025

set -e

echo "============================================================"
echo "           ROLLBACK: PostgreSQL → JSON"
echo "============================================================"
echo ""

# 1. Parar aplicação
echo "⏸️  Parando aplicação..."
docker-compose stop rodizio-app

# 2. Backup do estado atual
echo "💾 Criando backup do estado PostgreSQL..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker exec rodizio-postgres pg_dump -U rodizio_user rodizio > "data/backups/pg_backup_${TIMESTAMP}.sql"

# 3. Restaurar .env para JSON
echo "📝 Restaurando .env para usar JSON..."
cat > .env << 'EOF'
# Variáveis de Ambiente - ROLLBACK PARA JSON

# Database
DATABASE_URL=postgresql://rodizio_user:TFQ8fjRBLty6kofZR502VxIL1@172.23.0.1:5433/rodizio
DB_HOST=172.23.0.1
DB_PORT=5433
DB_NAME=rodizio
DB_USER=rodizio_user
DB_PASSWORD=TFQ8fjRBLty6kofZR502VxIL1

# Flask
SECRET_KEY=dev-secret-key-change-in-production-$(openssl rand -hex 32)
FLASK_ENV=development

# Migração - ROLLBACK ATIVO
USE_POSTGRES=false  # ⚠️ VOLTOU PARA JSON
PERSISTENCE=json

# Backup
BACKUP_DIR=data/backups
EOF

# 4. Copiar .env para container
echo "📋 Atualizando container..."
docker cp .env rodizio-organistas:/app/.env

# 5. Verificar se db.json existe
if [ ! -f "data/db.json" ]; then
    echo "⚠️  db.json não encontrado! Restaurando do backup..."
    LATEST_BACKUP=$(ls -t data/backups/db_pre_migrate_*.json | head -1)
    if [ -z "$LATEST_BACKUP" ]; then
        echo "❌ ERRO: Nenhum backup encontrado!"
        exit 1
    fi
    cp "$LATEST_BACKUP" data/db.json
    echo "✅ Restaurado de: $LATEST_BACKUP"
fi

# 6. Reiniciar aplicação
echo "🔄 Reiniciando aplicação com JSON..."
docker-compose start rodizio-app

# 7. Verificar status
sleep 3
echo ""
echo "============================================================"
echo "              ROLLBACK CONCLUÍDO!"
echo "============================================================"
echo ""
echo "✅ Aplicação voltou a usar db.json"
echo "📁 db.json: $(wc -l < data/db.json) linhas"
echo "💾 Backup PostgreSQL: data/backups/pg_backup_${TIMESTAMP}.sql"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   - Verifique se a aplicação está funcionando"
echo "   - PostgreSQL continua com os dados (não foram deletados)"
echo "   - Para reverter o rollback, execute: scripts/activate_postgres.sh"
echo ""
