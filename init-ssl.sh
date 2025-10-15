#!/bin/bash

# Script para inicializar certificados SSL com Let's Encrypt
# Execute este script APENAS na primeira vez

# CONFIGURAÇÕES - MODIFIQUE AQUI
DOMAIN="SEU_DOMINIO.COM"  # Substitua pelo seu domínio
EMAIL="seu.email@exemplo.com"  # Substitua pelo seu email

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
if [ "$DOMAIN" = "SEU_DOMINIO.COM" ] || [ "$EMAIL" = "seu.email@exemplo.com" ]; then
    echo -e "${RED}ERRO: Por favor, edite o script e configure seu domínio e email!${NC}"
    exit 1
fi

echo -e "${YELLOW}Domínio:${NC} $DOMAIN"
echo -e "${YELLOW}Email:${NC} $EMAIL"
echo ""

# Criar diretórios necessários
echo -e "${GREEN}1. Criando diretórios...${NC}"
mkdir -p certbot/conf certbot/www
echo "   ✓ Diretórios criados"

# Atualizar nginx.conf com o domínio
echo -e "${GREEN}2. Atualizando configuração do Nginx...${NC}"
sed -i "s/SEU_DOMINIO.COM/$DOMAIN/g" nginx.conf
echo "   ✓ nginx.conf atualizado"

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
    -subj "/CN=localhost" 2>/dev/null
mkdir -p "certbot/conf/live/$DOMAIN"
echo "   ✓ Certificado temporário criado"

# Iniciar Nginx
echo -e "${GREEN}5. Iniciando Nginx...${NC}"
docker-compose up -d nginx
sleep 5
echo "   ✓ Nginx iniciado"

# Deletar certificado dummy
echo -e "${GREEN}6. Removendo certificado temporário...${NC}"
docker-compose exec nginx rm -rf /etc/letsencrypt/live/$DOMAIN
echo "   ✓ Certificado temporário removido"

# Obter certificado real do Let's Encrypt
echo -e "${GREEN}7. Obtendo certificado Let's Encrypt...${NC}"
echo -e "${YELLOW}   Isso pode levar alguns minutos...${NC}"
docker-compose run --rm certbot certonly --webroot \
    -w /var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN

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
