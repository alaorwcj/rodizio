"""
Audit Repository - PostgreSQL
Gerencia logs de auditoria no PostgreSQL
"""

from typing import Optional, Dict, Any
from datetime import datetime
from .base_repository import BaseRepository
from database.models import AuditLog
from sqlalchemy import func


class AuditRepository(BaseRepository):
    """Repository para logs de auditoria"""
    
    def __init__(self):
        super().__init__()
    
    def log_action(
        self,
        acao: str,
        usuario_id: str,
        comum_id: Optional[str] = None,
        detalhes: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Registra uma ação de auditoria
        
        Args:
            acao: Nome da ação (ex: 'create_organista', 'update_escala')
            usuario_id: ID do usuário que executou a ação
            comum_id: ID da comum relacionada (opcional)
            detalhes: Detalhes adicionais em formato JSON (opcional)
        
        Returns:
            AuditLog: Log criado
        """
        log = AuditLog(
            acao=acao,
            usuario_id=usuario_id,
            comum_id=comum_id,
            detalhes=detalhes or {},
            timestamp=datetime.utcnow()
        )
        
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        
        return log
    
    def get_by_comum(
        self,
        comum_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> list[AuditLog]:
        """
        Busca logs de uma comum específica
        
        Args:
            comum_id: ID da comum
            limit: Quantidade máxima de registros
            offset: Posição inicial
        
        Returns:
            Lista de logs ordenados por timestamp DESC
        """
        return (
            self.session.query(AuditLog)
            .filter(AuditLog.comum_id == comum_id)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
    
    def get_by_usuario(
        self,
        usuario_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> list[AuditLog]:
        """
        Busca logs de um usuário específico
        
        Args:
            usuario_id: ID do usuário
            limit: Quantidade máxima de registros
            offset: Posição inicial
        
        Returns:
            Lista de logs ordenados por timestamp DESC
        """
        return (
            self.session.query(AuditLog)
            .filter(AuditLog.usuario_id == usuario_id)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
    
    def get_by_acao(
        self,
        acao: str,
        limit: int = 100,
        offset: int = 0
    ) -> list[AuditLog]:
        """
        Busca logs de uma ação específica
        
        Args:
            acao: Nome da ação
            limit: Quantidade máxima de registros
            offset: Posição inicial
        
        Returns:
            Lista de logs ordenados por timestamp DESC
        """
        return (
            self.session.query(AuditLog)
            .filter(AuditLog.acao == acao)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
    
    def get_recent(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> list[AuditLog]:
        """
        Busca logs mais recentes
        
        Args:
            limit: Quantidade máxima de registros
            offset: Posição inicial
        
        Returns:
            Lista de logs ordenados por timestamp DESC
        """
        return (
            self.session.query(AuditLog)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
    
    def count_by_acao(self, acao: str) -> int:
        """
        Conta quantas vezes uma ação foi executada
        
        Args:
            acao: Nome da ação
        
        Returns:
            Número de ocorrências
        """
        return (
            self.session.query(func.count(AuditLog.id))
            .filter(AuditLog.acao == acao)
            .scalar()
        )
    
    def count_by_usuario(self, usuario_id: str) -> int:
        """
        Conta quantas ações um usuário executou
        
        Args:
            usuario_id: ID do usuário
        
        Returns:
            Número de ações
        """
        return (
            self.session.query(func.count(AuditLog.id))
            .filter(AuditLog.usuario_id == usuario_id)
            .scalar()
        )
