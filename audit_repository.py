import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

class AuditRepo:
    def __init__(self, db_path: str = "data/rodizio.db"):
        self.db_path = db_path

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn

    def insert_log(self, log: Dict):
        q = (
            "INSERT OR REPLACE INTO logs_auditoria("
            "id, timestamp, tipo, categoria, acao, descricao, usuario_id, usuario_nome, usuario_tipo, "
            "regional_id, sub_regional_id, comum_id, status, ip, user_agent)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        )
        vals = (
            log.get("id"), log.get("timestamp"), log.get("tipo"), log.get("categoria"), log.get("acao"), log.get("descricao"),
            log.get("usuario_id"), log.get("usuario_nome"), log.get("usuario_tipo"),
            (log.get("contexto") or {}).get("regional_id"),
            (log.get("contexto") or {}).get("sub_regional_id"),
            (log.get("contexto") or {}).get("comum_id"),
            log.get("status"), log.get("ip"), log.get("user_agent")
        )
        with self._connect() as conn:
            conn.execute(q, vals)

    def _build_filters(self, filters: Dict, scope: Dict) -> Tuple[str, List]:
        where = []
        params: List = []
        # scope
        if scope:
            if scope.get("regional_id"):
                where.append("regional_id = ?")
                params.append(scope["regional_id"])
            if scope.get("sub_regional_id"):
                where.append("sub_regional_id = ?")
                params.append(scope["sub_regional_id"])
        # periodo
        periodo = (filters or {}).get("periodo", "30d")
        now = datetime.utcnow()
        if periodo == "24h":
            threshold = (now - timedelta(days=1)).isoformat()
            where.append("timestamp >= ?")
            params.append(threshold)
        elif periodo == "7d":
            threshold = (now - timedelta(days=7)).isoformat()
            where.append("timestamp >= ?")
            params.append(threshold)
        elif periodo == "30d":
            threshold = (now - timedelta(days=30)).isoformat()
            where.append("timestamp >= ?")
            params.append(threshold)
        # categoria/tipo/usuario/busca
        categoria = (filters or {}).get("categoria")
        if categoria:
            where.append("categoria = ?")
            params.append(categoria)
        tipo = (filters or {}).get("tipo")
        if tipo:
            where.append("tipo = ?")
            params.append(tipo)
        usuario = (filters or {}).get("usuario")
        if usuario:
            like = f"%{usuario.lower()}%"
            where.append("(LOWER(COALESCE(usuario_id,'')) LIKE ? OR LOWER(COALESCE(usuario_nome,'')) LIKE ?)")
            params.extend([like, like])
        busca = (filters or {}).get("busca")
        if busca:
            like = f"%{busca.lower()}%"
            where.append("(LOWER(COALESCE(descricao,'')) LIKE ? OR LOWER(COALESCE(acao,'')) LIKE ?)")
            params.extend([like, like])
        clause = (" WHERE " + " AND ".join(where)) if where else ""
        return clause, params

    def fetch_logs(self, filters: Dict, scope: Dict, pagina: int, por_pagina: int) -> Tuple[List[Dict], int]:
        where, params = self._build_filters(filters, scope)
        order = " ORDER BY timestamp DESC"
        limit = " LIMIT ? OFFSET ?"
        with self._connect() as conn:
            total = conn.execute(f"SELECT COUNT(*) FROM logs_auditoria{where}", params).fetchone()[0]
            params_page = params + [por_pagina, (pagina - 1) * por_pagina]
            rows = conn.execute(f"SELECT * FROM logs_auditoria{where}{order}{limit}", params_page).fetchall()
        logs = [dict(r) for r in rows]
        return logs, total

    def fetch_log(self, log_id: str) -> Optional[Dict]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM logs_auditoria WHERE id = ?", (log_id,)).fetchone()
        return dict(row) if row else None

    def stats(self, scope: Dict) -> Dict:
        where, params = self._build_filters({"periodo": "7d"}, scope)
        q_logs_7d = f"SELECT * FROM logs_auditoria{where}"
        with self._connect() as conn:
            rows = conn.execute(q_logs_7d, params).fetchall()
        logs = [dict(r) for r in rows]
        now = datetime.utcnow()
        iso_24h = (now - timedelta(hours=24)).isoformat()
        logins_7d = sum(1 for l in logs if l.get("tipo") == "login" and l.get("status") == "sucesso")
        logins_falhas = sum(1 for l in logs if l.get("tipo") == "login" and l.get("status") == "falha")
        alteracoes_24h = sum(1 for l in logs if l.get("tipo") in ("create","update","delete") and (l.get("timestamp") or '') >= iso_24h)
        usuarios_ativos = len({(l.get("usuario_id") or '') for l in logs if l.get("usuario_id")})
        return {
            "logins_7d": logins_7d,
            "logins_falhas": logins_falhas,
            "alteracoes_24h": alteracoes_24h,
            "usuarios_ativos": usuarios_ativos,
        }

    def export_csv(self, filters: Dict, scope: Dict) -> str:
        import csv
        from io import StringIO
        where, params = self._build_filters(filters, scope)
        order = " ORDER BY timestamp DESC"
        with self._connect() as conn:
            rows = conn.execute(f"SELECT * FROM logs_auditoria{where}{order}", params).fetchall()
        si = StringIO()
        writer = csv.writer(si)
        writer.writerow(["timestamp","tipo","categoria","acao","descricao","usuario_id","usuario_nome","usuario_tipo","regional_id","sub_regional_id","comum_id","status","ip","user_agent"]) 
        for r in rows:
            writer.writerow([
                r["timestamp"], r["tipo"], r["categoria"], r["acao"], r["descricao"],
                r["usuario_id"], r["usuario_nome"], r["usuario_tipo"],
                r["regional_id"], r["sub_regional_id"], r["comum_id"],
                r["status"], r["ip"], r["user_agent"]
            ])
        return si.getvalue()
