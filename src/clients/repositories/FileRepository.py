# clients/repositories/FileRepository.py
from pymongo import AsyncMongoClient
from datetime import datetime
from typing import Optional, Dict, List
import os
from helpers.logger import app_logger

logger = app_logger

class FileRepository:
    def __init__(self, db):
        self.db = db
        self.collection = db['files']

    async def register_file(self, file_id: str, project_id: str, filename: str, file_path: str, file_size: int) -> str:
        file_doc = {
            "file_id": file_id,
            "project_id": project_id,
            "filename": filename,
            "original_filename": os.path.basename(filename),
            "file_path": file_path,
            "file_size": file_size,
            "uploaded_at": datetime.utcnow(),
            "processed": False,
            "chunk_count": 0
        }
        await self.collection.insert_one(file_doc)
        logger.info(f"📄 Fichier enregistré: {file_id}")
        return file_id

    async def get_file(self, file_id: str) -> Optional[Dict]:
        return await self.collection.find_one({"file_id": file_id})

    async def update_file_status(self, file_id: str, processed: bool, chunk_count: Optional[int] = None) -> bool:
        update = {"$set": {"processed": processed}}
        if chunk_count is not None:
            update["$set"]["chunk_count"] = chunk_count
        result = await self.collection.update_one({"file_id": file_id}, update)
        return result.modified_count > 0

    async def get_project_files(self, project_id: str) -> List[Dict]:
        cursor = self.collection.find({"project_id": project_id}).sort("uploaded_at", -1)
        return await cursor.to_list(length=None)

    async def delete_file(self, file_id: str) -> bool:
        result = await self.collection.delete_one({"file_id": file_id})
        return result.deleted_count > 0