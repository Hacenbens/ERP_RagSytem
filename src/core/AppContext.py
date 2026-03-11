from fastapi import FastAPI
from contextlib import asynccontextmanager
from factories.DbFactory import DBClientFactory
from interfaces.IDBClientContext import IDBClientContext
from helpers.logger import app_logger
from helpers.config import get_settings

logger = app_logger
settings = get_settings()

class AppContext:
    """Contexte global de l'application"""
    
    def __init__(self):
        self.db_client: IDBClientContext = None
    
    async def startup(self):
        """Initialisation au démarrage"""
        logger.info("🚀 Démarrage de l'application...")
        
        # Initialiser MongoDB
        self.db_client = DBClientFactory.get_mongo_client()
        await self.db_client.connect()
        
        logger.info("✅ Application prête")
    
    async def shutdown(self):
        """Nettoyage à l'arrêt"""
        logger.info("🛑 Arrêt de l'application...")
        await DBClientFactory.close_all()

# Instance globale
app_context = AppContext()

async def get_db() -> IDBClientContext:
    """Retourne l'instance du client MongoDB (singleton)."""
    return app_context.db_client


# Lifespan manager pour FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    await app_context.startup()
    yield
    await app_context.shutdown()