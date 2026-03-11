from abc import ABC, abstractmethod
from typing import List, Optional
from models.db_schemes.Project import ProjectModel, ProjectCreate, ProjectUpdate

class IProjectRepository(ABC):
    """Interface pour le repository des projets"""
    
    @abstractmethod
    async def create(self, project: ProjectCreate) -> ProjectModel:
        """Créer un nouveau projet"""
        pass
    
    @abstractmethod
    async def get_by_id(self, project_id: str) -> Optional[ProjectModel]:
        """Récupérer un projet par son ID"""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ProjectModel]:
        """Récupérer tous les projets"""
        pass
    
    @abstractmethod
    async def update(self, project_id: str, update: ProjectUpdate) -> bool:
        """Mettre à jour un projet"""
        pass
    
    @abstractmethod
    async def delete(self, project_id: str) -> bool:
        """Supprimer un projet"""
        pass
    
    @abstractmethod
    async def increment_file_count(self, project_id: str) -> bool:
        """Incrémenter le compteur de fichiers"""
        pass
    
    @abstractmethod
    async def increment_chunk_count(self, project_id: str, count: int = 1) -> bool:
        """Incrémenter le compteur de chunks"""
        pass