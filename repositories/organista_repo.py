"""
Repository para Organistas
Gerencia todas operações CRUD de organistas no PostgreSQL
"""

from typing import List, Dict, Optional
from datetime import datetime
from database import get_db_session
from sqlalchemy import text
import uuid


class OrganistaRepository:
    """Repository para gerenciar organistas"""
    
    def get_by_id(self, organista_id: str) -> Optional[Dict]:
        """Buscar organista por ID"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT o.*, ot.nome as tipo_nome,
                           c.nome as comum_nome,
                           sr.nome as sub_regional_nome,
                           r.nome as regional_nome
                    FROM organistas o
                    LEFT JOIN organista_tipos ot ON o.tipo_id = ot.id
                    LEFT JOIN comuns c ON o.comum_id = c.id
                    LEFT JOIN sub_regionais sr ON c.sub_regional_id = sr.id
                    LEFT JOIN regionais r ON sr.regional_id = r.id
                    WHERE o.id = :id AND o.ativo = true
                """),
                {"id": organista_id}
            )
            row = result.fetchone()
            return dict(row._mapping) if row else None
    
    def get_by_comum(self, comum_id: str) -> List[Dict]:
        """Buscar todos organistas de uma comum"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT o.*, ot.nome as tipo_nome
                    FROM organistas o
                    LEFT JOIN organista_tipos ot ON o.tipo_id = ot.id
                    WHERE o.comum_id = :comum_id AND o.ativo = true
                    ORDER BY o.nome
                """),
                {"comum_id": comum_id}
            )
            return [dict(row._mapping) for row in result]
    
    def get_all_by_regional(self, regional_id: str) -> List[Dict]:
        """Buscar todos organistas de uma regional"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT o.*, ot.nome as tipo_nome,
                           c.nome as comum_nome,
                           sr.nome as sub_regional_nome
                    FROM organistas o
                    LEFT JOIN organista_tipos ot ON o.tipo_id = ot.id
                    JOIN comuns c ON o.comum_id = c.id
                    JOIN sub_regionais sr ON c.sub_regional_id = sr.id
                    WHERE sr.regional_id = :regional_id AND o.ativo = true
                    ORDER BY sr.nome, c.nome, o.nome
                """),
                {"regional_id": regional_id}
            )
            return [dict(row._mapping) for row in result]
    
    def get_all_by_sub_regional(self, sub_regional_id: str) -> List[Dict]:
        """Buscar todos organistas de uma sub-regional"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT o.*, ot.nome as tipo_nome,
                           c.nome as comum_nome
                    FROM organistas o
                    LEFT JOIN organista_tipos ot ON o.tipo_id = ot.id
                    JOIN comuns c ON o.comum_id = c.id
                    WHERE c.sub_regional_id = :sub_regional_id AND o.ativo = true
                    ORDER BY c.nome, o.nome
                """),
                {"sub_regional_id": sub_regional_id}
            )
            return [dict(row._mapping) for row in result]
    
    def create(self, data: Dict) -> Dict:
        """Criar novo organista"""
        organista_id = data.get('id') or str(uuid.uuid4())
        
        with get_db_session() as session:
            result = session.execute(
                text("""
                    INSERT INTO organistas (
                        id, nome, telefone, email, comum_id, tipo_id, ativo
                    ) VALUES (
                        :id, :nome, :telefone, :email, :comum_id, :tipo_id, true
                    )
                    RETURNING *
                """),
                {
                    "id": organista_id,
                    "nome": data["nome"],
                    "telefone": data.get("telefone"),
                    "email": data.get("email"),
                    "comum_id": data["comum_id"],
                    "tipo_id": data.get("tipo_id", 1)  # 1 = Titular por padrão
                }
            )
            session.commit()
            return dict(result.fetchone()._mapping)
    
    def update(self, organista_id: str, data: Dict) -> Optional[Dict]:
        """Atualizar organista"""
        # Construir SET dinamicamente baseado nos campos presentes
        set_clauses = []
        params = {"id": organista_id}
        
        if "nome" in data:
            set_clauses.append("nome = :nome")
            params["nome"] = data["nome"]
        if "telefone" in data:
            set_clauses.append("telefone = :telefone")
            params["telefone"] = data["telefone"]
        if "email" in data:
            set_clauses.append("email = :email")
            params["email"] = data["email"]
        if "tipo_id" in data:
            set_clauses.append("tipo_id = :tipo_id")
            params["tipo_id"] = data["tipo_id"]
        if "comum_id" in data:
            set_clauses.append("comum_id = :comum_id")
            params["comum_id"] = data["comum_id"]
        
        if not set_clauses:
            return self.get_by_id(organista_id)
        
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        set_clause = ", ".join(set_clauses)
        
        with get_db_session() as session:
            result = session.execute(
                text(f"""
                    UPDATE organistas 
                    SET {set_clause}
                    WHERE id = :id AND ativo = true
                    RETURNING *
                """),
                params
            )
            session.commit()
            row = result.fetchone()
            return dict(row._mapping) if row else None
    
    def delete(self, organista_id: str) -> bool:
        """Deletar (desativar) organista"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    UPDATE organistas 
                    SET ativo = false, updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                    RETURNING id
                """),
                {"id": organista_id}
            )
            session.commit()
            return result.fetchone() is not None
    
    def get_tipos(self) -> List[Dict]:
        """Listar tipos de organistas disponíveis"""
        with get_db_session() as session:
            result = session.execute(
                text("SELECT * FROM organista_tipos ORDER BY id")
            )
            return [dict(row._mapping) for row in result]
    
    def get_dias_permitidos(self, organista_id: str) -> List[str]:
        """Buscar dias da semana permitidos para o organista"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT dia_semana 
                    FROM organista_dias_permitidos 
                    WHERE organista_id = :organista_id
                    ORDER BY 
                        CASE dia_semana
                            WHEN 'domingo' THEN 1
                            WHEN 'segunda' THEN 2
                            WHEN 'terca' THEN 3
                            WHEN 'quarta' THEN 4
                            WHEN 'quinta' THEN 5
                            WHEN 'sexta' THEN 6
                            WHEN 'sabado' THEN 7
                        END
                """),
                {"organista_id": organista_id}
            )
            return [row[0] for row in result]
    
    def set_dias_permitidos(self, organista_id: str, dias: List[str]) -> None:
        """Configurar dias da semana permitidos para o organista"""
        with get_db_session() as session:
            # Remover dias antigos
            session.execute(
                text("DELETE FROM organista_dias_permitidos WHERE organista_id = :organista_id"),
                {"organista_id": organista_id}
            )
            
            # Adicionar novos dias
            for dia in dias:
                session.execute(
                    text("""
                        INSERT INTO organista_dias_permitidos (organista_id, dia_semana)
                        VALUES (:organista_id, :dia_semana)
                    """),
                    {"organista_id": organista_id, "dia_semana": dia}
                )
            
            session.commit()
    
    def get_regras_especiais(self, organista_id: str) -> List[Dict]:
        """Buscar regras especiais do organista"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT * FROM organista_regras_especiais 
                    WHERE organista_id = :organista_id AND ativo = true
                    ORDER BY created_at DESC
                """),
                {"organista_id": organista_id}
            )
            return [dict(row._mapping) for row in result]
    
    def add_regra_especial(self, organista_id: str, tipo: str, valor: str, descricao: str = None) -> Dict:
        """Adicionar regra especial para organista"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    INSERT INTO organista_regras_especiais 
                    (organista_id, tipo, valor, descricao, ativo)
                    VALUES (:organista_id, :tipo, :valor, :descricao, true)
                    RETURNING *
                """),
                {
                    "organista_id": organista_id,
                    "tipo": tipo,
                    "valor": valor,
                    "descricao": descricao
                }
            )
            session.commit()
            return dict(result.fetchone()._mapping)
    
    def search(self, termo: str, comum_id: str = None) -> List[Dict]:
        """Buscar organistas por nome ou telefone"""
        search_term = f"%{termo}%"
        
        with get_db_session() as session:
            if comum_id:
                result = session.execute(
                    text("""
                        SELECT o.*, ot.nome as tipo_nome
                        FROM organistas o
                        LEFT JOIN organista_tipos ot ON o.tipo_id = ot.id
                        WHERE o.comum_id = :comum_id 
                          AND o.ativo = true
                          AND (o.nome ILIKE :termo OR o.telefone ILIKE :termo)
                        ORDER BY o.nome
                    """),
                    {"comum_id": comum_id, "termo": search_term}
                )
            else:
                result = session.execute(
                    text("""
                        SELECT o.*, ot.nome as tipo_nome,
                               c.nome as comum_nome,
                               sr.nome as sub_regional_nome,
                               r.nome as regional_nome
                        FROM organistas o
                        LEFT JOIN organista_tipos ot ON o.tipo_id = ot.id
                        JOIN comuns c ON o.comum_id = c.id
                        JOIN sub_regionais sr ON c.sub_regional_id = sr.id
                        JOIN regionais r ON sr.regional_id = r.id
                        WHERE o.ativo = true
                          AND (o.nome ILIKE :termo OR o.telefone ILIKE :termo)
                        ORDER BY r.nome, sr.nome, c.nome, o.nome
                    """),
                    {"termo": search_term}
                )
            
            return [dict(row._mapping) for row in result]
