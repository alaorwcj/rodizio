# 🔄 Plano de Rollback - PostgreSQL → JSON

**Data:** 26 de outubro de 2025  
**Status Migração:** ✅ Concluída com sucesso

---

## 📊 Estado da Migração

### Dados Migrados
- ✅ **2 Regionais** (GRU, Outra)
- ✅ **2 Sub-Regionais**
- ✅ **7 Comuns**
- ✅ **24 Organistas únicos** (26 registros com duplicatas)
- ✅ **53 Tipos de organistas**
- ✅ **76 Dias permitidos**
- ✅ **6 Indisponibilidades**
- ✅ **303 Escalas regulares**
- ✅ **88 Escalas RJM**
- ✅ **9 Usuários**
- ✅ **10 Logs de auditoria**

### Backups Disponíveis
```
/app/data/backups/db_pre_migrate_20251026_143508.json  ← Último backup antes da migração
/app/data/db.json                                        ← Original (manter!)
```

### Configuração Atual
```bash
DATABASE_URL=postgresql://rodizio_user:***@172.23.0.1:5433/rodizio
USE_POSTGRES=true   # ✅ ATIVO
PERSISTENCE=postgres
```

---

## 🚨 Quando Fazer Rollback?

Execute rollback SE:
- ❌ Dados corrompidos ou inconsistentes
- ❌ Performance degradada significativamente
- ❌ Erros críticos não resolvíveis
- ❌ Funcionalidades quebradas

**NÃO execute rollback para:**
- ⚠️ Pequenos ajustes ou bugs menores (podem ser corrigidos)
- ⚠️ Queries que precisam otimização (adicionar índices)
- ⚠️ Testes ou validação (use ambiente de dev)

---

## 📋 Opções de Rollback

### Opção 1: Rollback Rápido (Script Automático) ⚡

**Quando usar:** Rollback urgente, problemas críticos

```bash
cd /root/app/rodizio
./scripts/rollback_to_json.sh
```

**O que faz:**
1. ⏸️ Para aplicação
2. 💾 Backup do PostgreSQL atual
3. 📝 Restaura .env para JSON
4. 📁 Verifica/restaura db.json
5. 🔄 Reinicia aplicação com JSON

**Tempo estimado:** ~30 segundos

---

### Opção 2: Rollback Manual (Passo a Passo) 🔧

**Quando usar:** Rollback controlado, inspeção detalhada

#### Passo 1: Parar Aplicação
```bash
docker-compose stop rodizio-app
```

#### Passo 2: Backup do Estado PostgreSQL
```bash
# Backup completo SQL
docker exec -it rodizio-postgres pg_dump -U rodizio_user rodizio > \
  data/backups/pg_backup_$(date +%Y%m%d_%H%M%S).sql

# OU backup via Python
docker exec rodizio-organistas python3 scripts/export_postgres_to_json.py
```

#### Passo 3: Verificar db.json
```bash
# Verificar se existe
ls -lh data/db.json

# Se não existir, restaurar do backup
cp data/backups/db_pre_migrate_20251026_143508.json data/db.json
```

#### Passo 4: Atualizar .env
```bash
# Editar .env
nano .env

# Alterar:
USE_POSTGRES=false  # ← de true para false
PERSISTENCE=json    # ← de postgres para json
```

#### Passo 5: Copiar .env para Container
```bash
docker cp .env rodizio-organistas:/app/.env
```

#### Passo 6: Reiniciar Aplicação
```bash
docker-compose start rodizio-app

# Verificar logs
docker-compose logs -f rodizio-app
```

#### Passo 7: Validar Funcionamento
```bash
# Testar login
curl -X POST http://localhost/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin_master","password":"senha"}'

# Verificar carregamento de dados
docker exec rodizio-organistas python3 -c "
import json
db = json.load(open('data/db.json'))
print(f'✅ JSON carregado: {len(db[\"regionais\"])} regionais')
"
```

**Tempo estimado:** ~5 minutos

---

### Opção 3: Rollback Completo com Reimportação 🔄

**Quando usar:** PostgreSQL totalmente corrompido, recomeçar do zero

```bash
# 1. Restaurar db.json do backup mais recente
cp data/backups/db_pre_migrate_20251026_143508.json data/db.json

# 2. Limpar PostgreSQL (CUIDADO!)
psql -U rodizio_user -h localhost -p 5433 -d rodizio << EOF
TRUNCATE TABLE organistas CASCADE;
TRUNCATE TABLE regionais CASCADE;
TRUNCATE TABLE usuarios CASCADE;
TRUNCATE TABLE logs_auditoria CASCADE;
EOF

# 3. Seguir Opção 2 (rollback manual)
```

