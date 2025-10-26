-- Schema PostgreSQL para Rodízio de Organistas CCB
-- Versão: 1.0
-- Data: 26/10/2025

-- Extensões úteis
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- Para busca fuzzy

-- ============================================================
-- HIERARQUIA ORGANIZACIONAL
-- ============================================================

CREATE TABLE IF NOT EXISTS regionais (
  id VARCHAR(50) PRIMARY KEY,
  nome VARCHAR(200) NOT NULL,
  ativo BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sub_regionais (
  id VARCHAR(50) PRIMARY KEY,
  regional_id VARCHAR(50) NOT NULL REFERENCES regionais(id) ON DELETE CASCADE,
  nome VARCHAR(200) NOT NULL,
  ativo BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS comuns (
  id VARCHAR(50) PRIMARY KEY,
  sub_regional_id VARCHAR(50) NOT NULL REFERENCES sub_regionais(id) ON DELETE CASCADE,
  nome VARCHAR(200) NOT NULL,
  endereco TEXT,
  cidade VARCHAR(100),
  ativo BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- ORGANISTAS
-- ============================================================

CREATE TABLE IF NOT EXISTS organistas (
  id VARCHAR(50) PRIMARY KEY,
  comum_id VARCHAR(50) NOT NULL REFERENCES comuns(id) ON DELETE CASCADE,
  nome VARCHAR(200) NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS organista_tipos (
  organista_id VARCHAR(50) NOT NULL REFERENCES organistas(id) ON DELETE CASCADE,
  tipo VARCHAR(50) NOT NULL,
  PRIMARY KEY (organista_id, tipo)
);

CREATE TABLE IF NOT EXISTS organista_dias_permitidos (
  organista_id VARCHAR(50) NOT NULL REFERENCES organistas(id) ON DELETE CASCADE,
  dia VARCHAR(20) NOT NULL,
  PRIMARY KEY (organista_id, dia)
);

CREATE TABLE IF NOT EXISTS organista_regras_especiais (
  organista_id VARCHAR(50) NOT NULL REFERENCES organistas(id) ON DELETE CASCADE,
  chave VARCHAR(100) NOT NULL,
  valor TEXT,
  PRIMARY KEY (organista_id, chave)
);

-- ============================================================
-- INDISPONIBILIDADES
-- ============================================================

CREATE TABLE IF NOT EXISTS indisponibilidades (
  id SERIAL PRIMARY KEY,
  comum_id VARCHAR(50) NOT NULL REFERENCES comuns(id) ON DELETE CASCADE,
  organista_id VARCHAR(50) NOT NULL REFERENCES organistas(id) ON DELETE CASCADE,
  data DATE NOT NULL,
  motivo TEXT,
  autor VARCHAR(50),
  status VARCHAR(20),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- ESCALAS
-- ============================================================

CREATE TABLE IF NOT EXISTS escala (
  id SERIAL PRIMARY KEY,
  comum_id VARCHAR(50) NOT NULL REFERENCES comuns(id) ON DELETE CASCADE,
  data DATE NOT NULL,
  dia_semana VARCHAR(20),
  meia_hora VARCHAR(200),
  culto VARCHAR(200),
  criado_em TIMESTAMPTZ DEFAULT NOW(),
  criado_por VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS escala_rjm (
  id VARCHAR(100) PRIMARY KEY,
  comum_id VARCHAR(50) NOT NULL REFERENCES comuns(id) ON DELETE CASCADE,
  data DATE NOT NULL,
  dia_semana VARCHAR(20),
  organista VARCHAR(200),
  criado_em TIMESTAMPTZ DEFAULT NOW(),
  criado_por VARCHAR(50)
);

-- Metadados de publicação de escala (por comum)
CREATE TABLE IF NOT EXISTS escala_publicacao (
  comum_id VARCHAR(50) PRIMARY KEY REFERENCES comuns(id) ON DELETE CASCADE,
  publicada_em TIMESTAMPTZ,
  publicada_por VARCHAR(50),
  periodo_inicio DATE,
  periodo_fim DATE
);

-- ============================================================
-- CONFIGURAÇÕES
-- ============================================================

CREATE TABLE IF NOT EXISTS comum_config (
  comum_id VARCHAR(50) PRIMARY KEY REFERENCES comuns(id) ON DELETE CASCADE,
  periodo_inicio DATE,
  periodo_fim DATE,
  fechamento_publicacao_dias INTEGER,
  dias_culto JSONB,  -- Array de dias permitidos
  horarios JSONB,    -- Configurações de horários
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Configurações de horários (por comum e dia)
CREATE TABLE IF NOT EXISTS comum_horarios (
  id SERIAL PRIMARY KEY,
  comum_id VARCHAR(50) NOT NULL REFERENCES comuns(id) ON DELETE CASCADE,
  dia_semana VARCHAR(20) NOT NULL,
  meia_hora TIME,
  culto TIME,
  rjm TIME,
  UNIQUE (comum_id, dia_semana)
);

-- ============================================================
-- SISTEMA DE TROCAS
-- ============================================================

CREATE TABLE IF NOT EXISTS trocas (
  id VARCHAR(100) PRIMARY KEY,
  comum_id VARCHAR(50) NOT NULL REFERENCES comuns(id) ON DELETE CASCADE,
  status VARCHAR(20),
  modalidade VARCHAR(50),
  tipo VARCHAR(50),
  data DATE,
  slot VARCHAR(50),
  solicitante_id VARCHAR(50),
  solicitante_nome VARCHAR(200),
  alvo_id VARCHAR(50),
  alvo_nome VARCHAR(200),
  motivo TEXT,
  criado_em TIMESTAMPTZ DEFAULT NOW(),
  atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trocas_historico (
  id SERIAL PRIMARY KEY,
  troca_id VARCHAR(100) NOT NULL REFERENCES trocas(id) ON DELETE CASCADE,
  quando TIMESTAMPTZ NOT NULL,
  acao VARCHAR(50),
  por VARCHAR(200)
);

-- ============================================================
-- USUÁRIOS DO SISTEMA
-- ============================================================

CREATE TABLE IF NOT EXISTS usuarios (
  id VARCHAR(50) PRIMARY KEY,
  nome VARCHAR(200) NOT NULL,
  password_hash TEXT NOT NULL,
  tipo VARCHAR(50) NOT NULL,  -- master, admin_regional, encarregado_sub, etc
  nivel VARCHAR(50) NOT NULL,  -- sistema, regional, sub_regional, comum
  contexto_id VARCHAR(50),     -- ID da regional/sub/comum
  ativo BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- AUDITORIA
-- ============================================================

CREATE TABLE IF NOT EXISTS logs_auditoria (
  id VARCHAR(100) PRIMARY KEY,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  tipo VARCHAR(50),
  categoria VARCHAR(50),
  acao VARCHAR(100),
  descricao TEXT,
  usuario_id VARCHAR(50),
  usuario_nome VARCHAR(200),
  usuario_tipo VARCHAR(50),
  regional_id VARCHAR(50),
  sub_regional_id VARCHAR(50),
  comum_id VARCHAR(50),
  status VARCHAR(20),
  ip VARCHAR(45),
  user_agent TEXT,
  dados_antes JSONB,
  dados_depois JSONB
);

-- ============================================================
-- ÍNDICES PARA PERFORMANCE
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_organistas_comum ON organistas(comum_id);
CREATE INDEX IF NOT EXISTS idx_indisponibilidades_comum_data ON indisponibilidades(comum_id, data);
CREATE INDEX IF NOT EXISTS idx_indisponibilidades_organista ON indisponibilidades(organista_id);
CREATE INDEX IF NOT EXISTS idx_indisponibilidades_data ON indisponibilidades(data);
CREATE INDEX IF NOT EXISTS idx_escala_comum_data ON escala(comum_id, data);
CREATE INDEX IF NOT EXISTS idx_escala_data ON escala(data);
CREATE INDEX IF NOT EXISTS idx_escala_rjm_comum_data ON escala_rjm(comum_id, data);
CREATE INDEX IF NOT EXISTS idx_trocas_comum_status ON trocas(comum_id, status);
CREATE INDEX IF NOT EXISTS idx_trocas_data ON trocas(data);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs_auditoria(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_logs_usuario ON logs_auditoria(usuario_id);
CREATE INDEX IF NOT EXISTS idx_logs_comum ON logs_auditoria(comum_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_tipo ON usuarios(tipo);

-- ============================================================
-- TRIGGERS PARA ATUALIZAÇÃO AUTOMÁTICA DE TIMESTAMPS
-- ============================================================

-- Função genérica para updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar triggers
CREATE TRIGGER update_regionais_updated_at BEFORE UPDATE ON regionais
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sub_regionais_updated_at BEFORE UPDATE ON sub_regionais
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_comuns_updated_at BEFORE UPDATE ON comuns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_organistas_updated_at BEFORE UPDATE ON organistas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_comum_config_updated_at BEFORE UPDATE ON comum_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_trocas_updated_at BEFORE UPDATE ON trocas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- COMENTÁRIOS NAS TABELAS (DOCUMENTAÇÃO)
-- ============================================================

COMMENT ON TABLE regionais IS 'Regionais da organização';
COMMENT ON TABLE sub_regionais IS 'Sub-regionais dentro de cada regional';
COMMENT ON TABLE comuns IS 'Comuns (igrejas) dentro de cada sub-regional';
COMMENT ON TABLE organistas IS 'Organistas cadastrados em cada comum';
COMMENT ON TABLE organista_tipos IS 'Tipos de culto que cada organista pode tocar (Meia-hora, Culto, RJM)';
COMMENT ON TABLE organista_dias_permitidos IS 'Dias da semana em que cada organista está disponível';
COMMENT ON TABLE indisponibilidades IS 'Datas em que organistas estão indisponíveis';
COMMENT ON TABLE escala IS 'Escala de cultos regulares e meia-hora';
COMMENT ON TABLE escala_rjm IS 'Escala específica para RJM (Reunião de Jovens e Menores)';
COMMENT ON TABLE trocas IS 'Sistema de trocas de escala entre organistas';
COMMENT ON TABLE usuarios IS 'Usuários do sistema (master, admins, encarregados)';
COMMENT ON TABLE logs_auditoria IS 'Logs de auditoria de todas as operações';

-- ============================================================
-- CONCESSÃO DE PERMISSÕES
-- ============================================================

GRANT ALL ON ALL TABLES IN SCHEMA public TO rodizio_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO rodizio_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO rodizio_user;

-- ============================================================
-- FIM DO SCHEMA
-- ============================================================
