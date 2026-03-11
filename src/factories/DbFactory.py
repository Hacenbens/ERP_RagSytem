from interfaces.IDBClientContext import IDBClientContext
from clients.MongoClient import MongoDBClient
from helpers.logger import app_logger
from helpers.config import get_settings



logger = app_logger
_settings = get_settings()

class DBClientFactory:
    """Factory pour créer des clients DB"""
    
    _clients = {}
    
    @classmethod
    def get_mongo_client(cls) -> IDBClientContext:
        """Obtenir un client MongoDB (singleton)"""
        key = "mongodb_default"
        
        if key not in cls._clients:
            # Construire l'URI depuis la config
            uri = f"mongodb://{_settings.MONGO_APP_USER}:{_settings.MONGO_APP_PASSWORD}@localhost:27017/{_settings.MONGODB_DATABASE}?authSource={_settings.MONGODB_DATABASE}"
            
            cls._clients[key] = MongoDBClient(
                connection_string=uri,
                database_name=_settings.MONGODB_DATABASE
            )
            logger.info("🏭 Client MongoDB créé")
        
        return cls._clients[key]
    
    @classmethod
    async def close_all(cls):
        """Fermer tous les clients"""
        for client in cls._clients.values():
            await client.disconnect()
        cls._clients.clear()