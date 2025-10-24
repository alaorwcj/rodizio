#!/bin/bash
set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Iniciando Sistema de Rodízio de Organistas ===${NC}"

# Criar diretório de dados se não existir
if [ ! -d "/app/data" ]; then
    echo -e "${YELLOW}Criando diretório de dados...${NC}"
    mkdir -p /app/data
fi

# Inicializar db.json se não existir
if [ ! -f "/app/data/db.json" ]; then
    echo -e "${YELLOW}Inicializando banco de dados com autenticação...${NC}"
    python update_db_passwords.py
    echo -e "${GREEN}Banco de dados inicializado com sucesso!${NC}"
    echo -e "${GREEN}🔑 Senha padrão para todos os usuários: 123456${NC}"
fi

# Definir permissões corretas
chmod 644 /app/data/db.json 2>/dev/null || true

echo -e "${GREEN}Sistema pronto! Iniciando servidor...${NC}"

# Iniciar aplicação com Gunicorn
exec gunicorn \
    --bind 0.0.0.0:8090 \
    --workers 2 \
    --threads 4 \
    --worker-class gthread \
    --worker-tmp-dir /dev/shm \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --timeout 120 \
    app:app
