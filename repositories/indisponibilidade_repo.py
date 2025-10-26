"""
Repository para Indisponibilidades
Gerencia períodos em que organistas não podem tocar
"""

from typing import List, Dict, Optional
from datetime import datetime
from database import get_db_session
from sqlalchemy import text
import uuid


class IndisponibilidadeRepository:
    """Repository para gerenciar indisponibilidades"""
    
    def get_by_organista_mes(self, organista_id: str, mes: str) -> Optional[Dict]:
        """Buscar indisponibilidade de um organista em um mês específico"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT i.*, o.nome as organista_nome
                    FROM indisponibilidades i
                    JOIN organistas o ON i.organista_id = o.id
                    WHERE i.organista_id = :organista_id AND i.mes = :mes
                """),
                {"organista_id": organista_id, "mes": mes}
            )
            row = result.fetchone()
            return dict(row._mapping) if row else None
    
    def get_by_comum_mes(self, comum_id: str, mes: str) -> List[Dict]:
        """Buscar todas indisponibilidades de uma comum em um mês"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT i.*, o.nome as organista_nome
                    FROM indisponibilidades i
                    JOIN organistas o ON i.organista_id = o.id
                    WHERE o.comum_id = :comum_id AND i.mes = :mes
                    ORDER BY o.nome
                """),
                {"comum_id": comum_id, "mes": mes}
            )
            return [dict(row._mapping) for row in result]
    
    def get_by_organista(self, organista_id: str) -> List[Dict]:
        """Buscar todas indisponibilidades de um organista"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT * FROM indisponibilidades
                    WHERE organista_id = :organista_id
                    ORDER BY mes DESC
                """),
                {"organista_id": organista_id}
            )
            return [dict(row._mapping) for row in result]
    
    def create(self, data: Dict) -> Dict:
        """Criar nova indisponibilidade"""
        indisp_id = data.get('id') or str(uuid.uuid4())
        
        with get_db_session() as session:
            result = session.execute(
                text("""
                    INSERT INTO indisponibilidades (
                        id, organista_id, mes, motivo
                    ) VALUES (
                        :id, :organista_id, :mes, :motivo
                    )
                    RETURNING *
                """),
                {
                    "id": indisp_id,
                    "organista_id": data["organista_id"],
                    "mes": data["mes"],
                    "motivo": data.get("motivo")
                }
            )
            session.commit()
            return dict(result.fetchone()._mapping)
    
    def update(self, indisp_id: str, data: Dict) -> Optional[Dict]:
        """Atualizar indisponibilidade"""
        set_clauses = []
        params = {"id": indisp_id}
        
        if "mes" in data:
            set_clauses.append("mes = :mes")
            params["mes"] = data["mes"]
        if "motivo" in data:
            set_clauses.append("motivo = :motivo")
            params["motivo"] = data["motivo"]
        
        if not set_clauses:
            return None
        
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        set_clause = ", ".join(set_clauses)
        
        with get_db_session() as session:
            result = session.execute(
                text(f"""
                    UPDATE indisponibilidades 
                    SET {set_clause}
                    WHERE id = :id
                    RETURNING *
                """),
                params
            )
            session.commit()
            row = result.fetchone()
            return dict(row._mapping) if row else None
    
    def delete(self, indisp_id: str) -> bool:
        """Deletar indisponibilidade"""
        with get_db_session() as session:
            result = session.execute(
                text("DELETE FROM indisponibilidades WHERE id = :id RETURNING id"),
                {"id": indisp_id}
            )
            session.commit()
            return result.fetchone() is not None
    
    def delete_by_organista_mes(self, organista_id: str, mes: str) -> bool:
        """Deletar indisponibilidade específica de um organista em um mês"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    DELETE FROM indisponibilidades 
                    WHERE organista_id = :organista_id AND mes = :mes
                    RETURNING id
                """),
                {"organista_id": organista_id, "mes": mes}
            )
            session.commit()
            return result.fetchone() is not None
    
    def is_organista_disponivel(self, organista_id: str, mes: str) -> bool:
        """Verificar se organista está disponível em um mês"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT COUNT(*) as count 
                    FROM indisponibilidades
                    WHERE organista_id = :organista_id AND mes = :mes
                """),
                {"organista_id": organista_id, "mes": mes}
            )
            row = result.fetchone()
            return row[0] == 0 if row else True
    
    def get_organistas_disponiveis_mes(self, comum_id: str, mes: str) -> List[Dict]:
        """Buscar organistas disponíveis em um mês"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT o.*, ot.nome as tipo_nome
                    FROM organistas o
                    LEFT JOIN organista_tipos ot ON o.tipo_id = ot.id
                    WHERE o.comum_id = :comum_id 
                      AND o.ativo = true
                      AND NOT EXISTS (
                          SELECT 1 FROM indisponibilidades i
                          WHERE i.organista_id = o.id AND i.mes = :mes
                      )
                    ORDER BY o.nome
                """),
                {"comum_id": comum_id, "mes": mes}
            )
            return [dict(row._mapping) for row in result]