---

## 🔙 Reverter Rollback (Ativar PostgreSQL Novamente)

Se fez rollback mas quer voltar ao PostgreSQL:

```bash
cd /root/app/rodizio
./scripts/activate_postgres.sh
```

OU manualmente:
```bash
# 1. Editar .env
USE_POSTGRES=true
PERSISTENCE=postgres

# 2. Copiar para container
docker cp .env rodizio-organistas:/app/.env

# 3. Reiniciar
docker-compose restart rodizio-app
```

---

## 📝 Checklist de Rollback

### Antes do Rollback
- [ ] Documentar motivo do rollback
- [ ] Backup do estado PostgreSQL atual
- [ ] Verificar se db.json existe e está íntegro
- [ ] Notificar usuários (se aplicável)
- [ ] Preparar janela de manutenção

### Durante o Rollback
- [ ] Executar script ou passos manuais
- [ ] Verificar logs de erro
- [ ] Validar carregamento do JSON
- [ ] Testar funcionalidades críticas

### Após o Rollback
- [ ] Confirmar aplicação funcionando
- [ ] Verificar integridade dos dados
- [ ] Monitorar por 24h
- [ ] Documentar lições aprendidas
- [ ] Decidir próximos passos

---

## 🛡️ Prevenção de Perda de Dados

### Backups Automáticos
Os seguintes backups são criados automaticamente:

1. **db.json** (sempre mantido)
   - `data/db.json` ← Original
   - `data/backups/db_pre_migrate_*.json` ← Pré-migração

2. **PostgreSQL** (criar manualmente)
   ```bash
   # Adicionar ao cron
   0 2 * * * cd /root/app/rodizio && \
     docker exec rodizio-postgres pg_dump -U rodizio_user rodizio | \
     gzip > data/backups/pg_backup_$(date +\%Y\%m\%d).sql.gz
   ```

### Manter Ambos Ativos (Temporário)

Durante período de transição, você pode:

1. **Usar PostgreSQL** (produção)
2. **Manter db.json atualizado** (backup hot)

```python
# Em app.py, após salvar no PostgreSQL
if os.getenv('DUAL_PERSISTENCE') == 'true':
    # Também salvar no JSON
    save_db(db)
```

---

## 📊 Comparação: JSON vs PostgreSQL

| Aspecto | JSON | PostgreSQL |
|---------|------|------------|
| Performance | ~100ms | ~5-10ms |
| Escalabilidade | Limitada | Excelente |
| Integridade | Manual | Automática (FK) |
| Backup | Simples | Robusto |
| Rollback | Instantâneo | Requer dump |
| Complexidade | Baixa | Média |

---

## 🚀 Recomendações

### Curto Prazo (1-2 semanas)
- ✅ Manter PostgreSQL ativo
- ✅ Monitorar performance e erros
- ✅ Manter db.json como backup quente
- ✅ Testar todas as funcionalidades

### Médio Prazo (1 mês)
- ✅ Se estável: desativar dual persistence
- ✅ Implementar repositories completos
- ✅ Refatorar app.py para usar ORM
- ✅ Otimizar queries

### Longo Prazo (3+ meses)
- ✅ Remover código JSON legado
- ✅ db.json apenas para import/export
- ✅ PostgreSQL como única fonte de verdade

---

## 📞 Contatos de Emergência

### Problemas Críticos
1. Verificar logs: `docker-compose logs -f rodizio-app`
2. Executar rollback: `./scripts/rollback_to_json.sh`
3. Documentar issue no GitHub
4. Se necessário: restaurar do backup

### Scripts Úteis
```bash
# Status da aplicação
docker-compose ps

# Logs em tempo real
docker-compose logs -f

# Verificar conexão PostgreSQL
docker exec rodizio-organistas python3 -c "
import psycopg2
conn = psycopg2.connect('postgresql://rodizio_user:senha@172.23.0.1:5433/rodizio')
print('✅ Conectado')
"

# Verificar JSON
wc -l data/db.json
```

---

## 📈 Histórico de Rollbacks

### Template para Documentar

```markdown
Data: __/__/____
Motivo: _________________
Executado por: __________
Duração downtime: ___ min
Dados perdidos: Sim/Não
Lições aprendidas:
- 
-
-
```

---

**Última atualização:** 26/10/2025  
**Próxima revisão:** Após 1 semana de PostgreSQL em produção
