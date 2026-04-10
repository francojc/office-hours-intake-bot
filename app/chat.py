import logging
import re
from pathlib import Path

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.rag import retrieve_context

logger = logging.getLogger(__name__)

router = APIRouter()

_system_prompt_template: str | None = None

SYSTEM_PROMPT_PATH = Path("docs/system-prompt.md")


def _load_system_prompt() -> str:
    """Load and cache the system prompt template from docs/."""
    global _system_prompt_template
    if _system_prompt_template is None:
        if not SYSTEM_PROMPT_PATH.exists():
            logger.warning(
                "System prompt file %s not found, using fallback",
                SYSTEM_PROMPT_PATH,
            )
            _system_prompt_template = (
                "You are a helpful assistant.\n\n{{retrieved_context}}"
            )
        else:
            raw = SYSTEM_PROMPT_PATH.read_text()
            match = re.search(
                r"^## Prompt\s*\n+```\n(.*?)```",
                raw,
                re.DOTALL | re.MULTILINE,
            )
            if match:
                _system_prompt_template = match.group(1).rstrip("\n")
            else:
                _system_prompt_template = raw
    return _system_prompt_template


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    context = retrieve_context(request.message)
    system_prompt = _load_system_prompt().replace(
        "{{retrieved_context}}", context
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": request.message},
    ]

    try:
        async with httpx.AsyncClient(
            base_url=settings.ollama_base_url,
            timeout=120.0,
        ) as client:
            response = await client.post(
                "/api/chat",
                json={
                    "model": settings.ollama_model,
                    "messages": messages,
                    "stream": False,
                    "options": {"num_predict": 256},
                },
            )
            response.raise_for_status()
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail=(
                f"Cannot connect to Ollama at "
                f"{settings.ollama_base_url}"
            ),
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Ollama returned {e.response.status_code}",
        )

    data = response.json()
    reply = data.get("message", {}).get("content", "")
    return ChatResponse(reply=reply)
