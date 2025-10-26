"""
Repository para Comuns e Hierarquia
Gerencia regionais, sub-regionais e comuns
"""

from typing import List, Dict, Optional
from database import get_db_session
from sqlalchemy import text
import uuid


class ComumRepository:
    """Repository para gerenciar hierarquia de regionais/sub-regionais/comuns"""
    
    # ========== REGIONAIS ==========
    
    def get_all_regionais(self) -> List[Dict]:
        """Listar todas regionais"""
        with get_db_session() as session:
            result = session.execute(
                text("SELECT * FROM regionais ORDER BY nome")
            )
            return [dict(row._mapping) for row in result]
    
    def get_regional_by_id(self, regional_id: str) -> Optional[Dict]:
        """Buscar regional por ID"""
        with get_db_session() as session:
            result = session.execute(
                text("SELECT * FROM regionais WHERE id = :id"),
                {"id": regional_id}
            )
            row = result.fetchone()
            return dict(row._mapping) if row else None
    
    def create_regional(self, nome: str, regional_id: str = None) -> Dict:
        """Criar nova regional"""
        regional_id = regional_id or str(uuid.uuid4())
        
        with get_db_session() as session:
            result = session.execute(
                text("""
                    INSERT INTO regionais (id, nome)
                    VALUES (:id, :nome)
                    RETURNING *
                """),
                {"id": regional_id, "nome": nome}
            )
            session.commit()
            return dict(result.fetchone()._mapping)
    
    def update_regional(self, regional_id: str, nome: str) -> Optional[Dict]:
        """Atualizar regional"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    UPDATE regionais 
                    SET nome = :nome, updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                    RETURNING *
                """),
                {"id": regional_id, "nome": nome}
            )
            session.commit()
            row = result.fetchone()
            return dict(row._mapping) if row else None
    
    # ========== SUB-REGIONAIS ==========
    
    def get_sub_regionais_by_regional(self, regional_id: str) -> List[Dict]:
        """Listar sub-regionais de uma regional"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT sr.*, r.nome as regional_nome
                    FROM sub_regionais sr
                    JOIN regionais r ON sr.regional_id = r.id
                    WHERE sr.regional_id = :regional_id
                    ORDER BY sr.nome
                """),
                {"regional_id": regional_id}
            )
            return [dict(row._mapping) for row in result]
    
    def get_sub_regional_by_id(self, sub_regional_id: str) -> Optional[Dict]:
        """Buscar sub-regional por ID"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT sr.*, r.nome as regional_nome, r.id as regional_id
                    FROM sub_regionais sr
                    JOIN regionais r ON sr.regional_id = r.id
                    WHERE sr.id = :id
                """),
                {"id": sub_regional_id}
            )
            row = result.fetchone()
            return dict(row._mapping) if row else None
    
    def create_sub_regional(self, regional_id: str, nome: str, sub_regional_id: str = None) -> Dict:
        """Criar nova sub-regional"""
        sub_regional_id = sub_regional_id or str(uuid.uuid4())
        
        with get_db_session() as session:
            result = session.execute(
                text("""
                    INSERT INTO sub_regionais (id, regional_id, nome)
                    VALUES (:id, :regional_id, :nome)
                    RETURNING *
                """),
                {"id": sub_regional_id, "regional_id": regional_id, "nome": nome}
            )
            session.commit()
            return dict(result.fetchone()._mapping)
    
    def update_sub_regional(self, sub_regional_id: str, nome: str) -> Optional[Dict]:
        """Atualizar sub-regional"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    UPDATE sub_regionais 
                    SET nome = :nome, updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                    RETURNING *
                """),
                {"id": sub_regional_id, "nome": nome}
            )
            session.commit()
            row = result.fetchone()
            return dict(row._mapping) if row else None
    
    # ========== COMUNS ==========
    
    def get_comuns_by_sub_regional(self, sub_regional_id: str) -> List[Dict]:
        """Listar comuns de uma sub-regional"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT c.*, 
                           sr.nome as sub_regional_nome,
                           sr.regional_id,
                           r.nome as regional_nome
                    FROM comuns c
                    JOIN sub_regionais sr ON c.sub_regional_id = sr.id
                    JOIN regionais r ON sr.regional_id = r.id
                    WHERE c.sub_regional_id = :sub_regional_id
                    ORDER BY c.nome
                """),
                {"sub_regional_id": sub_regional_id}
            )
            return [dict(row._mapping) for row in result]
    
    def get_comum_by_id(self, comum_id: str) -> Optional[Dict]:
        """Buscar comum por ID com hierarquia completa"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT c.*,
                           sr.nome as sub_regional_nome,
                           sr.id as sub_regional_id,
                           r.nome as regional_nome,
                           r.id as regional_id
                    FROM comuns c
                    JOIN sub_regionais sr ON c.sub_regional_id = sr.id
                    JOIN regionais r ON sr.regional_id = r.id
                    WHERE c.id = :id
                """),
                {"id": comum_id}
            )
            row = result.fetchone()
            return dict(row._mapping) if row else None
    
    def get_all_comuns_by_regional(self, regional_id: str) -> List[Dict]:
        """Listar todas comuns de uma regional"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT c.*,
                           sr.nome as sub_regional_nome,
                           sr.id as sub_regional_id
                    FROM comuns c
                    JOIN sub_regionais sr ON c.sub_regional_id = sr.id
                    WHERE sr.regional_id = :regional_id
                    ORDER BY sr.nome, c.nome
                """),
                {"regional_id": regional_id}
            )
            return [dict(row._mapping) for row in result]
    
    def create_comum(self, sub_regional_id: str, nome: str, comum_id: str = None) -> Dict:
        """Criar nova comum"""
        comum_id = comum_id or str(uuid.uuid4())
        
        with get_db_session() as session:
            result = session.execute(
                text("""
                    INSERT INTO comuns (id, sub_regional_id, nome)
                    VALUES (:id, :sub_regional_id, :nome)
                    RETURNING *
                """),
                {"id": comum_id, "sub_regional_id": sub_regional_id, "nome": nome}
            )
            session.commit()
            return dict(result.fetchone()._mapping)
    
    def update_comum(self, comum_id: str, nome: str) -> Optional[Dict]:
        """Atualizar comum"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    UPDATE comuns 
                    SET nome = :nome, updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                    RETURNING *
                """),
                {"id": comum_id, "nome": nome}
            )
            session.commit()
            row = result.fetchone()
            return dict(row._mapping) if row else None
    
    # ========== CONFIGURAÇÕES DE COMUM ==========
    
    def get_config(self, comum_id: str) -> Optional[Dict]:
        """Buscar configurações de uma comum"""
        with get_db_session() as session:
            result = session.execute(
                text("SELECT * FROM comum_config WHERE comum_id = :comum_id"),
                {"comum_id": comum_id}
            )
            row = result.fetchone()
            return dict(row._mapping) if row else None
    
    def update_config(self, comum_id: str, config: Dict) -> Dict:
        """Atualizar configurações de uma comum"""
        with get_db_session() as session:
            # Verificar se já existe
            existing = session.execute(
                text("SELECT id FROM comum_config WHERE comum_id = :comum_id"),
                {"comum_id": comum_id}
            ).fetchone()
            
            if existing:
                # Atualizar
                set_clauses = []
                params = {"comum_id": comum_id}
                
                if "bimestre_inicio" in config:
                    set_clauses.append("bimestre_inicio = :bimestre_inicio")
                    params["bimestre_inicio"] = config["bimestre_inicio"]
                if "bimestre_fim" in config:
                    set_clauses.append("bimestre_fim = :bimestre_fim")
                    params["bimestre_fim"] = config["bimestre_fim"]
                if "fechamento_dias" in config:
                    set_clauses.append("fechamento_dias = :fechamento_dias")
                    params["fechamento_dias"] = config["fechamento_dias"]
                
                set_clauses.append("updated_at = CURRENT_TIMESTAMP")
                set_clause = ", ".join(set_clauses)
                
                result = session.execute(
                    text(f"""
                        UPDATE comum_config 
                        SET {set_clause}
                        WHERE comum_id = :comum_id
                        RETURNING *
                    """),
                    params
                )
            else:
                # Criar
                result = session.execute(
                    text("""
                        INSERT INTO comum_config 
                        (comum_id, bimestre_inicio, bimestre_fim, fechamento_dias)
                        VALUES (:comum_id, :bimestre_inicio, :bimestre_fim, :fechamento_dias)
                        RETURNING *
                    """),
                    {
                        "comum_id": comum_id,
                        "bimestre_inicio": config.get("bimestre_inicio"),
                        "bimestre_fim": config.get("bimestre_fim"),
                        "fechamento_dias": config.get("fechamento_dias", 3)
                    }
                )
            
            session.commit()
            return dict(result.fetchone()._mapping)
    
    # ========== HORÁRIOS ==========
    
    def get_horarios(self, comum_id: str) -> List[Dict]:
        """Buscar horários configurados de uma comum"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT * FROM comum_horarios
                    WHERE comum_id = :comum_id AND ativo = true
                    ORDER BY dia_semana, horario
                """),
                {"comum_id": comum_id}
            )
            return [dict(row._mapping) for row in result]
    
    def add_horario(self, comum_id: str, dia_semana: str, horario: str) -> Dict:
        """Adicionar horário para uma comum"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    INSERT INTO comum_horarios (comum_id, dia_semana, horario, ativo)
                    VALUES (:comum_id, :dia_semana, :horario, true)
                    RETURNING *
                """),
                {
                    "comum_id": comum_id,
                    "dia_semana": dia_semana,
                    "horario": horario
                }
            )
            session.commit()
            return dict(result.fetchone()._mapping)
    
    def remove_horario(self, horario_id: int) -> bool:
        """Remover horário"""
        with get_db_session() as session:
            result = session.execute(
                text("DELETE FROM comum_horarios WHERE id = :id RETURNING id"),
                {"id": horario_id}
            )
            session.commit()
            return result.fetchone() is not None
    
    def update_horarios(self, comum_id: str, horarios: List[Dict]) -> List[Dict]:
        """Atualizar todos horários de uma comum"""
        with get_db_session() as session:
            # Remover horários antigos
            session.execute(
                text("DELETE FROM comum_horarios WHERE comum_id = :comum_id"),
                {"comum_id": comum_id}
            )
            
            # Adicionar novos
            created = []
            for h in horarios:
                result = session.execute(
                    text("""
                        INSERT INTO comum_horarios (comum_id, dia_semana, horario, ativo)
                        VALUES (:comum_id, :dia_semana, :horario, true)
                        RETURNING *
                    """),
                    {
                        "comum_id": comum_id,
                        "dia_semana": h["dia_semana"],
                        "horario": h["horario"]
                    }
                )
                created.append(dict(result.fetchone()._mapping))
            
            session.commit()
            return created
