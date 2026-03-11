from pymongo import AsyncMongoClient
from datetime import datetime
from typing import List, Optional, Any
from helpers.logger import app_logger

from models.db_schemes.Chunk import ChunkModel, ChunkCreate, ChunkMetadata

logger = app_logger

class ChunkRepository:
    """Repository pour la gestion des chunks avec modèles Pydantic"""
    
    def __init__(self, db):
        self.db = db
        self.collection = db['chunks']
    
    async def create(self, chunk_data: ChunkCreate) -> ChunkModel:
        """Créer un chunk à partir du modèle Pydantic"""
        chunk = ChunkModel(
            text=chunk_data.text,
            metadata=chunk_data.metadata,
            embedding=chunk_data.embedding
        )
        
        await self.collection.insert_one(chunk.dict(by_alias=True))
        return chunk
    
    async def create_many(self, chunks_data: List[ChunkCreate]) -> List[ChunkModel]:
        """Créer plusieurs chunks en une opération"""
        if not chunks_data:
            return []
        
        chunks = []
        for chunk_data in chunks_data:
            chunk = ChunkModel(
                text=chunk_data.text,
                metadata=chunk_data.metadata,
                embedding=chunk_data.embedding
            )
            chunks.append(chunk)
        
        await self.collection.insert_many([c.dict(by_alias=True) for c in chunks])
        logger.info(f"📦 {len(chunks)} chunks créés")
        
        return chunks
    
    async def store_langchain_chunks(self, project_id: str, file_id: str, 
                                    langchain_chunks: List[Any]) -> List[ChunkModel]:
        """
        Convertir et stocker des chunks provenant de langchain
        C'est la méthode utilisée par votre ProcessController
        """
        chunks_data = []
        
        for i, chunk in enumerate(langchain_chunks):
            # Extraire le texte et les métadonnées du chunk langchain
            text = chunk.page_content if hasattr(chunk, 'page_content') else str(chunk)
            
            # Récupérer les métadonnées existantes ou en créer de nouvelles
            source_metadata = chunk.metadata if hasattr(chunk, 'metadata') else {}
            
            # Créer les métadonnées Pydantic
            metadata = ChunkMetadata(
                project_id=project_id,
                file_id=file_id,
                chunk_index=i,
                source_file=source_metadata.get('source'),
                chunk_size=len(text),
                overlap=None
            )
            
            # Créer le DTO ChunkCreate
            chunk_data = ChunkCreate(
                text=text,
                metadata=metadata
            )
            chunks_data.append(chunk_data)
        
        # Stocker en base
        return await self.create_many(chunks_data)
    
    async def get_by_id(self, chunk_id: str) -> Optional[ChunkModel]:
        """Récupérer un chunk par son ID MongoDB"""
        from bson import ObjectId
        try:
            doc = await self.collection.find_one({"_id": ObjectId(chunk_id)})
            return ChunkModel(**doc) if doc else None
        except:
            return None
    
    async def get_by_file(self, file_id: str) -> List[ChunkModel]:
        """Récupérer tous les chunks d'un fichier"""
        cursor = self.collection.find({"metadata.file_id": file_id}).sort("metadata.chunk_index", 1)
        chunks = []
        async for doc in cursor:
            chunks.append(ChunkModel(**doc))
        return chunks
    
    async def get_by_project(self, project_id: str, skip: int = 0, limit: int = 100) -> List[ChunkModel]:
        """Récupérer les chunks d'un projet"""
        cursor = self.collection.find({"metadata.project_id": project_id})
        cursor.sort("metadata.chunk_index", 1).skip(skip).limit(limit)
        
        chunks = []
        async for doc in cursor:
            chunks.append(ChunkModel(**doc))
        return chunks
    
    async def delete_by_file(self, file_id: str) -> int:
        """Supprimer tous les chunks d'un fichier"""
        result = await self.collection.delete_many({"metadata.file_id": file_id})
        return result.deleted_count
    
    async def search(self, project_id: str, query: str, limit: int = 10) -> List[ChunkModel]:
        """Rechercher des chunks par texte"""
        cursor = self.collection.find(
            {
                "metadata.project_id": project_id,
                "$text": {"$search": query}
            },
            {"score": {"$meta": "textScore"}}
        )
        cursor.sort([("score", {"$meta": "textScore"})]).limit(limit)
        
        chunks = []
        async for doc in cursor:
            chunk = ChunkModel(**doc)
            chunk.score = doc.get("score")
            chunks.append(chunk)
        return chunks
    
    async def count_by_file(self, file_id: str) -> int:
        """Compter les chunks d'un fichier"""
        return await self.collection.count_documents({"metadata.file_id": file_id})