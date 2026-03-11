from pydantic import Field , BaseModel
from typing import Optional, List, Dict, Any
from .base import MongoBaseModel

class ChunkMetadata(BaseModel):
    """Métadonnées d'un chunk"""
    project_id: str
    file_id: str
    chunk_index: int
    source_file: Optional[str] = None
    chunk_size: int
    overlap: Optional[int] = None

class ChunkModel(MongoBaseModel):
    """Modèle pour les chunks"""
    
    text: str
    metadata: ChunkMetadata
    embedding: Optional[List[float]] = None
    
    class Collection:
        name = "chunks"

class ChunkCreate(BaseModel):
    """DTO pour création de chunk"""
    text: str
    metadata: ChunkMetadata
    embedding: Optional[List[float]] = None