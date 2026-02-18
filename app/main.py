from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import app.chat as chat_module
from app.chat import router as chat_router
from app.config import settings

app = FastAPI(title=settings.app_name)
app.include_router(chat_router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model_path": str(settings.model_path),
        "model_loaded": chat_module._model is not None,
    }


app.mount("/static", StaticFiles(directory="static"), name="static")
