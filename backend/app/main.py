from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.documents import router as documents_router
from app.api.routes.health import router as health_router
from app.api.routes.qa import router as qa_router
from app.api.routes.search import router as search_router
from app.api.routes.summary import router as summary_router
from app.core.database import Base, engine
import app.db.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    del app
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="AI Document Analyst API", lifespan=lifespan)
app.include_router(health_router)
app.include_router(documents_router)
app.include_router(qa_router)
app.include_router(search_router)
app.include_router(summary_router)
