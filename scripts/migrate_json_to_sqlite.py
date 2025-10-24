import os
import json
import sqlite3
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
JSON_PATH = os.path.abspath(os.path.join(DATA_DIR, 'db.json'))
SQLITE_PATH = os.path.abspath(os.path.join(DATA_DIR, 'rodizio.db'))

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS regionais (
  id TEXT PRIMARY KEY,
  nome TEXT NOT NULL,
  ativo INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS sub_regionais (
  id TEXT PRIMARY KEY,
  regional_id TEXT NOT NULL REFERENCES regionais(id) ON DELETE CASCADE,
  nome TEXT NOT NULL,
  ativo INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS comuns (
  id TEXT PRIMARY KEY,
  sub_regional_id TEXT NOT NULL REFERENCES sub_regionais(id) ON DELETE CASCADE,
  nome TEXT NOT NULL,
  endereco TEXT,
  cidade TEXT,
  ativo INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS organistas (
  id TEXT PRIMARY KEY,
  comum_id TEXT NOT NULL REFERENCES comuns(id) ON DELETE CASCADE,
  nome TEXT NOT NULL,
  password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS organista_tipos (
  organista_id TEXT NOT NULL REFERENCES organistas(id) ON DELETE CASCADE,
  tipo TEXT NOT NULL,
  PRIMARY KEY (organista_id, tipo)
);

CREATE TABLE IF NOT EXISTS organista_dias_permitidos (
  organista_id TEXT NOT NULL REFERENCES organistas(id) ON DELETE CASCADE,
  dia TEXT NOT NULL,
  PRIMARY KEY (organista_id, dia)
);

CREATE TABLE IF NOT EXISTS indisponibilidades (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  comum_id TEXT NOT NULL REFERENCES comuns(id) ON DELETE CASCADE,
  organista_id TEXT NOT NULL REFERENCES organistas(id) ON DELETE CASCADE,
  data TEXT NOT NULL,
  motivo TEXT,
  autor TEXT,
  status TEXT
);

CREATE TABLE IF NOT EXISTS escala (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  comum_id TEXT NOT NULL REFERENCES comuns(id) ON DELETE CASCADE,
  data TEXT NOT NULL,
  dia_semana TEXT,
  meia_hora TEXT,
  culto TEXT
);

CREATE TABLE IF NOT EXISTS escala_rjm (
  id TEXT PRIMARY KEY,
  comum_id TEXT NOT NULL REFERENCES comuns(id) ON DELETE CASCADE,
  data TEXT NOT NULL,
  dia_semana TEXT,
  organista TEXT
);

CREATE TABLE IF NOT EXISTS comum_config (
  comum_id TEXT PRIMARY KEY REFERENCES comuns(id) ON DELETE CASCADE,
  periodo_inicio TEXT,
  periodo_fim TEXT,
  fechamento_publicacao_dias INTEGER,
  dias_culto TEXT
);

CREATE TABLE IF NOT EXISTS trocas (
  id TEXT PRIMARY KEY,
  comum_id TEXT NOT NULL REFERENCES comuns(id) ON DELETE CASCADE,
  status TEXT,
  modalidade TEXT,
  tipo TEXT,
  data TEXT,
  slot TEXT,
  solicitante_id TEXT,
  solicitante_nome TEXT,
  alvo_id TEXT,
  alvo_nome TEXT,
  motivo TEXT,
  criado_em TEXT,
  atualizado_em TEXT
);

CREATE TABLE IF NOT EXISTS trocas_historico (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  troca_id TEXT NOT NULL REFERENCES trocas(id) ON DELETE CASCADE,
  quando TEXT,
  acao TEXT,
  por TEXT
);

CREATE TABLE IF NOT EXISTS logs_auditoria (
  id TEXT PRIMARY KEY,
  timestamp TEXT,
  tipo TEXT,
  categoria TEXT,
  acao TEXT,
  descricao TEXT,
  usuario_id TEXT,
  usuario_nome TEXT,
  usuario_tipo TEXT,
  regional_id TEXT,
  sub_regional_id TEXT,
  comum_id TEXT,
  status TEXT,
  ip TEXT,
  user_agent TEXT
);

CREATE INDEX IF NOT EXISTS idx_indisp_comum_data ON indisponibilidades(comum_id, data);
CREATE INDEX IF NOT EXISTS idx_escala_comum_data ON escala(comum_id, data);
CREATE INDEX IF NOT EXISTS idx_rjm_comum_data ON escala_rjm(comum_id, data);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs_auditoria(timestamp);
CREATE INDEX IF NOT EXISTS idx_trocas_comum_data ON trocas(comum_id, data);
"""

def backup_json():
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    src = JSON_PATH
    dst = os.path.join(DATA_DIR, f'db_backup_{ts}.json')
    if os.path.exists(src):
        import shutil
        shutil.copy2(src, dst)
        return dst
    return None


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_json():
    if not os.path.exists(JSON_PATH):
        raise FileNotFoundError(f'JSON não encontrado: {JSON_PATH}')
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def connect_db():
    return sqlite3.connect(SQLITE_PATH)


def create_schema(conn):
    conn.executescript(SCHEMA_SQL)


def insert_hierarchy(conn, db):
    cur = conn.cursor()
    regionais = db.get('regionais', {}) or {}
    for rid, r in regionais.items():
        cur.execute('INSERT OR REPLACE INTO regionais(id,nome,ativo) VALUES (?,?,?)', (
            r.get('id') or rid, r.get('nome',''), 1 if r.get('ativo', True) else 0
        ))
        subs = (r.get('sub_regionais') or {})
        for sid, s in subs.items():
            cur.execute('INSERT OR REPLACE INTO sub_regionais(id,regional_id,nome,ativo) VALUES (?,?,?,?)', (
                s.get('id') or sid, r.get('id') or rid, s.get('nome',''), 1 if s.get('ativo', True) else 0
            ))
            comuns = (s.get('comuns') or {})
            for cid, c in comuns.items():
                cur.execute('INSERT OR REPLACE INTO comuns(id,sub_regional_id,nome,endereco,cidade,ativo) VALUES (?,?,?,?,?,?)', (
                    c.get('id') or cid, s.get('id') or sid, c.get('nome',''), c.get('endereco',''), c.get('cidade',''), 1 if c.get('ativo', True) else 0
                ))

                # Organistas
                for o in c.get('organistas', []) or []:
                    cur.execute('INSERT OR REPLACE INTO organistas(id,comum_id,nome,password_hash) VALUES (?,?,?,?)', (
                        o.get('id'), c.get('id') or cid, o.get('nome',''), o.get('password_hash','')
                    ))
                    for t in o.get('tipos', []) or []:
                        cur.execute('INSERT OR IGNORE INTO organista_tipos(organista_id,tipo) VALUES (?,?)', (o.get('id'), t))
                    for d in o.get('dias_permitidos', []) or []:
                        cur.execute('INSERT OR IGNORE INTO organista_dias_permitidos(organista_id,dia) VALUES (?,?)', (o.get('id'), d))

                # Indisponibilidades
                for ind in c.get('indisponibilidades', []) or []:
                    cur.execute('INSERT INTO indisponibilidades(comum_id,organista_id,data,motivo,autor,status) VALUES (?,?,?,?,?,?)', (
                        c.get('id') or cid, ind.get('id'), ind.get('data'), ind.get('motivo'), ind.get('autor'), ind.get('status')
                    ))

                # Escala (culto/meia-hora)
                for e in c.get('escala', []) or []:
                    cur.execute('INSERT INTO escala(comum_id,data,dia_semana,meia_hora,culto) VALUES (?,?,?,?,?)', (
                        c.get('id') or cid, e.get('data'), e.get('dia_semana'), e.get('meia_hora'), e.get('culto')
                    ))

                # Escala RJM
                for rjm in c.get('escala_rjm', []) or []:
                    cur.execute('INSERT OR REPLACE INTO escala_rjm(id,comum_id,data,dia_semana,organista) VALUES (?,?,?,?,?)', (
                        rjm.get('id'), c.get('id') or cid, rjm.get('data'), rjm.get('dia_semana'), rjm.get('organista')
                    ))

                # Config da comum
                cfg = c.get('config') or {}
                periodo = cfg.get('periodo') or {}
                dias_culto = cfg.get('dias_culto') or []
                dias_culto_csv = ','.join(dias_culto) if isinstance(dias_culto, list) else str(dias_culto or '')
                cur.execute('INSERT OR REPLACE INTO comum_config(comum_id,periodo_inicio,periodo_fim,fechamento_publicacao_dias,dias_culto) VALUES (?,?,?,?,?)', (
                    c.get('id') or cid, periodo.get('inicio'), periodo.get('fim'), cfg.get('fechamento_publicacao_dias'), dias_culto_csv
                ))

                # Trocas
                for tr in c.get('trocas', []) or []:
                    cur.execute('INSERT OR REPLACE INTO trocas(id,comum_id,status,modalidade,tipo,data,slot,solicitante_id,solicitante_nome,alvo_id,alvo_nome,motivo,criado_em,atualizado_em) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (
                        tr.get('id'), c.get('id') or cid, tr.get('status'), tr.get('modalidade'), tr.get('tipo'), tr.get('data'), tr.get('slot'),
                        tr.get('solicitante_id'), tr.get('solicitante_nome'), tr.get('alvo_id'), tr.get('alvo_nome'), tr.get('motivo'), tr.get('criado_em'), tr.get('atualizado_em')
                    ))
                    for h in tr.get('historico', []) or []:
                        cur.execute('INSERT INTO trocas_historico(troca_id,quando,acao,por) VALUES (?,?,?,?)', (
                            tr.get('id'), h.get('quando'), h.get('acao'), h.get('por')
                        ))

    # Logs de auditoria (nível raiz)
    logs = db.get('logs_auditoria', []) or []
    for l in logs:
        cur.execute('INSERT OR REPLACE INTO logs_auditoria(id,timestamp,tipo,categoria,acao,descricao,usuario_id,usuario_nome,usuario_tipo,regional_id,sub_regional_id,comum_id,status,ip,user_agent) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (
            l.get('id'), l.get('timestamp'), l.get('tipo'), l.get('categoria'), l.get('acao'), l.get('descricao'),
            l.get('usuario_id'), l.get('usuario_nome'), l.get('usuario_tipo'),
            (l.get('contexto') or {}).get('regional_id'), (l.get('contexto') or {}).get('sub_regional_id'), (l.get('contexto') or {}).get('comum_id'),
            l.get('status'), l.get('ip'), l.get('user_agent')
        ))


def main():
    ensure_dirs()
    if not os.path.exists(JSON_PATH):
        raise SystemExit(f'Arquivo JSON não encontrado em {JSON_PATH}')
    if os.path.exists(SQLITE_PATH):
        raise SystemExit(f'Banco SQLite já existe em {SQLITE_PATH}. Remova-o manualmente para migrar novamente.')

    backup = backup_json()
    print(f'Backup do JSON: {backup}' if backup else 'Sem backup (arquivo não encontrado)')

    dbdata = load_json()
    conn = connect_db()
    try:
        with conn:
            create_schema(conn)
            insert_hierarchy(conn, dbdata)
        print(f'Migração concluída com sucesso: {SQLITE_PATH}')
    finally:
        conn.close()

if __name__ == '__main__':
    main()
