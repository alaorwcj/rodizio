"""
Repository para Usuários
Gerencia autenticação e permissões
"""

from typing import List, Dict, Optional
from database import get_db_session
from sqlalchemy import text
import uuid


class UsuarioRepository:
    """Repository para gerenciar usuários"""
    
    def get_by_id(self, usuario_id: str) -> Optional[Dict]:
        """Buscar usuário por ID"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT u.*,
                           CASE 
                               WHEN u.nivel = 'regional' THEN r.nome
                               WHEN u.nivel = 'sub_regional' THEN sr.nome
                               WHEN u.nivel = 'comum' THEN c.nome
                               ELSE NULL
                           END as contexto_nome
                    FROM usuarios u
                    LEFT JOIN regionais r ON u.nivel = 'regional' AND u.contexto_id = r.id
                    LEFT JOIN sub_regionais sr ON u.nivel = 'sub_regional' AND u.contexto_id = sr.id
                    LEFT JOIN comuns c ON u.nivel = 'comum' AND u.contexto_id = c.id
                    WHERE u.id = :id AND u.ativo = true
                """),
                {"id": usuario_id}
            )
            row = result.fetchone()
            return dict(row._mapping) if row else None
    
    def get_by_username(self, username: str) -> Optional[Dict]:
        """Buscar usuário por username (para login)"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT u.*,
                           CASE 
                               WHEN u.nivel = 'regional' THEN r.nome
                               WHEN u.nivel = 'sub_regional' THEN sr.nome
                               WHEN u.nivel = 'comum' THEN c.nome
                               ELSE NULL
                           END as contexto_nome
                    FROM usuarios u
                    LEFT JOIN regionais r ON u.nivel = 'regional' AND u.contexto_id = r.id
                    LEFT JOIN sub_regionais sr ON u.nivel = 'sub_regional' AND u.contexto_id = sr.id
                    LEFT JOIN comuns c ON u.nivel = 'comum' AND u.contexto_id = c.id
                    WHERE u.username = :username AND u.ativo = true
                """),
                {"username": username}
            )
            row = result.fetchone()
            return dict(row._mapping) if row else None
    
    def get_all(self, nivel: str = None) -> List[Dict]:
        """Listar todos usuários, opcionalmente filtrados por nível"""
        with get_db_session() as session:
            if nivel:
                result = session.execute(
                    text("""
                        SELECT u.*,
                               CASE 
                                   WHEN u.nivel = 'regional' THEN r.nome
                                   WHEN u.nivel = 'sub_regional' THEN sr.nome
                                   WHEN u.nivel = 'comum' THEN c.nome
                                   ELSE NULL
                               END as contexto_nome
                        FROM usuarios u
                        LEFT JOIN regionais r ON u.nivel = 'regional' AND u.contexto_id = r.id
                        LEFT JOIN sub_regionais sr ON u.nivel = 'sub_regional' AND u.contexto_id = sr.id
                        LEFT JOIN comuns c ON u.nivel = 'comum' AND u.contexto_id = c.id
                        WHERE u.ativo = true AND u.nivel = :nivel
                        ORDER BY u.nome
                    """),
                    {"nivel": nivel}
                )
            else:
                result = session.execute(
                    text("""
                        SELECT u.*,
                               CASE 
                                   WHEN u.nivel = 'regional' THEN r.nome
                                   WHEN u.nivel = 'sub_regional' THEN sr.nome
                                   WHEN u.nivel = 'comum' THEN c.nome
                                   ELSE NULL
                               END as contexto_nome
                        FROM usuarios u
                        LEFT JOIN regionais r ON u.nivel = 'regional' AND u.contexto_id = r.id
                        LEFT JOIN sub_regionais sr ON u.nivel = 'sub_regional' AND u.contexto_id = sr.id
                        LEFT JOIN comuns c ON u.nivel = 'comum' AND u.contexto_id = c.id
                        WHERE u.ativo = true
                        ORDER BY u.nivel, u.nome
                    """)
                )
            
            return [dict(row._mapping) for row in result]
    
    def create(self, data: Dict) -> Dict:
        """Criar novo usuário"""
        usuario_id = data.get('id') or str(uuid.uuid4())
        
        with get_db_session() as session:
            result = session.execute(
                text("""
                    INSERT INTO usuarios (
                        id, username, password_hash, nome, tipo, nivel, contexto_id, ativo
                    ) VALUES (
                        :id, :username, :password_hash, :nome, :tipo, :nivel, :contexto_id, true
                    )
                    RETURNING *
                """),
                {
                    "id": usuario_id,
                    "username": data["username"],
                    "password_hash": data["password_hash"],
                    "nome": data["nome"],
                    "tipo": data.get("tipo", "organista"),
                    "nivel": data.get("nivel", "comum"),
                    "contexto_id": data.get("contexto_id")
                }
            )
            session.commit()
            return dict(result.fetchone()._mapping)
    
    def update(self, usuario_id: str, data: Dict) -> Optional[Dict]:
        """Atualizar usuário"""
        set_clauses = []
        params = {"id": usuario_id}
        
        if "username" in data:
            set_clauses.append("username = :username")
            params["username"] = data["username"]
        if "nome" in data:
            set_clauses.append("nome = :nome")
            params["nome"] = data["nome"]
        if "tipo" in data:
            set_clauses.append("tipo = :tipo")
            params["tipo"] = data["tipo"]
        if "nivel" in data:
            set_clauses.append("nivel = :nivel")
            params["nivel"] = data["nivel"]
        if "contexto_id" in data:
            set_clauses.append("contexto_id = :contexto_id")
            params["contexto_id"] = data["contexto_id"]
        
        if not set_clauses:
            return self.get_by_id(usuario_id)
        
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        set_clause = ", ".join(set_clauses)
        
        with get_db_session() as session:
            result = session.execute(
                text(f"""
                    UPDATE usuarios 
                    SET {set_clause}
                    WHERE id = :id AND ativo = true
                    RETURNING *
                """),
                params
            )
            session.commit()
            row = result.fetchone()
            return dict(row._mapping) if row else None
    
    def update_password(self, usuario_id: str, password_hash: str) -> bool:
        """Atualizar senha do usuário"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    UPDATE usuarios 
                    SET password_hash = :password_hash,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id AND ativo = true
                    RETURNING id
                """),
                {"id": usuario_id, "password_hash": password_hash}
            )
            session.commit()
            return result.fetchone() is not None
    
    def delete(self, usuario_id: str) -> bool:
        """Deletar (desativar) usuário"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    UPDATE usuarios 
                    SET ativo = false, updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                    RETURNING id
                """),
                {"id": usuario_id}
            )
            session.commit()
            return result.fetchone() is not None
    
    def username_exists(self, username: str, exclude_id: str = None) -> bool:
        """Verificar se username já existe"""
        with get_db_session() as session:
            if exclude_id:
                result = session.execute(
                    text("""
                        SELECT COUNT(*) as count 
                        FROM usuarios
                        WHERE username = :username 
                          AND id != :exclude_id
                          AND ativo = true
                    """),
                    {"username": username, "exclude_id": exclude_id}
                )
            else:
                result = session.execute(
                    text("""
                        SELECT COUNT(*) as count 
                        FROM usuarios
                        WHERE username = :username AND ativo = true
                    """),
                    {"username": username}
                )
            
            row = result.fetchone()
            return row[0] > 0 if row else False
    
    def get_by_contexto(self, nivel: str, contexto_id: str) -> List[Dict]:
        """Buscar usuários de um contexto específico"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT * FROM usuarios
                    WHERE nivel = :nivel 
                      AND contexto_id = :contexto_id
                      AND ativo = true
                    ORDER BY nome
                """),
                {"nivel": nivel, "contexto_id": contexto_id}
            )
            return [dict(row._mapping) for row in result]
