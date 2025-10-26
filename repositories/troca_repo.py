"""
Repository para Trocas
Gerencia solicitações e aprovações de trocas de escala
"""

from typing import List, Dict, Optional
from datetime import datetime
from database import get_db_session
from sqlalchemy import text
import uuid


class TrocaRepository:
    """Repository para gerenciar trocas de escala"""
    
    def get_by_id(self, troca_id: str) -> Optional[Dict]:
        """Buscar troca por ID"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT t.*,
                           o1.nome as solicitante_nome,
                           o2.nome as destinatario_nome,
                           e.data as escala_data,
                           e.horario as escala_horario,
                           c.nome as comum_nome
                    FROM trocas t
                    JOIN organistas o1 ON t.solicitante_id = o1.id
                    LEFT JOIN organistas o2 ON t.destinatario_id = o2.id
                    JOIN escala e ON t.escala_id = e.id
                    JOIN comuns c ON e.comum_id = c.id
                    WHERE t.id = :id
                """),
                {"id": troca_id}
            )
            row = result.fetchone()
            return dict(row._mapping) if row else None
    
    def get_pendentes_by_comum(self, comum_id: str) -> List[Dict]:
        """Buscar trocas pendentes de uma comum"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT t.*,
                           o1.nome as solicitante_nome,
                           o2.nome as destinatario_nome,
                           e.data as escala_data,
                           e.horario as escala_horario
                    FROM trocas t
                    JOIN organistas o1 ON t.solicitante_id = o1.id
                    LEFT JOIN organistas o2 ON t.destinatario_id = o2.id
                    JOIN escala e ON t.escala_id = e.id
                    WHERE e.comum_id = :comum_id 
                      AND t.status = 'pendente'
                    ORDER BY t.created_at DESC
                """),
                {"comum_id": comum_id}
            )
            return [dict(row._mapping) for row in result]
    
    def get_by_organista(self, organista_id: str, status: str = None) -> List[Dict]:
        """Buscar trocas de um organista"""
        with get_db_session() as session:
            if status:
                result = session.execute(
                    text("""
                        SELECT t.*,
                               o1.nome as solicitante_nome,
                               o2.nome as destinatario_nome,
                               e.data as escala_data,
                               e.horario as escala_horario,
                               c.nome as comum_nome
                        FROM trocas t
                        JOIN organistas o1 ON t.solicitante_id = o1.id
                        LEFT JOIN organistas o2 ON t.destinatario_id = o2.id
                        JOIN escala e ON t.escala_id = e.id
                        JOIN comuns c ON e.comum_id = c.id
                        WHERE (t.solicitante_id = :organista_id 
                               OR t.destinatario_id = :organista_id)
                          AND t.status = :status
                        ORDER BY t.created_at DESC
                    """),
                    {"organista_id": organista_id, "status": status}
                )
            else:
                result = session.execute(
                    text("""
                        SELECT t.*,
                               o1.nome as solicitante_nome,
                               o2.nome as destinatario_nome,
                               e.data as escala_data,
                               e.horario as escala_horario,
                               c.nome as comum_nome
                        FROM trocas t
                        JOIN organistas o1 ON t.solicitante_id = o1.id
                        LEFT JOIN organistas o2 ON t.destinatario_id = o2.id
                        JOIN escala e ON t.escala_id = e.id
                        JOIN comuns c ON e.comum_id = c.id
                        WHERE t.solicitante_id = :organista_id 
                           OR t.destinatario_id = :organista_id
                        ORDER BY t.created_at DESC
                    """),
                    {"organista_id": organista_id}
                )
            
            return [dict(row._mapping) for row in result]
    
    def create(self, data: Dict) -> Dict:
        """Criar solicitação de troca"""
        troca_id = data.get('id') or str(uuid.uuid4())
        
        with get_db_session() as session:
            result = session.execute(
                text("""
                    INSERT INTO trocas (
                        id, escala_id, solicitante_id, destinatario_id, 
                        motivo, status
                    ) VALUES (
                        :id, :escala_id, :solicitante_id, :destinatario_id,
                        :motivo, 'pendente'
                    )
                    RETURNING *
                """),
                {
                    "id": troca_id,
                    "escala_id": data["escala_id"],
                    "solicitante_id": data["solicitante_id"],
                    "destinatario_id": data.get("destinatario_id"),
                    "motivo": data.get("motivo")
                }
            )
            session.commit()
            return dict(result.fetchone()._mapping)
    
    def aprovar(self, troca_id: str, aprovado_por: str, observacao: str = None) -> Optional[Dict]:
        """Aprovar troca"""
        with get_db_session() as session:
            # Atualizar status da troca
            result = session.execute(
                text("""
                    UPDATE trocas 
                    SET status = 'aprovada',
                        aprovado_por = :aprovado_por,
                        aprovado_em = CURRENT_TIMESTAMP,
                        observacao_aprovacao = :observacao,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id AND status = 'pendente'
                    RETURNING *
                """),
                {
                    "id": troca_id,
                    "aprovado_por": aprovado_por,
                    "observacao": observacao
                }
            )
            
            row = result.fetchone()
            if not row:
                return None
            
            troca = dict(row._mapping)
            
            # Adicionar ao histórico
            session.execute(
                text("""
                    INSERT INTO trocas_historico 
                    (troca_id, acao, realizado_por, observacao)
                    VALUES (:troca_id, 'aprovada', :realizado_por, :observacao)
                """),
                {
                    "troca_id": troca_id,
                    "realizado_por": aprovado_por,
                    "observacao": observacao
                }
            )
            
            session.commit()
            return troca
    
    def rejeitar(self, troca_id: str, rejeitado_por: str, motivo: str = None) -> Optional[Dict]:
        """Rejeitar troca"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    UPDATE trocas 
                    SET status = 'rejeitada',
                        aprovado_por = :rejeitado_por,
                        aprovado_em = CURRENT_TIMESTAMP,
                        observacao_aprovacao = :motivo,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id AND status = 'pendente'
                    RETURNING *
                """),
                {
                    "id": troca_id,
                    "rejeitado_por": rejeitado_por,
                    "motivo": motivo
                }
            )
            
            row = result.fetchone()
            if not row:
                return None
            
            troca = dict(row._mapping)
            
            # Adicionar ao histórico
            session.execute(
                text("""
                    INSERT INTO trocas_historico 
                    (troca_id, acao, realizado_por, observacao)
                    VALUES (:troca_id, 'rejeitada', :realizado_por, :observacao)
                """),
                {
                    "troca_id": troca_id,
                    "realizado_por": rejeitado_por,
                    "observacao": motivo
                }
            )
            
            session.commit()
            return troca
    
    def cancelar(self, troca_id: str, cancelado_por: str, motivo: str = None) -> Optional[Dict]:
        """Cancelar troca"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    UPDATE trocas 
                    SET status = 'cancelada',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id 
                      AND status IN ('pendente', 'aprovada')
                    RETURNING *
                """),
                {"id": troca_id}
            )
            
            row = result.fetchone()
            if not row:
                return None
            
            troca = dict(row._mapping)
            
            # Adicionar ao histórico
            session.execute(
                text("""
                    INSERT INTO trocas_historico 
                    (troca_id, acao, realizado_por, observacao)
                    VALUES (:troca_id, 'cancelada', :realizado_por, :observacao)
                """),
                {
                    "troca_id": troca_id,
                    "realizado_por": cancelado_por,
                    "observacao": motivo
                }
            )
            
            session.commit()
            return troca
    
    def get_historico(self, troca_id: str) -> List[Dict]:
        """Buscar histórico de ações de uma troca"""
        with get_db_session() as session:
            result = session.execute(
                text("""
                    SELECT * FROM trocas_historico
                    WHERE troca_id = :troca_id
                    ORDER BY created_at ASC
                """),
                {"troca_id": troca_id}
            )
            return [dict(row._mapping) for row in result]
    
    def get_estatisticas(self, comum_id: str = None, mes: str = None) -> Dict:
        """Obter estatísticas de trocas"""
        with get_db_session() as session:
            query = """
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN t.status = 'pendente' THEN 1 END) as pendentes,
                    COUNT(CASE WHEN t.status = 'aprovada' THEN 1 END) as aprovadas,
                    COUNT(CASE WHEN t.status = 'rejeitada' THEN 1 END) as rejeitadas,
                    COUNT(CASE WHEN t.status = 'cancelada' THEN 1 END) as canceladas
                FROM trocas t
                JOIN escala e ON t.escala_id = e.id
                WHERE 1=1
            """
            
            params = {}
            
            if comum_id:
                query += " AND e.comum_id = :comum_id"
                params["comum_id"] = comum_id
            
            if mes:
                query += " AND TO_CHAR(e.data, 'YYYY-MM') = :mes"
                params["mes"] = mes
            
            result = session.execute(text(query), params)
            row = result.fetchone()
            return dict(row._mapping) if row else {
                "total": 0, "pendentes": 0, "aprovadas": 0, 
                "rejeitadas": 0, "canceladas": 0
            }
