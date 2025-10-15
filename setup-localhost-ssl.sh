#!/bin/bash

# Script para gerar certificado SSL auto-assinado para localhost
# Use este para desenvolvimento local

echo "🔒 Gerando Certificado SSL Auto-Assinado para Localhost"
echo "======================================================"
echo ""

# Criar diretórios
echo "📁 Criando diretórios..."
mkdir -p certbot/conf/live/localhost
mkdir -p certbot/www

# Gerar certificado auto-assinado
echo "🔐 Gerando certificado (válido por 365 dias)..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout certbot/conf/live/localhost/privkey.pem \
    -out certbot/conf/live/localhost/fullchain.pem \
    -subj "/C=BR/ST=SP/L=SaoPaulo/O=Rodizio Organistas/OU=Dev/CN=localhost" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Certificado gerado com sucesso!"
else
    echo "❌ Erro ao gerar certificado"
    exit 1
fi

# Parar containers antigos
echo ""
echo "🛑 Parando containers antigos..."
docker-compose down

# Iniciar com HTTPS
echo ""
echo "🚀 Iniciando serviços com HTTPS..."
docker-compose up -d

echo ""
echo "======================================================"
echo "✅ CONFIGURAÇÃO CONCLUÍDA!"
echo "======================================================"
echo ""
echo "🌐 Acesse seu sistema em:"
echo "   https://localhost"
echo ""
echo "⚠️  AVISO: Você verá um aviso de segurança no navegador"
echo "   Isso é normal para certificados auto-assinados."
echo "   Clique em 'Avançado' → 'Continuar para localhost'"
echo ""
echo "📝 O certificado é válido por 365 dias"
echo ""
