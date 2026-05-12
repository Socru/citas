from fastapi import FastAPI
from . import models
from .database import engine
from .routers import rutas

# Esta línea crea todas las tablas en Postgres basándose en models.py
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SaaS Citas API",
    description="API para gestión de citas por WhatsApp",
    version="1.0.0"
)

app.include_router(rutas.router)

@app.get("/")
def read_root():
    return {"mensaje": "¡El servidor SaaS está vivo y conectado!"}