"""
Repository para Escalas
Gerencia criação, consulta e gestão de escalas e RJM
"""

from typing import List, Dict, Optional
from datetime import datetime, date
from database import get_db_session
from sqlalchemy import text
import uuid


class EscalaRepository:
    """Repository para gerenciar escalas"""
    
    def get_by_id(self, escala_id: str) -> Optional[Dict]:
        """Buscar escala por ID"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT e.*, 
                           o.nome as organista_nome,
                           c.nome as comum_nome,
                           sr.nome as sub_regional_nome,
                           r.nome as regional_nome
                    FROM escala e
                    LEFT JOIN organistas o ON e.organista_id = o.id
                    JOIN comuns c ON e.comum_id = c.id
                    JOIN sub_regionais sr ON c.sub_regional_id = sr.id
                    JOIN regionais r ON sr.regional_id = r.id
                    WHERE e.id = :id
                """),
                {"id": escala_id}
            )
            row = result.fetchone()
            return dict(row._mapping) if row else None
    
    def get_by_comum_mes(self, comum_id: str, mes: str) -> List[Dict]:
        """
        Buscar escalas de uma comum em um mês específico
        mes no formato: YYYY-MM
        """
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT e.*, o.nome as organista_nome
                    FROM escala e
                    LEFT JOIN organistas o ON e.organista_id = o.id
                    WHERE e.comum_id = :comum_id 
                      AND TO_CHAR(e.data, 'YYYY-MM') = :mes
                    ORDER BY e.data, e.horario
                """),
                {"comum_id": comum_id, "mes": mes}
            )
            return [dict(row._mapping) for row in result]
    
    def get_by_comum_periodo(self, comum_id: str, data_inicio: str, data_fim: str) -> List[Dict]:
        """Buscar escalas de uma comum em um período"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT e.*, o.nome as organista_nome
                    FROM escala e
                    LEFT JOIN organistas o ON e.organista_id = o.id
                    WHERE e.comum_id = :comum_id 
                      AND e.data BETWEEN :data_inicio AND :data_fim
                    ORDER BY e.data, e.horario
                """),
                {
                    "comum_id": comum_id,
                    "data_inicio": data_inicio,
                    "data_fim": data_fim
                }
            )
            return [dict(row._mapping) for row in result]
    
    def get_by_organista_mes(self, organista_id: str, mes: str) -> List[Dict]:
        """Buscar escalas de um organista em um mês"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT e.*, c.nome as comum_nome
                    FROM escala e
                    JOIN comuns c ON e.comum_id = c.id
                    WHERE e.organista_id = :organista_id 
                      AND TO_CHAR(e.data, 'YYYY-MM') = :mes
                    ORDER BY e.data, e.horario
                """),
                {"organista_id": organista_id, "mes": mes}
            )
            return [dict(row._mapping) for row in result]
    
    def create(self, data: Dict) -> Dict:
        """Criar nova escala"""
        escala_id = data.get('id') or str(uuid.uuid4())
        
        with get_db_session() as session:
            result = session.execute(
                text("""
                    INSERT INTO escala (
                        id, comum_id, data, horario, organista_id, tipo, observacao
                    ) VALUES (
                        :id, :comum_id, :data, :horario, :organista_id, :tipo, :observacao
                    )
                    RETURNING *
                """),
                {
                    "id": escala_id,
                    "comum_id": data["comum_id"],
                    "data": data["data"],
                    "horario": data.get("horario"),
                    "organista_id": data.get("organista_id"),
                    "tipo": data.get("tipo", "normal"),
                    "observacao": data.get("observacao")
                }
            )
            session.commit()
            return dict(result.fetchone()._mapping)
    
    def create_batch(self, escalas: List[Dict]) -> List[Dict]:
        """Criar múltiplas escalas de uma vez"""
        created = []
        
        with get_db_session() as session:
            for data in escalas:
                escala_id = data.get('id') or str(uuid.uuid4())
                
                result = session.execute(
                    text("""
                        INSERT INTO escala (
                            id, comum_id, data, horario, organista_id, tipo, observacao
                        ) VALUES (
                            :id, :comum_id, :data, :horario, :organista_id, :tipo, :observacao
                        )
                        RETURNING *
                    """),
                    {
                        "id": escala_id,
                        "comum_id": data["comum_id"],
                        "data": data["data"],
                        "horario": data.get("horario"),
                        "organista_id": data.get("organista_id"),
                        "tipo": data.get("tipo", "normal"),
                        "observacao": data.get("observacao")
                    }
                )
                created.append(dict(result.fetchone()._mapping))
            
            session.commit()
        
        return created
    
    def update(self, escala_id: str, data: Dict) -> Optional[Dict]:
        """Atualizar escala"""
        set_clauses = []
        params = {"id": escala_id}
        
        if "organista_id" in data:
            set_clauses.append("organista_id = :organista_id")
            params["organista_id"] = data["organista_id"]
        if "data" in data:
            set_clauses.append("data = :data")
            params["data"] = data["data"]
        if "horario" in data:
            set_clauses.append("horario = :horario")
            params["horario"] = data["horario"]
        if "tipo" in data:
            set_clauses.append("tipo = :tipo")
            params["tipo"] = data["tipo"]
        if "observacao" in data:
            set_clauses.append("observacao = :observacao")
            params["observacao"] = data["observacao"]
        
        if not set_clauses:
            return self.get_by_id(escala_id)
        
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        set_clause = ", ".join(set_clauses)
        
        with get_db_session() as session:
            result = session.execute(
                text(f"""
                    UPDATE escala 
                    SET {set_clause}
                    WHERE id = :id
                    RETURNING *
                """),
                params
            )
            session.commit()
            row = result.fetchone()
            return dict(row._mapping) if row else None
    
    def delete(self, escala_id: str) -> bool:
        """Deletar escala"""
        with get_db_session() as session:
            result = session.execute(
                text("DELETE FROM escala WHERE id = :id RETURNING id"),
                {"id": escala_id}
            )
            session.commit()
            return result.fetchone() is not None
    
    def delete_by_comum_mes(self, comum_id: str, mes: str) -> int:
        """Deletar todas escalas de uma comum em um mês"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    DELETE FROM escala 
                    WHERE comum_id = :comum_id 
                      AND TO_CHAR(data, 'YYYY-MM') = :mes
                    RETURNING id
                """),
                {"comum_id": comum_id, "mes": mes}
            )
            session.commit()
            return len(result.fetchall())
    
    # ========== RJM (Reunião de Jovens e Menores) ==========
    
    def get_rjm_by_comum_mes(self, comum_id: str, mes: str) -> List[Dict]:
        """Buscar escalas RJM de uma comum em um mês"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT r.*, o.nome as organista_nome
                    FROM escala_rjm r
                    LEFT JOIN organistas o ON r.organista_id = o.id
                    WHERE r.comum_id = :comum_id 
                      AND TO_CHAR(r.data, 'YYYY-MM') = :mes
                    ORDER BY r.data, r.horario
                """),
                {"comum_id": comum_id, "mes": mes}
            )
            return [dict(row._mapping) for row in result]
    
    def create_rjm(self, data: Dict) -> Dict:
        """Criar escala RJM"""
        rjm_id = data.get('id') or str(uuid.uuid4())
        
        with get_db_session() as session:
            result = session.execute(
                text("""
                    INSERT INTO escala_rjm (
                        id, comum_id, data, horario, organista_id, observacao
                    ) VALUES (
                        :id, :comum_id, :data, :horario, :organista_id, :observacao
                    )
                    RETURNING *
                """),
                {
                    "id": rjm_id,
                    "comum_id": data["comum_id"],
                    "data": data["data"],
                    "horario": data.get("horario"),
                    "organista_id": data.get("organista_id"),
                    "observacao": data.get("observacao")
                }
            )
            session.commit()
            return dict(result.fetchone()._mapping)
    
    def update_rjm(self, rjm_id: str, data: Dict) -> Optional[Dict]:
        """Atualizar escala RJM"""
        set_clauses = []
        params = {"id": rjm_id}
        
        if "organista_id" in data:
            set_clauses.append("organista_id = :organista_id")
            params["organista_id"] = data["organista_id"]
        if "data" in data:
            set_clauses.append("data = :data")
            params["data"] = data["data"]
        if "horario" in data:
            set_clauses.append("horario = :horario")
            params["horario"] = data["horario"]
        if "observacao" in data:
            set_clauses.append("observacao = :observacao")
            params["observacao"] = data["observacao"]
        
        if not set_clauses:
            return None
        
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        set_clause = ", ".join(set_clauses)
        
        with get_db_session() as session:
            result = session.execute(
                text(f"""
                    UPDATE escala_rjm 
                    SET {set_clause}
                    WHERE id = :id
                    RETURNING *
                """),
                params
            )
            session.commit()
            row = result.fetchone()
            return dict(row._mapping) if row else None
    
    def delete_rjm(self, rjm_id: str) -> bool:
        """Deletar escala RJM"""
        with get_db_session() as session:
            result = session.execute(
                text("DELETE FROM escala_rjm WHERE id = :id RETURNING id"),
                {"id": rjm_id}
            )
            session.commit()
            return result.fetchone() is not None
    
    # ========== Publicação ==========
    
    def get_publicacao(self, comum_id: str, mes: str) -> Optional[Dict]:
        """Buscar informação de publicação de escala"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT * FROM escala_publicacao
                    WHERE comum_id = :comum_id AND mes = :mes
                """),
                {"comum_id": comum_id, "mes": mes}
            )
            row = result.fetchone()
            return dict(row._mapping) if row else None
    
    def publicar(self, comum_id: str, mes: str, publicado_por: str) -> Dict:
        """Marcar escala como publicada"""
        with get_db_session() as session:
            # Verificar se já existe
            existing = session.execute(
                text("""
                    SELECT id FROM escala_publicacao
                    WHERE comum_id = :comum_id AND mes = :mes
                """),
                {"comum_id": comum_id, "mes": mes}
            ).fetchone()
            
            if existing:
                # Atualizar
                result = session.execute(
                    text("""
                        UPDATE escala_publicacao
                        SET publicado = true,
                            data_publicacao = CURRENT_TIMESTAMP,
                            publicado_por = :publicado_por,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE comum_id = :comum_id AND mes = :mes
                        RETURNING *
                    """),
                    {
                        "comum_id": comum_id,
                        "mes": mes,
                        "publicado_por": publicado_por
                    }
                )
            else:
                # Criar
                result = session.execute(
                    text("""
                        INSERT INTO escala_publicacao 
                        (comum_id, mes, publicado, data_publicacao, publicado_por)
                        VALUES (:comum_id, :mes, true, CURRENT_TIMESTAMP, :publicado_por)
                        RETURNING *
                    """),
                    {
                        "comum_id": comum_id,
                        "mes": mes,
                        "publicado_por": publicado_por
                    }
                )
            
            session.commit()
            return dict(result.fetchone()._mapping)
    
    def despublicar(self, comum_id: str, mes: str) -> bool:
        """Remover publicação de escala"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    UPDATE escala_publicacao
                    SET publicado = false,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE comum_id = :comum_id AND mes = :mes
                    RETURNING id
                """),
                {"comum_id": comum_id, "mes": mes}
            )
            session.commit()
            return result.fetchone() is not None
    
    # ========== Estatísticas ==========
    
    def get_estatisticas_organista(self, organista_id: str, mes: str = None) -> Dict:
        """Contar quantas escalas um organista tem"""
        with get_db_session() as session:
            if mes:
                result = session.execute(
                    text("""
                        SELECT COUNT(*) as total,
                               COUNT(CASE WHEN tipo = 'normal' THEN 1 END) as normais,
                               COUNT(CASE WHEN tipo = 'especial' THEN 1 END) as especiais
                        FROM escala
                        WHERE organista_id = :organista_id 
                          AND TO_CHAR(data, 'YYYY-MM') = :mes
                    """),
                    {"organista_id": organista_id, "mes": mes}
                )
            else:
                result = session.execute(
                    text("""
                        SELECT COUNT(*) as total,
                               COUNT(CASE WHEN tipo = 'normal' THEN 1 END) as normais,
                               COUNT(CASE WHEN tipo = 'especial' THEN 1 END) as especiais
                        FROM escala
                        WHERE organista_id = :organista_id
                    """),
                    {"organista_id": organista_id}
                )
            
            row = result.fetchone()
            return dict(row._mapping) if row else {"total": 0, "normais": 0, "especiais": 0}
    
    def get_organistas_disponiveis(self, comum_id: str, data: str, horario: str = None) -> List[Dict]:
        """
        Buscar organistas disponíveis para uma data/horário
        Considera: indisponibilidades, escalas já existentes, dias permitidos
        """
        dia_semana_map = {
            0: 'segunda', 1: 'terca', 2: 'quarta', 3: 'quinta',
            4: 'sexta', 5: 'sabado', 6: 'domingo'
        }
        
        # Descobrir dia da semana
        data_obj = datetime.fromisoformat(data)
        dia_semana = dia_semana_map[data_obj.weekday()]
        
        with get_db_session() as session:
            query = """
                SELECT DISTINCT o.*, ot.nome as tipo_nome
                FROM organistas o
                LEFT JOIN organista_tipos ot ON o.tipo_id = ot.id
                WHERE o.comum_id = :comum_id 
                  AND o.ativo = true
                  -- Não está em outra escala na mesma data/horário
                  AND NOT EXISTS (
                      SELECT 1 FROM escala e
                      WHERE e.organista_id = o.id
                        AND e.data = :data
            """
            
            params = {
                "comum_id": comum_id,
                "data": data,
                "mes": data[:7]  # YYYY-MM
            }
            
            if horario:
                query += " AND e.horario = :horario"
                params["horario"] = horario
            
            query += """
                  )
                  -- Não está indisponível neste mês
                  AND NOT EXISTS (
                      SELECT 1 FROM indisponibilidades i
                      WHERE i.organista_id = o.id
                        AND i.mes = :mes
                  )
                  -- Tem permissão para tocar neste dia da semana
                  AND (
                      NOT EXISTS (SELECT 1 FROM organista_dias_permitidos WHERE organista_id = o.id)
                      OR EXISTS (
                          SELECT 1 FROM organista_dias_permitidos odp
                          WHERE odp.organista_id = o.id
                            AND odp.dia_semana = :dia_semana
                      )
                  )
                ORDER BY o.nome
            """
            
            params["dia_semana"] = dia_semana
            
            result = session.execute(text(query), params)
            return [dict(row._mapping) for row in result]
