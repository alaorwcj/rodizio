# Multi-stage build para otimizar tamanho da imagem
FROM python:3.11-slim as builder

# Variáveis de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Diretório de trabalho temporário
WORKDIR /build

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt

# Imagem final
FROM python:3.11-slim

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production

# Criar usuário não-root para segurança
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data /app/templates /app/static && \
    chown -R appuser:appuser /app

# Diretório de trabalho
WORKDIR /app

# Copiar dependências do builder
COPY --from=builder /root/.local /home/appuser/.local

# Copiar código da aplicação
COPY --chown=appuser:appuser app.py .
COPY --chown=appuser:appuser update_db_passwords.py .
COPY --chown=appuser:appuser templates/ templates/
COPY --chown=appuser:appuser static/ static/
COPY --chown=appuser:appuser scripts/ scripts/
COPY --chown=appuser:appuser entrypoint.sh .
COPY --chown=appuser:appuser audit_repository.py .
# Tornar entrypoint executável
RUN chmod +x entrypoint.sh

# Mudar para usuário não-root
USER appuser

# Adicionar .local/bin ao PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Expor porta
EXPOSE 8080

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health').read()" || exit 1

# Entrypoint
ENTRYPOINT ["./entrypoint.sh"]
