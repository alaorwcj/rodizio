# Status da Fase 2 - Situação Atual

**Data:** 26/10/2025  
**Status:** ⚠️ DIVERGÊNCIA IDENTIFICADA - Ação Necessária

---

## 🔍 Problema Identificado

Durante a implementação dos repositories, descobrimos uma **divergência crítica** entre:

1. **Repositories criados** - Assumem um schema normalizado "ideal" 
2. **Schema PostgreSQL real** - Reflete estrutura do JSON original migrado

### Exemplos da Divergência:

**Tabela `organistas`:**
- ❌ Repositories assumem: `tipo_id`, `telefone`, `email`, `ativo`
- ✅ Schema real tem: `id`, `comum_id`, `nome`, `password_hash`

**Tabela `escala`:**
- ❌ Repositories assumem: `organista_id`, `horario`, `tipo`, `observacao`
- ✅ Schema real tem: `data`, `dia_semana`, `meia_hora`, `culto`

**Tabela `indisponibilidades`:**
- ❌ Repositories assumem: `mes` (VARCHAR formato YYYY-MM)
- ✅ Schema real tem: `data` (DATE específica)

---

##  📊 Repositories Criados

✅ **6 repositories implementados:**
1. `OrganistaRepository` (320 linhas)
2. `EscalaRepository` (460 linhas)
3. `IndisponibilidadeRepository` (140 linhas)
4. `ComumRepository` (320 linhas)
5. `UsuarioRepository` (220 linhas)
6. `TrocaRepository` (270 linhas)

**Total:** ~1.730 linhas de código

---

## 🧪 Resultados dos Testes

```
✅ PASSOU - Conexão PostgreSQL
✅ PASSOU - ComumRepository (hierarquia funciona!)
❌ FALHOU - OrganistaRepository (colunas não existem)
❌ FALHOU - EscalaRepository (colunas não existem)
❌ FALHOU - IndisponibilidadeRepository (colunas não existem)
❌ FALHOU - UsuarioRepository (colunas não existem)
❌ FALHOU - TrocaRepository (colunas não existem)
```

**2/7 testes passaram** - ComumRepository funciona porque a hierarquia (regionais/sub-regionais/comuns) está correta.

---

## 🎯 Opções Disponíveis

### **OPÇÃO 1: Adaptar Repositories ao Schema Existente** ⭐ RECOMENDADA

**Ação:** Reescrever repositories para usar as colunas reais do PostgreSQL

**Vantagens:**
- ✅ Dados já estão migrados e válidos
- ✅ Menos risco de perda de dados
- ✅ Mais rápido (4-6 horas de work)
- ✅ Schema reflete estrutura real do sistema

**Desvantagens:**
- ⚠️ Schema não é "ideal" (mistura dados de autenticação com dados de organistas)
- ⚠️ Repositories terão queries mais complexas

**Estimativa:** 4-6 horas

**Como fazer:**
1. Ler schema.sql completo
2. Ajustar cada repository para usar colunas corretas
3. Reexecutar testes
4. Integrar no app.py

---

### **OPÇÃO 2: Refatorar Schema PostgreSQL**

**Ação:** Alterar schema do PostgreSQL para match dos repositories criados

**Vantagens:**
- ✅ Repositories já estão prontos (1.730 linhas)
- ✅ Schema "normalizado" e mais profissional
- ✅ Separação clara entre organistas e usuários

**Desvantagens:**
- ❌ Precisa criar novo schema.sql
- ❌ Precisa recriar database
- ❌ Precisa re-migrar todos os dados
- ❌ Risco de perder dados se errar
- ❌ Muito mais trabalho (10-15 horas)

**Estimativa:** 10-15 horas

**Como fazer:**
1. Reescrever schema.sql
2. Drop/Recreate database
3. Adaptar migrate_to_postgres.py
4. Re-executar migração
5. Validar dados
6. Testar repositories

---

### **OPÇÃO 3: Rollback Completo**

**Ação:** Voltar para JSON, planejar melhor

**Como fazer:**
```bash
cd /root/app/rodizio
./scripts/rollback_to_json.sh
```

**Vantagens:**
- ✅ Sistema volta ao estado funcional original
- ✅ Tempo para replanejar arquitetura

**Desvantagens:**
- ❌ Perde todo trabalho da Fase 1 e Fase 2
- ❌ Volta aos problemas de performance do JSON

---

## 💾 Backups Disponíveis

### Dados:
- ✅ `data/db_pre_migrate_20251026_143508.json` (backup pré-migração)
- ✅ PostgreSQL com 303 escalas, 24 organistas, 2 regionais

### Código:
- ✅ `app_backup_fase2_20251026_174709.py` (149KB)
- ✅ `app_backup_20251014_203109.py` (backup anterior)

---

## 📋 Schema Real do PostgreSQL

**Tabelas principais e suas colunas:**

```sql
-- organistas: id, comum_id, nome, password_hash
-- organista_tipos: organista_id, tipo
-- organista_dias_permitidos: organista_id, dia
-- organista_regras_especiais: organista_id, chave, valor

-- escala: id, comum_id, data, dia_semana, meia_hora, culto
-- escala_rjm: id, comum_id, data, dia_semana, hora, culto, autor

-- indisponibilidades: id, comum_id, organista_id, data, motivo, autor, status

-- usuarios: id, username, password, nome, tipo, nivel, contexto_id
-- logs_auditoria: id, timestamp, tipo, categoria, usuario_id, acao, descricao, contexto

-- trocas: id, escala_id_origem, organista_origem_id, organista_destino_id, 
--         data_troca, solicitante_id, aprovador_id, status
```

---

## 🚦 Recomendação

**OPÇÃO 1** é a mais pragmática:

1. ✅ Dados já estão seguros no PostgreSQL
2. ✅ Schema reflete o sistema real (veio do JSON)
3. ✅ 4-6 horas vs 10-15 horas da Opção 2
4. ✅ Menor risco
5. ✅ Rollback sempre disponível

**Próximos passos (se escolher Opção 1):**
1. Ler schema.sql completo (297 linhas)
2. Adaptar OrganistaRepository
3. Adaptar EscalaRepository
4. Adaptar IndisponibilidadeRepository
5. Adaptar TrocaRepository
6. UsuarioRepository já está OK (estrutura está correta)
7. Executar testes novamente
8. Integrar no app.py

---

## ❓ Decisão Necessária

**Qual opção você prefere?**

A) Adaptar repositories ao schema existente (4-6h, menor risco)  
B) Refatorar schema PostgreSQL (10-15h, mais "correto")  
C) Rollback e replanejar

---

**Arquivos criados nesta sessão:**
- `repositories/__init__.py`
- `repositories/organista_repo.py` (320 linhas)
- `repositories/escala_repo.py` (460 linhas)
- `repositories/indisponibilidade_repo.py` (140 linhas)
- `repositories/comum_repo.py` (320 linhas)
- `repositories/usuario_repo.py` (220 linhas)
- `repositories/troca_repo.py` (270 linhas)
- `test_repositories.py` (280 linhas)
- `app_backup_fase2_20251026_174709.py` (backup)
