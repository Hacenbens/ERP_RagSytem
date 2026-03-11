from pydantic import BaseModel,Field
from typing import Optional, List
from .base import MongoBaseModel

class ProjectSettings(BaseModel):
    """Paramètres d'un projet"""
    chunk_size: int = 400
    chunk_overlap: int = 20
    language: str = "fr"

class ProjectModel(MongoBaseModel):
    """Modèle pour les projets"""
    
    project_id: str = Field(..., index=True, unique=True)
    name: str
    description: Optional[str] = None
    settings: ProjectSettings = Field(default_factory=ProjectSettings)
    
    # Statistiques
    file_count: int = 0
    chunk_count: int = 0
    
    class Collection:
        name = "projects"
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": "proj_123",
                "name": "ERP Project",
                "description": "Description du projet"
            }
        }

class ProjectCreate(BaseModel):
    """DTO pour création de projet"""
    project_id: str
    name: str
    description: Optional[str] = None
    settings: Optional[ProjectSettings] = None

class ProjectUpdate(BaseModel):
    """DTO pour mise à jour de projet"""
    name: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[ProjectSettings] = None