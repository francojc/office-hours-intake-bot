import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import app.chat as chat_module
import app.rag as rag_module
from app.chat import router as chat_router
from app.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    doc_count = rag_module.build_index()
    logger.info("Startup complete — RAG index: %d docs", doc_count)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(chat_router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model_path": str(settings.model_path),
        "model_loaded": chat_module._model is not None,
        "rag_index_loaded": rag_module._index is not None,
    }


app.mount("/static", StaticFiles(directory="static"), name="static")
