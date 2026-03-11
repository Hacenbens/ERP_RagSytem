from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import TypeVar, Generic, Type, Optional, List
from pydantic import BaseModel
from bson import ObjectId
import logging
import datetime


logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class BaseRepository(Generic[T]):
    """Repository de base avec opérations CRUD génériques"""
    
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str, model_class: Type[T]):
        self.db = db
        self.collection = db[collection_name]
        self.model_class = model_class
    
    async def insert_one(self, document: T) -> T:
        """Insérer un document"""
        doc_dict = document.dict(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(doc_dict)
        document.id = result.inserted_id
        logger.debug(f"Document inséré dans {self.collection.name}: {result.inserted_id}")
        return document
    
    async def insert_many(self, documents: List[T]) -> List[ObjectId]:
        """Insérer plusieurs documents"""
        docs_dict = [doc.dict(by_alias=True, exclude={"id"}) for doc in documents]
        result = await self.collection.insert_many(docs_dict)
        logger.debug(f"{len(result.inserted_ids)} documents insérés dans {self.collection.name}")
        return result.inserted_ids
    
    async def find_one(self, filter: dict) -> Optional[T]:
        """Trouver un document"""
        doc = await self.collection.find_one(filter)
        if doc:
            return self.model_class(**doc)
        return None
    
    async def find_many(self, filter: dict, skip: int = 0, limit: int = 100, sort: list = None) -> List[T]:
        """Trouver plusieurs documents"""
        cursor = self.collection.find(filter).skip(skip).limit(limit)
        if sort:
            cursor = cursor.sort(sort)
        
        results = []
        async for doc in cursor:
            results.append(self.model_class(**doc))
        return results
    
    async def update_one(self, filter: dict, update: dict) -> bool:
        """Mettre à jour un document"""
        if "$set" in update:
            update["$set"]["updated_at"] = datetime.utcnow()
        else:
            update = {"$set": {**update, "updated_at": datetime.utcnow()}}
        
        result = await self.collection.update_one(filter, update)
        return result.modified_count > 0
    
    async def delete_one(self, filter: dict) -> bool:
        """Supprimer un document"""
        result = await self.collection.delete_one(filter)
        return result.deleted_count > 0
    
    async def delete_many(self, filter: dict) -> int:
        """Supprimer plusieurs documents"""
        result = await self.collection.delete_many(filter)
        return result.deleted_count
    
    async def count(self, filter: dict = None) -> int:
        """Compter les documents"""
        return await self.collection.count_documents(filter or {})