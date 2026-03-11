from abc import ABC, abstractmethod
from typing import List, Optional, Any
from models.db_schemes.Chunk import ChunkModel, ChunkCreate

class IChunkRepository(ABC):
    """Interface pour le repository des chunks"""
    
    @abstractmethod
    async def create(self, chunk: ChunkCreate) -> ChunkModel:
        """Créer un chunk"""
        pass
    
    @abstractmethod
    async def create_many(self, chunks: List[ChunkCreate]) -> int:
        """Créer plusieurs chunks en une opération"""
        pass
    
    @abstractmethod
    async def get_by_id(self, chunk_id: str) -> Optional[ChunkModel]:
        """Récupérer un chunk par son ID MongoDB"""
        pass
    
    @abstractmethod
    async def get_by_file(self, file_id: str) -> List[ChunkModel]:
        """Récupérer tous les chunks d'un fichier"""
        pass
    
    @abstractmethod
    async def get_by_project(self, project_id: str, skip: int = 0, limit: int = 100) -> List[ChunkModel]:
        """Récupérer les chunks d'un projet"""
        pass
    
    @abstractmethod
    async def delete_by_file(self, file_id: str) -> int:
        """Supprimer tous les chunks d'un fichier"""
        pass
    
    @abstractmethod
    async def search(self, project_id: str, query: str, limit: int = 10) -> List[ChunkModel]:
        """Rechercher des chunks par texte"""
        pass
    
    @abstractmethod
    async def store_langchain_chunks(self, project_id: str, file_id: str, chunks: List[Any]) -> int:
        """Stocker des chunks provenant de langchain"""
        pass