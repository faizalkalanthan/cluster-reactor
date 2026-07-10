from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.db.bootstrap import initialize_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield

app = FastAPI(
    title="Cluster Reactor API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.include_router(api_router)


@app.get("/", tags=["root"])
def root() -> dict:
    return {
        "service": settings.app_name,
        "status": "running",
        "version": settings.app_version,
    }