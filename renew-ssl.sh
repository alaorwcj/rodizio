#!/bin/bash

# Script para renovar certificado SSL manualmente
# Execute quando quiser forçar uma renovação

echo "🔄 Renovando certificado SSL..."
docker-compose run --rm certbot renew

echo "♻️ Recarregando Nginx..."
docker-compose exec nginx nginx -s reload

echo "✅ Renovação concluída!"
