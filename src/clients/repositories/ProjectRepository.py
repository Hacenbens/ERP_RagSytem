from pymongo import AsyncMongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from typing import List, Optional
from helpers.logger import app_logger

from models.db_schemes.Project import ProjectModel, ProjectCreate, ProjectUpdate , ProjectSettings

logger = app_logger

class ProjectRepository:
    """Repository pour la gestion des projets avec modèles Pydantic"""
    
    def __init__(self, db):
        self.db = db
        self.collection = db['projects']
    
    async def create(self, project_data: ProjectCreate) -> ProjectModel:
        """Créer un projet à partir du modèle Pydantic"""
        # Vérifier si le projet existe déjà
        existing = await self.collection.find_one({"project_id": project_data.project_id})
        if existing:
            raise ValueError(f"Le projet {project_data.project_id} existe déjà")
        
        # Créer le modèle avec les valeurs par défaut
        project = ProjectModel(
            project_id=project_data.project_id,
            name=project_data.name,
            description=project_data.description,
            settings=project_data.settings or ProjectSettings()
        )
        
        # Insérer dans MongoDB
        await self.collection.insert_one(project.dict(by_alias=True))
        logger.info(f"📁 Projet créé: {project_data.project_id}")
        
        return project
    
    async def get_by_id(self, project_id: str) -> Optional[ProjectModel]:
        """Récupérer un projet par son ID"""
        doc = await self.collection.find_one({"project_id": project_id})
        return ProjectModel(**doc) if doc else None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ProjectModel]:
        """Récupérer tous les projets"""
        cursor = self.collection.find().skip(skip).limit(limit).sort("created_at", -1)
        projects = []
        async for doc in cursor:
            projects.append(ProjectModel(**doc))
        return projects
    
    async def update(self, project_id: str, update_data: ProjectUpdate) -> Optional[ProjectModel]:
        """Mettre à jour un projet"""
        # Préparer les données de mise à jour
        update_dict = update_data.dict(exclude_unset=True)
        if not update_dict:
            return await self.get_by_id(project_id)
        
        update_dict["updated_at"] = datetime.utcnow()
        
        # Mettre à jour
        result = await self.collection.update_one(
            {"project_id": project_id},
            {"$set": update_dict}
        )
        
        if result.modified_count > 0:
            logger.info(f"📝 Projet mis à jour: {project_id}")
            return await self.get_by_id(project_id)
        
        return await self.get_by_id(project_id)
    
    async def delete(self, project_id: str) -> bool:
        """Supprimer un projet"""
        result = await self.collection.delete_one({"project_id": project_id})
        if result.deleted_count > 0:
            logger.info(f"🗑️ Projet supprimé: {project_id}")
            return True
        return False
    
    async def increment_file_count(self, project_id: str) -> bool:
        """Incrémenter le compteur de fichiers"""
        result = await self.collection.update_one(
            {"project_id": project_id},
            {"$inc": {"file_count": 1}, "$set": {"updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    async def increment_chunk_count(self, project_id: str, count: int = 1) -> bool:
        """Incrémenter le compteur de chunks"""
        result = await self.collection.update_one(
            {"project_id": project_id},
            {"$inc": {"chunk_count": count}, "$set": {"updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0