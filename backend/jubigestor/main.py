from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from jubigestor.api.routes import chat, health

app = FastAPI(
    title="Jubigestor API",
    version="0.1.0",
    description="Asistente para trámites jubilatorios argentinos",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router, prefix="/api")
