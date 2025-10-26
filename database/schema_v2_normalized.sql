-- Schema PostgreSQL Normalizado para Rodízio de Organistas CCB
-- Versão: 2.0 (Normalizado)
-- Data: 26/10/2025
-- Compatível com Repositories implementados

-- Extensões úteis
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- Para busca fuzzy

-- ============================================================
-- HIERARQUIA ORGANIZACIONAL
-- ============================================================

CREATE TABLE IF NOT EXISTS regionais (
    id VARCHAR(50) PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sub_regionais (
    id VARCHAR(50) PRIMARY KEY,
    regional_id VARCHAR(50) NOT NULL REFERENCES regionais(id) ON DELETE CASCADE,
    nome VARCHAR(200) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS comuns (
    id VARCHAR(50) PRIMARY KEY,
    sub_regional_id VARCHAR(50) NOT NULL REFERENCES sub_regionais(id) ON DELETE CASCADE,
    nome VARCHAR(200) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- CONFIGURAÇÕES DE COMUM
-- ============================================================

CREATE TABLE IF NOT EXISTS comum_config (
    id SERIAL PRIMARY KEY,
    comum_id VARCHAR(50) NOT NULL REFERENCES comuns(id) ON DELETE CASCADE,
    bimestre_inicio DATE,
    bimestre_fim DATE,
    fechamento_dias INTEGER DEFAULT 3,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(comum_id)
);

CREATE TABLE IF NOT EXISTS comum_horarios (
    id SERIAL PRIMARY KEY,
    comum_id VARCHAR(50) NOT NULL REFERENCES comuns(id) ON DELETE CASCADE,
    dia_semana VARCHAR(20) NOT NULL,  -- domingo, segunda, terca, quarta, quinta, sexta, sabado
    horario TIME NOT NULL,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TIPOS DE ORGANISTAS (tabela de lookup)
-- ============================================================

CREATE TABLE IF NOT EXISTS organista_tipos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE,  -- Titular, Auxiliar, Substituto
    descricao TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Inserir tipos padrão
INSERT INTO organista_tipos (nome, descricao) VALUES
    ('Titular', 'Organista titular da comum'),
    ('Auxiliar', 'Organista auxiliar'),
    ('Substituto', 'Organista substituto')
ON CONFLICT (nome) DO NOTHING;

-- ============================================================
-- ORGANISTAS
-- ============================================================

CREATE TABLE IF NOT EXISTS organistas (
    id VARCHAR(50) PRIMARY KEY,
    comum_id VARCHAR(50) NOT NULL REFERENCES comuns(id) ON DELETE CASCADE,
    nome VARCHAR(200) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(100),
    tipo_id INTEGER DEFAULT 1 REFERENCES organista_tipos(id),
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS organista_dias_permitidos (
    id SERIAL PRIMARY KEY,
    organista_id VARCHAR(50) NOT NULL REFERENCES organistas(id) ON DELETE CASCADE,
    dia_semana VARCHAR(20) NOT NULL,  -- domingo, segunda, terca, quarta, quinta, sexta, sabado
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(organista_id, dia_semana)
);

CREATE TABLE IF NOT EXISTS organista_regras_especiais (
    id SERIAL PRIMARY KEY,
    organista_id VARCHAR(50) NOT NULL REFERENCES organistas(id) ON DELETE CASCADE,
    tipo VARCHAR(50) NOT NULL,  -- tipo da regra
    valor TEXT,
    descricao TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- INDISPONIBILIDADES
-- ============================================================

CREATE TABLE IF NOT EXISTS indisponibilidades (
    id VARCHAR(50) PRIMARY KEY,
    organista_id VARCHAR(50) NOT NULL REFERENCES organistas(id) ON DELETE CASCADE,
    mes VARCHAR(7) NOT NULL,  -- Formato: YYYY-MM
    motivo TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(organista_id, mes)
);

-- ============================================================
-- ESCALAS
-- ============================================================

CREATE TABLE IF NOT EXISTS escala (
    id VARCHAR(50) PRIMARY KEY,
    comum_id VARCHAR(50) NOT NULL REFERENCES comuns(id) ON DELETE CASCADE,
    data DATE NOT NULL,
    horario TIME,
    organista_id VARCHAR(50) REFERENCES organistas(id) ON DELETE SET NULL,
    tipo VARCHAR(20) DEFAULT 'normal',  -- normal, especial, feriado
    observacao TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS escala_rjm (
    id VARCHAR(50) PRIMARY KEY,
    comum_id VARCHAR(50) NOT NULL REFERENCES comuns(id) ON DELETE CASCADE,
    data DATE NOT NULL,
    horario TIME,
    organista_id VARCHAR(50) REFERENCES organistas(id) ON DELETE SET NULL,
    observacao TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS escala_publicacao (
    id SERIAL PRIMARY KEY,
    comum_id VARCHAR(50) NOT NULL REFERENCES comuns(id) ON DELETE CASCADE,
    mes VARCHAR(7) NOT NULL,  -- Formato: YYYY-MM
    publicado BOOLEAN DEFAULT FALSE,
    data_publicacao TIMESTAMPTZ,
    publicado_por VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(comum_id, mes)
);

-- ============================================================
-- TROCAS
-- ============================================================

CREATE TABLE IF NOT EXISTS trocas (
    id VARCHAR(50) PRIMARY KEY,
    escala_id VARCHAR(50) NOT NULL REFERENCES escala(id) ON DELETE CASCADE,
    solicitante_id VARCHAR(50) NOT NULL REFERENCES organistas(id) ON DELETE CASCADE,
    destinatario_id VARCHAR(50) REFERENCES organistas(id) ON DELETE SET NULL,
    motivo TEXT,
    status VARCHAR(20) DEFAULT 'pendente',  -- pendente, aprovada, rejeitada, cancelada
    aprovado_por VARCHAR(50),
    aprovado_em TIMESTAMPTZ,
    observacao_aprovacao TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trocas_historico (
    id SERIAL PRIMARY KEY,
    troca_id VARCHAR(50) NOT NULL REFERENCES trocas(id) ON DELETE CASCADE,
    acao VARCHAR(50) NOT NULL,  -- criada, aprovada, rejeitada, cancelada
    realizado_por VARCHAR(50),
    observacao TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- USUÁRIOS E AUTENTICAÇÃO
-- ============================================================

CREATE TABLE IF NOT EXISTS usuarios (
    id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    nome VARCHAR(200) NOT NULL,
    tipo VARCHAR(50) DEFAULT 'organista',  -- organista, encarregado_comum, encarregado_sub, admin_regional, master
    nivel VARCHAR(20) DEFAULT 'comum',  -- comum, sub_regional, regional, master
    contexto_id VARCHAR(50),  -- ID da comum, sub-regional ou regional
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- LOGS DE AUDITORIA
-- ============================================================

CREATE TABLE IF NOT EXISTS logs_auditoria (
    id VARCHAR(50) PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    tipo VARCHAR(20) NOT NULL,  -- login, logout, create, update, delete
    categoria VARCHAR(50) NOT NULL,  -- autenticacao, organista, escala, etc
    usuario_id VARCHAR(50),
    usuario_nome VARCHAR(200),
    usuario_tipo VARCHAR(50),
    acao VARCHAR(100) NOT NULL,
    descricao TEXT,
    contexto JSONB,  -- Dados contextuais (regional_id, comum_id, etc)
    dados_antes JSONB,
    dados_depois JSONB,
    ip VARCHAR(50),
    user_agent TEXT,
    status VARCHAR(20),  -- sucesso, falha, erro
    mensagem_erro TEXT
);

-- ============================================================
-- ÍNDICES PARA PERFORMANCE
-- ============================================================

-- Hierarquia
CREATE INDEX IF NOT EXISTS idx_sub_regionais_regional ON sub_regionais(regional_id);
CREATE INDEX IF NOT EXISTS idx_comuns_sub_regional ON comuns(sub_regional_id);

-- Organistas
CREATE INDEX IF NOT EXISTS idx_organistas_comum ON organistas(comum_id);
CREATE INDEX IF NOT EXISTS idx_organistas_tipo ON organistas(tipo_id);
CREATE INDEX IF NOT EXISTS idx_organistas_ativo ON organistas(ativo);
CREATE INDEX IF NOT EXISTS idx_organistas_nome ON organistas USING gin(nome gin_trgm_ops);

-- Escalas
CREATE INDEX IF NOT EXISTS idx_escala_comum ON escala(comum_id);
CREATE INDEX IF NOT EXISTS idx_escala_data ON escala(data);
CREATE INDEX IF NOT EXISTS idx_escala_comum_data ON escala(comum_id, data);
CREATE INDEX IF NOT EXISTS idx_escala_organista ON escala(organista_id);

CREATE INDEX IF NOT EXISTS idx_escala_rjm_comum ON escala_rjm(comum_id);
CREATE INDEX IF NOT EXISTS idx_escala_rjm_data ON escala_rjm(data);

-- Indisponibilidades
CREATE INDEX IF NOT EXISTS idx_indisponibilidades_organista ON indisponibilidades(organista_id);
CREATE INDEX IF NOT EXISTS idx_indisponibilidades_mes ON indisponibilidades(mes);

-- Trocas
CREATE INDEX IF NOT EXISTS idx_trocas_escala ON trocas(escala_id);
CREATE INDEX IF NOT EXISTS idx_trocas_solicitante ON trocas(solicitante_id);
CREATE INDEX IF NOT EXISTS idx_trocas_status ON trocas(status);

-- Usuários
CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username);
CREATE INDEX IF NOT EXISTS idx_usuarios_nivel ON usuarios(nivel);
CREATE INDEX IF NOT EXISTS idx_usuarios_contexto ON usuarios(contexto_id);

-- Logs
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs_auditoria(timestamp);
CREATE INDEX IF NOT EXISTS idx_logs_usuario ON logs_auditoria(usuario_id);
CREATE INDEX IF NOT EXISTS idx_logs_tipo ON logs_auditoria(tipo);
CREATE INDEX IF NOT EXISTS idx_logs_categoria ON logs_auditoria(categoria);

-- ============================================================
-- TRIGGERS PARA UPDATED_AT
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar trigger em todas as tabelas com updated_at
CREATE TRIGGER update_regionais_updated_at BEFORE UPDATE ON regionais
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sub_regionais_updated_at BEFORE UPDATE ON sub_regionais
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_comuns_updated_at BEFORE UPDATE ON comuns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_comum_config_updated_at BEFORE UPDATE ON comum_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_comum_horarios_updated_at BEFORE UPDATE ON comum_horarios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_organistas_updated_at BEFORE UPDATE ON organistas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_organista_regras_updated_at BEFORE UPDATE ON organista_regras_especiais
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_indisponibilidades_updated_at BEFORE UPDATE ON indisponibilidades
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_escala_updated_at BEFORE UPDATE ON escala
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_escala_rjm_updated_at BEFORE UPDATE ON escala_rjm
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_escala_publicacao_updated_at BEFORE UPDATE ON escala_publicacao
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_trocas_updated_at BEFORE UPDATE ON trocas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- COMENTÁRIOS DAS TABELAS
-- ============================================================

COMMENT ON TABLE regionais IS 'Regionais da organização';
COMMENT ON TABLE sub_regionais IS 'Sub-regionais dentro de cada regional';
COMMENT ON TABLE comuns IS 'Comuns dentro de cada sub-regional';
COMMENT ON TABLE organistas IS 'Organistas cadastrados';
COMMENT ON TABLE organista_tipos IS 'Tipos de organistas (Titular, Auxiliar, Substituto)';
COMMENT ON TABLE indisponibilidades IS 'Períodos em que organistas não podem tocar';
COMMENT ON TABLE escala IS 'Escalas de cultos normais';
COMMENT ON TABLE escala_rjm IS 'Escalas de RJM (Reunião de Jovens e Menores)';
COMMENT ON TABLE trocas IS 'Solicitações de troca de escala entre organistas';
COMMENT ON TABLE usuarios IS 'Usuários do sistema com permissões';
COMMENT ON TABLE logs_auditoria IS 'Registro de todas ações no sistema';
