# 🔒 Configuração HTTPS com Let's Encrypt

Este guia explica como configurar HTTPS no seu sistema de Rodízio de Organistas.

## 📋 Pré-requisitos

1. **Domínio próprio** apontando para o servidor
2. **DNS configurado** (A record apontando para o IP do servidor)
3. **Portas abertas** no firewall:
   - Porta 80 (HTTP)
   - Porta 443 (HTTPS)
4. **Docker e Docker Compose** instalados

## 🚀 Instalação (Primeira vez)

### Passo 1: Editar o script de inicialização

Edite o arquivo `init-ssl.sh` e configure:

```bash
DOMAIN="seudominio.com"  # Seu domínio real
EMAIL="seuemail@gmail.com"  # Seu email real
```

### Passo 2: Dar permissão de execução aos scripts

```bash
chmod +x init-ssl.sh
chmod +x renew-ssl.sh
```

### Passo 3: Executar a configuração inicial

```bash
./init-ssl.sh
```

Este script irá:
- ✅ Criar os diretórios necessários
- ✅ Atualizar a configuração do Nginx
- ✅ Baixar configurações SSL recomendadas
- ✅ Obter certificado do Let's Encrypt
- ✅ Configurar renovação automática

### Passo 4: Verificar se está funcionando

Acesse: `https://seudominio.com`

## 🔄 Renovação Automática

O certificado será **renovado automaticamente** a cada 12 horas.

### Renovação Manual

Se quiser forçar uma renovação:

```bash
./renew-ssl.sh
```

## 🛠️ Comandos Úteis

### Ver logs do Nginx
```bash
docker-compose logs -f nginx
```

### Ver logs do Certbot
```bash
docker-compose logs -f certbot
```

### Reiniciar serviços
```bash
docker-compose restart
```

### Parar serviços
```bash
docker-compose down
```

### Iniciar serviços
```bash
docker-compose up -d
```

## 🔍 Verificar Certificado

Verificar validade do certificado:
```bash
echo | openssl s_client -servername seudominio.com -connect seudominio.com:443 2>/dev/null | openssl x509 -noout -dates
```

## 📁 Estrutura de Arquivos

```
rodizio/
├── docker-compose.yml       # Configuração Docker com Nginx e Certbot
├── nginx.conf               # Configuração do Nginx
├── init-ssl.sh              # Script de inicialização SSL (executar 1x)
├── renew-ssl.sh             # Script de renovação manual
├── certbot/
│   ├── conf/                # Certificados SSL
│   └── www/                 # Challenge do Let's Encrypt
```

## ⚠️ Troubleshooting

### Erro: "Challenge failed"

**Causa:** DNS não está apontando corretamente ou portas bloqueadas

**Solução:**
1. Verifique se o domínio aponta para o IP correto:
   ```bash
   dig seudominio.com
   ```
2. Teste se a porta 80 está acessível:
   ```bash
   curl http://seudominio.com/.well-known/acme-challenge/test
   ```

### Erro: "Port 80/443 already in use"

**Causa:** Outra aplicação usando as portas

**Solução:**
```bash
# Parar outros serviços
sudo systemctl stop apache2
sudo systemctl stop nginx
```

### Certificado não renova automaticamente

**Solução:**
```bash
# Verificar logs
docker-compose logs certbot

# Forçar renovação
./renew-ssl.sh
```

## 🔐 Segurança

O sistema está configurado com:
- ✅ TLS 1.2 e 1.3
- ✅ Ciphers fortes
- ✅ HSTS (Strict Transport Security)
- ✅ Headers de segurança
- ✅ Redirecionamento HTTP → HTTPS

## 📞 Suporte

Se tiver problemas:
1. Verifique os logs: `docker-compose logs`
2. Teste a conectividade: `curl -I https://seudominio.com`
3. Verifique o DNS: `nslookup seudominio.com`

## 📚 Referências

- [Let's Encrypt](https://letsencrypt.org/)
- [Certbot](https://certbot.eff.org/)
- [Nginx](https://nginx.org/)
