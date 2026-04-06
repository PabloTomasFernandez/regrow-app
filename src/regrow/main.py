from fastapi import FastAPI
from contextlib import asynccontextmanager
from .adapters.db.engine import create_db 
from collections.abc import AsyncIterator
from .adapters.api.companies import router as companies_router



@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    create_db()
    yield

app = FastAPI(lifespan=lifespan, )
app.include_router(companies_router)
@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok"}