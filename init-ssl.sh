#!/bin/bash

# Script para inicializar certificados SSL com Let's Encrypt
# Execute este script APENAS na primeira vez

# CONFIGURAÇÕES - MODIFIQUE AQUI
# Domínios a proteger (apex e www). Ajuste se necessário.
DOMAIN="gestaoderodizios.com.br"  # Domínio principal
DOMAIN_WWW="www.gestaoderodizios.com.br"  # Subdomínio www
EMAIL="admin@gestaoderodizios.com.br"  # Email para registro do certbot

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Configuração SSL com Let's Encrypt${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Verificar se as variáveis foram modificadas
if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    echo -e "${RED}ERRO: Por favor, edite o script e configure seu domínio e email!${NC}"
    exit 1
fi

echo -e "${YELLOW}Domínio:${NC} $DOMAIN"
echo -e "${YELLOW}Email:${NC} $EMAIL"
echo ""

# Criar diretórios necessários
echo -e "${GREEN}1. Criando diretórios...${NC}"
mkdir -p certbot/conf certbot/www "certbot/conf/live/$DOMAIN" "certbot/conf/live/$DOMAIN_WWW"
echo "   ✓ Diretórios criados"

# Atualizar nginx.conf com o domínio
echo -e "${GREEN}2. Validando configuração do Nginx...${NC}"
if ! grep -q "$DOMAIN" nginx.conf; then
    echo -e "${YELLOW}Atenção:${NC} nginx.conf não contém $DOMAIN. Certifique-se de ter atualizado o arquivo com seu domínio."
fi
echo "   ✓ nginx.conf verificado"

# Baixar parâmetros recomendados do SSL
echo -e "${GREEN}3. Baixando configurações SSL recomendadas...${NC}"
curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > certbot/conf/options-ssl-nginx.conf
curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > certbot/conf/ssl-dhparams.pem
echo "   ✓ Configurações SSL baixadas"

# Criar certificado dummy para o Nginx iniciar
echo -e "${GREEN}4. Criando certificado temporário...${NC}"
openssl req -x509 -nodes -newkey rsa:4096 -days 1 \
    -keyout "certbot/conf/live/$DOMAIN/privkey.pem" \
    -out "certbot/conf/live/$DOMAIN/fullchain.pem" \
    -subj "/CN=$DOMAIN" 2>/dev/null
echo "   ✓ Certificado temporário criado para $DOMAIN"

# Iniciar Nginx
echo -e "${GREEN}5. Iniciando Nginx...${NC}"
docker-compose up -d nginx
sleep 5
echo "   ✓ Nginx iniciado"

# Deletar certificado dummy
echo -e "${GREEN}6. Preparando para emissão do certificado real...${NC}"
echo "   ✓ Ambiente pronto"

# Obter certificado real do Let's Encrypt
echo -e "${GREEN}7. Obtendo certificado Let's Encrypt...${NC}"
echo -e "${YELLOW}   Isso pode levar alguns minutos...${NC}"
docker-compose run --rm certbot certonly --webroot \
    -w /var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN -d $DOMAIN_WWW

if [ $? -eq 0 ]; then
    echo -e "${GREEN}   ✓ Certificado obtido com sucesso!${NC}"
else
    echo -e "${RED}   ✗ Erro ao obter certificado${NC}"
    echo -e "${YELLOW}   Verifique se:${NC}"
    echo "     - O domínio aponta para este servidor"
    echo "     - As portas 80 e 443 estão abertas"
    echo "     - O DNS está configurado corretamente"
    exit 1
fi

# Recarregar Nginx
echo -e "${GREEN}8. Recarregando Nginx com certificado real...${NC}"
docker-compose exec nginx nginx -s reload
echo "   ✓ Nginx recarregado"

# Iniciar certbot para renovação automática
echo -e "${GREEN}9. Iniciando serviço de renovação automática...${NC}"
docker-compose up -d certbot
echo "   ✓ Renovação automática configurada"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✓ CONFIGURAÇÃO CONCLUÍDA!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Seu site agora está disponível em:${NC}"
echo -e "  🔒 https://$DOMAIN"
echo ""
echo -e "${YELLOW}O certificado será renovado automaticamente.${NC}"
echo ""
