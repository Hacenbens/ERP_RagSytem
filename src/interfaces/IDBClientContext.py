# interfaces/IDBClientContext.py

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from models.db_schemes.Project import ProjectCreate, ProjectModel, ProjectUpdate
from models.db_schemes.Chunk import ChunkCreate, ChunkModel

class IDBClientContext(ABC):
    """Interface pour tous les clients de base de données"""

    # ===== Cycle de vie =====
    @abstractmethod
    async def connect(self) -> None:
        """Établit la connexion à la base de données."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Ferme la connexion à la base de données."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Vérifie l'état de la connexion."""
        pass

    # ===== Projets =====
    @abstractmethod
    async def create_project(self, project_data: ProjectCreate) -> ProjectModel:
        """Crée un nouveau projet."""
        pass

    @abstractmethod
    async def get_project(self, project_id: str) -> Optional[ProjectModel]:
        """Récupère un projet par son ID."""
        pass

    @abstractmethod
    async def get_all_projects(self, skip: int = 0, limit: int = 100) -> List[ProjectModel]:
        """Récupère tous les projets avec pagination."""
        pass

    @abstractmethod
    async def update_project(self, project_id: str, update_data: ProjectUpdate) -> Optional[ProjectModel]:
        """Met à jour un projet existant."""
        pass

    @abstractmethod
    async def delete_project(self, project_id: str) -> bool:
        """Supprime un projet et toutes ses données associées."""
        pass

    # ===== Chunks =====
    @abstractmethod
    async def store_chunks(self, project_id: str, file_id: str,
                           chunks: List[str], metadata: Optional[Dict] = None) -> int:
        """
        Stocke une liste de chunks simples (strings) dans la base.
        Retourne le nombre de chunks insérés.
        """
        pass

    @abstractmethod
    async def get_project_chunks(self, project_id: str, skip: int = 0,
                                 limit: int = 100) -> List[Dict]:
        """Récupère les chunks d'un projet (sous forme de dictionnaires)."""
        pass

    @abstractmethod
    async def get_file_chunks(self, file_id: str) -> List[Dict]:
        """Récupère tous les chunks d'un fichier spécifique."""
        pass

    @abstractmethod
    async def delete_file_chunks(self, file_id: str) -> int:
        """Supprime tous les chunks associés à un fichier."""
        pass

    @abstractmethod
    async def search_chunks(self, project_id: str, query: str,
                            limit: int = 10) -> List[Dict]:
        """Recherche des chunks par texte dans un projet."""
        pass

    @abstractmethod
    async def create_chunk(self, chunk_data: ChunkCreate) -> ChunkModel:
        """Crée un chunk à partir d'un DTO Pydantic."""
        pass

    # ===== Fichiers =====
    @abstractmethod
    async def register_file(self, file_id: str, project_id: str,
                            filename: str, file_path: str,
                            file_size: int) -> str:
        """Enregistre un fichier dans la base."""
        pass

    @abstractmethod
    async def get_file(self, file_id: str) -> Optional[Dict]:
        """Récupère les métadonnées d'un fichier."""
        pass

    @abstractmethod
    async def update_file_status(self, file_id: str, processed: bool,
                                 chunk_count: Optional[int] = None) -> bool:
        """Met à jour le statut de traitement d'un fichier."""
        pass