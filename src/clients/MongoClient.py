from pymongo import AsyncMongoClient
from pymongo.errors import ConnectionFailure
from interfaces.IDBClientContext import IDBClientContext
from helpers.logger import app_logger
from datetime import datetime
from typing import List, Dict, Optional, Any
from clients.repositories.ProjectRepository import ProjectRepository
from clients.repositories.ChunkRepository import ChunkRepository
from clients.repositories.FileRepository import FileRepository
from models.db_schemes.Chunk import ChunkCreate, ChunkModel
from models.db_schemes.Project import ProjectCreate, ProjectModel, ProjectUpdate
import os

logger = app_logger
class MongoDBClient(IDBClientContext):
    """Implémentation MongoDB"""
    
    def __init__(self, connection_string: str, database_name: str):
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None
        #repositories
        self.projects: Optional[ProjectRepository] = None
        self.chunks: Optional[ChunkRepository] = None
        self.files: Optional[FileRepository] = None
    
    async def connect(self):
        try:
            self.client = AsyncMongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            self.projects = ProjectRepository(db=self.db)
            self.chunks = ChunkRepository(db=self.db)
            self.files = FileRepository(db=self.db) 
            await self.client.admin.command('ping')
            logger.info(f"✅ MongoDB connecté: {self.database_name}")
        except ConnectionFailure as e:
            logger.error(f"❌ Échec connexion MongoDB: {e}")
            raise
    
    async def _create_indexes(self):
        """Créer les indexes"""
        try:
            # Index pour chunks
            chunks_collection = self.db['chunks']
            await chunks_collection.create_index([("metadata.project_id", 1), ("metadata.file_id", 1)])
            await chunks_collection.create_index([("metadata.file_id", 1)])
            await chunks_collection.create_index([("text", "text")])
            
            # Index pour projects
            projects_collection = self.db['projects']
            await projects_collection.create_index("project_id", unique=True)
            
            logger.info("📑 Indexes MongoDB créés")
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur lors de la création des indexes: {e}")
        
    
    async def disconnect(self):
        if self.client:
            self.client.close()
            logger.info("🔌 MongoDB déconnecté")
    
    async def health_check(self) -> bool:
        try:
            if self.client:
                await self.client.admin.command('ping')
                return True
            return False
        except Exception as e:
            return False
    
     # ===== Méthodes Projets avec Pydantic =====
    
    async def create_project(self, project_data: ProjectCreate) -> ProjectModel:
        """Créer un projet"""
        return await self.projects.create(project_data)
    
    async def get_project(self, project_id: str) -> Optional[ProjectModel]:
        """Récupérer un projet"""
        return await self.projects.get_by_id(project_id)
    
    async def get_all_projects(self, skip: int = 0, limit: int = 100) -> List[ProjectModel]:
        """Récupérer tous les projets"""
        return await self.projects.get_all(skip, limit)
    
    async def update_project(self, project_id: str, update_data: ProjectUpdate) -> Optional[ProjectModel]:
        """Mettre à jour un projet"""
        return await self.projects.update(project_id, update_data)
    
    async def delete_project(self, project_id: str) -> bool:
        """Supprimer un projet"""
        # Supprimer d'abord tous les chunks associés
        await self.chunks.delete_by_project(project_id)  # À implémenter si nécessaire
        
        # Supprimer tous les fichiers associés
        files = await self.files.get_project_files(project_id)
        for file in files:
            await self.files.delete_file(file["file_id"])
        
        # Supprimer le projet
        return await self.projects.delete(project_id)
    
    # ===== Méthodes Chunks avec Pydantic =====
    
    async def store_chunks(self, project_id: str, file_id: str, 
                          langchain_chunks: List[Any]) -> List[ChunkModel]:
        """
        Stocker des chunks provenant de langchain
        C'est la méthode appelée par votre ProcessController
        """
        return await self.chunks.store_langchain_chunks(project_id, file_id, langchain_chunks)
    
    async def create_chunk(self, chunk_data: ChunkCreate) -> ChunkModel:
        """Créer un chunk"""
        chunk = await self.chunks.create(chunk_data)
        
        # Mettre à jour les compteurs
        await self.projects.increment_chunk_count(chunk_data.metadata.project_id)
        
        file = await self.files.get_file(chunk_data.metadata.file_id)
        if file:
            await self.files.update_file_status(
                chunk_data.metadata.file_id, 
                processed=True, 
                chunk_count=(file.get("chunk_count", 0) + 1)
            )
        
        return chunk
    
    async def get_project_chunks(self, project_id: str, skip: int = 0, 
                                limit: int = 100) -> List[ChunkModel]:
        """Récupérer les chunks d'un projet"""
        return await self.chunks.get_by_project(project_id, skip, limit)
    
    async def get_file_chunks(self, file_id: str) -> List[ChunkModel]:
        """Récupérer les chunks d'un fichier"""
        return await self.chunks.get_by_file(file_id)
    
    async def delete_file_chunks(self, file_id: str) -> int:
        """Supprimer les chunks d'un fichier"""
        # Récupérer le fichier pour avoir le project_id
        file = await self.files.get_file(file_id)
        
        # Supprimer les chunks
        deleted = await self.chunks.delete_by_file(file_id)
        
        # Mettre à jour les compteurs
        if file and deleted > 0:
            await self.projects.increment_chunk_count(file["project_id"], -deleted)
            await self.files.update_file_status(file_id, processed=False, chunk_count=0)
        
        return deleted
    
    async def search_chunks(self, project_id: str, query: str, limit: int = 10) -> List[ChunkModel]:
        """Rechercher des chunks par texte"""
        return await self.chunks.search(project_id, query, limit)
    
    
    async def register_file(self, file_id: str, project_id: str,
                        filename: str, file_path: str, file_size: int) -> str:
        return await self.files.register_file(file_id, project_id, filename, file_path, file_size)

    async def get_file(self, file_id: str) -> Optional[Dict]:
        return await self.files.get_file(file_id)

    async def update_file_status(self, file_id: str, processed: bool,
                                chunk_count: Optional[int] = None) -> bool:
        return await self.files.update_file_status(file_id, processed, chunk_count)