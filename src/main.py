from fastapi import FastAPI
from routes import base,data  # noqa: E402


app = FastAPI()

app.include_router(base.base_router)
app.include_router(data.data_route)