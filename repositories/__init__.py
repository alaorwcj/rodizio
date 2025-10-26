"""
Repositories - Camada de acesso a dados para PostgreSQL
"""

from .organista_repo import OrganistaRepository
from .escala_repo import EscalaRepository
from .indisponibilidade_repo import IndisponibilidadeRepository
from .comum_repo import ComumRepository
from .usuario_repo import UsuarioRepository
from .troca_repo import TrocaRepository
from .audit_repository import AuditRepository

__all__ = [
    'OrganistaRepository',
    'EscalaRepository', 
    'IndisponibilidadeRepository',
    'ComumRepository',
    'UsuarioRepository',
    'TrocaRepository',
    'AuditRepository'
]
