import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

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
    ollama_ok = False
    ollama_model_available = False
    try:
        async with httpx.AsyncClient(
            base_url=settings.ollama_base_url,
            timeout=5.0,
        ) as client:
            resp = await client.get("/api/tags")
            if resp.status_code == 200:
                ollama_ok = True
                models = resp.json().get("models", [])
                ollama_model_available = any(
                    m.get("name", "").startswith(
                        settings.ollama_model
                    )
                    for m in models
                )
    except httpx.ConnectError:
        pass

    return {
        "status": "ok" if ollama_ok else "degraded",
        "ollama_url": settings.ollama_base_url,
        "ollama_reachable": ollama_ok,
        "ollama_model": settings.ollama_model,
        "ollama_model_available": ollama_model_available,
        "rag_index_loaded": rag_module._index is not None,
    }


app.mount("/static", StaticFiles(directory="static"), name="static")
