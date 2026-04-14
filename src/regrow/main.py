from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .adapters.api.campaigns import router as campaigns_router
from .adapters.api.clients import router as clients_router
from .adapters.api.companies import router as companies_router
from .adapters.api.projects import router as projects_router
from .adapters.db.engine import create_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    create_db()
    yield


app = FastAPI(
    lifespan=lifespan,
)
app.include_router(companies_router)
app.include_router(clients_router)
app.include_router(projects_router)
app.include_router(campaigns_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok"}
