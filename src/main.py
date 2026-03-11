from fastapi import FastAPI, Depends
from core.AppContext import lifespan, app_context
from interfaces.IDBClientContext import IDBClientContext
from routes import data_route,base_router # vos routes existantes

# Créer l'app FastAPI avec le lifespan
app = FastAPI(
    title="ERP RAG System",
    version="1.0.0",
    lifespan=lifespan
)

# Dépendance pour injecter le client DB
async def get_db() -> IDBClientContext:
    return app_context.db_client

# Route de santé
@app.get("/health")
async def health_check(db: IDBClientContext = Depends(get_db)):
    db_status = await db.health_check()
    return {
        "status": "ok",
        "database": "connected" if db_status else "disconnected",
        "version": "1.0.0"
    }

# Inclure vos routes existantes
app.include_router(data_route)
app.include_router(base_router)

